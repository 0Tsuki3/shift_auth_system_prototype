# services/staff_service.py
"""
スタッフ関連のビジネスロジック

このファイルは「スタッフに関する処理」を担当します。
Repository（データ保存）とValidator（チェック）を組み合わせます。
"""

from typing import List, Optional
from models.staff import Staff
from data_access.staff_repository import StaffRepository
from validators.staff_validator import StaffValidator


class StaffService:
    """
    スタッフサービス（ビジネスロジック）
    
    使い方:
        service = StaffService()
        staff = service.create_staff(staff_data)
    """
    
    def __init__(self):
        """
        初期化
        
        repository: データアクセス
        validator: バリデーション
        """
        self.repository = StaffRepository()
        self.validator = StaffValidator()
    
    def get_all_staff(self) -> List[Staff]:
        """
        全スタッフを取得
        
        Returns:
            Staffオブジェクトのリスト
        """
        return self.repository.find_all()
    
    def get_staff_by_id(self, staff_id: int) -> Optional[Staff]:
        """
        IDでスタッフを取得
        
        Args:
            staff_id: スタッフID
        
        Returns:
            Staffオブジェクト、見つからなければNone
        """
        return self.repository.find_by_id(staff_id)
    
    def get_staff_by_account(self, account: str) -> Optional[Staff]:
        """
        アカウント名でスタッフを取得
        
        Args:
            account: アカウント名
        
        Returns:
            Staffオブジェクト、見つからなければNone
        """
        return self.repository.find_by_account(account)
    
    def create_staff(self, staff: Staff) -> Staff:
        """
        スタッフを作成
        
        Args:
            staff: Staffオブジェクト（id=0）
        
        Returns:
            作成されたStaffオブジェクト（IDが採番される）
        
        Raises:
            ValueError: バリデーションエラー、重複エラー
        
        ビジネスロジック:
            1. バリデーション
            2. 重複チェック（Repository内で実施）
            3. 保存
        """
        # 1. バリデーション
        is_valid, errors = self.validator.validate(staff)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 保存（Repository内で重複チェック）
        try:
            saved_staff = self.repository.save(staff)
            return saved_staff
        except ValueError as e:
            # Repository層からの重複エラーをそのまま上げる
            raise
    
    def update_staff(self, staff: Staff) -> Staff:
        """
        スタッフを更新
        
        Args:
            staff: Staffオブジェクト（id>0）
        
        Returns:
            更新されたStaffオブジェクト
        
        Raises:
            ValueError: バリデーションエラー、存在しないID
        """
        # 1. バリデーション
        is_valid, errors = self.validator.validate(staff)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 存在チェック
        existing = self.repository.find_by_id(staff.id)
        if not existing:
            raise ValueError(f"スタッフID {staff.id} が見つかりません")
        
        # 3. 更新
        try:
            updated_staff = self.repository.save(staff)
            return updated_staff
        except ValueError as e:
            # Repository層からの重複エラーをそのまま上げる
            raise
    
    def delete_staff(self, staff_id: int) -> bool:
        """
        スタッフを削除
        
        Args:
            staff_id: スタッフID
        
        Returns:
            削除成功したかどうか
        """
        return self.repository.delete(staff_id)

