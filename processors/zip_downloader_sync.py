import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import time

BASE_URL = "https://dsa.court.gov.ua/dsa/inshe/oddata/532/?page="
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 800


def extract_zip_links(page):
    url = f"{BASE_URL}{page}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=True, download=True):
        if ".zip" in a["href"] and "2025" in a["download"]:
            links.append((a["href"], a["download"]))

    return links


def download_zip(url, filename, retries=3):
    save_path = DATA_DIR / filename
    if save_path.exists():
        return

    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=TIMEOUT) as r:
                if r.status_code == 200:
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    return
                else:
                    print(f"⚠️ Статус {r.status_code} при скачуванні {filename}")
        except Exception as e:
            print(f"❌ Спроба {attempt}/{retries} не вдалася для {filename}: {e}")
            time.sleep(3)

    print(f"⛔ Повна невдача: {filename} ({url})")


def main():
    print("🔎 Пошук архівів .zip за 2025 рік...")

    all_links = []
    for page in range(1, 100):
        links = extract_zip_links(page)
        if not links:
            break
        all_links.extend(links)

    print(f"🔽 Завантаження архівів: {len(all_links)}")

    for url, filename in tqdm(all_links):
        download_zip(url, filename)


if __name__ == "__main__":
    main()
