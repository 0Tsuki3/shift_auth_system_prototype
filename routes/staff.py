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
from services.shift_request_service import ShiftRequestService
from services.break_request_service import BreakRequestService
from services.shift_diff_service import ShiftDiffService
from presenters.shift_presenter import ShiftPresenter
from models.shift_request import ShiftRequest
from datetime import datetime, date, time

# Blueprintの作成
staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

# Serviceのインスタンス
shift_service = ShiftService()
staff_service = StaffService()
shift_request_service = ShiftRequestService()
break_request_service = BreakRequestService()
shift_diff_service = ShiftDiffService()
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


@staff_bp.route('/requests/<month>')
@login_required
def view_requests(month):
    """
    自分のシフト希望一覧表示
    
    URL: /staff/requests/2025-09
    
    ログイン中のスタッフが提出したシフト希望を表示
    """
    account = session.get('account')
    
    try:
        # 自分のシフト希望を取得
        requests = shift_request_service.get_requests_by_account(month, account)
        
        # 日付でソート
        requests = sorted(requests, key=lambda r: (r.date, r.start))
        
        return render_template(
            'staff_view_requests.html',
            month=month,
            requests=requests
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('staff.staff_home'))


@staff_bp.route('/requests/<month>/submit', methods=['GET', 'POST'])
@login_required
def submit_request(month):
    """
    シフト希望提出
    
    URL: /staff/requests/2025-09/submit
    
    GET: シフト希望提出フォームを表示
    POST: シフト希望を保存
    """
    account = session.get('account')
    
    if request.method == 'POST':
        try:
            # フォームデータを取得
            request_date = request.form.get('date')
            request_start = request.form.get('start')
            request_end = request.form.get('end')
            request_note = request.form.get('note', '')
            
            # バリデーション
            if not request_date or not request_start or not request_end:
                flash('日付、開始時刻、終了時刻は必須です', 'error')
                return render_template('staff_submit_request.html', month=month)
            
            # ShiftRequestオブジェクトを作成
            shift_request = ShiftRequest(
                id=0,  # 新規作成なのでID=0
                account=account,
                date=datetime.strptime(request_date, '%Y-%m-%d').date(),
                start=datetime.strptime(request_start, '%H:%M').time(),
                end=datetime.strptime(request_end, '%H:%M').time(),
                request_type='fixed',  # 固定希望
                read_status='unread',  # 未読
                note=request_note,
                created_at=datetime.now()
            )
            
            # シフト希望を保存
            saved_request = shift_request_service.create_request(month, shift_request)
            
            flash(f'シフト希望を提出しました（ID: {saved_request.id}）', 'success')
            return redirect(url_for('staff.view_requests', month=month))
        
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('staff_submit_request.html', month=month)
        except Exception as e:
            flash(f'エラーが発生しました: {str(e)}', 'error')
            return render_template('staff_submit_request.html', month=month)
    
    # GET: フォーム表示
    return render_template('staff_submit_request.html', month=month)


@staff_bp.route('/requests/<month>/delete/<int:request_id>', methods=['POST'])
@login_required
def delete_request(month, request_id):
    """
    シフト希望削除
    
    URL: /staff/requests/2025-09/delete/1
    
    POST: シフト希望を削除（自分の希望のみ）
    """
    account = session.get('account')
    
    try:
        # 削除対象の希望を取得
        shift_request = shift_request_service.get_request_by_id(month, request_id)
        
        # 自分の希望かチェック
        if shift_request.account != account:
            flash('他人のシフト希望は削除できません', 'error')
            return redirect(url_for('staff.view_requests', month=month))
        
        # 削除実行
        success = shift_request_service.delete_request(month, request_id)
        
        if success:
            flash('シフト希望を削除しました', 'success')
        else:
            flash('シフト希望の削除に失敗しました', 'error')
        
        return redirect(url_for('staff.view_requests', month=month))
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('staff.view_requests', month=month))


# ========================================
# 休憩希望API（スタッフ用）
# ========================================

@staff_bp.route('/api/break-requests/<month>/my', methods=['GET'])
@login_required
def api_get_my_break_requests(month):
    """
    自分の休憩希望一覧取得（JSON）
    
    URL: /staff/api/break-requests/<month>/my
    """
    try:
        from flask import jsonify
        
        account = session.get('account')
        
        # 自分のシフト希望を取得
        shift_requests = shift_request_service.get_requests_by_account(month, account)
        
        # 各シフト希望に紐づく休憩希望を取得
        result = []
        for sr in shift_requests:
            break_requests = break_request_service.get_break_requests_by_shift_request_id(month, sr.id)
            result.append({
                'shift_request_id': sr.id,
                'date': sr.date.strftime('%Y-%m-%d'),
                'start': sr.start.strftime('%H:%M'),
                'end': sr.end.strftime('%H:%M'),
                'break_requests': [{
                    'id': br.id,
                    'break_start': br.break_start.strftime('%H:%M'),
                    'break_end': br.break_end.strftime('%H:%M')
                } for br in break_requests]
            })
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@staff_bp.route('/api/shift-diff/<month>/my', methods=['GET'])
@login_required
def api_get_my_shift_diff(month):
    """
    自分のシフト希望と実際のシフトの差分を取得（JSON）
    
    URL: /staff/api/shift-diff/<month>/my
    """
    try:
        from flask import jsonify
        
        account = session.get('account')
        
        # 自分のシフト希望を取得
        shift_requests = shift_request_service.get_requests_by_account(month, account)
        
        # 自分の実際のシフトを取得
        actual_shifts = shift_service.get_shifts_by_account(month, account)
        
        # 差分を計算
        diff_result = shift_diff_service.calculate_batch_diff(shift_requests, actual_shifts)
        
        return jsonify(diff_result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

