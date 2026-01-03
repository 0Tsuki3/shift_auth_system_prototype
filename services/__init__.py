# services package
"""
サービス層（ビジネスロジック）

Repository + Validator を組み合わせて、
ビジネスロジックを実装します。

各Serviceは以下の機能を提供:
- get系: データ取得
- create: 新規作成（バリデーション → 保存）
- update: 更新（バリデーション → 保存）
- delete: 削除
"""

from .shift_service import ShiftService
from .staff_service import StaffService
from .auth_service import AuthService

__all__ = ['ShiftService', 'StaffService', 'AuthService']

