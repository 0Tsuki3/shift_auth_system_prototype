# routes package
"""
ルーティング層（Presentation層）

FlaskのBlueprintを使ってURLと処理を紐付けます。

各Blueprintは以下の機能を提供:
- auth: ログイン、ログアウト、公開ページ
- admin: 管理者専用ページ
- staff: スタッフ専用ページ
"""

from .auth import auth_bp
from .admin import admin_bp
from .staff import staff_bp

__all__ = ['auth_bp', 'admin_bp', 'staff_bp']

