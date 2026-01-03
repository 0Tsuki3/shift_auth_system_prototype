# routes/staff.py
"""
スタッフ用ルート（エンドポイント）

このファイルは「スタッフ専用ページ」のURLを担当します。
全てのエンドポイントに @login_required が付きます。
"""

from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from core.decorators import login_required
from services.shift_service import ShiftService
from services.staff_service import StaffService
from presenters.shift_presenter import ShiftPresenter
from datetime import datetime

# Blueprintの作成
staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

# Serviceのインスタンス
shift_service = ShiftService()
staff_service = StaffService()
shift_presenter = ShiftPresenter()


@staff_bp.route('/')
@login_required
def staff_home():
    """
    スタッフホームページ
    
    URL: /staff/
    
    ログイン中のスタッフのホーム
    """
    account = session.get('account')
    now_month = datetime.now().strftime('%Y-%m')
    
    try:
        # 今月の自分のシフトを取得
        shifts = shift_service.get_shifts_by_account(now_month, account)
        total_hours = shift_service.calculate_total_hours(now_month, account)
        
        return render_template(
            'staff_home.html',
            now_month=now_month,
            total_shifts=len(shifts),
            total_hours=total_hours
        )
    except Exception as e:
        flash(f'データ取得エラー: {str(e)}', 'error')
        return render_template('staff_home.html', now_month=now_month)


@staff_bp.route('/shifts/<month>')
@login_required
def view_my_shifts(month):
    """
    自分のシフト表示（月別）
    
    URL: /staff/shifts/2025-09
    
    ログイン中のスタッフのシフトのみ表示
    """
    account = session.get('account')
    
    try:
        # 自分のシフトを取得
        shifts = shift_service.get_shifts_by_account(month, account)
        
        # カレンダー形式に整形
        calendar_data = shift_presenter.format_for_calendar(shifts, month)
        
        # 給料計算
        staff = staff_service.get_staff_by_account(account)
        if staff:
            salary_info = shift_presenter.calculate_salary(shifts, staff)
        else:
            salary_info = None
        
        return render_template(
            'staff_shifts_calendar.html',
            month=month,
            calendar_data=calendar_data,
            salary_info=salary_info
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('staff.staff_home'))


@staff_bp.route('/salary/<month>')
@login_required
def view_salary(month):
    """
    給料明細表示
    
    URL: /staff/salary/2025-09
    
    ログイン中のスタッフの給料明細
    """
    account = session.get('account')
    
    try:
        # 自分のシフトを取得
        shifts = shift_service.get_shifts_by_account(month, account)
        staff = staff_service.get_staff_by_account(account)
        
        if not staff:
            flash('スタッフ情報が見つかりません', 'error')
            return redirect(url_for('staff.staff_home'))
        
        # 給料計算
        salary_info = shift_presenter.calculate_salary(shifts, staff)
        
        return render_template(
            'staff_salary.html',
            month=month,
            staff=staff,
            salary_info=salary_info,
            shifts=sorted(shifts, key=lambda s: s.date)
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('staff.staff_home'))

