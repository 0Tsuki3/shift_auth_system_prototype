# routes/auth.py
"""
認証関連のルート（エンドポイント）

このファイルは「ログイン・ログアウト」のURLを担当します。
URL → 処理 の対応を定義します。
"""

from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from services.auth_service import AuthService
from core.decorators import is_safe_url

# Blueprintの作成（auth関連のURLをまとめる）
auth_bp = Blueprint('auth', __name__)

# AuthServiceのインスタンス
auth_service = AuthService()


@auth_bp.route('/')
def public_home():
    """
    公開ホームページ
    
    URL: /
    
    誰でもアクセス可能（ログイン不要）
    """
    from datetime import datetime
    now_month = datetime.now().strftime('%Y-%m')
    
    return render_template('public_home.html', now_month=now_month)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    ログインページ
    
    URL: /login
    
    GET: ログインフォームを表示
    POST: ログイン処理を実行
    """
    # ログイン後のリダイレクト先を取得
    next_url = request.args.get('next') or request.form.get('next')
    
    if request.method == 'POST':
        # フォームからデータ取得
        account = request.form.get('account')
        password = request.form.get('password')
        
        # ログイン処理
        auth = auth_service.login(account, password)
        
        if auth:
            # ログイン成功：セッションに保存
            from services.staff_service import StaffService
            staff_service = StaffService()
            staff = staff_service.get_staff_by_account(account)
            
            session['account'] = auth.account
            session['role'] = auth.role
            
            if staff:
                session['last_name'] = staff.last_name
                session['first_name'] = staff.first_name
                session['name'] = staff.full_name
            
            flash(f'ようこそ、{session.get("name", account)}さん', 'success')
            
            # リダイレクト先の決定
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            
            # デフォルトのリダイレクト先
            if auth.is_admin:
                return redirect(url_for('admin.admin_home'))
            else:
                return redirect(url_for('staff.staff_home'))
        else:
            # ログイン失敗
            flash('アカウント名またはパスワードが違います', 'error')
    
    return render_template('login.html', next=next_url)


@auth_bp.route('/logout')
def logout():
    """
    ログアウト
    
    URL: /logout
    
    セッションをクリアしてログインページにリダイレクト
    """
    session.clear()
    flash('ログアウトしました', 'info')
    return redirect(url_for('auth.login'))

