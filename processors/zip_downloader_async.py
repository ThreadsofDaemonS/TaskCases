import aiohttp
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm

from processors.csv_loader import process_zip_file

BASE_URL = "https://dsa.court.gov.ua/dsa/inshe/oddata/532/?page="
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

MAX_CONCURRENT_DOWNLOADS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
TIMEOUT = aiohttp.ClientTimeout(total=800)

async def fetch_html(session, page: int) -> str:
    url = f"{BASE_URL}{page}"
    async with session.get(url) as response:
        return await response.text()

async def extract_zip_links(session, page: int):
    html = await fetch_html(session, page)
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True, download=True):
        if ".zip" in a["href"] and "2025" in a["download"]:
            href = a["href"]
            filename = a["download"]
            links.append((href, filename))

    return links

async def download_and_process(session, href: str, filename: str):
    zip_url = href if href.startswith("http") else f"https://court.gov.ua{href}"
    zip_path = DATA_DIR / filename

    if zip_path.exists():
        return await asyncio.to_thread(process_zip_file, zip_path)

    try:
        async with semaphore:
            async with session.get(zip_url) as resp:
                if resp.status == 200:
                    with open(zip_path, "wb") as f:
                        while chunk := await resp.content.read(1024):
                            f.write(chunk)

                    await asyncio.to_thread(process_zip_file, zip_path)
                else:
                    print(f"⚠️ Статус {resp.status} для {filename}")
    except Exception as e:
        print(f"❌ Помилка при скачуванні {filename}: {e}")

async def download_all_zips():
    print("🔎 Пошук архівів .zip за 2025 рік...")

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        all_links = []

        for page in range(1, 100):
            links = await extract_zip_links(session, page)
            if not links:
                break
            all_links.extend(links)

        print(f"🔽 Завантаження архівів: {len(all_links)}")
        tasks = [download_and_process(session, href, filename) for href, filename in all_links]
        await tqdm.gather(*tasks)
