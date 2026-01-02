# routes/admin.py
from flask import Blueprint, request, render_template, redirect, url_for, session
import csv
import os
import zipfile
import io
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from utils.csv_utils import *
from utils.staff_utils import load_staff, sort_staff_list, calculate_shift_hours , build_shift_dict
from utils.csv_utils import (
    load_shift_requests, save_shift_requests,
    save_imported_requests, create_monthly_csv_templates
)
from utils.date_utils import generate_date_label_list, generate_short_date_labels
from utils.graph_utils import calculate_daily_labor_cost, calculate_daily_work_hours  # ← 追加
from flask import send_file
from utils.csv_handler import load_exclude_data  # ← これを追記
from utils.date_utils import get_current_month
from utils.graph_utils import generate_time_segments, collect_events_with_details  # これも必要
from utils.csv_utils import load_shift_dicts  # 新しい関数だけインポート
from utils.data_utils import load_excludes_with_staff



admin_blueprint = Blueprint("admin", __name__)
staff_list = sort_staff_list(load_staff())

@admin_blueprint.route("/admin/home")
def admin_home():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    from datetime import datetime
    now_month = datetime.now().strftime("%Y-%m")
    return render_template("admin_home.html", name=session["name"], now_month=now_month)

@admin_blueprint.route("/admin/edit", methods=["GET", "POST"])
def admin_edit():
    staff_list = sort_staff_list(load_staff())

    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    month = request.args.get("month")
    if not month:
        today = datetime.today()
        month_list = [
            (today - timedelta(days=30)).strftime("%Y-%m"),
            today.strftime("%Y-%m"),
            (today + timedelta(days=30)).strftime("%Y-%m"),
        ]
        return render_template("edit_select_month.html", month_list=month_list)


    create_monthly_csv_templates(month)

    dates = generate_date_list(month)
    notes = load_notes(month)

    if request.method == "POST":
        updated_shifts = []
        for staff in staff_list:
            for date in dates:
                safe_name = staff["name"].replace(" ", "_")
                for i in range(3):
                    start = request.form.get(f"start_{safe_name}_{date}_{i}", "").strip()
                    end = request.form.get(f"end_{safe_name}_{date}_{i}", "").strip()
                    if start and end:
                        updated_shifts.append({
                            "last_name": staff["name"].split()[0],
                            "first_name": staff["name"].split()[1],
                            "date": date, "index": i, "start": start, "end": end
                        })
        save_shifts(month, updated_shifts)
        notes = {date: request.form.get(f"note_{date}", "").strip() for date in dates}
        save_notes(month, notes)
        return redirect(url_for("admin.admin_edit", month=month))

    shifts = build_shift_dict(load_shifts(month), staff_list)
    total_hours = {
        s["name"]: sum(calculate_shift_hours(start, end)
                       for d in shifts.get(s["name"], {}).values()
                       for start, end in d.values())
        for s in staff_list if s.get("type") == "社員"
    }
    group_name_map = {
        0: "社員",
        1: "複数・両方", 2: "複数・キッチン", 3: "複数・トップ",
        4: "朝・両方", 5: "朝・キッチン", 6: "朝・トップ",
        7: "昼・両方", 8: "昼・キッチン", 9: "昼・トップ",
        10: "夜・両方", 11: "夜・キッチン", 12: "夜・トップ",
    }



    date_labels = generate_date_label_list(month)


    return render_template("admin_edit.html",
                        dates=dates,
                        staff_list=staff_list,
                        shifts=shifts,
                        total_hours=total_hours,
                        group_name_map=group_name_map,
                        notes=notes,
                        month=month,
                        calculate_shift_hours=calculate_shift_hours,
                        date_labels=date_labels
                        )


# その他 add_staff、upload_staff、import_shift などのルートもここに追加可能


@admin_blueprint.route("/admin/panel")
def admin_panel():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    shift_data = load_shift_requests(month)

    return render_template("admin_panel.html", shifts=shift_data, month=month)




@admin_blueprint.route("/admin/add_staff", methods=["GET", "POST"])
def add_staff():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    message = None
    if request.method == "POST":
        account = request.form["account"]
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        password = request.form["password"]
        position = request.form["position"]
        experience = request.form["experience"]
        emp_type = request.form["type"]
        shift_pref = request.form["shift_pref"]

        hashed_password = generate_password_hash(password)

        append_auth({
            "account": account,
            "last_name": last_name,
            "first_name": first_name,
            "role": "staff",
            "hourly_wage": "1200",
            "password": hashed_password
        })

        append_staff({
            "account": account,
            "last_name": last_name,
            "first_name": first_name,
            "position": position,
            "experience": experience,
            "type": emp_type,
            "shift_pref": shift_pref
        })

        message = f"{last_name} {first_name} さんを登録しました！"

    return render_template("admin_add_staff.html", message=message)


@admin_blueprint.route('/admin/upload_staff', methods=['GET', 'POST'])
def upload_staff():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            stream = file.stream.read().decode("utf-8").splitlines()
            reader = csv.DictReader(stream)

            for row in reader:
                append_auth({
                    "account": row['account'].strip(),
                    "last_name": row['last_name'].strip(),
                    "first_name": row['first_name'].strip(),
                    "role": row.get('role', 'staff').strip(),
                    "hourly_wage": row.get('hourly_wage', '1200').strip(),
                    "password": generate_password_hash(row['password'].strip())  # ← ハッシュ化
                })

                append_staff({
                    "account": row['account'].strip(),
                    "last_name": row['last_name'].strip(),
                    "first_name": row['first_name'].strip(),
                    "position": row.get('position', '').strip(),
                    "experience": row.get('experience', '').strip(),
                    "type": row.get('type', '').strip(),
                    "shift_pref": row.get('shift_pref', '').strip()
                })

            return redirect(url_for("admin.admin_home"))

    return render_template('staff_upload.html')

@admin_blueprint.route("/admin/import_confirm", methods=["GET", "POST"])
def import_confirm():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    # ▼ URLの?month=2025-06などから取得（なければ来月）
    month = request.args.get("month")
    if not month:
        today = datetime.today()
        next_month_date = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        month = next_month_date.strftime("%Y-%m")

    create_monthly_csv_templates(month)

    request_data = load_shift_requests(month)
    imported_data = load_csv(get_path("imported_requests", month))
    imported_accounts = {r["account"] for r in imported_data}

    if request.method == "POST":
        selected_accounts = request.form.getlist("accounts")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        imported = []
        for row in request_data:
            if row["account"] in selected_accounts:
                row["imported_at"] = timestamp
                row["submitted_at"] = row.get("submitted_at", "")
                imported.append(row)

        save_imported_requests(month, imported)

        save_shifts(month, [
            {
                "last_name": r["name"].split()[0],
                "first_name": r["name"].split()[1],
                "date": r["date"],
                "index": r["index"],
                "start": r["start"],
                "end": r["end"]
            }
            for r in imported
        ])

        remaining = [r for r in request_data if r["account"] not in selected_accounts]
        save_shift_requests(month, remaining)

        return redirect(url_for("admin.admin_edit", month=month))

    # ▼ 全アカウント名取得（staff.csvベース）
    all_accounts = {
        s["account"]: f'{s["last_name"]} {s["first_name"]}'
        for s in sort_staff_list(load_staff())
    }

    # ▼ 提出済み & インポート対象（submitted_atあり、かつまだimportedに入ってない）
    submitted_by = {}
    for row in request_data:
        acc = row["account"]
        if acc in imported_accounts:
            continue
        submitted_at = row.get("submitted_at", "").strip()
        if submitted_at:
            if acc not in submitted_by or submitted_by[acc] < submitted_at:
                submitted_by[acc] = submitted_at

    submitted_list = sorted([
        {
            "account": acc,
            "name": all_accounts.get(acc, acc),
            "submitted_at": submitted_by[acc],
            "count": sum(1 for r in request_data if r["account"] == acc)
        }
        for acc in submitted_by
    ], key=lambda x: x["submitted_at"])

    # ▼ 未提出リスト（imported済みも提出済みも除外）
    submitted_or_imported = set(submitted_by.keys()) | imported_accounts
    not_submitted_list = [
        {"account": acc, "name": name}
        for acc, name in all_accounts.items() if acc not in submitted_or_imported
    ]

    return render_template("import_confirm.html",
                           next_month=month,
                           submitted_list=submitted_list,
                           not_submitted=not_submitted_list)

@admin_blueprint.route("/admin/import_shift", methods=["POST"])
def import_shift():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    month = request.form.get("month")
    selected_accounts = set(request.form.getlist("accounts"))

    all_requests = load_shift_requests(month)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    imported = []
    for row in all_requests:
        if row["account"] in selected_accounts:
            row["imported_at"] = timestamp
            row["submitted_at"] = row.get("submitted_at", "")
            imported.append(row)

    if imported:
        # 1. 既存の shift を読み込む
        existing_shift = load_shifts(month)

        # 2. 今回インポート分を変換して追加
        imported_shift = [
            {
                "last_name": r["name"].split()[0],
                "first_name": r["name"].split()[1],
                "date": r["date"],
                "index": r["index"],
                "start": r["start"],
                "end": r["end"]
            } for r in imported
        ]

        # 3. 既存 + インポート分 を保存
        all_shift = existing_shift + imported_shift
        save_shifts(month, all_shift)

        # 4. imported_requests に保存
        save_imported_requests(month, imported)

    # 5. 未インポートの希望だけ shift_request に残す
    remaining = [r for r in all_requests if r["account"] not in selected_accounts]
    save_shift_requests(month, remaining)

    return redirect(url_for("admin.admin_edit", month=month))


# routes/admin.py の最後あたりに追加

@admin_blueprint.route("/admin/graph/vertical")
def graph_vertical_admin():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    create_monthly_csv_templates(month)

    staff_list = load_staff()
    shift_list = load_shifts(month)
    date_list = generate_date_list(month)
    date_labels = generate_short_date_labels(month)

    # 棒グラフデータを生成（既存の関数を使ってもOK）
    from utils.graph_utils import generate_compact_bar_data
    graph_data = generate_compact_bar_data(shift_list, staff_list, date_list)

    # 備考の読み込み
    notes = load_notes(month)

    return render_template("graph_vertical_admin.html",
                           graph_data=graph_data,
                           month=month,
                           notes=notes,
                           date_list=date_list,
                           date_labels=date_labels
                           )


from flask import render_template
from utils.graph_utils import generate_vertical_graph_data_admin  # 追加
from utils.csv_utils import load_notes, save_notes

@admin_blueprint.route("/graph/vertical_admin")
def vertical_graph_admin():
    month = request.args.get("month", datetime.today().strftime("%Y-%m"))  # ← GETパラメータから取得
    create_monthly_csv_templates(month)


    staff_list = load_staff()
    shift_list = load_shifts(month)
    graph_data, time_slots = generate_vertical_graph_data_admin(month)
    notes = load_notes(month)  # ← 🔥ここ追加
    date_labels = generate_short_date_labels(month)
    daily_cost = calculate_daily_labor_cost(shift_list, staff_list)
    daily_hours = calculate_daily_work_hours(shift_list, staff_list)  # ← 追加


    return render_template("graph_vertical_admin.html",
                           month=month,
                           graph_data=graph_data,
                           time_slots=time_slots,
                           notes=notes,
                           date_labels=date_labels,
                           daily_cost=daily_cost,
                           daily_hours=daily_hours 
                           )  # ← 🔥これも忘れずに


@admin_blueprint.route("/download")
def download_all_csv():
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # dataフォルダ全体を再帰的にZIPに追加
        data_path = "data"
        if os.path.exists(data_path):
            for root, dirs, files in os.walk(data_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    # 相対パスをarcnameとして使用（data/から始まるパス）
                    arcname = os.path.relpath(file_path, ".")
                    zipf.write(file_path, arcname=arcname)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        attachment_filename='data_folder.zip',  # ファイル名を変更
        as_attachment=True
    )

@admin_blueprint.route("/admin/import_select")
def import_select():
    today = datetime.today()
    month_list = [
        (today - timedelta(days=30)).strftime("%Y-%m"),
        today.strftime("%Y-%m"),
        (today + timedelta(days=30)).strftime("%Y-%m"),
    ]
    return render_template("import_select_month.html", month_list=month_list)

from utils.csv_utils import load_imported_requests


@admin_blueprint.route("/admin/view_imported_shift")
def view_imported_shift():
    
    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    create_monthly_csv_templates(month)

    staff_list = sort_staff_list(load_staff())
    date_map = generate_short_date_labels(month)
    dates = [d["date"] for d in date_map]

    imported_shifts_raw = load_imported_requests(month)  # imported_requests_YYYY-MM.csvを読む関数

    # name → date → index → {start, end}
    imported_shifts = {}
    for s in imported_shifts_raw:
        name = s["name"]
        date = s["date"]
        index = int(s.get("index", 0))
        start = s["start"]
        end = s["end"]
        imported_shifts.setdefault(name, {}).setdefault(date, {})[index] = (start, end)

    all_staff = []
    for staff in staff_list:
        name = staff["name"]
        shift_dict = {}
        for date in dates:
            entries = []
            if name in imported_shifts and date in imported_shifts[name]:
                for start, end in imported_shifts[name][date].values():
                    entries.append({"start": start, "end": end})
            if entries:
                shift_dict[date] = entries
        all_staff.append({
            "name": name,
            "shifts": shift_dict
        })

    return render_template("view_imported_shift_table.html",
                           month=month,
                           date_map=date_map,
                           all_staff=all_staff)



from dateutil.relativedelta import relativedelta  # 必要なら pip install python-dateutil

@admin_blueprint.route("/admin/graph_select")
def graph_month_select():
    today = datetime.today()
    this_month = today.strftime("%Y-%m")
    prev_month = (today - relativedelta(months=1)).strftime("%Y-%m")
    next_month = (today + relativedelta(months=1)).strftime("%Y-%m")
    
    return render_template("graph_month_select.html",
                           this_month=this_month,
                           prev_month=prev_month,
                           next_month=next_month)


@admin_blueprint.route("/admin/segment_preview")
def segment_preview():
    # 日付をクエリから取得、なければ今日の日付（YYYY-MM-DD 形式）
    month = request.args.get("month", get_current_month())
    date_str = request.args.get("date", None)

    shift_data_raw = load_shifts(month)
    staff_list = load_staff()  # ← 追加！
    shift_data = load_shift_dicts(month)  # ← これに変更

    exclude_data = load_excludes_with_staff(month, staff_list)
    events = collect_events_with_details(date_str, shift_data, staff_list)  # ← 修正

    segments = generate_time_segments(events)

    print("=== DEBUG shift_data ===")
    for i, row in enumerate(shift_data[:5]):
        print(f"Row {i}: {row} ({type(row)})")

    print("=== shift_data sample ===")
    for i, s in enumerate(shift_data[:3]):
        print(f"{i}: {s} ({type(s)})")

    return render_template("segment_preview.html", date=date_str, segments=segments)




@admin_blueprint.route("/view_all")
def view_all_shifts():
    from utils.csv_utils import load_csv, get_path, generate_date_list
    from datetime import datetime
    import calendar

    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    shift_data = load_csv(get_path("shift", month))
    staff_data = load_csv("data/staff.csv")
    date_list = generate_date_list(month)

    # 各日付のシフトを分けて整理
    daily_shifts = {}
    for date in date_list:
        daily_shifts[date] = [row for row in shift_data if row["date"] == date]

    return render_template("view_all.html",
                           month=month,
                           staff_data=staff_data,
                           daily_shifts=daily_shifts,
                           date_list=date_list,
                           datetime=datetime)



@admin_blueprint.route("/view_all_shift_chart")
def view_all_shift_chart():
    from utils.csv_utils import load_csv, get_path, generate_date_list
    from utils.shift_utils import load_shift_dicts
    from datetime import datetime

    month = request.args.get("month", datetime.today().strftime("%Y-%m"))

    shift_data = load_shift_dicts(month)  # ← 修正済み
    exclude_data = load_csv(get_path("exclude_time", month))
    staff_data = load_csv("data/staff.csv")
    date_list = generate_date_list(month)

    all_schedules = {}

    for date in date_list:
        schedule = {}
        shift_rows = shift_data.get(date, [])
        for staff in staff_data:
            full_name = staff["last_name"] + staff["first_name"]
            shifts = [
                (row["start"], row["end"])
                for row in shift_rows
                if row["last_name"] + row["first_name"] == full_name
            ]
            excludes = [
                {
                    "start": row["start"],
                    "end": row["end"],
                    "category": row["category"]
                }
                for row in exclude_data
                if row["date"] == date and row["name"].replace(" ", "") == full_name
            ]
            schedule[full_name] = {"shift": shifts, "exclude": excludes}
        all_schedules[date] = schedule

    return render_template("view_all_shift_chart.html", month=month, schedules=all_schedules)


@admin_blueprint.route("/view_all_segment_preview")
def view_all_segment_preview():
    from utils.csv_utils import generate_date_list
    from datetime import datetime

    month = request.args.get("month", datetime.today().strftime("%Y-%m"))

    staff_list = load_staff()
    shift_data = load_shift_dicts(month)
    exclude_data = load_excludes_with_staff(month, staff_list)
    date_list = generate_date_list(month)

    print("=== DEBUG shift_data ===")
    for i, row in enumerate(shift_data[:5]):
        print(f"Row {i}: {row} ({type(row)})")

    all_segments = []
    for date in date_list:
        daily_shifts = [row for row in shift_data if row["date"] == date]
        print(f"=== {date} の daily_shifts ===")
        for i, s in enumerate(daily_shifts):
            print(f"{i}: {s} ({type(s)})")

        # 安全なコピー（deepcopy は不要）
        safe_daily_shifts = list(daily_shifts)

        events = collect_events_with_details(safe_daily_shifts, date, staff_list)
        segments = generate_time_segments(events)
        all_segments.append({"date": date, "segments": segments})

    return render_template("view_all_segment_preview.html",
                           month=month,
                           all_segments=all_segments)

@admin_blueprint.route("/admin/monthly_shift_select")
def monthly_shift_select():
    from datetime import datetime, timedelta
    today = datetime.today()
    month_list = [
        (today - timedelta(days=30)).strftime("%Y-%m"),
        today.strftime("%Y-%m"),
        (today + timedelta(days=30)).strftime("%Y-%m"),
    ]
    return render_template("monthly_shift_select.html", month_list=month_list)
