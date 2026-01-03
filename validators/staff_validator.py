# validators/staff_validator.py
"""
スタッフデータのバリデーション

このファイルは「スタッフデータが正しいかチェック」を担当します。
例: アカウント名が3文字以上、時給が0以上、など
"""

from typing import Tuple, List
from models.staff import Staff
from datetime import datetime


class StaffValidator:
    """
    スタッフバリデーション
    
    使い方:
        validator = StaffValidator()
        is_valid, errors = validator.validate(staff)
        if not is_valid:
            print("エラー:", errors)
    """
    
    def validate(self, staff: Staff) -> Tuple[bool, List[str]]:
        """
        スタッフデータの妥当性チェック
        
        Args:
            staff: Staffオブジェクト
        
        Returns:
            (is_valid, errors)
            - is_valid: True=OK, False=NG
            - errors: エラーメッセージのリスト
        
        チェック内容:
            - 必須項目（account, last_name, first_name）
            - アカウント名の長さ（3文字以上）
            - アカウント名の文字種（英数字とアンダースコアのみ）
            - 時給の下限（0以上のみ、上限なし）
            - 入社日の形式（YYYY-MM-DD）
        """
        errors = []
        
        # 1. 必須項目チェック
        if not staff.account:
            errors.append("アカウント名は必須です")
        elif len(staff.account) < 3:
            errors.append("アカウント名は3文字以上にしてください")
        elif not self._is_valid_account_name(staff.account):
            errors.append("アカウント名は英数字とアンダースコアのみ使用できます")
        
        if not staff.last_name:
            errors.append("姓は必須です")
        
        if not staff.first_name:
            errors.append("名は必須です")
        
        # 2. 時給のチェック
        if staff.hourly_wage < 0:
            errors.append("時給は0以上にしてください")
        
        # 3. 入社日の形式チェック（任意項目だがある場合はチェック）
        if staff.hired_date:
            try:
                datetime.strptime(staff.hired_date, '%Y-%m-%d')
            except ValueError:
                errors.append("入社日はYYYY-MM-DD形式で入力してください")
        
        # 結果を返す
        return len(errors) == 0, errors
    
    def _is_valid_account_name(self, account: str) -> bool:
        """
        アカウント名の文字種チェック（内部用）
        
        Args:
            account: アカウント名
        
        Returns:
            True: OK（英数字とアンダースコアのみ）
            False: NG（それ以外の文字が含まれる）
        """
        import re
        # 英数字とアンダースコアのみ許可
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, account))


