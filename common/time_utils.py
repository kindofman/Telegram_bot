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


