import os
import csv

from utils.csv_utils import get_path


def load_shift_data_for_date(date):
    month = date[:7]
    path = f"data/shift/shift_{month}.csv"
    result = []
    if not os.path.exists(path):
        return result
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"] == date:
                result.append({
                    "name": row["last_name"] + row["first_name"],
                    "start": row["start"],
                    "end": row["end"]
                })
    return result



def load_shift_dicts(month):
    path = get_path("shift", month)
    shift_dict = {}
    if os.path.exists(path):
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                date = row["date"]
                if date not in shift_dict:
                    shift_dict[date] = []
                shift_dict[date].append(row)
    return shift_dict
