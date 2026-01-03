# services/auth_service.py
"""
認証関連のビジネスロジック

このファイルは「認証に関する処理」を担当します。
ログイン、パスワードハッシュ化などを扱います。
"""

from typing import Optional
from models.auth import Auth
from data_access.auth_repository import AuthRepository
from validators.auth_validator import AuthValidator
from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:
    """
    認証サービス（ビジネスロジック）
    
    使い方:
        service = AuthService()
        auth = service.login('nakamura', 'password123')
    """
    
    def __init__(self):
        """
        初期化
        
        repository: データアクセス
        validator: バリデーション
        """
        self.repository = AuthRepository()
        self.validator = AuthValidator()
    
    def login(self, account: str, password: str) -> Optional[Auth]:
        """
        ログイン処理
        
        Args:
            account: アカウント名
            password: 平文パスワード
        
        Returns:
            Authオブジェクト（ログイン成功）
            None（ログイン失敗）
        
        ビジネスロジック:
            1. アカウント検索
            2. パスワード照合
        """
        # 1. アカウント検索
        auth = self.repository.find_by_account(account)
        if not auth:
            return None
        
        # 2. パスワード照合
        if check_password_hash(auth.password, password):
            return auth
        
        return None
    
    def create_auth(self, account: str, password: str, role: str) -> Auth:
        """
        認証情報を作成
        
        Args:
            account: アカウント名
            password: 平文パスワード
            role: ロール（'admin' or 'staff'）
        
        Returns:
            作成されたAuthオブジェクト
        
        Raises:
            ValueError: バリデーションエラー、重複エラー
        
        ビジネスロジック:
            1. パスワードバリデーション
            2. パスワードハッシュ化
            3. Authオブジェクト作成
            4. バリデーション
            5. 保存
        """
        # 1. パスワードバリデーション
        is_valid, errors = self.validator.validate_password(password)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"パスワードエラー: {error_message}")
        
        # 2. パスワードハッシュ化
        password_hash = generate_password_hash(password)
        
        # 3. Authオブジェクト作成
        auth = Auth(
            id=0,  # 自動採番
            account=account,
            password=password_hash,
            role=role
        )
        
        # 4. バリデーション
        is_valid, errors = self.validator.validate(auth)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"入力エラー: {error_message}")
        
        # 5. 保存（Repository内で重複チェック）
        try:
            saved_auth = self.repository.save(auth)
            return saved_auth
        except ValueError as e:
            # Repository層からの重複エラーをそのまま上げる
            raise
    
    def update_password(self, account: str, new_password: str) -> Auth:
        """
        パスワードを更新
        
        Args:
            account: アカウント名
            new_password: 新しい平文パスワード
        
        Returns:
            更新されたAuthオブジェクト
        
        Raises:
            ValueError: バリデーションエラー、存在しないアカウント
        """
        # 1. パスワードバリデーション
        is_valid, errors = self.validator.validate_password(new_password)
        if not is_valid:
            error_message = "、".join(errors)
            raise ValueError(f"パスワードエラー: {error_message}")
        
        # 2. アカウント存在チェック
        auth = self.repository.find_by_account(account)
        if not auth:
            raise ValueError(f"アカウント '{account}' が見つかりません")
        
        # 3. パスワードハッシュ化
        password_hash = generate_password_hash(new_password)
        
        # 4. パスワード更新
        auth.password = password_hash
        
        # 5. 保存
        updated_auth = self.repository.save(auth)
        return updated_auth
    
    def delete_auth(self, auth_id: int) -> bool:
        """
        認証情報を削除
        
        Args:
            auth_id: 認証ID
        
        Returns:
            削除成功したかどうか
        """
        return self.repository.delete(auth_id)

