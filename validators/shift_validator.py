# validators/shift_validator.py
"""
シフトデータのバリデーション

このファイルは「シフトデータが正しいかチェック」を担当します。
例: 開始時刻 < 終了時刻、勤務時間が12時間以内、など
"""

from typing import Tuple, List
from models.shift import Shift
from datetime import datetime, date


class ShiftValidator:
    """
    シフトバリデーション
    
    使い方:
        validator = ShiftValidator()
        is_valid, errors = validator.validate(shift)
        if not is_valid:
            print("エラー:", errors)
    """
    
    def validate(self, shift: Shift) -> Tuple[bool, List[str]]:
        """
        シフトデータの妥当性チェック
        
        Args:
            shift: Shiftオブジェクト
        
        Returns:
            (is_valid, errors)
            - is_valid: True=OK, False=NG
            - errors: エラーメッセージのリスト
        
        チェック内容:
            - 必須項目（account, date, start, end）
            - 時刻の論理チェック（start < end）
            - 勤務時間の最小値（1分以上）
        """
        errors = []
        
        # 1. 必須項目チェック
        if not shift.account:
            errors.append("アカウント名は必須です")
        
        if not shift.date:
            errors.append("日付は必須です")
        
        if not shift.start:
            errors.append("開始時刻は必須です")
        
        if not shift.end:
            errors.append("終了時刻は必須です")
        
        # 必須項目が無い場合はここで終了
        if errors:
            return False, errors
        
        # 2. 時刻の論理チェック
        if shift.start >= shift.end:
            errors.append("終了時刻は開始時刻より後にしてください")
        
        # 3. 勤務時間のチェック
        try:
            duration = shift.duration_hours()
            
            # 最低1分（1/60時間 = 0.01666...時間）以上
            min_duration = 1 / 60  # 1分
            if duration < min_duration:
                errors.append("勤務時間は1分以上にしてください")
        
        except Exception as e:
            errors.append(f"勤務時間の計算エラー: {str(e)}")
        
        # 結果を返す
        return len(errors) == 0, errors
    
    def validate_month(self, month: str) -> Tuple[bool, str]:
        """
        月の形式をチェック
        
        Args:
            month: 'YYYY-MM' 形式の文字列
        
        Returns:
            (is_valid, error_message)
        
        チェック内容:
            - 形式が 'YYYY-MM' であること
            - 実在する年月であること
        """
        try:
            # 'YYYY-MM' 形式か確認
            datetime.strptime(month, '%Y-%m')
            return True, ""
        except ValueError:
            return False, "月の形式が不正です（YYYY-MM形式で指定してください）"

