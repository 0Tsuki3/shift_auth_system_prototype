# services/shift_service.py
"""
シフト関連のビジネスロジック

このファイルは「シフトに関する処理」を担当します。
Repository（データ保存）とValidator（チェック）を組み合わせます。
"""

from typing import List
from models.shift import Shift
from data_access.shift_repository import ShiftRepository
from validators.shift_validator import ShiftValidator


class ShiftService:
    """
    シフトサービス（ビジネスロジック）
    
    使い方:
        service = ShiftService()
        shift = service.create_shift('2025-09', shift_data)
    """
    
    def __init__(self):
        """
        初期化
        
        repository: データアクセス
        validator: バリデーション
        """
        self.repository = ShiftRepository()
        self.validator = ShiftValidator()
    
    def get_shifts_by_month(self, month: str) -> List[Shift]:
        """
        月別シフトを取得
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            Shiftオブジェクトのリスト
        
        Raises:
            ValueError: 月の形式が不正な場合
        """
        # 月の形式チェック
        is_valid, error = self.validator.validate_month(month)
        if not is_valid:
            raise ValueError(error)
        
        # データ取得
        return self.repository.find_all_by_month(month)
    
    def get_shifts_by_account(self, month: str, account: str) -> List[Shift]:
        """
        アカウント別シフトを取得
        
        Args:
            month: 'YYYY-MM' 形式
            account: アカウント名
        
        Returns:
            Shiftオブジェクトのリスト
        """
        # 月の形式チェック
        is_valid, error = self.validator.validate_month(month)
        if not is_valid:
            raise ValueError(error)
        
        # データ取得
        return self.repository.find_by_account(month, account)
    
    def create_shift(self, month: str, shift: Shift) -> Shift:
        """
        シフトを作成
        
        Args:
            month: 'YYYY-MM' 形式
            shift: Shiftオブジェクト（id=0）
        
        Returns:
            作成されたShiftオブジェクト（IDが採番される）
        
        Raises:
            ValueError: バリデーションエラー
        
        ビジネスロジック:
            1. バリデーション
            2. 保存
        """
        # 1. バリデーション
        is_valid, errors = self.validator.validate(shift)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 保存
        saved_shift = self.repository.save(month, shift)
        return saved_shift
    
    def update_shift(self, month: str, shift: Shift) -> Shift:
        """
        シフトを更新
        
        Args:
            month: 'YYYY-MM' 形式
            shift: Shiftオブジェクト（id>0）
        
        Returns:
            更新されたShiftオブジェクト
        
        Raises:
            ValueError: バリデーションエラー、存在しないID
        """
        # 1. バリデーション
        is_valid, errors = self.validator.validate(shift)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 存在チェック
        existing = self.repository.find_by_id(month, shift.id)
        if not existing:
            raise ValueError(f"シフトID {shift.id} が見つかりません")
        
        # 3. 更新
        updated_shift = self.repository.save(month, shift)
        return updated_shift
    
    def delete_shift(self, month: str, shift_id: int) -> bool:
        """
        シフトを削除
        
        Args:
            month: 'YYYY-MM' 形式
            shift_id: シフトID
        
        Returns:
            削除成功したかどうか
        """
        return self.repository.delete(month, shift_id)
    
    def calculate_total_hours(self, month: str, account: str) -> float:
        """
        月間勤務時間を計算
        
        Args:
            month: 'YYYY-MM' 形式
            account: アカウント名
        
        Returns:
            合計勤務時間（時間単位）
        """
        shifts = self.get_shifts_by_account(month, account)
        total_hours = sum(shift.duration_hours() for shift in shifts)
        return round(total_hours, 2)

