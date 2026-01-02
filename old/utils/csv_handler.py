import csv
import os

def load_shifts(month):
    path = f"data/shift/shift_{month}.csv"
    shifts = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["start"] and row["end"]:
                    shifts.append(row)
    return shifts

def load_exclude_data(month):
    path = f"data/exclude_time/exclude_time_{month}.csv"
    excludes = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["start"] and row["end"]:
                    excludes.append(row)
    return excludes
