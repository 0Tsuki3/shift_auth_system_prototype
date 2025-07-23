# utils/csv_utils.py
import os, csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


def get_path(base, month): return f"data/{base}/{base}_{month}.csv"

def load_csv(path): return list(csv.DictReader(open(path, newline='', encoding='utf-8'))) if os.path.exists(path) else []

def save_csv(path, data, headers):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader(); writer.writerows(data)

def load_shifts(month): return load_csv(get_path("shift", month))

def save_shifts(month, shifts): save_csv(get_path("shift", month), shifts, ["last_name", "first_name", "date", "index", "start", "end"])

def load_shift_requests(month): return load_csv(get_path("shift_request", month))

def save_shift_requests(month, requests):
    save_csv(
        get_path("shift_request", month),
        requests,
        ["account", "name", "date", "index", "start", "end", "wished", "submitted_at"]  # ← 追加！
    )

def save_imported_requests(month, data):
    path = get_path("imported_requests", month)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "account", "name", "date", "index", "start", "end", "wished", "submitted_at", "imported_at"
        ])
        if os.path.getsize(path) == 0:
            writer.writeheader()
        writer.writerows(data)



def load_notes(month):
    path = get_path("notes", month); notes = {}
    if os.path.exists(path):
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f): notes[row["date"]] = row["note"]
    return notes

def save_notes(month, notes_dict):
    path = get_path("notes", month)
    save_csv(path, [{"date": d, "note": n} for d, n in notes_dict.items()], ["date", "note"])


def generate_date_list(month: str) -> list:
    base = datetime.strptime(month + "-01", "%Y-%m-%d")
    result = []
    while base.month == int(month.split("-")[1]):
        result.append(base.strftime("%Y-%m-%d"))
        base += timedelta(days=1)
    return result

def load_auth_data():
    auth_data = {}
    if os.path.exists("auth.csv"):
        with open("auth.csv", newline='', encoding="utf-8") as f:
            for row in csv.DictReader(f):
                auth_data[row["account"]] = row
    return auth_data

# utils/csv_utils.py に追加

from pathlib import Path

def create_monthly_csv_templates(month: str):
    base_path = Path("data")
    files_to_create = {
        "shift": ["last_name", "first_name", "date", "index", "start", "end"],
        "shift_request": ["account", "last_name", "first_name", "date", "index", "start", "end", "wished"],
        "imported_requests": ["account", "last_name", "first_name", "date", "index", "start", "end", "wished", "imported_at"],
        "notes": ["date", "note"]
    }

    created_files = []

    for category, headers in files_to_create.items():
        dir_path = base_path / category
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f"{category}_{month}.csv"
        if not file_path.exists():
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
            created_files.append(str(file_path))

    return created_files

def append_auth(row):
    path = "auth.csv"
    write_header = not os.path.exists(path)
    with open(path, "a", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "account", "last_name", "first_name", "role", "hourly_wage", "password"
        ])
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def append_staff(row):
    path = "staff.csv"
    write_header = not os.path.exists(path)
    with open(path, "a", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["account", "last_name", "first_name", "position", "experience", "type", "shift_pref"])
        if write_header:
            writer.writeheader()
        writer.writerow(row)



def build_shift_dict(shift_list, staff_list):
    """
    shift.csv の flatなリストを staff_name → date → index → {start, end} に変換
    """
    shifts = defaultdict(lambda: defaultdict(dict))

    for row in shift_list:
        name = row["last_name"] + " " + row["first_name"]
        date = row["date"]
        index = int(row.get("index", 0))
        start = row["start"]
        end = row["end"]
        shifts[name][date][index] = {"start": start, "end": end}

    return shifts


def load_imported_requests(month):
    path = f"data/imported_requests/imported_requests_{month}.csv"
    imported_requests = []
    if os.path.exists(path):
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                imported_requests.append(row)
    return imported_requests



def load_shift_dicts(month):  # 新しい関数名
    """shift_{month}.csv を list of dict で返す安全な関数"""
    return load_csv(get_path("shift", month))
