from flask import Flask
from routes.auth import auth_blueprint
from routes.admin import admin_blueprint
from routes.staff import staff_blueprint
from routes.stock import stock_bp # ← 追加
from routes.manual import manual_bp
from routes.shift_public import shift_public_bp
from routes.manual_memo import kitchen_memo_bp
from routes.order_memo import order_memo_bp
from routes.notice_memo import notice_memo_bp
from routes.daily_shift import daily_shift_bp
from routes.exclude_api import exclude_api
from routes.monthly_shift import monthly_shift_bp  # すでに存在していればOK



app = Flask(__name__)
app.secret_key = "secret_key_for_session"



# 各ブループリントを登録
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(staff_blueprint)
app.register_blueprint(stock_bp)  # ← 追加
app.register_blueprint(manual_bp)
app.register_blueprint(shift_public_bp)
app.register_blueprint(kitchen_memo_bp)
app.register_blueprint(order_memo_bp)
app.register_blueprint(notice_memo_bp)
app.register_blueprint(daily_shift_bp)
app.register_blueprint(exclude_api)
app.register_blueprint(monthly_shift_bp)



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5050))  # Render対応
    app.run(host='0.0.0.0', port=port)
