# models/auth.py
"""
認証データのモデル（データ構造の定義）

このファイルは「認証情報1件分のデータ」がどういう形をしているかを定義します。
例: 「adminアカウント、パスワードハッシュ、管理者権限」という情報を1つのオブジェクトとして扱う
"""

from dataclasses import dataclass


@dataclass
class Auth:
    """
    認証情報1件分のデータ構造
    
    属性:
        account: アカウント名（ログインID、例: "admin"）
        last_name: 姓（例: "最強"）
        first_name: 名（例: "管理者"）
        role: 権限（"admin" または "staff"）
        hourly_wage: 時給（例: 1000）
        password: パスワードハッシュ（暗号化されたパスワード）
    """
    account: str        # アカウント名
    last_name: str      # 姓
    first_name: str     # 名
    role: str           # 権限（admin or staff）
    hourly_wage: int    # 時給
    password: str       # パスワードハッシュ（暗号化済み）
    
    @property
    def full_name(self) -> str:
        """
        フルネームを返す
        
        Returns:
            "姓 名" の形式（例: "最強 管理者"）
        """
        return f"{self.last_name} {self.first_name}"
    
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
                'account': 'admin',
                'last_name': '最強',
                'first_name': '管理者',
                'role': 'admin',
                'hourly_wage': 0,
                'password': 'pbkdf2:sha256:...'
            }
        """
        return {
            'account': self.account,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'role': self.role,
            'hourly_wage': self.hourly_wage,
            'password': self.password
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Auth':
        """
        辞書型からAuthオブジェクトを作る（CSVから読み込む時に使う）
        
        Args:
            data: CSVから読んだ1行分のデータ
        
        Returns:
            Authオブジェクト
        """
        return cls(
            account=data['account'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            role=data['role'],
            hourly_wage=int(data.get('hourly_wage', 0)),  # 数値に変換
            password=data['password']
        )

