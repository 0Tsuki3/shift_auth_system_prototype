# services/break_service.py
"""
休憩関連のビジネスロジック

このファイルは「休憩に関する処理」を担当します。
Repository（データ保存）とValidator（チェック）を組み合わせます。
"""

from typing import List, Dict
from models.break_model import Break
from models.shift import Shift
from data_access.break_repository import BreakRepository
from validators.break_validator import BreakValidator


class BreakService:
    """
    休憩サービス（ビジネスロジック）
    
    使い方:
        service = BreakService()
        break_obj = service.create_break('2025-02', break_data, shift)
    """
    
    def __init__(self):
        """
        初期化
        
        repository: データアクセス
        validator: バリデーション
        """
        self.repository = BreakRepository()
        self.validator = BreakValidator()
    
    def get_breaks_by_shift_id(self, month: str, shift_id: int) -> List[Break]:
        """
        シフトIDで休憩を取得
        
        Args:
            month: 'YYYY-MM' 形式
            shift_id: シフトID
        
        Returns:
            Breakオブジェクトのリスト
        """
        return self.repository.find_by_shift_id(month, shift_id)
    
    def get_breaks_by_month(self, month: str) -> List[Break]:
        """
        月別休憩を全件取得
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            Breakオブジェクトのリスト
        """
        return self.repository.find_all_by_month(month)
    
    def create_break(self, month: str, break_obj: Break, shift: Shift = None) -> Break:
        """
        休憩を作成
        
        Args:
            month: 'YYYY-MM' 形式
            break_obj: Breakオブジェクト（id=0）
            shift: シフトオブジェクト（バリデーション用、オプション）
        
        Returns:
            作成されたBreakオブジェクト（IDが採番される）
        
        Raises:
            ValueError: バリデーションエラー
        
        ビジネスロジック:
            1. 個別バリデーション
            2. 既存休憩との被りチェック
            3. 保存
        """
        # 1. 個別バリデーション
        is_valid, errors = self.validator.validate(break_obj, shift)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 既存休憩との被りチェック
        existing_breaks = self.repository.find_by_shift_id(month, break_obj.shift_id)
        all_breaks = existing_breaks + [break_obj]
        
        is_valid_overlap, overlap_errors = self.validator.validate_no_overlap(all_breaks)
        if not is_valid_overlap:
            error_message = "、".join(overlap_errors)
            raise ValueError(f"休憩時間の被りエラー: {error_message}")
        
        # 3. 保存
        saved_break = self.repository.save(month, break_obj)
        return saved_break
    
    def update_break(self, month: str, break_obj: Break, shift: Shift = None) -> Break:
        """
        休憩を更新
        
        Args:
            month: 'YYYY-MM' 形式
            break_obj: Breakオブジェクト（id指定済み）
            shift: シフトオブジェクト（バリデーション用、オプション）
        
        Returns:
            更新されたBreakオブジェクト
        
        Raises:
            ValueError: バリデーションエラー
        """
        # 1. 個別バリデーション
        is_valid, errors = self.validator.validate(break_obj, shift)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 既存休憩との被りチェック（自分自身を除く）
        existing_breaks = self.repository.find_by_shift_id(month, break_obj.shift_id)
        other_breaks = [b for b in existing_breaks if b.id != break_obj.id]
        all_breaks = other_breaks + [break_obj]
        
        is_valid_overlap, overlap_errors = self.validator.validate_no_overlap(all_breaks)
        if not is_valid_overlap:
            error_message = "、".join(overlap_errors)
            raise ValueError(f"休憩時間の被りエラー: {error_message}")
        
        # 3. 保存
        saved_break = self.repository.save(month, break_obj)
        return saved_break
    
    def delete_break(self, month: str, break_id: int) -> bool:
        """
        休憩を削除
        
        Args:
            month: 'YYYY-MM' 形式
            break_id: 休憩ID
        
        Returns:
            削除成功したらTrue、失敗したらFalse
        """
        return self.repository.delete(month, break_id)
    
    def delete_breaks_by_shift_id(self, month: str, shift_id: int) -> int:
        """
        シフトIDに紐づく休憩を全削除
        
        Args:
            month: 'YYYY-MM' 形式
            shift_id: シフトID
        
        Returns:
            削除された休憩の数
        """
        return self.repository.delete_by_shift_id(month, shift_id)
    
    def create_multiple_breaks(self, month: str, breaks: List[Break], shift: Shift = None) -> List[Break]:
        """
        複数の休憩を一括作成
        
        Args:
            month: 'YYYY-MM' 形式
            breaks: Breakオブジェクトのリスト
            shift: シフトオブジェクト（バリデーション用、オプション）
        
        Returns:
            作成されたBreakオブジェクトのリスト
        
        Raises:
            ValueError: バリデーションエラー
        """
        # 1. 一括バリデーション
        if shift:
            is_valid, errors = self.validator.validate_all_with_shift(breaks, shift)
            if not is_valid:
                error_message = "、".join(errors)
                raise ValueError(f"入力エラー: {error_message}")
        
        # 2. 既存休憩との被りチェック
        if breaks:
            shift_id = breaks[0].shift_id
            existing_breaks = self.repository.find_by_shift_id(month, shift_id)
            all_breaks = existing_breaks + breaks
            
            is_valid_overlap, overlap_errors = self.validator.validate_no_overlap(all_breaks)
            if not is_valid_overlap:
                error_message = "、".join(overlap_errors)
                raise ValueError(f"休憩時間の被りエラー: {error_message}")
        
        # 3. 一括保存
        saved_breaks = []
        for break_obj in breaks:
            saved_break = self.repository.save(month, break_obj)
            saved_breaks.append(saved_break)
        
        return saved_breaks
