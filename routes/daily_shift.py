from flask import Blueprint, render_template
import csv
import os
from datetime import datetime
from utils.exclude_time_utils import load_exclude_data
from utils.shift_utils import load_shift_data_for_date

daily_shift_bp = Blueprint("daily_shift", __name__)

@daily_shift_bp.route("/daily_shift/<date>")
def daily_shift(date):
    month = date[:7]
    shift_data = load_shift_data_for_date(date)
    exclude_data = load_exclude_data(month)

    # その日だけ抽出
    exclude_today = [e for e in exclude_data if e["date"] == date]

    # スタッフ一覧を取得（その日入ってる人だけ）
    staff_names = sorted(set(s["name"] for s in shift_data))

    # スタッフごとの時間データをまとめる
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

    return render_template("daily_shift.html", date=date, schedule=schedule)
