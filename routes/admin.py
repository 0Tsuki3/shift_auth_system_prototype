# routes/admin.py
"""
管理者用ルート（エンドポイント）

このファイルは「管理者専用ページ」のURLを担当します。
全てのエンドポイントに @admin_required が付きます。
"""

from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from core.decorators import admin_required
from services.shift_service import ShiftService
from services.shift_request_service import ShiftRequestService
from services.staff_service import StaffService
from presenters.shift_presenter import ShiftPresenter
from datetime import datetime

# Blueprintの作成
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Serviceのインスタンス
shift_service = ShiftService()
shift_request_service = ShiftRequestService()
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
        
        # スタッフ情報をマッピング（account → Staff）
        staff_dict = {staff.account: staff for staff in staff_list}
        
        # カレンダー形式に整形
        calendar_data = shift_presenter.format_for_calendar(shifts, month)
        
        # カレンダーデータにスタッフ情報を追加
        for date_str, day_shifts in calendar_data.items():
            for shift_data in day_shifts:
                account = shift_data['account']
                if account in staff_dict:
                    staff = staff_dict[account]
                    shift_data['full_name'] = staff.full_name
                    shift_data['position'] = staff.position
                else:
                    shift_data['full_name'] = account  # スタッフが見つからない場合はアカウント名
                    shift_data['position'] = '不明'
                # duration_hoursはhoursに既に含まれているので名前を統一
                shift_data['duration_hours'] = shift_data['hours']
        
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
            from datetime import datetime as dt
            
            # フォームからデータ取得
            account = request.form.get('account')
            date_str = request.form.get('date')
            start_str = request.form.get('start')
            end_str = request.form.get('end')
            
            # 時刻文字列を正規化（秒が含まれている場合は除去）
            def normalize_time(time_str):
                parts = time_str.split(':')
                return f"{parts[0]}:{parts[1]}"  # HH:MM のみ
            
            start_str = normalize_time(start_str)
            end_str = normalize_time(end_str)
            
            # 文字列を適切な型に変換
            date_obj = dt.strptime(date_str, '%Y-%m-%d').date()
            start_time = dt.strptime(start_str, '%H:%M').time()
            end_time = dt.strptime(end_str, '%H:%M').time()
            
            # Shiftオブジェクト作成（id=0で新規作成）
            shift = Shift(
                id=0,
                account=account,
                date=date_obj,
                start=start_time,
                end=end_time
            )
            
            # シフト作成（バリデーション＋保存）
            shift_service.create_shift(month, shift)
            
            flash(f'{date_str} のシフトを追加しました', 'success')
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


@admin_bp.route('/shifts/<month>/edit/<int:shift_id>', methods=['GET', 'POST'])
@admin_required
def edit_shift(month, shift_id):
    """
    シフト編集
    
    URL: /admin/shifts/2025-09/edit/5
    
    GET: 編集フォーム表示
    POST: シフトを更新
    """
    if request.method == 'POST':
        try:
            from models.shift import Shift
            from datetime import datetime as dt
            
            # フォームからデータ取得
            account = request.form.get('account')
            date_str = request.form.get('date')
            start_str = request.form.get('start')
            end_str = request.form.get('end')
            
            # 時刻文字列を正規化（秒が含まれている場合は除去）
            def normalize_time(time_str):
                parts = time_str.split(':')
                return f"{parts[0]}:{parts[1]}"  # HH:MM のみ
            
            start_str = normalize_time(start_str)
            end_str = normalize_time(end_str)
            
            # 文字列を適切な型に変換
            date_obj = dt.strptime(date_str, '%Y-%m-%d').date()
            start_time = dt.strptime(start_str, '%H:%M').time()
            end_time = dt.strptime(end_str, '%H:%M').time()
            
            # Shiftオブジェクト作成（既存のIDを保持）
            shift = Shift(
                id=shift_id,
                account=account,
                date=date_obj,
                start=start_time,
                end=end_time
            )
            
            # シフト更新（バリデーション＋保存）
            shift_service.update_shift(month, shift)
            
            flash(f'{date_str} のシフトを更新しました', 'success')
            return redirect(url_for('admin.view_shifts', month=month))
        
        except ValueError as e:
            flash(str(e), 'error')
    
    # GET: 編集フォーム表示
    try:
        # 既存のシフトデータを取得
        existing_shift = shift_service.get_shifts_by_month(month)
        shift = None
        for s in existing_shift:
            if s.id == shift_id:
                shift = s
                break
        
        if not shift:
            flash(f'シフトID {shift_id} が見つかりません', 'error')
            return redirect(url_for('admin.view_shifts', month=month))
        
        # スタッフリストを取得
        staff_list = staff_service.get_all_staff()
        
        return render_template(
            'admin_edit_shift.html',
            month=month,
            shift=shift,
            staff_list=staff_list
        )
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('admin.admin_home'))


@admin_bp.route('/shifts/<month>/delete/<int:shift_id>', methods=['POST'])
@admin_required
def delete_shift(month, shift_id):
    """
    シフト削除
    
    URL: /admin/shifts/2025-09/delete/5
    
    POST: シフトを削除
    """
    try:
        # シフトの存在チェックと情報取得
        existing_shifts = shift_service.get_shifts_by_month(month)
        shift_to_delete = None
        for s in existing_shifts:
            if s.id == shift_id:
                shift_to_delete = s
                break
        
        if not shift_to_delete:
            flash(f'シフトID {shift_id} が見つかりません', 'error')
            return redirect(url_for('admin.view_shifts', month=month))
        
        # シフト削除
        success = shift_service.delete_shift(month, shift_id)
        
        if success:
            flash(f'{shift_to_delete.date} のシフトを削除しました', 'success')
        else:
            flash('シフトの削除に失敗しました', 'error')
        
        return redirect(url_for('admin.view_shifts', month=month))
    
    except Exception as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('admin.view_shifts', month=month))


@admin_bp.route('/shift-requests/<month>')
@admin_required
def view_shift_requests(month):
    """
    シフト希望一覧表示（管理者用）
    
    URL: /admin/shift-requests/2025-09
    
    スタッフから提出されたシフト希望を一覧表示
    """
    try:
        # シフト希望を取得
        shift_requests = shift_request_service.get_requests_by_month(month)
        
        # スタッフ情報を取得
        staff_list = staff_service.get_all_staff()
        staff_dict = {staff.account: staff for staff in staff_list}
        
        # シフト希望にスタッフ情報を追加
        requests_with_staff = []
        for req in shift_requests:
            staff = staff_dict.get(req.account)
            requests_with_staff.append({
                'request': req,
                'staff_name': staff.full_name if staff else req.account,
                'position': staff.position if staff else '不明'
            })
        
        # 既読ステータス別にグループ化
        unread_requests = [r for r in requests_with_staff if r['request'].read_status == 'unread']
        read_requests = [r for r in requests_with_staff if r['request'].read_status == 'read']
        
        return render_template(
            'admin_shift_requests.html',
            month=month,
            unread_requests=unread_requests,
            read_requests=read_requests,
            total_requests=len(shift_requests)
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.admin_home'))


@admin_bp.route('/shift-requests/<month>/import/<int:request_id>', methods=['POST'])
@admin_required
def import_shift_request(month, request_id):
    """
    シフト希望を確定シフトにインポート
    
    URL: /admin/shift-requests/2025-09/import/5
    
    POST: シフト希望を確定シフトに変換して保存
    """
    try:
        from models.shift import Shift
        
        # シフト希望を取得
        shift_request = shift_request_service.get_request_by_id(month, request_id)
        
        # 確定シフトに変換
        shift = Shift(
            id=0,  # 新規作成
            account=shift_request.account,
            date=shift_request.date,
            start=shift_request.start,
            end=shift_request.end
        )
        
        # シフトを作成
        shift_service.create_shift(month, shift)
        
        # シフト希望を既読に更新
        shift_request_service.mark_as_read(month, request_id)
        
        # スタッフ名を取得して表示
        staff = staff_service.get_all_staff()
        staff_dict = {s.account: s for s in staff}
        staff_name = staff_dict[shift_request.account].full_name if shift_request.account in staff_dict else shift_request.account
        
        flash(f'{staff_name} のシフト希望（{shift_request.date}）を確定シフトに追加しました', 'success')
        return redirect(url_for('admin.view_shift_requests', month=month))
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.view_shift_requests', month=month))


@admin_bp.route('/shift-requests/<month>/mark-read/<int:request_id>', methods=['POST'])
@admin_required
def mark_request_as_read(month, request_id):
    """
    シフト希望を既読にする
    
    URL: /admin/shift-requests/2025-09/mark-read/5
    
    POST: シフト希望の既読ステータスを 'read' に更新
    """
    try:
        # シフト希望を既読にする
        shift_request = shift_request_service.mark_as_read(month, request_id)
        
        # スタッフ名を取得して表示
        staff = staff_service.get_all_staff()
        staff_dict = {s.account: s for s in staff}
        staff_name = staff_dict[shift_request.account].full_name if shift_request.account in staff_dict else shift_request.account
        
        flash(f'{staff_name} のシフト希望（{shift_request.date}）を既読にしました', 'info')
        return redirect(url_for('admin.view_shift_requests', month=month))
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.view_shift_requests', month=month))

