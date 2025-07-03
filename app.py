from flask import Flask
from routes.auth import auth_blueprint
from routes.admin import admin_blueprint
from routes.staff import staff_blueprint
from routes.stock import stock_blueprint  # ← 追加
from routes.manual import manual_bp
from routes.shift_public import shift_public_bp
from routes.manual_memo import memo_bp



app = Flask(__name__)
app.secret_key = "secret_key_for_session"



# 各ブループリントを登録
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(staff_blueprint)
app.register_blueprint(stock_blueprint)  # ← 追加
app.register_blueprint(manual_bp)
app.register_blueprint(shift_public_bp)
app.register_blueprint(memo_bp)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5050))  # Render対応
    app.run(host='0.0.0.0', port=port)
