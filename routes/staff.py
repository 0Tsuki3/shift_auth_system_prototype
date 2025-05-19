# routes/staff.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
import csv
import os

from datetime import datetime, timedelta

from utils.csv_utils import generate_date_list, load_shift_requests, save_shift_requests, create_monthly_csv_templates

from utils.lock_utils import is_editable  # ← これを忘れずにインポート！

import calendar
from utils.date_utils import generate_weekdays_for_month




staff_blueprint = Blueprint("staff", __name__)





def is_month_locked(month: str) -> bool:
    # たとえば 2025-05 なら 2025-06-01 を過ぎてたらロック
    today = datetime.today()
    target = datetime.strptime(month, "%Y-%m")
    lock_day = (target + timedelta(days=32)).replace(day=1)  # 翌月1日
    return today >= lock_day

@staff_blueprint.route("/submit_shift/<account>", methods=["GET", "POST"])
def submit_shift(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))

    name = session["name"]
    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    create_monthly_csv_templates(month)

    shifts = {}
    all_data = load_shift_requests(month)
    weekday_map = generate_weekdays_for_month(month)
    first_weekday = ['月', '火', '水', '木', '金', '土', '日'].index(weekday_map[f"{month}-01"])
    year, m = map(int, month.split("-"))
    total_days = calendar.monthrange(year, m)[1]

    # 既存シフト読み込み（本人の分だけ）
    for row in all_data:
        if row["account"] == account:
            date, index = row["date"], int(row.get("index", 1))
            shifts.setdefault(date, {})[index] = {
                "start": row["start"],
                "end": row["end"]
            }

    # 提出状態の判定
    submitted_at = ""
    for row in all_data:
        if row["account"] == account and row.get("submitted_at"):
            submitted_at = max(submitted_at, row["submitted_at"])

    # POST処理（保存 or 送信）
    if request.method == "POST":
        action = request.form.get("action")  # 'save' or 'submit'

        submitted_at_str = ""
        if action == "submit":
            submitted_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            flash("送信しました")
        else:
            flash("保存しました（未送信の状態です）")

        new_data = []
        for key in request.form:
            if key.startswith("start_"):
                _, index_str, date = key.split("_", 2)
                index = int(index_str.replace("new", "")) if "new" in index_str else int(index_str)
                start = request.form.get(key, "").strip()
                end = request.form.get(f"end_{index_str}_{date}", "").strip()
                if start and end:
                    wished = str(round((datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).seconds / 3600, 1))
                    new_data.append({
                        "account": account,
                        "name": name,
                        "date": date,
                        "index": index,
                        "start": start,
                        "end": end,
                        "wished": wished,
                        "submitted_at": submitted_at_str
                    })

        # 自分以外の行はそのまま残して、新しい分と合成
        others = [r for r in all_data if r["account"] != account]
        save_shift_requests(month, others + new_data)

        return redirect(url_for("staff.submit_shift", account=account, month=month))

    return render_template(
        "submit_shift.html",
        name=name,
        shifts=shifts,
        dates=generate_date_list(month),
        month=month,
        account=account,
        submitted_at=submitted_at,
        now=datetime.now(),
        first_weekday=first_weekday,
        weekday_map=weekday_map,
        total_days=total_days
    )


# routes/staff.py

@staff_blueprint.route("/account/<account>")
def account_page(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))
    return render_template("staff_home.html", name=session["name"], account=account)


@staff_blueprint.route("/submit_shift_select/<account>")
def submit_month_select(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))

    today = datetime.today()
    month_list = [
        (today - timedelta(days=30)).strftime("%Y-%m"),
        today.strftime("%Y-%m"),
        (today + timedelta(days=30)).strftime("%Y-%m"),
    ]

    shift_data = {
        m: [r for r in load_shift_requests(m) if r["account"] == account]
        for m in month_list
    }

    # 各月の submitted_at を取得
    status_map = {}
    for m in month_list:
        records = shift_data[m]
        submitted_list = [r.get("submitted_at") for r in records if r.get("submitted_at")]
        submitted_at = max(submitted_list) if submitted_list else ""
        status_map[m] = submitted_at

    return render_template(
        "submit_select_month.html",
        account=account,
        name=session["name"],
        month_list=month_list,
        status_map=status_map,
        is_editable=is_editable  # 🔥 これが抜けてた！
    )




@staff_blueprint.route("/view_shift/<account>/<month>")
def view_shift(account, month):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))

    # シフトデータ読み込み
    shifts = [r for r in load_shift_requests(month) if r["account"] == account]
    return render_template("view_shift.html", shifts=shifts, month=month, name=session["name"])
