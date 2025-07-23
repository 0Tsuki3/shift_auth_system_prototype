# routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash
from utils.csv_utils import load_auth_data

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/")
def public_home():
    from datetime import datetime
    now_month = datetime.now().strftime("%Y-%m")
    return render_template('public_home.html', now_month=now_month)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    error = None
    
    if request.method == "POST":
        account = request.form["account"]
        password = request.form["password"]
        auth_data = load_auth_data()

        if account in auth_data and check_password_hash(auth_data[account]["password"], password):
            session.update({
                "account": account,
                "last_name": auth_data[account]["last_name"],
                "first_name": auth_data[account]["first_name"],
                "role": auth_data[account]["role"],
                "name": f"{auth_data[account]['last_name']} {auth_data[account]['first_name']}"
            })

            # 🔽 ここで admin / staff を分ける
            if session["role"] == "admin":
                return redirect(url_for("admin.admin_home"))
            else:
                return redirect(url_for("staff.staff_home", account=account))
        else:
            error = "アカウント名またはパスワードが違います"

    return render_template("login.html", error=error)




@auth_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))  # トップページへリダイレクト