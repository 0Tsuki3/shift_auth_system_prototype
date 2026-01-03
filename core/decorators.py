# core/decorators.py
"""
認証・認可のデコレーター

このファイルは「ログインチェック」「権限チェック」を担当します。
Routesで使用して、アクセス制御を行います。

使い方:
    @login_required
    def some_page():
        return "ログインが必要なページ"
    
    @admin_required
    def admin_page():
        return "管理者専用ページ"
"""

from functools import wraps
from flask import session, redirect, url_for, request
from urllib.parse import urlparse, urljoin


def is_safe_url(target: str) -> bool:
    """
    リダイレクト先URLが安全かチェック
    
    Args:
        target: リダイレクト先URL
    
    Returns:
        True: 安全、False: 危険
    
    セキュリティ:
        外部サイトへのリダイレクトを防ぐ
        例: https://evil.com にリダイレクトされないようにする
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def login_required(func):
    """
    ログイン必須デコレーター
    
    使い方:
        @login_required
        def my_page():
            return "ログイン済みユーザーのみアクセス可能"
    
    動作:
        1. セッションに'account'があるかチェック
        2. なければログインページにリダイレクト
        3. あれば元の関数を実行
    
    ログイン後のリダイレクト:
        ログイン前にアクセスしようとしたURLを保持
        例: /admin → /login?next=/admin → ログイン成功 → /admin
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # セッションにaccountがあるかチェック
        if 'account' not in session:
            # ログインページにリダイレクト（元のURLを保持）
            return redirect(url_for('auth.login', next=request.url))
        
        # ログイン済みなら元の関数を実行
        return func(*args, **kwargs)
    
    return wrapper


def admin_required(func):
    """
    管理者専用デコレーター
    
    使い方:
        @admin_required
        def admin_panel():
            return "管理者専用パネル"
    
    動作:
        1. セッションに'role'があるかチェック
        2. roleが'admin'でなければログインページにリダイレクト
        3. 'admin'なら元の関数を実行
    
    注意:
        @login_requiredも兼ねています（ログインチェック不要）
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ログインチェック + 管理者チェック
        if session.get('role') != 'admin':
            # ログインページにリダイレクト（元のURLを保持）
            return redirect(url_for('auth.login', next=request.url))
        
        # 管理者なら元の関数を実行
        return func(*args, **kwargs)
    
    return wrapper


def role_required(required_role: str):
    """
    特定のロール専用デコレーター（汎用版）
    
    使い方:
        @role_required('manager')
        def manager_page():
            return "マネージャー専用ページ"
    
    Args:
        required_role: 必要なロール名
    
    注意:
        現在は'admin'と'staff'のみですが、
        将来的に'manager'などを追加する時に便利
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # ログインチェック + ロールチェック
            if session.get('role') != required_role:
                # ログインページにリダイレクト（元のURLを保持）
                return redirect(url_for('auth.login', next=request.url))
            
            # 条件を満たせば元の関数を実行
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

