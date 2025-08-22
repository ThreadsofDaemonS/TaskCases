import csv
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.database import Case, Court, Stage, Base

DB_PATH = "sqlite:///./cases.db"

def read_case_numbers_from_csv(csv_path: Path) -> set[str]:
    case_numbers = set()
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            number = row.get("case_number")
            if number:
                case_numbers.add(number.strip())
    return case_numbers

def search_cases(csv_path: Path):
    engine = create_engine(DB_PATH, echo=False)
    session = Session(engine)

    case_numbers = read_case_numbers_from_csv(csv_path)
    if not case_numbers:
        print("⚠️ Немає номерів справ у CSV.")
        return

    print(f"🔍 Пошук {len(case_numbers)} справ у базі...")
    stmt = select(Case).where(Case.case_number.in_(case_numbers)).join(Court).join(Stage)

    results = session.execute(stmt).scalars().all()

    if not results:
        print("❌ Не знайдено збігів.")
        return

    print(f"✅ Знайдено {len(results)} збіг(ів):")
    for case in results:
        print(f"📁 {case.case_number} | Суд: {case.court.name} | Стадія: {case.stage.name} | Дата: {case.date}")
