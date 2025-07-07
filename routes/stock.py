from flask import Blueprint, render_template, request, redirect, url_for, session
import csv
import os

stock_bp = Blueprint('stock', __name__)
STOCK_CSV = os.path.join('data', 'stock.csv')
STOCK_ALERT_CSV = os.path.join('data', 'stock_alert.csv')

def get_home_url():
    if session.get('is_admin'):
        return url_for('admin.admin_home')
    elif session.get('is_staff'):
        return url_for('staff.staff_home')
    else:
        return url_for('auth.public_home')

# ストック一覧表示
@stock_bp.route('/stock', methods=['GET'])
def stock_list():
    stocks = []
    with open(STOCK_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stocks.append(row)
    home_url = get_home_url()
    return render_template('stock.html', stocks=stocks, home_url=home_url)

# 在庫数の増減
@stock_bp.route('/stock/update', methods=['POST'])
def stock_update():
    item = request.form['item']
    action = request.form['action']  # 'plus' or 'minus'
    stocks = []
    with open(STOCK_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stocks.append(row)
    for row in stocks:
        if row['item'] == item:
            qty = int(row['quantity'])
            if action == 'plus':
                qty += 1
            elif action == 'minus' and qty > 0:
                qty -= 1
            row['quantity'] = str(qty)
    with open(STOCK_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(stocks)
    return redirect(url_for('stock.stock_list'))

# 商品追加
@stock_bp.route('/stock/add', methods=['POST'])
def stock_add():
    item = request.form['item'].strip()
    quantity = request.form['quantity'].strip()
    if not item or not quantity.isdigit():
        return redirect(url_for('stock.stock_list'))
    stocks = []
    with open(STOCK_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stocks.append(row)
    # 既存商品名チェック
    for row in stocks:
        if row['item'] == item:
            return redirect(url_for('stock.stock_list'))
    stocks.append({'item': item, 'quantity': quantity})
    with open(STOCK_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(stocks)
    return redirect(url_for('stock.stock_list'))

# 一括保存
@stock_bp.route('/stock/bulk_update', methods=['POST'])
def bulk_update():
    items = request.form.getlist('item')
    quantities = request.form.getlist('quantity')
    stocks = []
    for item, qty in zip(items, quantities):
        stocks.append({'item': item, 'quantity': qty})
    with open(STOCK_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(stocks)
    return redirect(url_for('stock.stock_list'))

# アラート管理ページ
@stock_bp.route('/stock/alert', methods=['GET'])
def stock_alert():
    # stock_alert.csvがなければ空で作成
    if not os.path.exists(STOCK_ALERT_CSV):
        with open(STOCK_ALERT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
            writer.writeheader()
    soldout = []
    lowstock = []
    with open(STOCK_ALERT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            qty = int(row['quantity'])
            if qty == 0:
                soldout.append(row)
            elif qty > 0:
                lowstock.append(row)
    home_url = get_home_url()
    return render_template('stock_alert.html', soldout=soldout, lowstock=lowstock, home_url=home_url)

# アラート商品削除
@stock_bp.route('/stock/alert/delete', methods=['POST'])
def stock_alert_delete():
    item = request.form['item']
    rows = []
    with open(STOCK_ALERT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['item'] != item:
                rows.append(row)
    with open(STOCK_ALERT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(rows)
    return redirect(url_for('stock.stock_alert'))

# アラート商品在庫減算
@stock_bp.route('/stock/alert/minus', methods=['POST'])
def stock_alert_minus():
    item = request.form['item']
    rows = []
    with open(STOCK_ALERT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['item'] == item:
                qty = int(row['quantity'])
                if qty > 0:
                    qty -= 1
                row['quantity'] = str(qty)
            rows.append(row)
    with open(STOCK_ALERT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(rows)
    return redirect(url_for('stock.stock_alert'))

# アラート商品追加
@stock_bp.route('/stock/alert/add', methods=['POST'])
def stock_alert_add():
    item = request.form['item'].strip()
    quantity = request.form['quantity'].strip()
    if not item or not quantity.isdigit():
        return redirect(url_for('stock.stock_alert'))
    qty = int(quantity)
    if qty < 0:
        return redirect(url_for('stock.stock_alert'))
    rows = []
    with open(STOCK_ALERT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if row['item'] == item:
                # 既存商品名は追加しない
                return redirect(url_for('stock.stock_alert'))
    rows.append({'item': item, 'quantity': str(qty)})
    with open(STOCK_ALERT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(rows)
    return redirect(url_for('stock.stock_alert'))

# アラート商品在庫増加
@stock_bp.route('/stock/alert/plus', methods=['POST'])
def stock_alert_plus():
    item = request.form['item']
    rows = []
    with open(STOCK_ALERT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['item'] == item:
                qty = int(row['quantity'])
                qty += 1
                row['quantity'] = str(qty)
            rows.append(row)
    with open(STOCK_ALERT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(rows)
    return redirect(url_for('stock.stock_alert'))

# 売り切れ商品を1個に戻す
@stock_bp.route('/stock/alert/restore', methods=['POST'])
def stock_alert_restore():
    item = request.form['item']
    rows = []
    with open(STOCK_ALERT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['item'] == item:
                row['quantity'] = '1'
            rows.append(row)
    with open(STOCK_ALERT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(rows)
    return redirect(url_for('stock.stock_alert'))

# ストック商品削除
@stock_bp.route('/stock/delete', methods=['POST'])
def stock_delete():
    item = request.form['item']
    rows = []
    with open(STOCK_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['item'] != item:
                rows.append(row)
    with open(STOCK_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['item', 'quantity'])
        writer.writeheader()
        writer.writerows(rows)
    return redirect(url_for('stock.stock_list'))
