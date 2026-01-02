# models/staff.py
"""
スタッフデータのモデル（データ構造の定義）

このファイルは「スタッフ1人分のデータ」がどういう形をしているかを定義します。
例: 「中村元さん、ポジションはキッチン、経験3年」という情報を1つのオブジェクトとして扱う
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Staff:
    """
    スタッフ1人分のデータ構造
    
    属性:
        id: スタッフID（一意な識別子、例: 1, 2, 3...）
        account: アカウント名（ログインID、例: "nakamura"）
        last_name: 姓（例: "中村"）
        first_name: 名（例: "元"）
        hourly_wage: 時給（例: 1000）※セキュリティはService/Routes層で制御
        position: ポジション（例: "kitchen", "hall"）
        hired_date: 勤務開始日（例: "2025-01-01"）
        type: 雇用形態（例: "正社員", "アルバイト"）
        memo: メモ（自由記述、将来的な拡張用）
    """
    id: int                          # スタッフID（このスタッフを一意に識別）
    account: str                     # アカウント名（ログインID）
    last_name: str                   # 姓
    first_name: str                  # 名
    hourly_wage: int = 0             # 時給（デフォルト0）
    position: Optional[str] = None   # ポジション（任意項目）
    hired_date: Optional[str] = None # 勤務開始日（任意項目）
    type: Optional[str] = None       # 雇用形態（任意項目）
    memo: Optional[str] = None       # メモ（任意項目、自由記述）
    
    @property
    def full_name(self) -> str:
        """
        フルネームを返す
        
        Returns:
            "姓 名" の形式（例: "中村 元"）
        """
        return f"{self.last_name} {self.first_name}"
    
    def to_dict(self) -> dict:
        """
        辞書型に変換（CSVに保存する時などに使う）
        
        Returns:
            {
                'id': 1,
                'account': 'nakamura',
                'last_name': '中村',
                'first_name': '元',
                'hourly_wage': 1000,
                'position': 'kitchen',
                'hired_date': '2025-01-01',
                'type': 'アルバイト',
                'memo': '...'
            }
        """
        return {
            'id': self.id,
            'account': self.account,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'hourly_wage': self.hourly_wage,
            'position': self.position or '',       # Noneの場合は空文字
            'hired_date': self.hired_date or '',   # Noneの場合は空文字
            'type': self.type or '',
            'memo': self.memo or ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Staff':
        """
        辞書型からStaffオブジェクトを作る（CSVから読み込む時に使う）
        
        Args:
            data: CSVから読んだ1行分のデータ
        
        Returns:
            Staffオブジェクト
        
        Note:
            idが無い場合は0を設定（後で採番）
            旧フィールド（experience, shift_pref）も読めるが無視
        """
        return cls(
            id=int(data.get('id', 0)),
            account=data['account'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            hourly_wage=int(data.get('hourly_wage', 0)),
            position=data.get('position') or None,       # 空文字の場合はNone
            hired_date=data.get('hired_date') or None,   # 新フィールド
            type=data.get('type') or None,
            memo=data.get('memo') or None                # 新フィールド
        )

