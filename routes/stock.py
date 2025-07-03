from flask import Blueprint, render_template, request, redirect, url_for, session
import pandas as pd
import os

stock_blueprint = Blueprint('stock', __name__, url_prefix='/stock')

STOCK_FILE = 'data/stock.csv'

def load_stock():
    if not os.path.exists(STOCK_FILE):
        return pd.DataFrame(columns=['item', 'quantity'])
    return pd.read_csv(STOCK_FILE)

def save_stock(df):
    df.to_csv(STOCK_FILE, index=False)

@stock_blueprint.route('/', methods=['GET', 'POST'])
def stock_home():
    df = load_stock()

    if request.method == 'POST':
        # 削除処理
        delete_item = request.form.get('delete_item')
        if delete_item:
            df = df[df['item'] != delete_item]
            save_stock(df)
            return redirect(url_for('stock.stock_home'))

        # 既存商品の更新
        for item in df['item']:
            qty = request.form.get(item)
            if qty is not None and qty.isdigit():
                df.loc[df['item'] == item, 'quantity'] = int(qty)

        # 新規追加
        new_item = request.form.get('new_item_name')
        new_qty = request.form.get('new_item_qty')
        if new_item and new_qty and new_qty.isdigit():
            if new_item not in df['item'].values:
                new_row = {'item': new_item, 'quantity': int(new_qty)}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        save_stock(df)
        return redirect(url_for('stock.stock_home'))

    stock_list = df.to_dict(orient='records')
    return render_template('stock.html', stock_list=stock_list, account=session.get("account"))
