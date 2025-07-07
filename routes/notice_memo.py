from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import csv
import uuid
from datetime import datetime

notice_memo_bp = Blueprint('notice_memo', __name__, url_prefix='/manual/memo/notice')

NOTICE_MEMO_FILE = 'data/manuals/notice_memo.csv'

def load_notice_memos():
    if not os.path.exists(NOTICE_MEMO_FILE):
        return []
    with open(NOTICE_MEMO_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_notice_memos(memos):
    with open(NOTICE_MEMO_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'text', 'timestamp'])
        writer.writeheader()
        writer.writerows(memos)

@notice_memo_bp.route('/', methods=['GET', 'POST'])
def view_notice_memo():
    memos = load_notice_memos()
    return render_template('manual_memo.html', memos=memos, title='お知らせメモ', add_url=url_for('notice_memo.add_notice_memo'), delete_url='notice_memo.delete_notice_memo', account=session.get("account"))

@notice_memo_bp.route('/add', methods=['POST'])
def add_notice_memo():
    text = request.form['text']
    new_memo = {
        'id': str(uuid.uuid4()),
        'text': text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    memos = load_notice_memos()
    memos.append(new_memo)
    save_notice_memos(memos)
    return redirect(url_for('notice_memo.view_notice_memo'))

@notice_memo_bp.route('/delete/<memo_id>')
def delete_notice_memo(memo_id):
    memos = load_notice_memos()
    memos = [m for m in memos if m['id'] != memo_id]
    save_notice_memos(memos)
    return redirect(url_for('notice_memo.view_notice_memo')) 