from flask import Blueprint, render_template
from utils.shift_utils import load_shift_data_for_date
from utils.exclude_time_utils import load_exclude_data
from utils.csv_utils import generate_date_list
from datetime import datetime

monthly_shift_bp = Blueprint("monthly_shift", __name__)




@monthly_shift_bp.route("/monthly_shift_chart")
def monthly_shift_chart():
    # 表示対象の月（例: 2025-07）
    month = datetime.today().strftime("%Y-%m")
    date_list = generate_date_list(month)

    # 除外時間（全体）を読み込み
    exclude_data_all = load_exclude_data(month)

    # 各日付ごとのデータを構築
    all_data = []

    for date in date_list:
        shift_data = load_shift_data_for_date(date)
        exclude_today = [e for e in exclude_data_all if e["date"] == date]
        staff_names = sorted(set(s["name"] for s in shift_data))

        schedule = {name: {"shift": [], "exclude": []} for name in staff_names}

        for s in shift_data:
            schedule[s["name"]]["shift"].append((s["start"], s["end"]))
        for e in exclude_today:
            name = e["name"]
            if name in schedule:
                schedule[name]["exclude"].append({
                    "start": e["start"],
                    "end": e["end"],
                    "category": e["category"]
                })

        all_data.append({"date": date, "schedule": schedule})

    return render_template("monthly_shift_chart.html", month=month, all_data=all_data)
