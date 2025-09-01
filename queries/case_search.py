from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.database import SessionLocal, Case, Court, Stage

def search_cases(case_numbers: list[str]):
    total = len(case_numbers)
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
