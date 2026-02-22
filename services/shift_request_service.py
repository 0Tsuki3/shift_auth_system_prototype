# services/shift_request_service.py
"""
シフト希望関連のビジネスロジック

このファイルは「シフト希望に関する処理」を担当します。
Repository（データ保存）とValidator（チェック）を組み合わせます。
"""

from typing import List
from models.shift_request import ShiftRequest
from data_access.shift_request_repository import ShiftRequestRepository
from validators.shift_request_validator import ShiftRequestValidator


class ShiftRequestService:
    """
    シフト希望サービス（ビジネスロジック）
    
    使い方:
        service = ShiftRequestService()
        request = service.create_request('2025-09', request_data)
    """
    
    def __init__(self):
        """
        初期化
        
        repository: データアクセス
        validator: バリデーション
        """
        self.repository = ShiftRequestRepository()
        self.validator = ShiftRequestValidator()
    
    def get_requests_by_month(self, month: str) -> List[ShiftRequest]:
        """
        月別シフト希望を取得
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            ShiftRequestオブジェクトのリスト
        
        Raises:
            ValueError: 月の形式が不正な場合
        """
        # 月の形式チェック
        is_valid, error = self.validator.validate_month(month)
        if not is_valid:
            raise ValueError(error)
        
        # データ取得
        return self.repository.find_all_by_month(month)
    
    def get_requests_by_account(self, month: str, account: str) -> List[ShiftRequest]:
        """
        アカウント別シフト希望を取得
        
        Args:
            month: 'YYYY-MM' 形式
            account: アカウント名
        
        Returns:
            ShiftRequestオブジェクトのリスト
        """
        # 月の形式チェック
        is_valid, error = self.validator.validate_month(month)
        if not is_valid:
            raise ValueError(error)
        
        # データ取得
        return self.repository.find_by_account(month, account)
    
    def get_requests_by_status(self, month: str, status: str) -> List[ShiftRequest]:
        """
        ステータス別シフト希望を取得
        
        Args:
            month: 'YYYY-MM' 形式
            status: ステータス（pending/approved/rejected）
        
        Returns:
            ShiftRequestオブジェクトのリスト
        """
        # 月の形式チェック
        is_valid, error = self.validator.validate_month(month)
        if not is_valid:
            raise ValueError(error)
        
        # データ取得
        return self.repository.find_by_status(month, status)
    
    def get_request_by_id(self, month: str, request_id: int) -> ShiftRequest:
        """
        IDでシフト希望を取得
        
        Args:
            month: 'YYYY-MM' 形式
            request_id: シフト希望ID
        
        Returns:
            ShiftRequestオブジェクト
        
        Raises:
            ValueError: 見つからない場合
        """
        request = self.repository.find_by_id(month, request_id)
        if not request:
            raise ValueError(f"シフト希望ID {request_id} が見つかりません")
        return request
    
    def create_request(self, month: str, request: ShiftRequest) -> ShiftRequest:
        """
        シフト希望を作成
        
        Args:
            month: 'YYYY-MM' 形式
            request: ShiftRequestオブジェクト（id=0）
        
        Returns:
            作成されたShiftRequestオブジェクト（IDが採番される）
        
        Raises:
            ValueError: バリデーションエラー
        
        ビジネスロジック:
            1. バリデーション
            2. 保存
        """
        # 1. バリデーション
        is_valid, errors = self.validator.validate(request)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 保存
        saved_request = self.repository.save(month, request)
        return saved_request
    
    def update_request(self, month: str, request: ShiftRequest) -> ShiftRequest:
        """
        シフト希望を更新
        
        Args:
            month: 'YYYY-MM' 形式
            request: ShiftRequestオブジェクト（id>0）
        
        Returns:
            更新されたShiftRequestオブジェクト
        
        Raises:
            ValueError: バリデーションエラー、存在しないID
        """
        # 1. バリデーション
        is_valid, errors = self.validator.validate(request)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 存在チェック
        existing = self.repository.find_by_id(month, request.id)
        if not existing:
            raise ValueError(f"シフト希望ID {request.id} が見つかりません")
        
        # 3. 更新
        updated_request = self.repository.save(month, request)
        return updated_request
    
    def delete_request(self, month: str, request_id: int) -> bool:
        """
        シフト希望を削除
        
        Args:
            month: 'YYYY-MM' 形式
            request_id: シフト希望ID
        
        Returns:
            削除成功したかどうか
        """
        return self.repository.delete(month, request_id)
    
    def update_status(self, month: str, request_id: int, status: str) -> ShiftRequest:
        """
        シフト希望のステータスを更新（管理者用）
        
        Args:
            month: 'YYYY-MM' 形式
            request_id: シフト希望ID
            status: 新しいステータス（pending/approved/rejected）
        
        Returns:
            更新されたShiftRequestオブジェクト
        
        Raises:
            ValueError: 存在しないID、無効なステータス
        """
        # ステータスの妥当性チェック
        valid_statuses = ['pending', 'approved', 'rejected']
        if status not in valid_statuses:
            raise ValueError(f"ステータスは {'/'.join(valid_statuses)} のいずれかにしてください")
        
        # シフト希望の取得
        request = self.repository.find_by_id(month, request_id)
        if not request:
            raise ValueError(f"シフト希望ID {request_id} が見つかりません")
        
        # ステータス更新
        request.status = status
        updated_request = self.repository.save(month, request)
        return updated_request
