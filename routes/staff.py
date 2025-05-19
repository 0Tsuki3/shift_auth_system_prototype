# routes/staff.py
from flask import Blueprint, request, render_template, redirect, url_for, session
import csv
import os
from datetime import datetime, timedelta
from utils.csv_utils import generate_date_list, load_shift_requests, save_shift_requests, create_monthly_csv_templates
from utils.lock_utils import is_editable  # ← これを忘れずにインポート！

staff_blueprint = Blueprint("staff", __name__)



# routes/staff.py（抜粋）
from datetime import datetime


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

    # 🔸 送信解除処理（クエリパラメータで ?reset=1 が来たら）
    if request.args.get("reset") == "1":
        for row in all_data:
            if row["account"] == account:
                row["submitted_at"] = ""
        save_shift_requests(month, all_data)
        return redirect(url_for("staff.submit_shift", account=account, month=month))

    # 🔸 既存シフト読み込み（その人の分だけ）
    for row in all_data:
        if row["account"] == account:
            date, index = row["date"], int(row.get("index", 1))
            shifts.setdefault(date, {})[index] = {
                "start": row["start"],
                "end": row["end"]
            }

    # 🔸 送信日時の取得（この人の中で一番新しいやつ）
    submitted_at = ""
    for row in all_data:
        if row["account"] == account and row.get("submitted_at"):
            submitted_at = max(submitted_at, row["submitted_at"])

    # 🔒 ロック中（submitted_atあり）で送信解除でない場合は編集禁止
    if request.method == "POST":
        action = request.form.get("action")  # 'save' or 'submit'
        if submitted_at and action != "reset":
            return "すでに送信済みです。編集するには送信状態を解除してください。"

        new_data = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if action == "submit" else ""

        for key in request.form:
            if key.startswith("start_"):
                _, index_str, date = key.split("_", 2)
                index = int(index_str.replace("new", "")) if "new" in index_str else int(index_str)
                start = request.form.get(key, "").strip()
                end = request.form.get(f"end_{index_str}_{date}", "").strip()
                if start and end:
                    wished = str(round((datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).seconds / 3600, 1))
                    new_data.append({
                        "account": account, "name": name, "date": date, "index": index,
                        "start": start, "end": end, "wished": wished,
                        "submitted_at": now_str
                    })

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
        now=datetime.now()
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
