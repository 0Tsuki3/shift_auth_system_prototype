# routes/staff.py
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
import csv
import os

from datetime import datetime, timedelta

from utils.csv_utils import generate_date_list, load_shift_requests, save_shift_requests, create_monthly_csv_templates

from utils.lock_utils import is_editable  # ← これを忘れずにインポート！

import calendar
from utils.date_utils import generate_weekdays_for_month

from utils.csv_utils import get_path, create_monthly_csv_templates, load_csv

from utils.date_utils import generate_date_label_list




from icalendar import Calendar, Event
from flask import make_response
from pytz import timezone



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


@staff_blueprint.route("/view_shift/<account>")
def view_confirmed_shift(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))

    name = session["name"]
    full_name = session["last_name"] + session["first_name"]
    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    shift_path = get_path("shift", month)
    create_monthly_csv_templates(month)

    # shift.csv 読み込み（氏名ベースでフィルター）
    shift_list = [r for r in load_csv(shift_path) if r.get("last_name", "") + r.get("first_name", "") == full_name]

    def calc_hours(start, end):
        try:
            s = datetime.strptime(start, "%H:%M")
            e = datetime.strptime(end, "%H:%M")
            duration = (e - s).seconds / 3600
            break_time = 1 if duration >= 8 else 0.5 if duration >= 6 else 0
            return max(duration - break_time, 0)
        except:
            return 0

    date_map = generate_date_label_list(month)
    date_label_dict = {d["date"]: d["label"] for d in date_map}
    shift_data = []
    total_hours = 0

    for row in shift_list:
        date = row["date"]
        start = row["start"]
        end = row["end"]
        hours = round(calc_hours(start, end), 1)
        total_hours += hours
        shift_data.append({
            "label": date_label_dict.get(date, date),
            "start": start,
            "end": end,
            "hours": hours
        })
    # 🔸 時給取得（auth.csvから）
    auth_list = load_csv("auth.csv")
    hourly_wage=1200
    for row in auth_list:
        if row.get("account", "").strip() == account.strip():
            try:
                hourly_wage = int(row.get("hourly_wage", 1200))
            except:
                hourly_wage = 1200
            break
        

    
    calendar_data = []
    for d in date_map:
        matching = [r for r in shift_list if r["date"] == d["date"]]
        if matching:
            m = matching[0]
            calendar_data.append({"label": d["label"], "shift": {"start": m["start"], "end": m["end"]}})
        else:
            calendar_data.append({"label": d["label"], "shift": None})

    return render_template(
        "view_shift.html",
        account=account,
        name=name,
        month=month,
        shift_data=shift_data,
        total_hours=round(total_hours, 1),
        estimated_pay=round(total_hours * hourly_wage),
        calendar_data=calendar_data
    )




@staff_blueprint.route("/download_ics/<account>")
def download_ics(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))

    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    shift_path = get_path("shift", month)
    create_monthly_csv_templates(month)

    # ✅ auth.csv から氏名を取得
    auth_list = load_csv("auth.csv")
    full_name = ""
    for row in auth_list:
        if row.get("account", "").strip() == account.strip():
            full_name = row.get("last_name", "") + row.get("first_name", "")
            break

    if not full_name:
        return "氏名が見つかりませんでした", 404

    # ✅ 氏名で照合して shift を抽出
    shift_list = [
        r for r in load_csv(shift_path)
        if r.get("last_name", "") + r.get("first_name", "") == full_name
    ]

    cal = Calendar()
    cal.add('prodid', '-//ShiftApp//')
    cal.add('version', '2.0')

    from pytz import timezone
    jst = timezone("Asia/Tokyo")

    for row in shift_list:
        try:
            date = row["date"]
            start_dt = jst.localize(datetime.strptime(date + " " + row["start"], "%Y-%m-%d %H:%M"))
            end_dt = jst.localize(datetime.strptime(date + " " + row["end"], "%Y-%m-%d %H:%M"))

            event = Event()
            event.add('summary', '人関勤務')
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            event.add('dtstamp', datetime.now(jst))
            event.add('description', f"{row['start']} - {row['end']}")
            event.add('location', '職場')

            cal.add_component(event)
        except Exception as e:
            print("❌ iCal生成エラー:", e)
            continue

    response = make_response(cal.to_ical())
    response.headers.set('Content-Disposition', f'attachment; filename=shift_{month}.ics')
    response.headers.set('Content-Type', 'text/calendar; charset=utf-8')
    return response



from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for

@staff_blueprint.route("/account/<account>")
def staff_home(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))

    # 今日の日付から this_month, next_month を作成
    today = datetime.today()
    this_month = today.strftime("%Y-%m")
    if today.month == 12:
        next_month = f"{today.year + 1}-01"
    else:
        next_month = f"{today.year}-{today.month + 1:02d}"

    return render_template(
        "staff_home.html",
        account=account,
        name=session["name"],
        this_month=this_month,
        next_month=next_month
    )


@staff_blueprint.route("/history_menu/<account>")
def staff_history_menu(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))
    return render_template("history_menu.html", account=account)


from utils.staff_utils import load_staff, sort_staff_list, build_shift_dict
from utils.csv_utils import create_monthly_csv_templates, load_shifts
from utils.date_utils import generate_short_date_labels


@staff_blueprint.route("/view_all/<account>")
def view_all_readonly(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))


    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    create_monthly_csv_templates(month)

    # 管理者と同じスタッフの並び順・分類
    staff_list = sort_staff_list(load_staff())
    date_map = generate_short_date_labels(month)
    dates = [d["date"] for d in date_map]

    # シフトデータを staff["name"] → date → {index: {start, end}} で構築
    shifts = build_shift_dict(load_shifts(month), staff_list)

    all_staff = []
    for staff in staff_list:
        shift_dict = {}
        for date in dates:
            entries = []
            if staff["name"] in shifts and date in shifts[staff["name"]]:
                for start, end in shifts[staff["name"]][date].values():
                    entries.append({"start": start, "end": end})
            if entries:
                shift_dict[date] = entries
        all_staff.append({
            "name": staff["name"],
            "shifts": shift_dict
        })

    return render_template("view_all_readonly.html",
                           month=month,
                           date_map=date_map,
                           all_staff=all_staff,
                           account=account)
# routes/staff.py（抜粋）

@staff_blueprint.route("/graph/<account>")
def staff_graph(account):
    if "account" not in session or session["account"] != account:
        return redirect(url_for("auth.login"))

    from utils.graph_utils import generate_vertical_graph_data_admin
    from utils.csv_utils import load_notes, load_csv, get_path
    from utils.date_utils import generate_short_date_labels

    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    graph_data, time_slots = generate_vertical_graph_data_admin(month)
    notes = load_notes(month)
    date_labels = generate_short_date_labels(month)

    return render_template(
        "graph_vertical_admin.html",
        graph_data=graph_data,
        month=month,
        notes=notes,
        date_labels=date_labels,
        daily_cost={},  # スタッフには人件費表示なし
        daily_hours={},  # スタッフには人時数表示なし
        account=account
    )
