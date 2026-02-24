# data_access/break_request_repository.py
"""
休憩希望データのRepository（データアクセス層）

このファイルは「休憩希望データの読み書き」を担当します。
現時点ではCSVを使い、将来的にSQLに移行します。
"""

import os
import csv
from typing import List, Optional
from datetime import datetime
from models.break_request import BreakRequest


class BreakRequestRepository:
    """
    休憩希望データアクセス（CSV実装）
    
    CSVファイルの配置:
        data/break_request/break_request_YYYY-MM.csv
        例: data/break_request/break_request_2025-02.csv
    
    将来的にSQLに移行する際は、このクラスを差し替えるだけでOK
    """
    
    def __init__(self):
        """
        初期化
        
        data_dir: 休憩希望データを保存するフォルダ
        """
        self.data_dir = 'data/break_request'
        # フォルダが無ければ作成
        os.makedirs(self.data_dir, exist_ok=True)
    
    def find_all_by_month(self, month: str) -> List[BreakRequest]:
        """
        月別休憩希望を全件取得
        
        Args:
            month: 'YYYY-MM' 形式（例: '2025-02'）
        
        Returns:
            BreakRequestオブジェクトのリスト
        """
        file_path = self._get_file_path(month)
        
        # ファイルが無ければ空リストを返す
        if not os.path.exists(file_path):
            return []
        
        break_requests = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 必須フィールドの存在チェック
                required_fields = ['id', 'shift_request_id', 'break_start', 'break_end']
                if all(row.get(field) for field in required_fields):
                    try:
                        break_request = BreakRequest.from_dict(row)
                        break_requests.append(break_request)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: 休憩希望データの読み込みエラー: {row}, {e}")
                        continue
                else:
                    missing = [f for f in required_fields if not row.get(f)]
                    print(f"Warning: 必須フィールドが欠けています: {missing}, 行: {row}")
        
        return break_requests
    
    def find_by_shift_request_id(self, month: str, shift_request_id: int) -> List[BreakRequest]:
        """
        シフト希望IDで休憩希望を検索（1つのシフト希望に複数の休憩希望）
        
        Args:
            month: 'YYYY-MM' 形式
            shift_request_id: シフト希望ID
        
        Returns:
            BreakRequestオブジェクトのリスト
        """
        all_break_requests = self.find_all_by_month(month)
        return [br for br in all_break_requests if br.shift_request_id == shift_request_id]
    
    def find_by_id(self, month: str, break_request_id: int) -> Optional[BreakRequest]:
        """
        IDで休憩希望を検索
        
        Args:
            month: 'YYYY-MM' 形式
            break_request_id: 休憩希望ID
        
        Returns:
            BreakRequestオブジェクト、見つからなければNone
        """
        all_break_requests = self.find_all_by_month(month)
        for br in all_break_requests:
            if br.id == break_request_id:
                return br
        return None
    
    def save(self, month: str, break_request: BreakRequest) -> BreakRequest:
        """
        休憩希望を保存（追加または更新）
        
        Args:
            month: 'YYYY-MM' 形式
            break_request: BreakRequestオブジェクト
        
        Returns:
            保存されたBreakRequestオブジェクト（IDが採番される）
        """
        all_break_requests = self.find_all_by_month(month)
        
        # ID採番（新規の場合）
        if break_request.id == 0:
            max_id = max([br.id for br in all_break_requests], default=0)
            break_request.id = max_id + 1
            all_break_requests.append(break_request)
        else:
            # 既存データを更新
            updated = False
            for i, br in enumerate(all_break_requests):
                if br.id == break_request.id:
                    all_break_requests[i] = break_request
                    updated = True
                    break
            
            if not updated:
                # IDが指定されているが存在しない場合は追加
                all_break_requests.append(break_request)
        
        # ファイルに保存
        self._save_all(month, all_break_requests)
        return break_request
    
    def delete(self, month: str, break_request_id: int) -> bool:
        """
        休憩希望を削除
        
        Args:
            month: 'YYYY-MM' 形式
            break_request_id: 休憩希望ID
        
        Returns:
            削除成功したらTrue、失敗したらFalse
        """
        all_break_requests = self.find_all_by_month(month)
        
        # 削除対象を除外
        filtered_break_requests = [br for br in all_break_requests if br.id != break_request_id]
        
        # 削除できたかチェック
        if len(filtered_break_requests) == len(all_break_requests):
            return False  # 削除対象が見つからなかった
        
        # ファイルに保存
        self._save_all(month, filtered_break_requests)
        return True
    
    def delete_by_shift_request_id(self, month: str, shift_request_id: int) -> int:
        """
        シフト希望IDに紐づく休憩希望を全削除
        
        Args:
            month: 'YYYY-MM' 形式
            shift_request_id: シフト希望ID
        
        Returns:
            削除された休憩希望の数
        """
        all_break_requests = self.find_all_by_month(month)
        
        # 削除対象を除外
        filtered_break_requests = [br for br in all_break_requests if br.shift_request_id != shift_request_id]
        deleted_count = len(all_break_requests) - len(filtered_break_requests)
        
        if deleted_count > 0:
            self._save_all(month, filtered_break_requests)
        
        return deleted_count
    
    def _save_all(self, month: str, break_requests: List[BreakRequest]) -> None:
        """
        全休憩希望データをファイルに保存
        
        Args:
            month: 'YYYY-MM' 形式
            break_requests: BreakRequestオブジェクトのリスト
        """
        file_path = self._get_file_path(month)
        
        # フォルダが無ければ作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'shift_request_id', 'break_start', 'break_end']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for break_request in break_requests:
                writer.writerow(break_request.to_dict())
    
    def _get_file_path(self, month: str) -> str:
        """
        月別ファイルパスを取得
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            ファイルパス（例: 'data/break_request/break_request_2025-02.csv'）
        """
        return os.path.join(self.data_dir, f'break_request_{month}.csv')
