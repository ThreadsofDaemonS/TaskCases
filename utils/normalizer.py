#utils/normalizer.py


from datetime import datetime, date
from typing import Optional

def parse_date(date_str: str) -> Optional[date]:
    """Парсить дату у форматі DD.MM.YYYY. Повертає None, якщо не вдалося розпізнати."""
    if not date_str or not isinstance(date_str, str):
        return None

    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None
