from flask import Blueprint, request, jsonify
import os
import csv
from datetime import datetime

exclude_api = Blueprint("exclude_api", __name__)

@exclude_api.route("/api/exclude/add", methods=["POST"])
def add_exclude_time():
    data = request.get_json()
    date = data.get("date")           # e.g. "2025-07-16"
    name = data.get("name")           # e.g. "山田太郎"
    start = data.get("start")         # e.g. "14:00"
    end = data.get("end")             # e.g. "15:00"
    category = data.get("category")   # e.g. "break"

    if not (date and name and start and end and category):
        return jsonify({"error": "Missing required fields"}), 400

    month = date[:7]  # "2025-07"
    path = f"data/exclude_time/exclude_time_{month}.csv"

    os.makedirs(os.path.dirname(path), exist_ok=True)

    # すでにあるデータを読み込み
    rows = []
    if os.path.exists(path):
        with open(path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

    # 追加する行
    new_row = {
        "date": date,
        "start": start,
        "end": end,
        "category": category,
        "name": name
    }

    rows.append(new_row)

    # 書き込み
    with open(path, "w", newline='', encoding="utf-8") as f:
        fieldnames = ["date", "start", "end", "category", "name"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return jsonify({"status": "ok"})




@exclude_api.route("/api/exclude/update", methods=["POST"])
def update_exclude_time():
    data = request.get_json()

    date = data.get("date")
    name = data.get("name")
    start = data.get("start")
    end = data.get("end")
    category = data.get("category")

    original_start = data.get("original_start")
    original_end = data.get("original_end")
    original_category = data.get("original_category")

    if not all([date, name, start, end, category, original_start, original_end, original_category]):
        return jsonify({"error": "Missing fields"}), 400

    month = date[:7]
    path = f"data/exclude_time/exclude_time_{month}.csv"

    # 読み込み
    rows = []
    if os.path.exists(path):
        with open(path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

    # 対象データの削除（該当日・名前・start・end・categoryすべて一致）
    updated_rows = [
        row for row in rows
        if not (
            row["date"] == date and
            row["name"] == name and
            row["start"] == original_start and
            row["end"] == original_end and
            row["category"] == original_category
        )
    ]

    # 新しいデータを追加
    new_row = {
        "date": date,
        "start": start,
        "end": end,
        "category": category,
        "name": name
    }
    updated_rows.append(new_row)

    # 保存
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "start", "end", "category", "name"])
        writer.writeheader()
        writer.writerows(updated_rows)

    return jsonify({"status": "updated"})


@exclude_api.route("/api/exclude/delete", methods=["POST"])
def delete_exclude_time():
    data = request.get_json()
    date = data.get("date")
    name = data.get("name")
    start = data.get("start")
    end = data.get("end")
    category = data.get("category")

    if not all([date, name, start, end, category]):
        return jsonify({"error": "Missing fields"}), 400

    month = date[:7]
    path = f"data/exclude_time/exclude_time_{month}.csv"

    # 現在のデータ読み込み
    rows = []
    if os.path.exists(path):
        with open(path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    # 該当データを除外
    updated_rows = [
        row for row in rows
        if not (
            row["date"] == date and
            row["name"] == name and
            row["start"] == start and
            row["end"] == end and
            row["category"] == category
        )
    ]

    # 上書き保存
    with open(path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "start", "end", "category", "name"])
        writer.writeheader()
        writer.writerows(updated_rows)

    return jsonify({"status": "deleted"})
