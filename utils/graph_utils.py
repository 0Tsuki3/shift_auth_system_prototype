from datetime import datetime, timedelta
from collections import defaultdict
from utils.csv_utils import load_csv, get_path, generate_date_list, load_shift_dicts
from utils.date_utils import generate_short_date_labels
from utils.exclude_time_utils import load_excludes_with_staff
from utils.staff_utils import load_staff  # ← こっちに移す




def generate_vertical_graph_data_admin(month):
    from utils.csv_utils import load_csv, get_path, generate_date_list
    from datetime import datetime
    from collections import defaultdict

    # データ読み込み
    shift_data = load_csv(get_path("shift", month))
    exclude_data = load_csv(get_path("exclude_time", month))
    all_dates = generate_date_list(month)

    graph_data = []

    time_format = "%H:%M"

    for date in all_dates:
        events = []

        # シフトから出勤・退勤イベントを作成
        for row in shift_data:
            if row["date"] != date:
                continue
            name = f'{row["last_name"]}{row["first_name"]}'
            try:
                start_dt = datetime.strptime(row["start"], time_format)
                end_dt = datetime.strptime(row["end"], time_format)
            except ValueError:
                continue
            events.append({"time": start_dt, "name": name, "type": "enter", "role": "work"})
            events.append({"time": end_dt,   "name": name, "type": "leave", "role": "work"})

        # 除外時間からイベントを作成
        for row in exclude_data:
            if row["date"] != date:
                continue
            name = row["name"].replace(" ", "")
            category = row["category"]
            try:
                start_dt = datetime.strptime(row["start"], time_format)
                end_dt = datetime.strptime(row["end"], time_format)
            except ValueError:
                continue
            events.append({"time": start_dt, "name": name, "type": "enter", "role": "exclude", "category": category})
            events.append({"time": end_dt,   "name": name, "type": "leave", "role": "exclude", "category": category})

        # イベントを時刻順にソート
        events.sort(key=lambda x: x["time"])

        # セグメント作成
        segments = []
        current_time = None
        present_members = set()
        excluded_members = defaultdict(str)  # name -> category

        for i, event in enumerate(events):
            if current_time is not None and current_time != event["time"]:
                start_str = current_time.strftime(time_format)
                end_str = event["time"].strftime(time_format)
                duration_minutes = int((event["time"] - current_time).total_seconds() // 60)
                height = duration_minutes * 10  # 6でもいいが見やすさで調整

                segments.append({
                    "start": start_str,
                    "end": end_str,
                    "count": len(present_members),
                    "height": height,
                    "members": sorted(present_members),
                    "excluded": [f"{excluded_members[name]} {name}" for name in sorted(excluded_members.keys())]
                })

            # イベントの適用
            name = event["name"]
            if event["type"] == "enter":
                if event["role"] == "work":
                    present_members.add(name)
                elif event["role"] == "exclude":
                    excluded_members[name] = event["category"]
                    # 除外中は人数から除外
                    present_members.discard(name)
            elif event["type"] == "leave":
                if event["role"] == "work":
                    present_members.discard(name)
                elif event["role"] == "exclude":
                    excluded_members.pop(name, None)
                    # 除外から戻ってきたら再カウント（ただし勤務時間内なら）
                    present_members.add(name)

            current_time = event["time"]

        graph_data.append({
            "date": date,
            "segments": segments
        })

    return graph_data, []  # time_slotsは不要になるので空リスト

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



def generate_time_segments(events):
    segments = []
    current_time = "07:00"
    active_set = set()
    exclude_dict = {"break": set(), "desk": set(), "other": set()}

    for event in events:
        next_time = event["time"]
        if current_time != next_time:
            segments.append({
                "start": current_time,
                "end": next_time,
                "active": list(active_set - set.union(*exclude_dict.values())),
                "break": list(exclude_dict["break"]),
                "desk": list(exclude_dict["desk"]),
                "other": list(exclude_dict["other"]),
            })
            current_time = next_time

        name = event["name"]
        if event["type"] == "in":
            active_set.add(name)
        elif event["type"] == "out":
            active_set.discard(name)
        elif event["type"] == "exclude_start":
            exclude_dict[event["category"]].add(name)
        elif event["type"] == "exclude_end":
            exclude_dict[event["category"]].discard(name)

    if current_time < "23:30":
        segments.append({
            "start": current_time,
            "end": "23:30",
            "active": list(active_set - set.union(*exclude_dict.values())),
            "break": list(exclude_dict["break"]),
            "desk": list(exclude_dict["desk"]),
            "other": list(exclude_dict["other"]),
        })

    return segments



def collect_events_with_details(date, shift_data, staff_list):
    events = []
    for row in shift_data:
        if row["date"] != date:
            continue

        # 名前生成
        name = row["last_name"] + row["first_name"]

        # スタッフ情報をstaff_listから取得（first/last name 両方でマッチ）
        staff_info = next(
            (s for s in staff_list if s["last_name"] == row["last_name"] and s["first_name"] == row["first_name"]),
            {}
        )

        position = staff_info.get("type", "不明")         # 'type'は社員/バイト
        experience = staff_info.get("experience", "不明") # 'experience'はベテラン/新人
        role = staff_info.get("role", "不明")             # 'role'はトップ/キッチン/両方 など

        # 開始イベント
        events.append({
            "time": row["start"],
            "type": "work_start",
            "staff": row,
            "name": name,
            "position": position,
            "experience": experience,
            "role": role
        })

        # 終了イベント
        events.append({
            "time": row["end"],
            "type": "work_end",
            "staff": row,
            "name": name,
            "position": position,
            "experience": experience,
            "role": role
        })

    # ソート（時間順、type順）
    events.sort(key=lambda x: (x["time"], 0 if x["type"] == "work_end" else 1))

    print("=== イベント一覧 ===")
    for e in events:
        print(e)
    return events




def aggregate_staff_counts(events, time_segments):
    results = []

    for i in range(len(time_segments) - 1):
        start = time_segments[i]
        end = time_segments[i + 1]
        segment_counts = {
            "start": start,
            "end": end,
            "稼働中": 0,
            "休憩中": 0,
            "デスク": 0,
            "その他": 0,
            "names": [],  # 吹き出し用（必要なら）
        }

        for event in events:
            e_time = event["time"]
            if start <= e_time < end:
                status = event.get("status", "その他")
                if status not in segment_counts:
                    segment_counts[status] = 0
                segment_counts[status] += 1

                name = event.get("name", "")
                if name:
                    segment_counts["names"].append(f"{name}（{status}）")

        results.append(segment_counts)

    return results





def generate_all_day_view(month):
    staff_list = load_staff()
    shift_data = load_shift_dicts(month)
    exclude_data = load_excludes_with_staff(month, staff_list)
    date_list = generate_date_list(month)

    all_data = []
    for date in date_list:
        daily_shifts = [row for row in shift_data if row["date"] == date]
        events = collect_events_with_details(date, daily_shifts, staff_list)  # ← 修正
        segments = generate_time_segments(events)
        all_data.append({
            "date": date,
            "schedule": segments
        })

    return all_data
