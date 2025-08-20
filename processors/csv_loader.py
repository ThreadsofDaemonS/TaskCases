import zipfile
import chardet
import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CSV_DIR = DATA_DIR / "csv"
CSV_DIR.mkdir(parents=True, exist_ok=True)

def detect_encoding(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        raw = f.read(10000)
    result = chardet.detect(raw)
    return result['encoding'] or 'utf-8'

def process_zip_file(zip_path: Path):
    if not zip_path.exists():
        print(f"⚠️ Файл не знайдено: {zip_path}")
        return

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)

        for csv_file in DATA_DIR.glob("*.csv"):
            encoding = detect_encoding(csv_file)
            print(f"📄 Обробка {csv_file.name} (кодування: {encoding})")

            with open(csv_file, encoding=encoding) as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    print(row)
                    if i >= 2:  # лише перші 3 рядки
                        break
    except Exception as e:
        print(f"❌ Помилка при обробці {zip_path.name}: {e}")
