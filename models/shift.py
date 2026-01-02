# models/shift.py
"""
シフトデータのモデル（データ構造の定義）

このファイルは「シフト1件分のデータ」がどういう形をしているかを定義します。
例: 「nakamuraアカウントが2025-09-07の09:00-15:00に勤務」という情報を1つのオブジェクトとして扱う

設計方針:
- スタッフはaccountで管理（名前は変わる可能性があるため）
- 名前が必要な時はStaffRepositoryからaccountで検索
"""

from dataclasses import dataclass
from datetime import date, time, datetime


@dataclass
class Shift:
    """
    シフト1件分のデータ構造
    
    @dataclass: Pythonの便利機能。自動的に__init__などを作ってくれる
    
    属性（このクラスが持つデータ）:
        account: アカウントID（例: "nakamura"）
        date: 日付（例: 2025-09-07）
        index: 同じ日に複数シフトがある時の番号（0, 1, 2...）
        start: 開始時刻（例: 09:00）
        end: 終了時刻（例: 15:00）
    """
    account: str        # アカウントID（スタッフを一意に識別）
    date: date          # 日付
    index: int          # シフト番号（同じ日に複数ある時用）
    start: time         # 開始時刻
    end: time           # 終了時刻
    
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
                'account': 'nakamura',
                'date': '2025-09-07',
                'index': 0,
                'start': '09:00',
                'end': '15:00'
            }
        """
        return {
            'account': self.account,
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
                  {'account': 'nakamura', 'date': '2025-09-07', ...}
        
        Returns:
            Shiftオブジェクト
        
        Note:
            旧形式（last_name, first_nameを持つ）にも対応
            その場合はaccountフィールドを優先使用
        """
        # accountが無い場合は旧形式として扱う（後方互換性）
        account = data.get('account')
        if not account and 'last_name' in data and 'first_name' in data:
            # 旧形式の場合: 名前からアカウントを推測（一時的な対応）
            # TODO: 将来的には全データをaccount形式に移行する
            account = f"{data['last_name']}_{data['first_name']}"
        
        return cls(
            account=account,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),  # 文字列→日付
            index=int(data['index']),
            start=datetime.strptime(data['start'], '%H:%M').time(),   # 文字列→時刻
            end=datetime.strptime(data['end'], '%H:%M').time()
        )

