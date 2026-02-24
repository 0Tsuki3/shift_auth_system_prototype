# services/shift_diff_service.py
"""
シフト差分計算サービス

このファイルは「シフト希望と実際のシフトの差分」を計算します。
差分は始業時刻と終業時刻のみで判定（休憩時間は差分には含めない）
"""

from typing import Dict, Optional, List
from datetime import time, datetime, timedelta
from models.shift import Shift
from models.shift_request import ShiftRequest


class ShiftDiffService:
    """
    シフト差分計算サービス
    
    使い方:
        service = ShiftDiffService()
        diff = service.calculate_diff(shift_request, actual_shift)
    """
    
    def calculate_diff(self, shift_request: ShiftRequest, actual_shift: Optional[Shift]) -> Dict:
        """
        シフト希望と実際のシフトの差分を計算
        
        Args:
            shift_request: ShiftRequestオブジェクト（希望）
            actual_shift: Shiftオブジェクト（実際）、未確定の場合はNone
        
        Returns:
            差分情報の辞書:
            {
                'has_diff': bool,  # 差分があるか
                'status': str,     # 'matched'（一致）, 'modified'（変更あり）, 'not_assigned'（未割当）
                'start_diff_minutes': int,  # 始業時刻の差分（分）
                'end_diff_minutes': int,    # 終業時刻の差分（分）
                'start_diff_text': str,     # 始業時刻の差分テキスト（例: "+1時間"）
                'end_diff_text': str,       # 終業時刻の差分テキスト（例: "-30分"）
                'summary': str              # サマリーテキスト
            }
        """
        # 実際のシフトがない場合
        if not actual_shift:
            return {
                'has_diff': True,
                'status': 'not_assigned',
                'start_diff_minutes': 0,
                'end_diff_minutes': 0,
                'start_diff_text': '',
                'end_diff_text': '',
                'summary': 'シフト未割当'
            }
        
        # 日付が違う場合（異常系）
        if shift_request.date != actual_shift.date:
            return {
                'has_diff': True,
                'status': 'date_mismatch',
                'start_diff_minutes': 0,
                'end_diff_minutes': 0,
                'start_diff_text': '',
                'end_diff_text': '',
                'summary': '日付不一致'
            }
        
        # 始業時刻の差分（分）
        start_diff_minutes = self._time_diff_minutes(shift_request.start, actual_shift.start)
        
        # 終業時刻の差分（分）
        end_diff_minutes = self._time_diff_minutes(shift_request.end, actual_shift.end)
        
        # 差分があるかチェック
        has_diff = (start_diff_minutes != 0) or (end_diff_minutes != 0)
        
        # 差分テキスト生成
        start_diff_text = self._format_time_diff(start_diff_minutes) if start_diff_minutes != 0 else ''
        end_diff_text = self._format_time_diff(end_diff_minutes) if end_diff_minutes != 0 else ''
        
        # サマリー生成
        if not has_diff:
            summary = '希望通り'
            status = 'matched'
        else:
            parts = []
            if start_diff_minutes != 0:
                parts.append(f"開始 {start_diff_text}")
            if end_diff_minutes != 0:
                parts.append(f"終了 {end_diff_text}")
            summary = "、".join(parts)
            status = 'modified'
        
        return {
            'has_diff': has_diff,
            'status': status,
            'start_diff_minutes': start_diff_minutes,
            'end_diff_minutes': end_diff_minutes,
            'start_diff_text': start_diff_text,
            'end_diff_text': end_diff_text,
            'summary': summary
        }
    
    def calculate_batch_diff(self, shift_requests: List[ShiftRequest], actual_shifts: List[Shift]) -> Dict[int, Dict]:
        """
        複数のシフト希望と実際のシフトの差分を一括計算
        
        Args:
            shift_requests: ShiftRequestオブジェクトのリスト
            actual_shifts: Shiftオブジェクトのリスト
        
        Returns:
            {shift_request_id: 差分情報} の辞書
        """
        # 実際のシフトを日付とアカウントでマッピング
        shift_map = {}
        for shift in actual_shifts:
            key = (shift.account, shift.date)
            shift_map[key] = shift
        
        # 各シフト希望に対して差分を計算
        result = {}
        for shift_request in shift_requests:
            key = (shift_request.account, shift_request.date)
            actual_shift = shift_map.get(key)
            diff = self.calculate_diff(shift_request, actual_shift)
            result[shift_request.id] = diff
        
        return result
    
    def _time_diff_minutes(self, time1: time, time2: time) -> int:
        """
        2つの時刻の差分を分単位で計算
        
        Args:
            time1: 基準時刻（希望）
            time2: 比較時刻（実際）
        
        Returns:
            差分（分）。time2の方が遅い場合は正、早い場合は負
        """
        # timeをdatetimeに変換
        dt1 = datetime.combine(datetime.min, time1)
        dt2 = datetime.combine(datetime.min, time2)
        
        # 差分を計算
        delta = dt2 - dt1
        
        # 分単位に変換
        minutes = int(delta.total_seconds() / 60)
        
        return minutes
    
    def _format_time_diff(self, minutes: int) -> str:
        """
        時刻差分を人間が読みやすいテキストに変換
        
        Args:
            minutes: 差分（分）
        
        Returns:
            テキスト（例: "+1時間30分", "-45分"）
        """
        if minutes == 0:
            return "変更なし"
        
        # 符号
        sign = "+" if minutes > 0 else ""
        abs_minutes = abs(minutes)
        
        # 時間と分に分解
        hours = abs_minutes // 60
        mins = abs_minutes % 60
        
        # テキスト生成
        parts = []
        if hours > 0:
            parts.append(f"{hours}時間")
        if mins > 0:
            parts.append(f"{mins}分")
        
        time_text = "".join(parts)
        
        # 符号を付けて返す
        if minutes > 0:
            return f"+{time_text}"
        else:
            return f"-{time_text}"
