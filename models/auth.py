# models/auth.py
"""
認証データのモデル（データ構造の定義）

このファイルは「認証情報1件分のデータ」がどういう形をしているかを定義します。
例: 「adminアカウント、パスワードハッシュ、管理者権限」という情報を1つのオブジェクトとして扱う

設計方針:
- 名前や時給などの個人情報はStaffモデルに集約
- 認証に必要な情報（account, password, role）のみ保持
- accountでStaffを参照する
"""

from dataclasses import dataclass


@dataclass
class Auth:
    """
    認証情報1件分のデータ構造
    
    属性:
        id: 認証ID（一意な識別子、例: 1, 2, 3...）
        account: アカウント名（ログインID、例: "admin"）
        password: パスワードハッシュ（暗号化されたパスワード）
        role: 権限（"admin" または "staff"）
    """
    id: int             # 認証ID（この認証情報を一意に識別）
    account: str        # アカウント名
    password: str       # パスワードハッシュ（暗号化済み）
    role: str           # 権限（admin or staff）
    
    @property
    def is_admin(self) -> bool:
        """
        管理者かどうかを判定
        
        Returns:
            True: 管理者、False: 一般スタッフ
        """
        return self.role == 'admin'
    
    def to_dict(self) -> dict:
        """
        辞書型に変換（CSVに保存する時などに使う）
        
        Returns:
            {
                'id': 1,
                'account': 'admin',
                'password': 'pbkdf2:sha256:...',
                'role': 'admin'
            }
        """
        return {
            'id': self.id,
            'account': self.account,
            'password': self.password,
            'role': self.role
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Auth':
        """
        辞書型からAuthオブジェクトを作る（CSVから読み込む時に使う）
        
        Args:
            data: CSVから読んだ1行分のデータ
        
        Returns:
            Authオブジェクト
        
        Note:
            旧形式（last_name, first_name, hourly_wageを持つ）にも対応
            idが無い場合は0を設定（後で採番）
        """
        return cls(
            id=int(data.get('id', 0)),
            account=data['account'],
            password=data['password'],
            role=data['role']
        )

