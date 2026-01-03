# app.py
"""
Flaskアプリケーションのメインファイル

このファイルは「アプリ全体の起動」を担当します。
- Flaskアプリの作成
- 設定
- Blueprintの登録
- エラーハンドリング
"""

import os
from flask import Flask, render_template
from routes import auth_bp, admin_bp, staff_bp


def create_app():
    """
    Flaskアプリケーションを作成
    
    Returns:
        Flask: 設定済みのFlaskアプリ
    
    設計パターン: Application Factory
        テストやデプロイ時に異なる設定で起動できる
    """
    # Flaskアプリの作成
    app = Flask(__name__)
    
    # 設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # XSS対策
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF対策
    
    # Blueprintの登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    
    # エラーハンドリング
    @app.errorhandler(404)
    def not_found(error):
        """404エラーページ"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500エラーページ"""
        return render_template('500.html'), 500
    
    # ヘルスチェック（GCP App Engine用）
    @app.route('/_ah/health')
    def health_check():
        """ヘルスチェックエンドポイント"""
        return 'ok', 200
    
    return app


# アプリの作成
app = create_app()


if __name__ == '__main__':
    """
    開発サーバーで起動
    
    本番環境ではgunicornなどを使用:
        gunicorn app:app
    """
    # ポート番号（環境変数 or デフォルト5050）
    port = int(os.environ.get('PORT', 5050))
    
    # デバッグモード（開発時のみTrue）
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # サーバー起動
    print(f"""
    ================================================
    🚀 Shift Management System Starting...
    ================================================
    
    📍 URL: http://localhost:{port}
    
    🔐 ログインページ: http://localhost:{port}/login
    👤 管理者ページ: http://localhost:{port}/admin/
    👥 スタッフページ: http://localhost:{port}/staff/
    
    💡 Ctrl+C で停止
    ================================================
    """)
    
    app.run(
        host='0.0.0.0',  # 外部からアクセス可能
        port=port,
        debug=debug
    )

