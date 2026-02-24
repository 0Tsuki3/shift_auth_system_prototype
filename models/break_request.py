# models/break_request.py
"""
休憩希望データのモデル（データ構造の定義）

このファイルは「シフト希望の休憩時間1件分のデータ」がどういう形をしているかを定義します。
例: 「シフト希望ID=1の勤務で14:00-15:00の休憩を希望」という情報を1つのオブジェクトとして扱う

設計方針:
- 休憩希望はシフト希望IDで紐付け（正規化）
- 1つのシフト希望に複数の休憩希望を持てる
- DB移行時もそのまま使える構造
"""

from dataclasses import dataclass
from datetime import time, datetime
from typing import Optional


@dataclass
class BreakRequest:
    """
    休憩希望1件分のデータ構造
    
    @dataclass: Pythonの便利機能。自動的に__init__などを作ってくれる
    
    属性（このクラスが持つデータ）:
        id: 休憩希望ID（一意な識別子、例: 1, 2, 3...）
        shift_request_id: どのシフト希望の休憩か（ShiftRequestモデルのidを参照）
        break_start: 休憩開始時刻（例: 14:00）
        break_end: 休憩終了時刻（例: 15:00）
    """
    id: int                      # 休憩希望ID（この休憩希望を一意に識別）
    shift_request_id: int       # シフト希望ID（どのシフト希望の休憩か）
    break_start: time           # 休憩開始時刻
    break_end: time             # 休憩終了時刻
    
    def duration_hours(self) -> float:
        """
        休憩時間を計算する（時間単位）
        
        例: 14:00-15:00 なら 1.0 時間
        
        Returns:
            休憩時間（小数点付き、例: 1.0, 0.5）
        """
        from datetime import date as dt_date
        # datetimeに変換して差分を計算
        start_dt = datetime.combine(dt_date.min, self.break_start)
        end_dt = datetime.combine(dt_date.min, self.break_end)
        
        # 秒単位の差分を時間単位に変換
        delta = end_dt - start_dt
        hours = delta.total_seconds() / 3600
        
        return hours
    
    def to_dict(self) -> dict:
        """
        辞書型に変換（CSVに保存する時などに使う）
        
        Returns:
            {
                'id': 1,
                'shift_request_id': 123,
                'break_start': '14:00',
                'break_end': '15:00'
            }
        """
        return {
            'id': self.id,
            'shift_request_id': self.shift_request_id,
            'break_start': self.break_start.strftime('%H:%M'),
            'break_end': self.break_end.strftime('%H:%M')
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BreakRequest':
        """
        辞書型からBreakRequestオブジェクトを作る（CSVから読み込む時に使う）
        
        @classmethod: クラスメソッド。BreakRequest.from_dict()のように呼ぶ
        
        Args:
            data: CSVから読んだ1行分のデータ
                  {'id': 1, 'shift_request_id': 123, 'break_start': '14:00', ...}
        
        Returns:
            BreakRequestオブジェクト
        
        Note:
            idが無い場合は0を設定（後で採番）
        """
        # IDの取得（新規の場合は0）
        break_request_id = int(data.get('id', 0))
        shift_request_id = int(data['shift_request_id'])
        
        return cls(
            id=break_request_id,
            shift_request_id=shift_request_id,
            break_start=datetime.strptime(data['break_start'], '%H:%M').time(),
            break_end=datetime.strptime(data['break_end'], '%H:%M').time()
        )
