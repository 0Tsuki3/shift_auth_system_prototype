from datetime import datetime, timedelta
from collections import defaultdict
from utils.csv_utils import load_csv, get_path, generate_date_list
from utils.date_utils import generate_short_date_labels


def generate_vertical_graph_data_admin(month):
    from utils.csv_utils import load_csv, get_path, generate_date_list
    from datetime import datetime, timedelta

    shift_path = get_path("shift", month)
    shift_data = load_csv(shift_path)

    def generate_time_slots(start="07:00", end="23:30"):
        fmt = "%H:%M"
        start_time = datetime.strptime(start, fmt)
        end_time = datetime.strptime(end, fmt)
        slots = []
        while start_time <= end_time:
            slots.append(start_time.strftime(fmt))
            start_time += timedelta(minutes=30)
        return slots

    time_slots = generate_time_slots()
    result = {}

    all_dates = generate_date_list(month)
    for date in all_dates:
        result[date] = {slot: [] for slot in time_slots}

    for row in shift_data:
        date = row["date"]
        name = f'{row["last_name"]} {row["first_name"]}'
        try:
            start_dt = datetime.strptime(row["start"], "%H:%M")
            end_dt = datetime.strptime(row["end"], "%H:%M")
        except ValueError:
            continue

        t = start_dt
        while t < end_dt:
            slot = t.strftime("%H:%M")
            if slot in result[date]:
                result[date][slot].append(name)
            t += timedelta(minutes=30)

    graph_data = []
    for date in sorted(result.keys()):
        day_slots = result[date]
        segments = []
        current_names = set()
        current_start = time_slots[0]

        for slot in time_slots:
            names = set(day_slots[slot])
            if names != current_names:
                if current_names or current_start != slot:
                    height = (datetime.strptime(slot, "%H:%M") - datetime.strptime(current_start, "%H:%M")).seconds // 6
                    segments.append({
                        "start": current_start,
                        "end": slot,
                        "count": len(current_names),
                        "height": height,
                        "members": list(current_names)  # ★ここを追加
                    })
                current_start = slot
                current_names = names

        if current_start != "23:30":
            height = (datetime.strptime("23:30", "%H:%M") - datetime.strptime(current_start, "%H:%M")).seconds // 6
            segments.append({
                "start": current_start,
                "end": "23:30",
                "count": len(current_names),
                "height": height,
                "members": list(current_names)  # ★ここも追加
            })

        graph_data.append({
            "date": date,
            "segments": segments
        })

    return graph_data, time_slots


def calculate_daily_labor_cost(shift_list, staff_list, hourly_wage=1200):
    """
    各日のバイトの総人件費を算出する（社員は除外）
    - 22時以降は1.25倍
    - 6h以上で0.5h休憩、8h以上で1h休憩（22時以前の時間から引く）
    """
    staff_info = {s["last_name"] + s["first_name"]: s for s in staff_list}
    cost_by_date = defaultdict(float)

    for shift in shift_list:
        name = shift.get("name") or (shift.get("last_name", "") + shift.get("first_name", ""))
        date = shift["date"]
        staff = staff_info.get(name)

        if not staff or staff.get("type") == "社員":
            continue

        try:
            start = datetime.strptime(shift["start"], "%H:%M")
            end = datetime.strptime(shift["end"], "%H:%M")
        except:
            continue

        total_minutes = int((end - start).total_seconds() // 60)

        # 時間帯ごとの労働時間（分）
        before_22 = 0
        after_22 = 0
        time = start
        while time < end:
            next_time = time + timedelta(minutes=30)
            if time.hour < 22:
                before_22 += 30
            else:
                after_22 += 30
            time = next_time

        # 休憩時間（分）
        if total_minutes >= 8 * 60:
            break_minutes = 60
        elif total_minutes >= 6 * 60:
            break_minutes = 30
        else:
            break_minutes = 0

        # 休憩は22時以前の時間から引く
        before_22_work = max(before_22 - break_minutes, 0)

        # 人件費計算
        cost = (before_22_work / 60) * hourly_wage + (after_22 / 60) * hourly_wage * 1.25
        cost_by_date[date] += cost

    return {k: int(round(v)) for k, v in cost_by_date.items()}




def generate_time_slots(start_time="07:00", end_time="23:30"):
    time_slots = []
    current = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    while current <= end:
        time_slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)
    return time_slots

def generate_compact_bar_data(month):
    shift_path = get_path("shift", month)
    shift_list = load_csv(shift_path)
    date_list = generate_date_list(month)
    time_slots = generate_time_slots()

    result = []

    for date in date_list:
        date_str = date  # 例: "2025-05-01"
        relevant_shifts = [s for s in shift_list if s["date"] == date_str]

        if not relevant_shifts:
            result.append({
                "date": date_str,
                "segments": [{
                    "start": "07:00",
                    "end": "23:30",
                    "count": 0,
                    "members": []
                }]
            })
            continue

        # 30分刻みの人数集計
        slot_counts = {slot: [] for slot in time_slots}
        for shift in relevant_shifts:
            start = shift["start"]
            end = shift["end"]
            for slot in time_slots:
                if start <= slot < end:
                    slot_counts[slot].append(shift["name"] if "name" in shift else "")

        # 連続する区間で人数が変わるところをまとめる
        segments = []
        prev_count = None
        prev_members = None
        current_start = None

        for i, slot in enumerate(time_slots):
            members = slot_counts[slot]
            count = len(members)

            if prev_count is None:
                current_start = slot
                prev_count = count
                prev_members = members
            elif count != prev_count:
                segments.append({
                    "start": current_start,
                    "end": slot,
                    "count": prev_count,
                    "members": prev_members
                })
                current_start = slot
                prev_count = count
                prev_members = members

        # 最後の区間
        segments.append({
            "start": current_start,
            "end": "23:30",
            "count": prev_count,
            "members": prev_members
        })

        result.append({
            "date": date_str,
            "segments": segments
        })

    return result

def calculate_daily_work_hours(shift_list, staff_list):
    """
    各日のバイトの人時数を算出する（社員は除外、休憩込み）
    """
    staff_info = {s["last_name"] + s["first_name"]: s for s in staff_list}
    hours_by_date = defaultdict(float)

    for shift in shift_list:
        name = shift.get("name") or (shift.get("last_name", "") + shift.get("first_name", ""))
        date = shift["date"]
        staff = staff_info.get(name)
        if not staff or staff.get("type") == "社員":
            continue

        try:
            start = datetime.strptime(shift["start"], "%H:%M")
            end = datetime.strptime(shift["end"], "%H:%M")
        except:
            continue

        duration = (end - start).seconds / 3600  # 時間（float）
        hours_by_date[date] += round(duration, 2)

    return dict(hours_by_date)

