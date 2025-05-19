# utils/lock_utils.py
from datetime import datetime

締切日 = 20  # 20日が提出締切

def is_editable(month: str, submitted_at: str) -> bool:
    """提出済みの月かつ、提出日が締切前なら編集可"""
    if not submitted_at:
        return True  # そもそも未提出

    submitted = datetime.strptime(submitted_at, "%Y-%m-%d %H:%M:%S")
    deadline = datetime.strptime(month + f"-{締切日}", "%Y-%m-%d")

    return submitted <= deadline
