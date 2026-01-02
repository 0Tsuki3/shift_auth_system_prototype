from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import csv
import uuid
from datetime import datetime, timedelta

order_memo_bp = Blueprint('order_memo', __name__, url_prefix='/manual/memo/order')

ORDER_MEMO_FILE = 'data/manuals/order_memo.csv'
ORDER_FIELDS = ['id', 'item_name', 'quantity', 'checked', 'ordered_at', 'ordered_by', 'timestamp']

def load_order_memos():
    if not os.path.exists(ORDER_MEMO_FILE):
        return []
    with open(ORDER_MEMO_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_order_memos(memos):
    with open(ORDER_MEMO_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ORDER_FIELDS)
        writer.writeheader()
        writer.writerows(memos)

@order_memo_bp.route('/', methods=['GET', 'POST'])
def view_order_memo():
    memos = load_order_memos()
    unchecked = [m for m in memos if m.get('checked', '0') == '0']
    checked = []
    yesterday = (datetime.now() - timedelta(days=1)).date()
    for m in memos:
        if m.get('checked', '0') == '1':
            ordered_at = m.get('ordered_at', '')
            if ordered_at:
                try:
                    ordered_date = datetime.strptime(ordered_at[:10], '%Y-%m-%d').date()
                    if ordered_date >= yesterday:
                        checked.append(m)
                except Exception:
                    checked.append(m)  # パース失敗は表示
    # 発注済みは発注日昇順でソート
    checked.sort(key=lambda m: m.get('ordered_at', ''))
    return render_template('order_memo.html', unchecked=unchecked, checked=checked, title='発注メモ', add_url=url_for('order_memo.add_order_memo'), account=session.get("account"))

@order_memo_bp.route('/add', methods=['POST'])
def add_order_memo():
    item_name = request.form['item_name']
    quantity = request.form.get('quantity', '')
    ordered_by = request.form.get('ordered_by', '')
    new_memo = {
        'id': str(uuid.uuid4()),
        'item_name': item_name,
        'quantity': quantity,
        'checked': '0',
        'ordered_at': '',
        'ordered_by': ordered_by,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    memos = load_order_memos()
    memos.append(new_memo)
    save_order_memos(memos)
    return redirect(url_for('order_memo.view_order_memo'))

@order_memo_bp.route('/check/<memo_id>', methods=['POST'])
def check_order_memo(memo_id):
    memos = load_order_memos()
    memo = next((m for m in memos if m['id'] == memo_id), None)
    if not memo:
        return redirect(url_for('order_memo.view_order_memo'))
    if memo.get('checked', '0') == '0':
        memo['checked'] = '1'
        memo['ordered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        memo['ordered_by'] = request.form.get('ordered_by', '')
    else:
        memo['checked'] = '0'
        memo['ordered_at'] = ''
        memo['ordered_by'] = ''
    save_order_memos(memos)
    return redirect(url_for('order_memo.view_order_memo'))

@order_memo_bp.route('/edit/<memo_id>', methods=['GET', 'POST'])
def edit_order_memo(memo_id):
    memos = load_order_memos()
    memo = next((m for m in memos if m['id'] == memo_id), None)
    if not memo:
        return redirect(url_for('order_memo.view_order_memo'))
    if request.method == 'POST':
        memo['item_name'] = request.form['item_name']
        memo['quantity'] = request.form.get('quantity', '')
        memo['ordered_by'] = request.form.get('ordered_by', '')
        save_order_memos(memos)
        return redirect(url_for('order_memo.view_order_memo'))
    return render_template('order_memo_edit.html', memo=memo)

@order_memo_bp.route('/update_ordered_by/<memo_id>', methods=['POST'])
def update_ordered_by(memo_id):
    memos = load_order_memos()
    memo = next((m for m in memos if m['id'] == memo_id), None)
    if not memo:
        return redirect(url_for('order_memo.view_order_memo'))
    memo['ordered_by'] = request.form.get('ordered_by', '')
    save_order_memos(memos)
    return redirect(url_for('order_memo.view_order_memo'))

@order_memo_bp.route('/delete/<memo_id>')
def delete_order_memo(memo_id):
    memos = load_order_memos()
    memos = [m for m in memos if m['id'] != memo_id]
    save_order_memos(memos)
    return redirect(url_for('order_memo.view_order_memo')) 