# utils/date_utils.py

from datetime import datetime, timedelta

import calendar



def is_editable(month: str, submitted_at: str | None) -> bool:
    """その月のシフトが編集可能かどうか"""
    today = datetime.today()
    year, mon = map(int, month.split("-"))
    first_of_next_month = datetime(year, mon, 1)
    if mon == 12:
        first_of_next_month = datetime(year + 1, 1, 1)
    else:
        first_of_next_month = datetime(year, mon + 1, 1)

    now = datetime.now()
    deadline = datetime(year, mon, 20, 23, 59, 59)

    # 1. 翌月1日以降はロック
    if now >= first_of_next_month:
        return False

    # 2. 締切（20日）前なら未提出でも提出済みでも編集可
    if now <= deadline:
        return True

    # 3. 締切後かつすでに提出済みなら編集不可
    if submitted_at:
        return False

    # 4. 締切後でも未提出ならまだOK
    return True


def generate_weekdays_for_month(month_str):
    """
    month_str: '2025-06' のような形式
    return: {'2025-06-01': '日', '2025-06-02': '月', ...}
    """
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    result = {}
    year, month = map(int, month_str.split('-'))
    for day in range(1, 32):
        try:
            date = datetime(year, month, day)
        except ValueError:
            break
        date_str = date.strftime("%Y-%m-%d")
        weekday_str = weekdays[date.weekday()]
        result[date_str] = weekday_str
    return result


def generate_date_label_list(month_str):
    """
    month_str: '2025-06'
    return: [{'date': '2025-06-01', 'label': '06-01（日）'}, ...]
    """
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    result = []
    year, month = map(int, month_str.split('-'))

    for day in range(1, 32):
        try:
            date = datetime(year, month, day)
        except ValueError:
            break
        date_str = date.strftime("%Y-%m-%d")
        label = date.strftime("%m-%d") + f"（{weekdays[date.weekday()]}）"
        result.append({"date": date_str, "label": label})

    return result



def generate_short_date_labels(month_str):
    """
    例: '2025-06' → [{'date': '2025-06-01', 'label': '1（土）'}, ...]
    """
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    year, month = map(int, month_str.split('-'))
    results = []

    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        date = datetime(year, month, day)
        date_str = date.strftime('%Y-%m-%d')
        label = f"{day}({weekdays[date.weekday()]})"
        results.append({'date': date_str, 'label': label})

    return results


def generate_date_list(month_str):
    """
    例: '2025-06' → [{'date': '2025-06-01', 'weekday': '日'}, ...]
    """
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    year, month = map(int, month_str.split('-'))
    results = []

    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        date = datetime(year, month, day)
        date_str = date.strftime('%Y-%m-%d')
        weekday_str = weekdays[date.weekday()]
        results.append({'date': date_str, 'weekday': weekday_str})

    return results



def get_current_month():
    return datetime.now().strftime("%Y-%m")


