from datetime import datetime, timedelta
from typing import List


MONTHS = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]



def convert_date(date: datetime) -> str:
    weekday = date.isoweekday()
    insertion_weekday = WEEKDAYS[weekday - 1]
    insertion_month = MONTHS[date.month - 1]
    return f"{insertion_weekday}, {date.day} {insertion_month}"


def get_dates_ahead(days_show: int) -> List[str]:
    return [
        convert_date(datetime.now() + timedelta(i)) for i in range(days_show)
    ]


def is_date_button(date: str) -> bool:
    parts = date.split()
    try:
        assert len(parts) == 3
        weekday, day, month = date.split()
        assert day.isdigit()
        assert int(day) in range(1, 32)
        assert month in MONTHS
        assert weekday[:-1] in WEEKDAYS
        return True
    except AssertionError:
        return False


def month_ru_to_eng(month):
    mapping = {
        "января": "january",
        "февраля": "february",
        "марта": "march",
        "апреля": "april",
        "мая": "may",
        "июня": "june",
        "июля": "july",
        "августа": "august",
        "сентября": "september",
        "октября": "october",
        "ноября": "november",
        "декабря": "december",
    }
    return mapping[month]


def normalize_date(date: str):
    year = datetime.now().year
    date = date.split(", ")[-1]
    day, month = date.split()
    date = datetime.strptime(f"{day} {month_ru_to_eng(month)}, {year}", "%d %B, %Y")
    return date

def sorted_dates(dates: List[str]) -> List[str]:
    return sorted(dates, key=normalize_date)

