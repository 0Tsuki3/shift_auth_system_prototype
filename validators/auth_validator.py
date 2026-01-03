# validators/auth_validator.py
"""
認証データのバリデーション

このファイルは「認証データが正しいかチェック」を担当します。
例: パスワードの強度、ロールの妥当性、など
"""

from typing import Tuple, List
from models.auth import Auth


class AuthValidator:
    """
    認証バリデーション
    
    使い方:
        validator = AuthValidator()
        is_valid, errors = validator.validate(auth)
        if not is_valid:
            print("エラー:", errors)
    """
    
    # 許可されるロール
    VALID_ROLES = ['admin', 'staff']
    
    def validate(self, auth: Auth) -> Tuple[bool, List[str]]:
        """
        認証データの妥当性チェック
        
        Args:
            auth: Authオブジェクト
        
        Returns:
            (is_valid, errors)
            - is_valid: True=OK, False=NG
            - errors: エラーメッセージのリスト
        
        チェック内容:
            - 必須項目（account, password, role）
            - アカウント名の長さ（3文字以上）
            - パスワードハッシュの存在
            - ロールの妥当性（admin or staff）
        """
        errors = []
        
        # 1. 必須項目チェック
        if not auth.account:
            errors.append("アカウント名は必須です")
        elif len(auth.account) < 3:
            errors.append("アカウント名は3文字以上にしてください")
        
        if not auth.password:
            errors.append("パスワードは必須です")
        
        if not auth.role:
            errors.append("ロールは必須です")
        elif auth.role not in self.VALID_ROLES:
            errors.append(f"ロールは {', '.join(self.VALID_ROLES)} のいずれかを指定してください")
        
        # 結果を返す
        return len(errors) == 0, errors
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        パスワードの妥当性チェック（平文パスワード用）
        
        Args:
            password: 平文パスワード
        
        Returns:
            (is_valid, errors)
        
        チェック内容:
            - 空欄でないこと（必須）
        
        Note:
            新規登録やパスワード変更時に使用
            強度チェックは行わない（ユーザーに任せる）
        """
        errors = []
        
        if not password or len(password) == 0:
            errors.append("パスワードは必須です")
        
        return len(errors) == 0, errors

