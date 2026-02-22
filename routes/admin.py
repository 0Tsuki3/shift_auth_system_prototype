# routes/admin.py
"""
管理者用ルート（エンドポイント）

このファイルは「管理者専用ページ」のURLを担当します。
全てのエンドポイントに @admin_required が付きます。
"""

from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from core.decorators import admin_required
from services.shift_service import ShiftService
from services.staff_service import StaffService
from presenters.shift_presenter import ShiftPresenter
from datetime import datetime

# Blueprintの作成
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Serviceのインスタンス
shift_service = ShiftService()
staff_service = StaffService()
shift_presenter = ShiftPresenter()


@admin_bp.route('/')
@admin_required
def admin_home():
    """
    管理者ホームページ
    
    URL: /admin/
    
    管理者専用のダッシュボード
    """
    now_month = datetime.now().strftime('%Y-%m')
    
    # 今月のシフト統計
    try:
        shifts = shift_service.get_shifts_by_month(now_month)
        staff_list = staff_service.get_all_staff()
        
        return render_template(
            'admin_home.html',
            now_month=now_month,
            total_shifts=len(shifts),
            total_staff=len(staff_list)
        )
    except Exception as e:
        flash(f'データ取得エラー: {str(e)}', 'error')
        return render_template('admin_home.html', now_month=now_month)


@admin_bp.route('/shifts/<month>')
@admin_required
def view_shifts(month):
    """
    シフト一覧表示（月別）
    
    URL: /admin/shifts/2025-09
    
    カレンダー形式でシフトを表示
    """
    try:
        shifts = shift_service.get_shifts_by_month(month)
        staff_list = staff_service.get_all_staff()
        
        # カレンダー形式に整形
        calendar_data = shift_presenter.format_for_calendar(shifts, month)
        
        return render_template(
            'admin_shifts_calendar.html',
            month=month,
            calendar_data=calendar_data,
            staff_list=staff_list
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.admin_home'))


@admin_bp.route('/staff')
@admin_required
def staff_list():
    """
    スタッフ一覧
    
    URL: /admin/staff
    
    全スタッフの一覧を表示
    """
    try:
        staff_list = staff_service.get_all_staff()
        
        return render_template(
            'admin_staff_list.html',
            staff_list=staff_list
        )
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('admin.admin_home'))


@admin_bp.route('/staff/add', methods=['GET', 'POST'])
@admin_required
def add_staff():
    """
    スタッフ追加
    
    URL: /admin/staff/add
    
    GET: 追加フォーム表示
    POST: スタッフを追加
    """
    if request.method == 'POST':
        try:
            from models.staff import Staff
            from services.auth_service import AuthService
            
            # フォームからデータ取得
            account = request.form.get('account')
            last_name = request.form.get('last_name')
            first_name = request.form.get('first_name')
            hourly_wage = int(request.form.get('hourly_wage', 0))
            position = request.form.get('position')
            password = request.form.get('password')
            role = request.form.get('role', 'staff')
            
            # スタッフ作成
            staff = Staff(
                id=0,
                account=account,
                last_name=last_name,
                first_name=first_name,
                hourly_wage=hourly_wage,
                position=position
            )
            staff_service.create_staff(staff)
            
            # 認証情報作成
            auth_service = AuthService()
            auth_service.create_auth(account, password, role)
            
            flash(f'スタッフ「{last_name} {first_name}」を追加しました', 'success')
            return redirect(url_for('admin.staff_list'))
        
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('admin_add_staff.html')


@admin_bp.route('/shifts/<month>/add', methods=['GET', 'POST'])
@admin_required
def add_shift(month):
    """
    シフト追加
    
    URL: /admin/shifts/2025-09/add
    
    GET: 追加フォーム表示
    POST: シフトを追加
    """
    if request.method == 'POST':
        try:
            from models.shift import Shift
            
            # フォームからデータ取得
            account = request.form.get('account')
            date = request.form.get('date')
            start = request.form.get('start')
            end = request.form.get('end')
            
            # Shiftオブジェクト作成（id=0で新規作成）
            shift = Shift(
                id=0,
                account=account,
                date=date,
                start=start,
                end=end
            )
            
            # シフト作成（バリデーション＋保存）
            shift_service.create_shift(month, shift)
            
            flash(f'{date} のシフトを追加しました', 'success')
            return redirect(url_for('admin.view_shifts', month=month))
        
        except ValueError as e:
            flash(str(e), 'error')
    
    # GET: フォーム表示
    try:
        staff_list = staff_service.get_all_staff()
        return render_template(
            'admin_add_shift.html',
            month=month,
            staff_list=staff_list
        )
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('admin.admin_home'))

