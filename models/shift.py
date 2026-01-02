# models/shift.py
"""
シフトデータのモデル（データ構造の定義）

このファイルは「シフト1件分のデータ」がどういう形をしているかを定義します。
例: 「中村元さんが2025-09-07の09:00-15:00に勤務」という情報を1つのオブジェクトとして扱う
"""

from dataclasses import dataclass
from datetime import date, time, datetime


@dataclass
class Shift:
    """
    シフト1件分のデータ構造
    
    @dataclass: Pythonの便利機能。自動的に__init__やto_dict()などを作ってくれる
    
    属性（このクラスが持つデータ）:
        last_name: 姓（例: "中村"）
        first_name: 名（例: "元"）
        date: 日付（例: 2025-09-07）
        index: 同じ日に複数シフトがある時の番号（0, 1, 2...）
        start: 開始時刻（例: 09:00）
        end: 終了時刻（例: 15:00）
    """
    last_name: str      # 姓
    first_name: str     # 名
    date: date          # 日付
    index: int          # シフト番号（同じ日に複数ある時用）
    start: time         # 開始時刻
    end: time           # 終了時刻
    
    @property
    def full_name(self) -> str:
        """
        フルネームを返す
        
        @property: 関数だけど、プロパティのように使える
        例: shift.full_name  ← カッコなしで呼べる
        
        Returns:
            "姓 名" の形式（例: "中村 元"）
        """
        return f"{self.last_name} {self.first_name}"
    
    def duration_hours(self) -> float:
        """
        勤務時間を計算する（時間単位）
        
        例: 09:00-15:00 なら 6.0 時間
        
        Returns:
            勤務時間（小数点付き、例: 6.0, 4.5）
        """
        # datetimeに変換して差分を計算
        start_dt = datetime.combine(date.min, self.start)
        end_dt = datetime.combine(date.min, self.end)
        
        # 秒単位の差分を時間単位に変換
        delta = end_dt - start_dt
        hours = delta.total_seconds() / 3600
        
        return hours
    
    def to_dict(self) -> dict:
        """
        辞書型に変換（CSVに保存する時などに使う）
        
        Returns:
            {
                'last_name': '中村',
                'first_name': '元',
                'date': '2025-09-07',
                'index': 0,
                'start': '09:00',
                'end': '15:00'
            }
        """
        return {
            'last_name': self.last_name,
            'first_name': self.first_name,
            'date': self.date.strftime('%Y-%m-%d'),  # 日付を文字列に
            'index': self.index,
            'start': self.start.strftime('%H:%M'),   # 時刻を文字列に
            'end': self.end.strftime('%H:%M')
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Shift':
        """
        辞書型からShiftオブジェクトを作る（CSVから読み込む時に使う）
        
        @classmethod: クラスメソッド。Shift.from_dict()のように呼ぶ
        
        Args:
            data: CSVから読んだ1行分のデータ
                  {'last_name': '中村', 'first_name': '元', ...}
        
        Returns:
            Shiftオブジェクト
        """
        return cls(
            last_name=data['last_name'],
            first_name=data['first_name'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),  # 文字列→日付
            index=int(data['index']),
            start=datetime.strptime(data['start'], '%H:%M').time(),   # 文字列→時刻
            end=datetime.strptime(data['end'], '%H:%M').time()
        )

