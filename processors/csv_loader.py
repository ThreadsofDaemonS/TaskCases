# processors/csv_loader.py

# reader = csv.DictReader(f, delimiter="\t")

import csv
import zipfile
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.database import SessionLocal, Court, Stage, Case
from sqlalchemy import select
from utils.normalizer import parse_date

DATA_DIR = Path(__file__).parent.parent / "data"
CSV_DIR = DATA_DIR / "csv"
CSV_DIR.mkdir(parents=True, exist_ok=True)

def unzip(zip_path: Path) -> list[Path]:
    csv_paths = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(CSV_DIR)
        for file in zip_ref.namelist():
            if file.endswith(".csv"):
                csv_paths.append(CSV_DIR / file)
    return csv_paths

def insert_or_get(session: Session, model, name: str):
    instance = session.query(model).filter_by(name=name).first()
    if instance:
        return instance
    instance = model(name=name)
    session.add(instance)
    session.flush()
    return instance

def process_csv_file(csv_path: Path):
    print(f"📥 Обробка CSV: {csv_path.name}")
    session = SessionLocal()
    count = 0
    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            # print("🧾 Заголовки в CSV:", reader.fieldnames)

            for row in reader:
                try:
                    court_name = row.get("court_name") or "Невідомо"
                    stage_name = row.get("stage_name") or "Невідомо"
                    case_number = row.get("case_number") or None
                    plaintiff = row.get("plaintiff") or None
                    defendant = row.get("defendant") or None
                    date_str = row.get("registration_date") or None

                    if not any([court_name, stage_name, case_number, date_str]):
                        continue  # Повністю пустий — пропускаємо

                    court = insert_or_get(session, Court, court_name)
                    stage = insert_or_get(session, Stage, stage_name)

                    case = Case(
                        case_number=case_number,
                        plaintiff=plaintiff,
                        defendant=defendant,
                        date=parse_date(date_str) if date_str else None,
                        court=court,
                        stage=stage
                    )
                    session.add(case)
                    count += 1

                except IntegrityError:
                    session.rollback()
                except Exception as e:
                    print(f"❌ Помилка в рядку: {e}")
        session.commit()
        print(f"✅ Додано {count} справ із {csv_path.name}")
    except Exception as e:
        print(f"❌ Загальна помилка при обробці {csv_path.name}: {e}")
    finally:
        session.close()
        os.remove(csv_path)

def process_zip_file(zip_path: Path):
    try:
        csv_paths = unzip(zip_path)
        for csv_file in csv_paths:
            process_csv_file(csv_file)
    except Exception as e:
        print(f"❌ Помилка при обробці ZIP {zip_path.name}: {e}")
    finally:
        try:
            os.remove(zip_path)
        except Exception as e:
            print(f"⚠️ Не вдалося видалити ZIP: {zip_path} — {e}")
