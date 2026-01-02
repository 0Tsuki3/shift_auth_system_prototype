# data_access/auth_repository.py
"""
認証データのRepository（データアクセス層）

このファイルは「認証データの読み書き」を担当します。
現時点ではCSVを使い、将来的にSQLに移行します。
"""

import os
import csv
from typing import List, Optional
from models.auth import Auth


class AuthRepository:
    """
    認証データアクセス（CSV実装）
    
    CSVファイルの配置:
        data/auth.csv
    
    将来的にSQLに移行する際は、このクラスを差し替えるだけでOK
    """
    
    def __init__(self):
        """
        初期化
        
        auth_file: 認証データのCSVファイルパス
        """
        self.auth_file = 'data/auth.csv'
        # data/フォルダが無ければ作成
        os.makedirs('data', exist_ok=True)
    
    def find_all(self) -> List[Auth]:
        """
        全認証情報を取得
        
        Returns:
            Authオブジェクトのリスト
        """
        if not os.path.exists(self.auth_file):
            return []
        
        auth_list = []
        with open(self.auth_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('account'):  # 空行をスキップ
                    try:
                        auth = Auth.from_dict(row)
                        auth_list.append(auth)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: 認証データの読み込みエラー: {row}, {e}")
                        continue
        
        return auth_list
    
    def find_by_id(self, auth_id: int) -> Optional[Auth]:
        """
        IDで認証情報を検索
        
        Args:
            auth_id: 認証ID
        
        Returns:
            Authオブジェクト、見つからなければNone
        """
        all_auth = self.find_all()
        for auth in all_auth:
            if auth.id == auth_id:
                return auth
        return None
    
    def find_by_account(self, account: str) -> Optional[Auth]:
        """
        アカウント名で認証情報を検索（ログイン時に使用）
        
        Args:
            account: アカウント名
        
        Returns:
            Authオブジェクト、見つからなければNone
        """
        all_auth = self.find_all()
        for auth in all_auth:
            if auth.account == account:
                return auth
        return None
    
    def save_all(self, auth_list: List[Auth]) -> None:
        """
        認証情報一括保存（上書き）
        
        Args:
            auth_list: Authオブジェクトのリスト
        """
        # ID自動採番（IDが0のものに新しいIDを振る）
        max_id = max([a.id for a in auth_list if a.id > 0], default=0)
        for auth in auth_list:
            if auth.id == 0:
                max_id += 1
                auth.id = max_id
        
        # CSV保存
        with open(self.auth_file, 'w', newline='', encoding='utf-8') as f:
            if auth_list:
                fieldnames = ['id', 'account', 'password', 'role']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # アカウント名でソート
                sorted_auth = sorted(auth_list, key=lambda a: a.account)
                
                for auth in sorted_auth:
                    writer.writerow(auth.to_dict())
            else:
                # 空の場合はヘッダーだけ
                fieldnames = ['id', 'account', 'password', 'role']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
    
    def save(self, auth: Auth) -> Auth:
        """
        認証情報1件を保存（新規または更新）
        
        Args:
            auth: Authオブジェクト
        
        Returns:
            保存されたAuthオブジェクト（IDが自動採番される）
        """
        all_auth = self.find_all()
        
        # 既存の認証情報を更新
        if auth.id > 0:
            for i, a in enumerate(all_auth):
                if a.id == auth.id:
                    all_auth[i] = auth
                    self.save_all(all_auth)
                    return auth
        
        # アカウント重複チェック
        for a in all_auth:
            if a.account == auth.account and a.id != auth.id:
                raise ValueError(f"アカウント '{auth.account}' は既に存在します")
        
        # 新規認証情報を追加
        all_auth.append(auth)
        self.save_all(all_auth)
        return auth
    
    def delete(self, auth_id: int) -> bool:
        """
        認証情報を削除
        
        Args:
            auth_id: 認証ID
        
        Returns:
            削除成功したかどうか
        """
        all_auth = self.find_all()
        original_count = len(all_auth)
        all_auth = [a for a in all_auth if a.id != auth_id]
        
        if len(all_auth) < original_count:
            self.save_all(all_auth)
            return True
        
        return False

