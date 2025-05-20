from datetime import datetime, timedelta
from collections import defaultdict
from utils.csv_utils import load_csv, get_path, generate_date_list

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
    """
    staff_info = {s["last_name"] + s["first_name"]: s for s in staff_list}
    cost_by_date = {}

    for shift in shift_list:
        # name は name があるなら使い、それ以外は last_name + first_name
        name = shift.get("name") or (shift.get("last_name", "") + shift.get("first_name", ""))
        date = shift["date"]
        staff = staff_info.get(name)

        if not staff or staff.get("type") == "社員":
            continue

        start = datetime.strptime(shift["start"], "%H:%M")
        end = datetime.strptime(shift["end"], "%H:%M")
        duration = (end - start).seconds / 3600  # 時間（float）

        # 拘束時間に応じた休憩時間
        if duration >= 8:
            break_time = 1
        elif duration >= 6:
            break_time = 0.5
        else:
            break_time = 0
        work_time = max(duration - break_time, 0)

        cost_by_date[date] = cost_by_date.get(date, 0) + round(work_time * hourly_wage)

    return cost_by_date
