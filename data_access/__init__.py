# data_access package
"""
Repository層（データアクセス層）

現時点ではCSV実装、将来的にSQLに移行します。
各Repositoryは以下の機能を提供:
- find_all(): 全件取得
- find_by_id(): ID検索
- save(): 保存（新規・更新）
- delete(): 削除
- ID自動採番
"""

from .shift_repository import ShiftRepository
from .staff_repository import StaffRepository
from .auth_repository import AuthRepository

__all__ = ['ShiftRepository', 'StaffRepository', 'AuthRepository']

