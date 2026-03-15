# models/break.py
"""
休憩データのモデル（データ構造の定義）

このファイルは「シフトの休憩時間1件分のデータ」がどういう形をしているかを定義します。
例: 「シフトID=1の勤務で14:00-15:00の休憩」という情報を1つのオブジェクトとして扱う

設計方針:
- 休憩はシフトIDで紐付け（正規化）
- 1つのシフトに複数の休憩を持てる
- DB移行時もそのまま使える構造
"""

from dataclasses import dataclass
from datetime import time, datetime
from typing import Optional


@dataclass
class Break:
    """
    休憩時間1件分のデータ構造
    
    @dataclass: Pythonの便利機能。自動的に__init__などを作ってくれる
    
    属性（このクラスが持つデータ）:
        id: 休憩ID（一意な識別子、例: 1, 2, 3...）
        shift_id: どのシフトの休憩か（Shiftモデルのidを参照）
        break_start: 休憩開始時刻（例: 14:00）
        break_end: 休憩終了時刻（例: 15:00）
    """
    id: int                 # 休憩ID（この休憩を一意に識別）
    shift_id: int          # シフトID（どのシフトの休憩か）
    break_start: time      # 休憩開始時刻
    break_end: time        # 休憩終了時刻
    
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
                'shift_id': 123,
                'break_start': '14:00',
                'break_end': '15:00'
            }
        """
        return {
            'id': self.id,
            'shift_id': self.shift_id,
            'break_start': self.break_start.strftime('%H:%M'),
            'break_end': self.break_end.strftime('%H:%M')
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Break':
        """
        辞書型からBreakオブジェクトを作る（CSVから読み込む時に使う）
        
        @classmethod: クラスメソッド。Break.from_dict()のように呼ぶ
        
        Args:
            data: CSVから読んだ1行分のデータ
                  {'id': 1, 'shift_id': 123, 'break_start': '14:00', ...}
        
        Returns:
            Breakオブジェクト
        
        Note:
            idが無い場合は0を設定（後で採番）
        """
        # IDの取得（新規の場合は0）
        break_id = int(data.get('id', 0))
        shift_id = int(data['shift_id'])
        
        return cls(
            id=break_id,
            shift_id=shift_id,
            break_start=datetime.strptime(data['break_start'], '%H:%M').time(),
            break_end=datetime.strptime(data['break_end'], '%H:%M').time()
        )
