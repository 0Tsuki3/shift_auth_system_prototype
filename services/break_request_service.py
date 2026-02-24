# services/break_request_service.py
"""
休憩希望関連のビジネスロジック

このファイルは「休憩希望に関する処理」を担当します。
Repository（データ保存）とValidator（チェック）を組み合わせます。
"""

from typing import List
from models.break_request import BreakRequest
from models.shift_request import ShiftRequest
from data_access.break_request_repository import BreakRequestRepository
from validators.break_validator import BreakValidator


class BreakRequestService:
    """
    休憩希望サービス（ビジネスロジック）
    
    使い方:
        service = BreakRequestService()
        break_request = service.create_break_request('2025-02', break_request_data)
    """
    
    def __init__(self):
        """
        初期化
        
        repository: データアクセス
        validator: バリデーション（Break用のValidatorを流用）
        """
        self.repository = BreakRequestRepository()
        self.validator = BreakValidator()
    
    def get_break_requests_by_shift_request_id(self, month: str, shift_request_id: int) -> List[BreakRequest]:
        """
        シフト希望IDで休憩希望を取得
        
        Args:
            month: 'YYYY-MM' 形式
            shift_request_id: シフト希望ID
        
        Returns:
            BreakRequestオブジェクトのリスト
        """
        return self.repository.find_by_shift_request_id(month, shift_request_id)
    
    def get_break_requests_by_month(self, month: str) -> List[BreakRequest]:
        """
        月別休憩希望を全件取得
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            BreakRequestオブジェクトのリスト
        """
        return self.repository.find_all_by_month(month)
    
    def create_break_request(self, month: str, break_request: BreakRequest) -> BreakRequest:
        """
        休憩希望を作成
        
        Args:
            month: 'YYYY-MM' 形式
            break_request: BreakRequestオブジェクト（id=0）
        
        Returns:
            作成されたBreakRequestオブジェクト（IDが採番される）
        
        Raises:
            ValueError: バリデーションエラー
        """
        # BreakRequestをBreakに変換してバリデーション（時刻チェックのため）
        from models.break_model import Break
        temp_break = Break(
            id=0,
            shift_id=break_request.shift_request_id,
            break_start=break_request.break_start,
            break_end=break_request.break_end
        )
        
        # 個別バリデーション（シフトとの整合性チェックは行わない）
        is_valid, errors = self.validator.validate(temp_break, shift=None)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 既存休憩希望との被りチェック
        existing_break_requests = self.repository.find_by_shift_request_id(month, break_request.shift_request_id)
        
        # BreakRequestをBreakに変換してバリデーション
        existing_breaks = [
            Break(id=br.id, shift_id=0, break_start=br.break_start, break_end=br.break_end)
            for br in existing_break_requests
        ]
        all_breaks = existing_breaks + [temp_break]
        
        is_valid_overlap, overlap_errors = self.validator.validate_no_overlap(all_breaks)
        if not is_valid_overlap:
            error_message = "、".join(overlap_errors)
            raise ValueError(f"休憩時間の被りエラー: {error_message}")
        
        # 保存
        saved_break_request = self.repository.save(month, break_request)
        return saved_break_request
    
    def update_break_request(self, month: str, break_request: BreakRequest) -> BreakRequest:
        """
        休憩希望を更新
        
        Args:
            month: 'YYYY-MM' 形式
            break_request: BreakRequestオブジェクト（id指定済み）
        
        Returns:
            更新されたBreakRequestオブジェクト
        
        Raises:
            ValueError: バリデーションエラー
        """
        # BreakRequestをBreakに変換してバリデーション
        from models.break_model import Break
        temp_break = Break(
            id=break_request.id,
            shift_id=break_request.shift_request_id,
            break_start=break_request.break_start,
            break_end=break_request.break_end
        )
        
        # 個別バリデーション
        is_valid, errors = self.validator.validate(temp_break, shift=None)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 既存休憩希望との被りチェック（自分自身を除く）
        existing_break_requests = self.repository.find_by_shift_request_id(month, break_request.shift_request_id)
        other_break_requests = [br for br in existing_break_requests if br.id != break_request.id]
        
        other_breaks = [
            Break(id=br.id, shift_id=0, break_start=br.break_start, break_end=br.break_end)
            for br in other_break_requests
        ]
        all_breaks = other_breaks + [temp_break]
        
        is_valid_overlap, overlap_errors = self.validator.validate_no_overlap(all_breaks)
        if not is_valid_overlap:
            error_message = "、".join(overlap_errors)
            raise ValueError(f"休憩時間の被りエラー: {error_message}")
        
        # 保存
        saved_break_request = self.repository.save(month, break_request)
        return saved_break_request
    
    def delete_break_request(self, month: str, break_request_id: int) -> bool:
        """
        休憩希望を削除
        
        Args:
            month: 'YYYY-MM' 形式
            break_request_id: 休憩希望ID
        
        Returns:
            削除成功したらTrue、失敗したらFalse
        """
        return self.repository.delete(month, break_request_id)
    
    def delete_break_requests_by_shift_request_id(self, month: str, shift_request_id: int) -> int:
        """
        シフト希望IDに紐づく休憩希望を全削除
        
        Args:
            month: 'YYYY-MM' 形式
            shift_request_id: シフト希望ID
        
        Returns:
            削除された休憩希望の数
        """
        return self.repository.delete_by_shift_request_id(month, shift_request_id)
