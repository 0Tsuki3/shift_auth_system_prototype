# data_access/break_repository.py
"""
休憩データのRepository（データアクセス層）

このファイルは「休憩データの読み書き」を担当します。
現時点ではCSVを使い、将来的にSQLに移行します。
"""

import os
import csv
from typing import List, Optional
from datetime import datetime
from models.break_model import Break


class BreakRepository:
    """
    休憩データアクセス（CSV実装）
    
    CSVファイルの配置:
        data/break/break_YYYY-MM.csv
        例: data/break/break_2025-02.csv
    
    将来的にSQLに移行する際は、このクラスを差し替えるだけでOK
    """
    
    def __init__(self):
        """
        初期化
        
        data_dir: 休憩データを保存するフォルダ
        """
        self.data_dir = 'data/break'
        # フォルダが無ければ作成
        os.makedirs(self.data_dir, exist_ok=True)
    
    def find_all_by_month(self, month: str) -> List[Break]:
        """
        月別休憩を全件取得
        
        Args:
            month: 'YYYY-MM' 形式（例: '2025-02'）
        
        Returns:
            Breakオブジェクトのリスト
        """
        file_path = self._get_file_path(month)
        
        # ファイルが無ければ空リストを返す
        if not os.path.exists(file_path):
            return []
        
        breaks = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 必須フィールドの存在チェック
                required_fields = ['id', 'shift_id', 'break_start', 'break_end']
                if all(row.get(field) for field in required_fields):
                    try:
                        break_obj = Break.from_dict(row)
                        breaks.append(break_obj)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: 休憩データの読み込みエラー: {row}, {e}")
                        continue
                else:
                    missing = [f for f in required_fields if not row.get(f)]
                    print(f"Warning: 必須フィールドが欠けています: {missing}, 行: {row}")
        
        return breaks
    
    def find_by_shift_id(self, month: str, shift_id: int) -> List[Break]:
        """
        シフトIDで休憩を検索（1つのシフトに複数の休憩）
        
        Args:
            month: 'YYYY-MM' 形式
            shift_id: シフトID
        
        Returns:
            Breakオブジェクトのリスト
        """
        all_breaks = self.find_all_by_month(month)
        return [b for b in all_breaks if b.shift_id == shift_id]
    
    def find_by_id(self, month: str, break_id: int) -> Optional[Break]:
        """
        IDで休憩を検索
        
        Args:
            month: 'YYYY-MM' 形式
            break_id: 休憩ID
        
        Returns:
            Breakオブジェクト、見つからなければNone
        """
        all_breaks = self.find_all_by_month(month)
        for break_obj in all_breaks:
            if break_obj.id == break_id:
                return break_obj
        return None
    
    def save(self, month: str, break_obj: Break) -> Break:
        """
        休憩を保存（追加または更新）
        
        Args:
            month: 'YYYY-MM' 形式
            break_obj: Breakオブジェクト
        
        Returns:
            保存されたBreakオブジェクト（IDが採番される）
        """
        all_breaks = self.find_all_by_month(month)
        
        # ID採番（新規の場合）
        if break_obj.id == 0:
            max_id = max([b.id for b in all_breaks], default=0)
            break_obj.id = max_id + 1
            all_breaks.append(break_obj)
        else:
            # 既存データを更新
            updated = False
            for i, b in enumerate(all_breaks):
                if b.id == break_obj.id:
                    all_breaks[i] = break_obj
                    updated = True
                    break
            
            if not updated:
                # IDが指定されているが存在しない場合は追加
                all_breaks.append(break_obj)
        
        # ファイルに保存
        self._save_all(month, all_breaks)
        return break_obj
    
    def delete(self, month: str, break_id: int) -> bool:
        """
        休憩を削除
        
        Args:
            month: 'YYYY-MM' 形式
            break_id: 休憩ID
        
        Returns:
            削除成功したらTrue、失敗したらFalse
        """
        all_breaks = self.find_all_by_month(month)
        
        # 削除対象を除外
        filtered_breaks = [b for b in all_breaks if b.id != break_id]
        
        # 削除できたかチェック
        if len(filtered_breaks) == len(all_breaks):
            return False  # 削除対象が見つからなかった
        
        # ファイルに保存
        self._save_all(month, filtered_breaks)
        return True
    
    def delete_by_shift_id(self, month: str, shift_id: int) -> int:
        """
        シフトIDに紐づく休憩を全削除
        
        Args:
            month: 'YYYY-MM' 形式
            shift_id: シフトID
        
        Returns:
            削除された休憩の数
        """
        all_breaks = self.find_all_by_month(month)
        
        # 削除対象を除外
        filtered_breaks = [b for b in all_breaks if b.shift_id != shift_id]
        deleted_count = len(all_breaks) - len(filtered_breaks)
        
        if deleted_count > 0:
            self._save_all(month, filtered_breaks)
        
        return deleted_count
    
    def _save_all(self, month: str, breaks: List[Break]) -> None:
        """
        全休憩データをファイルに保存
        
        Args:
            month: 'YYYY-MM' 形式
            breaks: Breakオブジェクトのリスト
        """
        file_path = self._get_file_path(month)
        
        # フォルダが無ければ作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'shift_id', 'break_start', 'break_end']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for break_obj in breaks:
                writer.writerow(break_obj.to_dict())
    
    def _get_file_path(self, month: str) -> str:
        """
        月別ファイルパスを取得
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            ファイルパス（例: 'data/break/break_2025-02.csv'）
        """
        return os.path.join(self.data_dir, f'break_{month}.csv')
