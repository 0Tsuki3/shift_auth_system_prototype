# --- routes/manual_memo.py ---
from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import csv
import uuid
from datetime import datetime

memo_bp = Blueprint('memo', __name__, url_prefix='/manual/memo')

MEMO_FILE = 'data/manuals/memo.csv'
CATEGORIES = ['仕込み', '発注', 'お知らせ']


def load_memos():
    if not os.path.exists(MEMO_FILE):
        return []
    with open(MEMO_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_memos(memos):
    with open(MEMO_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'category', 'text', 'timestamp'])
        writer.writeheader()
        writer.writerows(memos)


@memo_bp.route('/', methods=['GET', 'POST'])
def view_memo():
    selected = request.args.get('category', CATEGORIES[0])
    memos = load_memos()
    memos = [m for m in memos if m['category'] == selected]
    return render_template('manual_memo.html', memos=memos, categories=CATEGORIES, selected=selected, account=session.get("account"))


@memo_bp.route('/add', methods=['POST'])
def add_memo():
    category = request.form['category']
    text = request.form['text']
    new_memo = {
        'id': str(uuid.uuid4()),
        'category': category,
        'text': text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    memos = load_memos()
    memos.append(new_memo)
    save_memos(memos)
    return redirect(url_for('memo.view_memo', category=category))


@memo_bp.route('/delete/<memo_id>')
def delete_memo(memo_id):
    memos = load_memos()
    memos = [m for m in memos if m['id'] != memo_id]
    save_memos(memos)
    return redirect(request.referrer or url_for('memo.view_memo'))
