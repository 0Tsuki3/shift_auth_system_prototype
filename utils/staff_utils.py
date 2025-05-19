# utils/staff_utils.py
import csv, os
from utils.csv_utils import generate_date_list


def load_staff():
    path = "staff.csv"
    if not os.path.exists(path):
        return []

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        staff_list = []
        for row in reader:
            # 必要なカラムをすべて含めて返すようにする！
            staff_list.append({
                "account": row["account"],
                "last_name": row["last_name"],
                "first_name": row["first_name"],
                "name": f'{row["last_name"]} {row["first_name"]}',
                "position": row.get("position", ""),
                "experience": row.get("experience", ""),
                "type": row.get("type", ""),
                "shift_pref": row.get("shift_pref", ""),
            })
        return staff_list


def sort_staff_list(staff_list):
    def score(staff):
        if staff['position'] == '社員':
            staff['group'] = 0
            return (0, 0, staff['name'])

        time_map = {'オール': 1, '朝': 2, '昼': 3, '夜': 4}
        role_map = {'両方': 0, 'キッチン': 1, 'トップ': 2}
        exp_score = 0 if staff.get('experience') == 'ベテラン' else 1

        # 🛠 shift_pref に修正
        time_score = time_map.get(staff.get('shift_pref', 'オール'), 1)
        role_score = role_map.get(staff.get('position', ''), 2)

        group = (time_score - 1) * 3 + 1 + role_score
        staff['group'] = group
        return (group, exp_score, staff['name'])

    return sorted(staff_list, key=score)

def calculate_shift_hours(start, end):
    from datetime import datetime
    s, e = datetime.strptime(start, '%H:%M'), datetime.strptime(end, '%H:%M')
    return max((e - s).total_seconds() / 3600, 0)

def build_shift_dict(shift_rows, staff_list):
    shift_dict = {s["name"]: {} for s in staff_list}
    for row in shift_rows:
        name = f"{row['last_name']} {row['first_name']}"
        date = row['date']
        index = int(row['index'])
        shift_dict.setdefault(name, {}).setdefault(date, {})[index] = (row['start'], row['end'])
    return shift_dict
