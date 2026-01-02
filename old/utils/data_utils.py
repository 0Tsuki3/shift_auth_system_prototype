import csv
import os

def load_excludes(month):
    path = f"data/exclude/exclude_{month}.csv"
    excludes = []
    if os.path.exists(path):
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                excludes.append(row)
    return excludes

def load_excludes_with_staff(month, staff_list):
    excludes = load_excludes(month)
    account_to_name = {
        s["account"]: {"last_name": s["last_name"], "first_name": s["first_name"]}
        for s in staff_list
    }

    for e in excludes:
        name_info = account_to_name.get(e["account"], {"last_name": "不明", "first_name": ""})
        e.update(name_info)

    return excludes
