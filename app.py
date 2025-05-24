from flask import Flask
from routes.auth import auth_blueprint
from routes.admin import admin_blueprint
from routes.staff import staff_blueprint

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(staff_blueprint)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5050))  # ← RenderではPORT環境変数が使われる
    #register_upload_routes(app, staff_list, shift_list)
    app.run(host='0.0.0.0', port=port)
