# run_search.py

from pathlib import Path
from queries.case_search import search_cases

SEARCH_DIR = Path("search_input")

def choose_csv():
    if not SEARCH_DIR.exists():
        print(f"❌ Папка {SEARCH_DIR} не існує")
        return

    files = list(SEARCH_DIR.glob("*.csv"))
    if not files:
        print(f"❌ У папці '{SEARCH_DIR}' немає CSV-файлів")
        return

    print(f"📁 Файли у папці '{SEARCH_DIR.name}':")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file.name}")

    choice = input("Оберіть номер або введіть шлях до CSV: ").strip()
    try:
        index = int(choice)
        csv_path = files[index - 1]
    except (ValueError, IndexError):
        csv_path = Path(choice)

    if not csv_path.exists():
        print(f"❌ Файл {csv_path} не знайдено")
        return

    search_cases(csv_path)

if __name__ == "__main__":
    choose_csv()
