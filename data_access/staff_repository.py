# data_access/staff_repository.py
"""
スタッフデータのRepository（データアクセス層）

このファイルは「スタッフデータの読み書き」を担当します。
現時点ではCSVを使い、将来的にSQLに移行します。
"""

import os
import csv
from typing import List, Optional
from models.staff import Staff


class StaffRepository:
    """
    スタッフデータアクセス（CSV実装）
    
    CSVファイルの配置:
        data/staff.csv
    
    将来的にSQLに移行する際は、このクラスを差し替えるだけでOK
    """
    
    def __init__(self):
        """
        初期化
        
        staff_file: スタッフデータのCSVファイルパス
        """
        self.staff_file = 'data/staff.csv'
        # data/フォルダが無ければ作成
        os.makedirs('data', exist_ok=True)
    
    def find_all(self) -> List[Staff]:
        """
        全スタッフを取得
        
        Returns:
            Staffオブジェクトのリスト
        """
        if not os.path.exists(self.staff_file):
            return []
        
        staff_list = []
        with open(self.staff_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('account'):  # 空行をスキップ
                    try:
                        staff = Staff.from_dict(row)
                        staff_list.append(staff)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: スタッフデータの読み込みエラー: {row}, {e}")
                        continue
        
        return staff_list
    
    def find_by_id(self, staff_id: int) -> Optional[Staff]:
        """
        IDでスタッフを検索
        
        Args:
            staff_id: スタッフID
        
        Returns:
            Staffオブジェクト、見つからなければNone
        """
        all_staff = self.find_all()
        for staff in all_staff:
            if staff.id == staff_id:
                return staff
        return None
    
    def find_by_account(self, account: str) -> Optional[Staff]:
        """
        アカウント名でスタッフを検索
        
        Args:
            account: アカウント名
        
        Returns:
            Staffオブジェクト、見つからなければNone
        """
        all_staff = self.find_all()
        for staff in all_staff:
            if staff.account == account:
                return staff
        return None
    
    def save_all(self, staff_list: List[Staff]) -> None:
        """
        スタッフ一括保存（上書き）
        
        Args:
            staff_list: Staffオブジェクトのリスト
        """
        # ID自動採番（IDが0のものに新しいIDを振る）
        max_id = max([s.id for s in staff_list if s.id > 0], default=0)
        for staff in staff_list:
            if staff.id == 0:
                max_id += 1
                staff.id = max_id
        
        # CSV保存
        with open(self.staff_file, 'w', newline='', encoding='utf-8') as f:
            if staff_list:
                fieldnames = ['id', 'account', 'last_name', 'first_name', 
                             'hourly_wage', 'position', 'hired_date', 'type', 'memo']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # アカウント名でソート
                sorted_staff = sorted(staff_list, key=lambda s: s.account)
                
                for staff in sorted_staff:
                    writer.writerow(staff.to_dict())
            else:
                # 空の場合はヘッダーだけ
                fieldnames = ['id', 'account', 'last_name', 'first_name', 
                             'hourly_wage', 'position', 'hired_date', 'type', 'memo']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
    
    def save(self, staff: Staff) -> Staff:
        """
        スタッフ1件を保存（新規または更新）
        
        Args:
            staff: Staffオブジェクト
        
        Returns:
            保存されたStaffオブジェクト（IDが自動採番される）
        """
        all_staff = self.find_all()
        
        # 既存のスタッフを更新
        if staff.id > 0:
            for i, s in enumerate(all_staff):
                if s.id == staff.id:
                    all_staff[i] = staff
                    self.save_all(all_staff)
                    return staff
        
        # アカウント重複チェック
        for s in all_staff:
            if s.account == staff.account and s.id != staff.id:
                raise ValueError(f"アカウント '{staff.account}' は既に存在します")
        
        # 新規スタッフを追加
        all_staff.append(staff)
        self.save_all(all_staff)
        return staff
    
    def delete(self, staff_id: int) -> bool:
        """
        スタッフを削除
        
        Args:
            staff_id: スタッフID
        
        Returns:
            削除成功したかどうか
        """
        all_staff = self.find_all()
        original_count = len(all_staff)
        all_staff = [s for s in all_staff if s.id != staff_id]
        
        if len(all_staff) < original_count:
            self.save_all(all_staff)
            return True
        
        return False

