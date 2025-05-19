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
    def get_group(staff):
        if staff["type"] == "社員":
            return 0  # 社員は常にグループ0

        shift_pref_order = ["複数", "朝", "昼", "夜"]
        position_order = ["両方", "キッチン", "トップ"]

        try:
            time_index = shift_pref_order.index(staff["shift_pref"])
        except ValueError:
            time_index = len(shift_pref_order)

        try:
            pos_index = position_order.index(staff["position"])
        except ValueError:
            pos_index = len(position_order)

        # グループ番号は 1～（社員を0として）
        return 1 + time_index * len(position_order) + pos_index

    for staff in staff_list:
        staff["group"] = get_group(staff)

    return sorted(staff_list, key=lambda s: (s["group"], s["experience"] != "ベテラン", s["name"]))

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
