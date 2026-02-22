# models/shift_request.py
"""
シフト希望データのモデル（データ構造の定義）

このファイルは「スタッフが提出したシフト希望1件分のデータ」がどういう形をしているかを定義します。
例: 「nakamuraアカウントが2025-09-07の09:00-15:00を希望」という情報を1つのオブジェクトとして扱う

設計方針:
- スタッフはaccountで管理（名前は変わる可能性があるため）
- 希望はステータス管理（pending/approved/rejected）
"""

from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional


@dataclass
class ShiftRequest:
    """
    シフト希望1件分のデータ構造
    
    @dataclass: Pythonの便利機能。自動的に__init__などを作ってくれる
    
    属性（このクラスが持つデータ）:
        id: シフト希望ID（一意な識別子、例: 1, 2, 3...）
        account: アカウントID（例: "nakamura"）
        date: 希望日付（例: 2025-09-07）
        start: 希望開始時刻（例: 09:00）
        end: 希望終了時刻（例: 15:00）
        request_type: 希望タイプ（fixed: 固定希望、conditional: 条件付き希望）※現在はfixedのみ対応
        read_status: 既読ステータス（unread: 未読、read: 既読）
        note: 備考（任意）
        created_at: 提出日時
    """
    id: int             # シフト希望ID（この希望を一意に識別）
    account: str        # アカウントID（スタッフを参照）
    date: date          # 希望日付
    start: time         # 希望開始時刻
    end: time           # 希望終了時刻
    request_type: str = 'fixed'  # 希望タイプ（fixed: 固定希望）
    read_status: str = 'unread'  # 既読ステータス（unread: 未読、read: 既読）
    note: str = ''      # 備考
    created_at: Optional[datetime] = None  # 提出日時
    
    def duration_hours(self) -> float:
        """
        希望勤務時間を計算する（時間単位）
        
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
                'id': 1,
                'account': 'nakamura',
                'date': '2025-09-07',
                'start': '09:00',
                'end': '15:00',
                'request_type': 'fixed',
                'read_status': 'unread',
                'note': '',
                'created_at': '2025-09-01 10:00:00'
            }
        """
        return {
            'id': self.id,
            'account': self.account,
            'date': self.date.strftime('%Y-%m-%d'),  # 日付を文字列に
            'start': self.start.strftime('%H:%M'),   # 時刻を文字列に
            'end': self.end.strftime('%H:%M'),
            'request_type': self.request_type,
            'read_status': self.read_status,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ShiftRequest':
        """
        辞書型からShiftRequestオブジェクトを作る（CSVから読み込む時に使う）
        
        @classmethod: クラスメソッド。ShiftRequest.from_dict()のように呼ぶ
        
        Args:
            data: CSVから読んだ1行分のデータ
                  {'id': 1, 'account': 'nakamura', 'date': '2025-09-07', ...}
        
        Returns:
            ShiftRequestオブジェクト
        
        Note:
            idが無い場合は0を設定（後で採番）
            旧データ（status）との互換性維持のため、statusがあればread_statusに変換
        """
        # IDの取得（新規の場合は0）
        request_id = int(data.get('id', 0))
        
        # created_atの取得
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # 日付フォーマットが異なる場合は現在時刻を設定
                created_at = datetime.now()
        
        # 旧データ（status）との互換性維持
        # statusがあればread_statusに変換（pending/approved/rejected → unread/read）
        if 'read_status' in data:
            read_status = data.get('read_status', 'unread')
        elif 'status' in data:
            # 旧statusをread_statusに変換
            old_status = data.get('status', 'pending')
            if old_status == 'pending':
                read_status = 'unread'
            else:  # approved or rejected
                read_status = 'read'
        else:
            read_status = 'unread'
        
        return cls(
            id=request_id,
            account=data['account'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),  # 文字列→日付
            start=datetime.strptime(data['start'], '%H:%M').time(),   # 文字列→時刻
            end=datetime.strptime(data['end'], '%H:%M').time(),
            request_type=data.get('request_type', 'fixed'),
            read_status=read_status,
            note=data.get('note', ''),
            created_at=created_at
        )
