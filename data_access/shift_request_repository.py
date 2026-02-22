# data_access/shift_request_repository.py
"""
シフト希望データのRepository（データアクセス層）

このファイルは「シフト希望データの読み書き」を担当します。
現時点ではCSVを使い、将来的にSQLに移行します。
"""

import os
import csv
from typing import List, Optional
from datetime import datetime
from models.shift_request import ShiftRequest


class ShiftRequestRepository:
    """
    シフト希望データアクセス（CSV実装）
    
    CSVファイルの配置:
        data/shift_request/shift_request_YYYY-MM.csv
        例: data/shift_request/shift_request_2025-09.csv
    
    将来的にSQLに移行する際は、このクラスを差し替えるだけでOK
    """
    
    def __init__(self):
        """
        初期化
        
        data_dir: シフト希望データを保存するフォルダ
        """
        self.data_dir = 'data/shift_request'
        # フォルダが無ければ作成
        os.makedirs(self.data_dir, exist_ok=True)
    
    def find_all_by_month(self, month: str) -> List[ShiftRequest]:
        """
        月別シフト希望を全件取得
        
        Args:
            month: 'YYYY-MM' 形式（例: '2025-09'）
        
        Returns:
            ShiftRequestオブジェクトのリスト
        
        使い方:
            repo = ShiftRequestRepository()
            requests = repo.find_all_by_month('2025-09')
            for req in requests:
                print(req.account, req.start)
        """
        file_path = self._get_file_path(month)
        
        # ファイルが無ければ空リストを返す
        if not os.path.exists(file_path):
            return []
        
        requests = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 必須フィールドの存在チェック（全て必須）
                required_fields = ['id', 'account', 'date', 'start', 'end']
                if all(row.get(field) for field in required_fields):
                    try:
                        request = ShiftRequest.from_dict(row)
                        requests.append(request)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: シフト希望データの読み込みエラー: {row}, {e}")
                        continue
                else:
                    # 必須フィールドが欠けている場合は警告
                    missing = [f for f in required_fields if not row.get(f)]
                    print(f"Warning: 必須フィールドが欠けています: {missing}, 行: {row}")
        
        return requests
    
    def find_by_id(self, month: str, request_id: int) -> Optional[ShiftRequest]:
        """
        IDでシフト希望を検索
        
        Args:
            month: 'YYYY-MM' 形式
            request_id: シフト希望ID
        
        Returns:
            ShiftRequestオブジェクト、見つからなければNone
        """
        all_requests = self.find_all_by_month(month)
        for req in all_requests:
            if req.id == request_id:
                return req
        return None
    
    def find_by_account(self, month: str, account: str) -> List[ShiftRequest]:
        """
        アカウント名でシフト希望を検索
        
        Args:
            month: 'YYYY-MM' 形式
            account: アカウント名
        
        Returns:
            該当するShiftRequestオブジェクトのリスト
        """
        all_requests = self.find_all_by_month(month)
        return [r for r in all_requests if r.account == account]
    
    def find_by_read_status(self, month: str, read_status: str) -> List[ShiftRequest]:
        """
        既読ステータスでシフト希望を検索
        
        Args:
            month: 'YYYY-MM' 形式
            read_status: 既読ステータス（unread/read）
        
        Returns:
            該当するShiftRequestオブジェクトのリスト
        """
        all_requests = self.find_all_by_month(month)
        return [r for r in all_requests if r.read_status == read_status]
    
    def save_all_by_month(self, month: str, requests: List[ShiftRequest]) -> None:
        """
        月別シフト希望を一括保存（上書き）
        
        Args:
            month: 'YYYY-MM' 形式
            requests: ShiftRequestオブジェクトのリスト
        
        使い方:
            requests = repo.find_all_by_month('2025-09')
            requests.append(new_request)  # 新しい希望を追加
            repo.save_all_by_month('2025-09', requests)
        """
        file_path = self._get_file_path(month)
        
        # ID自動採番（IDが0のものに新しいIDを振る）
        max_id = max([r.id for r in requests if r.id > 0], default=0)
        for request in requests:
            if request.id == 0:
                max_id += 1
                request.id = max_id
            # created_atが無い場合は現在時刻を設定
            if request.created_at is None:
                request.created_at = datetime.now()
        
        # CSV保存
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if requests:
                # シフト希望データがある場合
                fieldnames = ['id', 'account', 'date', 'start', 'end', 'request_type', 'read_status', 'note', 'created_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # date, start時刻でソート
                sorted_requests = sorted(requests, key=lambda r: (r.date, r.start))
                
                for request in sorted_requests:
                    writer.writerow(request.to_dict())
            else:
                # 空の場合はヘッダーだけ
                fieldnames = ['id', 'account', 'date', 'start', 'end', 'request_type', 'read_status', 'note', 'created_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
    
    def save(self, month: str, request: ShiftRequest) -> ShiftRequest:
        """
        シフト希望1件を保存（新規または更新）
        
        Args:
            month: 'YYYY-MM' 形式
            request: ShiftRequestオブジェクト
        
        Returns:
            保存されたShiftRequestオブジェクト（IDが自動採番される）
        
        使い方:
            new_request = ShiftRequest(id=0, account='nakamura', ...)
            saved_request = repo.save('2025-09', new_request)
            print(saved_request.id)  # → 自動採番されたID
        """
        all_requests = self.find_all_by_month(month)
        
        # 既存の希望を更新
        if request.id > 0:
            for i, r in enumerate(all_requests):
                if r.id == request.id:
                    all_requests[i] = request
                    self.save_all_by_month(month, all_requests)
                    return request
        
        # 新規希望を追加
        all_requests.append(request)
        self.save_all_by_month(month, all_requests)
        return request
    
    def delete(self, month: str, request_id: int) -> bool:
        """
        シフト希望を削除
        
        Args:
            month: 'YYYY-MM' 形式
            request_id: シフト希望ID
        
        Returns:
            削除成功したかどうか
        """
        all_requests = self.find_all_by_month(month)
        original_count = len(all_requests)
        all_requests = [r for r in all_requests if r.id != request_id]
        
        if len(all_requests) < original_count:
            self.save_all_by_month(month, all_requests)
            return True
        
        return False
    
    def _get_file_path(self, month: str) -> str:
        """
        月からCSVファイルパスを生成（内部用）
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            ファイルパス（例: 'data/shift_request/shift_request_2025-09.csv'）
        """
        return os.path.join(self.data_dir, f'shift_request_{month}.csv')
