# utils/date_utils.py
from datetime import datetime

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
