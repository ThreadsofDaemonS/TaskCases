# processors/zip_downloader_async.py

# for a in soup.find_all("a", href=True, download=True):
#     download = a.get("download", "")
#     href = a["href"]
#
#     if not download.lower().endswith(".zip"):
#         continue
#     if "2025" not in download:
#         continue
#
#     links.append((href, download))
#
# return links



import aiohttp
import asyncio
from pathlib import Path
import mimetypes
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm
from processors.csv_loader import process_zip_file, process_csv_file
import zipfile  # ⬅️ додано для перехоплення BadZipFile

BASE_URL = "https://dsa.court.gov.ua/dsa/inshe/oddata/532/?page="
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

MAX_CONCURRENT_DOWNLOADS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
TIMEOUT = aiohttp.ClientTimeout(total=900)

async def fetch_html(session, page: int) -> str:
    url = f"{BASE_URL}{page}"
    async with session.get(url) as response:
        return await response.text()

async def extract_zip_links(session, page: int):
    html = await fetch_html(session, page)
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True, download=True):
        download = a.get("download", "")
        href = a["href"]

        if not download.lower().endswith(".zip"):
            continue
        if "2025" not in download:
            continue

        links.append((href, download))

    return links

async def get_last_page(session) -> int:
    html = await fetch_html(session, 1)
    soup = BeautifulSoup(html, "html.parser")
    pages = []

    for a in soup.find_all("a", href=True):
        if "?page=" in a["href"]:
            try:
                pages.append(int(a["href"].split("?page=")[-1]))
            except ValueError:
                continue
    return max(pages) if pages else 1

async def download_and_process(session, href: str, filename: str):
    zip_url = href if href.startswith("http") else f"https://court.gov.ua{href}"
    zip_path = DATA_DIR / filename

    if zip_path.exists():
        await handle_file(zip_path)
        return

    try:
        async with semaphore:
            async with session.get(zip_url) as resp:
                if resp.status == 200:
                    with open(zip_path, "wb") as f:
                        while chunk := await resp.content.read(1024):
                            f.write(chunk)
                    await handle_file(zip_path)
                else:
                    print(f"⚠️ Статус {resp.status} для {filename}")
    except Exception as e:
        print(f"❌ Помилка при скачуванні {filename}: {e}")

async def handle_file(zip_path: Path):
    mime_type, _ = mimetypes.guess_type(zip_path)
    ext = zip_path.suffix.lower()

    try:
        if ext == ".zip":
            try:
                await process_zip_file(zip_path)
            except zipfile.BadZipFile:
                print(f"❌ {zip_path.name} — невалідний ZIP")
        elif ext == ".csv" or mime_type == "text/csv":
            await process_csv_file(zip_path)
        else:
            print(f"⚠️ Пропущено файл (невідомий тип): {zip_path}")
    except Exception as e:
        print(f"❌ Помилка при обробці {zip_path.name}: {e}")

async def download_all_zips():
    print("🔎 Пошук архівів .zip за 2025 рік...")
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        last_page = await get_last_page(session)
        print(f"📄 Виявлено сторінок: {last_page}")

        all_links = []
        for page in range(1, last_page + 1):
            links = await extract_zip_links(session, page)
            all_links.extend(links)

        print(f"🔽 Завантаження архівів: {len(all_links)}")
        tasks = [download_and_process(session, href, filename) for href, filename in all_links]
        await tqdm.gather(*tasks)
