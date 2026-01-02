# models/staff.py
"""スタッフデータモデル"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Staff:
    """スタッフのデータ構造"""
    account: str
    last_name: str
    first_name: str
    position: Optional[str] = None
    experience: Optional[str] = None
    type: Optional[str] = None  # 社員/バイトなど
    shift_pref: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """フルネームを取得"""
        return f"{self.last_name} {self.first_name}"
    
    def to_dict(self) -> dict:
        """辞書型に変換（CSV保存用）"""
        return {
            'account': self.account,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'position': self.position or '',
            'experience': self.experience or '',
            'type': self.type or '',
            'shift_pref': self.shift_pref or ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Staff':
        """辞書型から作成（CSV読み込み用）"""
        return cls(
            account=data.get('account', ''),
            last_name=data.get('last_name', ''),
            first_name=data.get('first_name', ''),
            position=data.get('position'),
            experience=data.get('experience'),
            type=data.get('type'),
            shift_pref=data.get('shift_pref')
        )

