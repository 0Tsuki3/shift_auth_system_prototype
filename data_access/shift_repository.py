# data_access/shift_repository.py
"""
シフトデータのRepository（データアクセス層）

このファイルは「シフトデータの読み書き」を担当します。
現時点ではCSVを使い、将来的にSQLに移行します。
"""

import os
import csv
from typing import List, Optional
from datetime import datetime
from models.shift import Shift


class ShiftRepository:
    """
    シフトデータアクセス（CSV実装）
    
    CSVファイルの配置:
        data/shift/shift_YYYY-MM.csv
        例: data/shift/shift_2025-09.csv
    
    将来的にSQLに移行する際は、このクラスを差し替えるだけでOK
    """
    
    def __init__(self):
        """
        初期化
        
        data_dir: シフトデータを保存するフォルダ
        """
        self.data_dir = 'data/shift'
        # フォルダが無ければ作成
        os.makedirs(self.data_dir, exist_ok=True)
    
    def find_all_by_month(self, month: str) -> List[Shift]:
        """
        月別シフトを全件取得
        
        Args:
            month: 'YYYY-MM' 形式（例: '2025-09'）
        
        Returns:
            Shiftオブジェクトのリスト
        
        使い方:
            repo = ShiftRepository()
            shifts = repo.find_all_by_month('2025-09')
            for shift in shifts:
                print(shift.account, shift.start)
        """
        file_path = self._get_file_path(month)
        
        # ファイルが無ければ空リストを返す
        if not os.path.exists(file_path):
            return []
        
        shifts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 空行や不完全な行をスキップ
                if row.get('account') and row.get('start') and row.get('end'):
                    try:
                        shift = Shift.from_dict(row)
                        shifts.append(shift)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: シフトデータの読み込みエラー: {row}, {e}")
                        continue
        
        return shifts
    
    def find_by_id(self, month: str, shift_id: int) -> Optional[Shift]:
        """
        IDでシフトを検索
        
        Args:
            month: 'YYYY-MM' 形式
            shift_id: シフトID
        
        Returns:
            Shiftオブジェクト、見つからなければNone
        """
        all_shifts = self.find_all_by_month(month)
        for shift in all_shifts:
            if shift.id == shift_id:
                return shift
        return None
    
    def find_by_account(self, month: str, account: str) -> List[Shift]:
        """
        アカウント名でシフトを検索
        
        Args:
            month: 'YYYY-MM' 形式
            account: アカウント名
        
        Returns:
            該当するShiftオブジェクトのリスト
        """
        all_shifts = self.find_all_by_month(month)
        return [s for s in all_shifts if s.account == account]
    
    def save_all_by_month(self, month: str, shifts: List[Shift]) -> None:
        """
        月別シフトを一括保存（上書き）
        
        Args:
            month: 'YYYY-MM' 形式
            shifts: Shiftオブジェクトのリスト
        
        使い方:
            shifts = repo.find_all_by_month('2025-09')
            shifts.append(new_shift)  # 新しいシフトを追加
            repo.save_all_by_month('2025-09', shifts)
        """
        file_path = self._get_file_path(month)
        
        # ID自動採番（IDが0のものに新しいIDを振る）
        max_id = max([s.id for s in shifts if s.id > 0], default=0)
        for shift in shifts:
            if shift.id == 0:
                max_id += 1
                shift.id = max_id
        
        # CSV保存
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if shifts:
                # シフトデータがある場合
                fieldnames = ['id', 'account', 'date', 'start', 'end']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # start時刻でソート（同じ日の複数シフトを時系列順に）
                sorted_shifts = sorted(shifts, key=lambda s: (s.date, s.start))
                
                for shift in sorted_shifts:
                    writer.writerow(shift.to_dict())
            else:
                # 空の場合はヘッダーだけ
                fieldnames = ['id', 'account', 'date', 'start', 'end']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
    
    def save(self, month: str, shift: Shift) -> Shift:
        """
        シフト1件を保存（新規または更新）
        
        Args:
            month: 'YYYY-MM' 形式
            shift: Shiftオブジェクト
        
        Returns:
            保存されたShiftオブジェクト（IDが自動採番される）
        
        使い方:
            new_shift = Shift(id=0, account='nakamura', ...)
            saved_shift = repo.save('2025-09', new_shift)
            print(saved_shift.id)  # → 自動採番されたID
        """
        all_shifts = self.find_all_by_month(month)
        
        # 既存のシフトを更新
        if shift.id > 0:
            for i, s in enumerate(all_shifts):
                if s.id == shift.id:
                    all_shifts[i] = shift
                    self.save_all_by_month(month, all_shifts)
                    return shift
        
        # 新規シフトを追加
        all_shifts.append(shift)
        self.save_all_by_month(month, all_shifts)
        return shift
    
    def delete(self, month: str, shift_id: int) -> bool:
        """
        シフトを削除
        
        Args:
            month: 'YYYY-MM' 形式
            shift_id: シフトID
        
        Returns:
            削除成功したかどうか
        """
        all_shifts = self.find_all_by_month(month)
        original_count = len(all_shifts)
        all_shifts = [s for s in all_shifts if s.id != shift_id]
        
        if len(all_shifts) < original_count:
            self.save_all_by_month(month, all_shifts)
            return True
        
        return False
    
    def _get_file_path(self, month: str) -> str:
        """
        月からCSVファイルパスを生成（内部用）
        
        Args:
            month: 'YYYY-MM' 形式
        
        Returns:
            ファイルパス（例: 'data/shift/shift_2025-09.csv'）
        """
        return os.path.join(self.data_dir, f'shift_{month}.csv')

