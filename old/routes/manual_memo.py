# --- routes/manual_memo.py ---
from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import csv
import uuid
from datetime import datetime, date

kitchen_memo_bp = Blueprint('kitchen_memo', __name__, url_prefix='/manual/memo/kitchen')

KITCHEN_MEMO_FILE = 'data/manuals/kitchen_memo.csv'
KITCHEN_FIELDS = ['id', 'item_name', 'quantity', 'timing', 'due_date', 'checked', 'checked_at', 'done_by', 'timestamp']
KITCHEN_TIMINGS = ['指定しない', '開け', '中', '締め']


def load_kitchen_memos():
    if not os.path.exists(KITCHEN_MEMO_FILE):
        return []
    with open(KITCHEN_MEMO_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_kitchen_memos(memos):
    with open(KITCHEN_MEMO_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=KITCHEN_FIELDS)
        writer.writeheader()
        writer.writerows(memos)


@kitchen_memo_bp.route('/', methods=['GET', 'POST'])
def view_kitchen_memo():
    memos = load_kitchen_memos()
    today = date.today()
    unchecked = []
    for m in memos:
        if m.get('checked', '0') != '0':
            continue
        due = m.get('due_date', '').strip()
        if due:
            try:
                due_dt = datetime.strptime(due, '%Y-%m-%d').date()
                if due_dt < today:
                    continue  # 今日より前は除外
            except Exception:
                pass  # 日付パース失敗は表示
        unchecked.append(m)
    # タイミングの順序指定
    timing_order = {'指定しない': 0, '開け': 1, '中': 2, '締め': 3}
    def sort_key(m):
        due = m.get('due_date', '')
        timing = m.get('timing', '指定しない')
        return (
            due if due else '9999-99-99',
            timing_order.get(timing, 99)
        )
    unchecked.sort(key=sort_key)
    checked = [m for m in memos if m.get('checked', '0') == '1']
    # 完了済みはchecked_at昇順
    checked.sort(key=lambda m: m.get('checked_at', ''))
    return render_template('manual_memo.html', unchecked=unchecked, checked=checked, title='仕込みメモ', add_url=url_for('kitchen_memo.add_kitchen_memo'), delete_url='kitchen_memo.delete_kitchen_memo', check_url='kitchen_memo.check_kitchen_memo', timings=KITCHEN_TIMINGS, account=session.get("account"))


@kitchen_memo_bp.route('/add', methods=['POST'])
def add_kitchen_memo():
    item_name = request.form['item_name']
    quantity = request.form['quantity']
    timing = request.form['timing']
    due_date = request.form.get('due_date', '')
    new_memo = {
        'id': str(uuid.uuid4()),
        'item_name': item_name,
        'quantity': quantity,
        'timing': timing,
        'due_date': due_date,
        'checked': '0',
        'checked_at': '',
        'done_by': '',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    memos = load_kitchen_memos()
    memos.append(new_memo)
    save_kitchen_memos(memos)
    return redirect(url_for('kitchen_memo.view_kitchen_memo'))


@kitchen_memo_bp.route('/delete/<memo_id>')
def delete_kitchen_memo(memo_id):
    memos = load_kitchen_memos()
    memos = [m for m in memos if m['id'] != memo_id]
    save_kitchen_memos(memos)
    return redirect(url_for('kitchen_memo.view_kitchen_memo'))


@kitchen_memo_bp.route('/check/<memo_id>', methods=['GET', 'POST'])
def check_kitchen_memo(memo_id):
    memos = load_kitchen_memos()
    memo = next((m for m in memos if m['id'] == memo_id), None)
    if not memo:
        return redirect(url_for('kitchen_memo.view_kitchen_memo'))
    if memo.get('checked', '0') == '0':
        memo['checked'] = '1'
        memo['checked_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        memo['done_by'] = ''
    else:
        memo['checked'] = '0'
        memo['checked_at'] = ''
        memo['done_by'] = ''
    save_kitchen_memos(memos)
    return redirect(url_for('kitchen_memo.view_kitchen_memo'))


@kitchen_memo_bp.route('/edit/<memo_id>', methods=['GET', 'POST'])
def edit_kitchen_memo(memo_id):
    memos = load_kitchen_memos()
    memo = next((m for m in memos if m['id'] == memo_id), None)
    if not memo:
        return redirect(url_for('kitchen_memo.view_kitchen_memo'))
    if request.method == 'POST':
        memo['item_name'] = request.form['item_name']
        memo['quantity'] = request.form['quantity']
        memo['timing'] = request.form['timing']
        memo['due_date'] = request.form.get('due_date', '')
        save_kitchen_memos(memos)
        return redirect(url_for('kitchen_memo.view_kitchen_memo'))
    return render_template('manual_memo_edit.html', memo=memo, timings=KITCHEN_TIMINGS)


@kitchen_memo_bp.route('/update_done_by/<memo_id>', methods=['POST'])
def update_done_by(memo_id):
    memos = load_kitchen_memos()
    memo = next((m for m in memos if m['id'] == memo_id), None)
    if not memo:
        return redirect(url_for('kitchen_memo.view_kitchen_memo'))
    memo['done_by'] = request.form.get('done_by', '')
    save_kitchen_memos(memos)
    return redirect(url_for('kitchen_memo.view_kitchen_memo'))
