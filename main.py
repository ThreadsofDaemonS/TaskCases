from db.database import Base, engine
from processors.zip_downloader_async import download_all_zips

if __name__ == "__main__":
    # Створення таблиць у БД
    Base.metadata.create_all(bind=engine)

    # Асинхронне завантаження ZIP-файлів (сам завантажувач залишився асинхронним)
    import asyncio
    asyncio.run(download_all_zips())
