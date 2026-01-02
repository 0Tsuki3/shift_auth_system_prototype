import csv
import os

def load_exclude_data(month):
    path = f"data/exclude_time/exclude_time_{month}.csv"
    data = []
    if not os.path.exists(path):
        return data
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data



def save_exclude_data(month, data):
    path = f"data/exclude_time/exclude_time_{month}.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline='', encoding='utf-8') as f:
        fieldnames = ["date", "start", "end", "category", "name"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)




def load_excludes_with_staff(month, staff_list):
    raw_data = load_exclude_data(month)
    filtered = []

    for row in raw_data:
        name = row.get("name")
        if not name:
            continue
        if not any(staff["name"] == name for staff in staff_list):
            continue
        filtered.append({
            "name": name,
            "date": row.get("date"),
            "start": row.get("start"),
            "end": row.get("end"),
            "category": row.get("category"),
        })
    return filtered
