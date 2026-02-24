# validators/break_validator.py
"""
休憩データのバリデーション

このファイルは「休憩データが正しいかチェック」を担当します。
例: 休憩開始 < 休憩終了、休憩時間がシフト時間内、休憩同士が被っていない、など
"""

from typing import Tuple, List
from models.break_model import Break
from models.shift import Shift
from datetime import datetime, time as dt_time


class BreakValidator:
    """
    休憩バリデーション
    
    使い方:
        validator = BreakValidator()
        is_valid, errors = validator.validate(break_obj, shift)
        if not is_valid:
            print("エラー:", errors)
    """
    
    def validate(self, break_obj: Break, shift: Shift = None) -> Tuple[bool, List[str]]:
        """
        休憩データの妥当性チェック
        
        Args:
            break_obj: Breakオブジェクト
            shift: シフトオブジェクト（時間内チェックに使用、オプション）
        
        Returns:
            (is_valid, errors)
            - is_valid: True=OK, False=NG
            - errors: エラーメッセージのリスト
        
        チェック内容:
            - 必須項目（shift_id, break_start, break_end）
            - 時刻の論理チェック（break_start < break_end）
            - 休憩時間の最小値（1分以上）
            - （シフトが与えられた場合）休憩時間がシフト時間内にあるか
        """
        errors = []
        
        # 1. 必須項目チェック
        if not break_obj.shift_id:
            errors.append("シフトIDは必須です")
        
        if not break_obj.break_start:
            errors.append("休憩開始時刻は必須です")
        
        if not break_obj.break_end:
            errors.append("休憩終了時刻は必須です")
        
        # 必須項目が無い場合はここで終了
        if errors:
            return False, errors
        
        # 2. 時刻の論理チェック
        if break_obj.break_start >= break_obj.break_end:
            errors.append("休憩終了時刻は休憩開始時刻より後にしてください")
        
        # 3. 休憩時間のチェック
        try:
            duration = break_obj.duration_hours()
            
            # 最低1分（1/60時間 = 0.01666...時間）以上
            min_duration = 1 / 60  # 1分
            if duration < min_duration:
                errors.append("休憩時間は1分以上にしてください")
        
        except Exception as e:
            errors.append(f"休憩時間の計算エラー: {str(e)}")
        
        # 4. シフト時間内チェック（シフトが与えられた場合）
        if shift:
            if break_obj.break_start < shift.start:
                errors.append(f"休憩開始時刻はシフト開始時刻（{shift.start.strftime('%H:%M')}）より後にしてください")
            
            if break_obj.break_end > shift.end:
                errors.append(f"休憩終了時刻はシフト終了時刻（{shift.end.strftime('%H:%M')}）より前にしてください")
        
        # 結果を返す
        return len(errors) == 0, errors
    
    def validate_no_overlap(self, breaks: List[Break]) -> Tuple[bool, List[str]]:
        """
        複数の休憩時間が被っていないかチェック
        
        Args:
            breaks: Breakオブジェクトのリスト
        
        Returns:
            (is_valid, errors)
            - is_valid: True=OK（被りなし）, False=NG（被りあり）
            - errors: エラーメッセージのリスト
        """
        errors = []
        
        # 休憩時間を開始時刻でソート
        sorted_breaks = sorted(breaks, key=lambda b: b.break_start)
        
        # 隣接する休憩時間をチェック
        for i in range(len(sorted_breaks) - 1):
            current = sorted_breaks[i]
            next_break = sorted_breaks[i + 1]
            
            # 現在の休憩終了時刻 > 次の休憩開始時刻 なら被っている
            if current.break_end > next_break.break_start:
                errors.append(
                    f"休憩時間が被っています: "
                    f"{current.break_start.strftime('%H:%M')}-{current.break_end.strftime('%H:%M')} と "
                    f"{next_break.break_start.strftime('%H:%M')}-{next_break.break_end.strftime('%H:%M')}"
                )
        
        return len(errors) == 0, errors
    
    def validate_all_with_shift(self, breaks: List[Break], shift: Shift) -> Tuple[bool, List[str]]:
        """
        複数の休憩時間を一括バリデーション（シフトとの整合性チェック含む）
        
        Args:
            breaks: Breakオブジェクトのリスト
            shift: シフトオブジェクト
        
        Returns:
            (is_valid, errors)
            - is_valid: True=全てOK, False=1つ以上NG
            - errors: エラーメッセージのリスト
        """
        all_errors = []
        
        # 1. 各休憩の個別バリデーション
        for i, break_obj in enumerate(breaks):
            is_valid, errors = self.validate(break_obj, shift)
            if not is_valid:
                # エラーメッセージに休憩番号を追加
                for error in errors:
                    all_errors.append(f"休憩{i+1}: {error}")
        
        # 2. 休憩同士の被りチェック
        is_valid_overlap, overlap_errors = self.validate_no_overlap(breaks)
        if not is_valid_overlap:
            all_errors.extend(overlap_errors)
        
        return len(all_errors) == 0, all_errors
