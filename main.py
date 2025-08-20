import asyncio
from processors.zip_downloader_async import download_all_zips

if __name__ == "__main__":
    asyncio.run(download_all_zips())
