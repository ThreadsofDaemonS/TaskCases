import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm.asyncio import tqdm

BASE_URL = "https://dsa.court.gov.ua/dsa/inshe/oddata/532/?page="
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

MAX_CONCURRENT_DOWNLOADS = 3
TIMEOUT = aiohttp.ClientTimeout(total=800)
semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


async def fetch_html(session, page):
    url = f"{BASE_URL}{page}"
    async with session.get(url) as resp:
        return await resp.text()


async def extract_zip_links(session, page):
    html = await fetch_html(session, page)
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True, download=True):
        if ".zip" in a["href"] and "2025" in a["download"]:
            href = a["href"]
            filename = a["download"]
            links.append((href, filename))

    return links


async def download_zip(session, url, filename, retries=3):
    save_path = DATA_DIR / filename
    if save_path.exists():
        return

    for attempt in range(1, retries + 1):
        try:
            async with semaphore:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(save_path, "wb") as f:
                            while chunk := await resp.content.read(1024):
                                f.write(chunk)
                        return
                    else:
                        print(f"⚠️ Статус {resp.status} при скачуванні {filename}")
        except Exception as e:
            print(f"❌ Спроба {attempt}/{retries} не вдалася для {filename}: {e}")
            await asyncio.sleep(3)

    print(f"⛔ Повна невдача: {filename}")


async def main():
    print("🔎 Пошук архівів .zip за 2025 рік...")

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        all_links = []

        for page in range(1, 100):
            links = await extract_zip_links(session, page)
            if not links:
                break
            all_links.extend(links)

        print(f"🔽 Завантаження архівів: {len(all_links)}")

        tasks = [download_zip(session, url, filename) for url, filename in all_links]
        await tqdm.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
