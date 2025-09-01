from pathlib import Path
import pandas as pd
from queries.case_search import search_cases

SEARCH_DIR = Path("search_input")

def read_file(path: Path) -> pd.DataFrame | None:
    try:
        if path.suffix.lower() == ".csv":
            try:
                return pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
            except UnicodeDecodeError:
                return pd.read_csv(path, encoding="cp1251", on_bad_lines="skip")
        elif path.suffix.lower() == ".xlsx":
            return pd.read_excel(path)
        else:
            print(f"❌ Непідтримуваний формат: {path.suffix}")
            return None
    except Exception as e:
        print(f"❌ Помилка при читанні файлу: {e}")
        return None

def choose_file():
    if not SEARCH_DIR.exists():
        print(f"❌ Папка {SEARCH_DIR} не існує")
        return

    files = list(SEARCH_DIR.glob("*.csv")) + list(SEARCH_DIR.glob("*.xlsx"))
    if not files:
        print(f"❌ У папці '{SEARCH_DIR.name}' немає CSV або XLSX-файлів")
        return

    print(f"📁 Файли у папці '{SEARCH_DIR.name}':")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file.name}")

    choice = input("Оберіть номер або введіть шлях до файлу: ").strip()
    try:
        index = int(choice)
        file_path = files[index - 1]
    except (ValueError, IndexError):
        file_path = Path(choice)

    if not file_path.exists():
        print(f"❌ Файл {file_path} не знайдено")
        return

    df = read_file(file_path)
    if df is None or df.empty:
        print("❌ Неможливо прочитати дані з файлу або файл порожній")
        return

    # Визначимо колонку з номерами справ
    case_column = None
    for col in df.columns:
        if "case" in str(col).lower() and "number" in str(col).lower():
            case_column = col
            break

    # Якщо не знайшли — візьмемо першу колонку
    if case_column is None:
        case_column = df.columns[0]

    # Створимо новий DataFrame з нормалізованими номерами справ
    try:
        df = df[[case_column]].rename(columns={case_column: "case_number"})
    except Exception as e:
        print(f"❌ Не вдалося виділити колонку: {e}")
        return
    print(df["case_number"].tolist())
    search_cases(df)

if __name__ == "__main__":
    choose_file()
