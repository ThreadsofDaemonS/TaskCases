from pathlib import Path
from queries.case_search import search_cases
import pandas as pd

SEARCH_DIR = Path("search_input")

def choose_file():
    if not SEARCH_DIR.exists():
        print(f"❌ Папка {SEARCH_DIR} не існує")
        return

    files = list(SEARCH_DIR.glob("*.csv")) + list(SEARCH_DIR.glob("*.xlsx"))
    if not files:
        print(f"❌ У папці '{SEARCH_DIR}' немає CSV або XLSX-файлів")
        return

    print(f"📁 Файли у папці '{SEARCH_DIR.name}':")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file.name}")

    choice = input("Оберіть номер або введіть шлях: ").strip()
    try:
        index = int(choice)
        file_path = files[index - 1]
    except (ValueError, IndexError):
        file_path = Path(choice)

    if not file_path.exists():
        print(f"❌ Файл {file_path} не знайдено")
        return

    try:
        case_numbers = extract_case_numbers(file_path)
    except Exception as e:
        print(f"❌ Помилка при читанні файлу: {e}")
        return

    search_cases(case_numbers)

def extract_case_numbers(file_path: Path) -> list[str]:
    if file_path.suffix.lower() == ".csv":
        # Пробуємо прочитати з урахуванням BOM і різних кодувань
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
    elif file_path.suffix.lower() == ".xlsx":
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Непідтримуваний формат файлу")

    # Перша колонка — з номерами справ
    first_column = df.columns[0]
    return df[first_column].dropna().astype(str).tolist()

if __name__ == "__main__":
    choose_file()
