# core package
"""
コア機能（デコレーターなど）

アプリ全体で使用する共通機能を提供:
- decorators: 認証・認可のデコレーター
"""

from .decorators import login_required, admin_required, role_required, is_safe_url

__all__ = ['login_required', 'admin_required', 'role_required', 'is_safe_url']

