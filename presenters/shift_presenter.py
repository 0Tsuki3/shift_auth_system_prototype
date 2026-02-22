# presenters/shift_presenter.py
"""
シフトデータの表示用整形

このファイルは「シフトデータを表示用に加工」を担当します。
例: カレンダー形式、テーブル形式、給料計算など
"""

from typing import List, Dict
from datetime import datetime, timedelta
from models.shift import Shift
from models.staff import Staff


class ShiftPresenter:
    """
    シフトプレゼンター（表示用データ整形）
    
    使い方:
        presenter = ShiftPresenter()
        calendar_data = presenter.format_for_calendar(shifts, '2025-09')
    """
    
    def format_for_calendar(self, shifts: List[Shift], month: str) -> Dict[str, List[Dict]]:
        """
        カレンダー表示用にシフトを整形
        
        Args:
            shifts: Shiftオブジェクトのリスト
            month: 'YYYY-MM' 形式
        
        Returns:
            {
                '2025-09-01': [
                    {'id': 1, 'account': 'nakamura', 'start': '09:00', 'end': '15:00', 'hours': 6.0},
                    ...
                ],
                '2025-09-02': [...],
                ...
            }
        
        使い方:
            HTMLで日付ごとにシフトを表示
        """
        # その月の全日付を初期化
        year, mon = map(int, month.split('-'))
        calendar_data = {}
        
        # 月の最初の日
        first_day = datetime(year, mon, 1)
        
        # 次の月の最初の日（月末の計算用）
        if mon == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, mon + 1, 1)
        
        # 月末の日
        last_day = next_month - timedelta(days=1)
        
        # 全日付を初期化
        current_day = first_day
        while current_day <= last_day:
            date_str = current_day.strftime('%Y-%m-%d')
            calendar_data[date_str] = []
            current_day += timedelta(days=1)
        
        # シフトデータを振り分け
        for shift in shifts:
            date_str = shift.date.strftime('%Y-%m-%d')
            if date_str in calendar_data:
                calendar_data[date_str].append({
                    'id': shift.id,
                    'account': shift.account,
                    'start': shift.start.strftime('%H:%M'),
                    'end': shift.end.strftime('%H:%M'),
                    'hours': round(shift.duration_hours(), 2)
                })
        
        # 各日付のシフトを開始時刻でソート
        for date_str in calendar_data:
            calendar_data[date_str].sort(key=lambda x: x['start'])
        
        return calendar_data
    
    def format_for_table(self, shifts: List[Shift], staff_list: List[Staff]) -> List[Dict]:
        """
        テーブル表示用にシフトを整形（スタッフごと）
        
        Args:
            shifts: Shiftオブジェクトのリスト
            staff_list: Staffオブジェクトのリスト
        
        Returns:
            [
                {
                    'staff': Staff,
                    'shifts': [Shift, Shift, ...],
                    'total_hours': 120.5,
                    'total_days': 15
                },
                ...
            ]
        
        使い方:
            スタッフごとのシフト一覧表示
        """
        table_data = []
        
        for staff in staff_list:
            # このスタッフのシフトを抽出
            staff_shifts = [s for s in shifts if s.account == staff.account]
            
            # 勤務時間の合計
            total_hours = sum(s.duration_hours() for s in staff_shifts)
            
            # 勤務日数
            total_days = len(staff_shifts)
            
            table_data.append({
                'staff': staff,
                'shifts': sorted(staff_shifts, key=lambda s: s.date),  # 日付順
                'total_hours': round(total_hours, 2),
                'total_days': total_days
            })
        
        # スタッフ名でソート
        table_data.sort(key=lambda x: x['staff'].account)
        
        return table_data
    
    def calculate_salary(self, shifts: List[Shift], staff: Staff) -> Dict:
        """
        給料計算
        
        Args:
            shifts: Shiftオブジェクトのリスト
            staff: Staffオブジェクト
        
        Returns:
            {
                'total_hours': 120.5,
                'hourly_wage': 1200,
                'total_salary': 144600,
                'days': 15
            }
        
        使い方:
            給料明細の生成
        """
        # 勤務時間の合計
        total_hours = sum(s.duration_hours() for s in shifts)
        
        # 給料計算
        total_salary = int(total_hours * staff.hourly_wage)
        
        # 勤務日数
        days = len(shifts)
        
        return {
            'total_hours': round(total_hours, 2),
            'hourly_wage': staff.hourly_wage,
            'total_salary': total_salary,
            'days': days
        }
    
    def format_for_timeline(self, shifts: List[Shift], date_str: str) -> List[Dict]:
        """
        タイムライン表示用にシフトを整形（1日分）
        
        Args:
            shifts: Shiftオブジェクトのリスト
            date_str: 'YYYY-MM-DD' 形式
        
        Returns:
            [
                {
                    'account': 'nakamura',
                    'start': '09:00',
                    'end': '15:00',
                    'start_minutes': 540,  # 9:00 = 540分
                    'duration_minutes': 360  # 6時間 = 360分
                },
                ...
            ]
        
        使い方:
            1日のシフトをタイムライン（横棒グラフ）で表示
        """
        timeline_data = []
        
        for shift in shifts:
            if shift.date.strftime('%Y-%m-%d') == date_str:
                # 開始時刻を分単位に変換（0:00からの経過分）
                start_minutes = shift.start.hour * 60 + shift.start.minute
                
                # 勤務時間を分単位に変換
                duration_minutes = int(shift.duration_hours() * 60)
                
                timeline_data.append({
                    'account': shift.account,
                    'start': shift.start.strftime('%H:%M'),
                    'end': shift.end.strftime('%H:%M'),
                    'start_minutes': start_minutes,
                    'duration_minutes': duration_minutes
                })
        
        # 開始時刻でソート
        timeline_data.sort(key=lambda x: x['start_minutes'])
        
        return timeline_data

