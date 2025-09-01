from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.database import SessionLocal, Case
import pandas as pd


def search_cases(df: pd.DataFrame):
    if "case_number" not in df.columns:
        print("❌ DataFrame не містить колонки 'case_number'")
        return

    # Очищення: пробіли, \n, \t
    df["case_number"] = df["case_number"].astype(str).str.strip()
    df["case_number"] = df["case_number"].str.replace(r"\s+", "", regex=True)

    case_numbers = df["case_number"].dropna().unique().tolist()
    total = len(case_numbers)

    if total == 0:
        print("❌ Жодного коректного номера справи не знайдено")
        return

    print(f"🔍 Пошук {total} справ у базі...")

    CHUNK_SIZE = 900
    all_results = []

    with SessionLocal() as session:
        for i in range(0, total, CHUNK_SIZE):
            chunk = case_numbers[i:i + CHUNK_SIZE]
            stmt = (
                select(Case)
                .options(
                    selectinload(Case.court),
                    selectinload(Case.stage)
                )
                .where(Case.case_number.in_(chunk))
            )
            chunk_results = session.execute(stmt).scalars().all()

            for case in chunk_results:
                all_results.append({
                    "case_number": case.case_number,
                    "court": case.court.name if case.court else "–",
                    "stage": case.stage.name if case.stage else "–",
                })

    print(f"✅ Знайдено {len(all_results)} збігів")
    print("🔎 Перші 10 збігів:")
    for row in all_results[:10]:
        print(f"➡ {row['case_number']} ({row['court']}, {row['stage']})")
