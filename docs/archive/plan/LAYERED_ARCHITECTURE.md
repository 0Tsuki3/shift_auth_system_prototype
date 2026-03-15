# 工程別アーキテクチャ完全ガイド

**目的**: アプリを工程（レイヤー）別に分けて、わかりやすく管理する  
**最終更新**: 2025-12-06

---

## 🎯 なぜ工程別に分けるのか？

### 現状の問題（全部1ファイルに混在）

```python
# routes/admin.py（現在: 600行以上）
@admin_blueprint.route("/admin/edit")
def admin_edit():
    # データ取得
    staff = pd.read_csv('staff.csv')
    shifts = pd.read_csv('data/shift/shift_2025-12.csv')
    
    # バリデーション
    if not month:
        return "エラー"
    
    # データ処理
    total = sum(...)
    
    # データ保存
    df.to_csv('data/shift/shift_2025-12.csv')
    
    # 表示
    return render_template('edit.html', ...)
```

**問題点:**
- ❌ 1つの関数が長すぎる（100行以上）
- ❌ 何をしているかわかりにくい
- ❌ バグが見つけにくい
- ❌ 修正するとき全体を理解する必要がある
- ❌ 再利用できない
- ❌ テストが書けない

### 工程別に分けた場合

```python
# routes/admin/shift_manage.py（改善後: 50行）
@admin_bp.route("/admin/edit")
def admin_edit():
    # 各工程は別ファイルの専門クラスに任せる
    shifts = ShiftRepository().get_by_month(month)      # データ取得
    ShiftValidator().validate(shifts)                   # バリデーション
    total = ShiftService().calculate_total(shifts)      # ビジネスロジック
    data = ShiftPresenter().format_for_view(shifts)     # 表示用整形
    return render_template('edit.html', data=data)      # 表示
```

**メリット:**
- ✅ 各ファイルが短い（50-100行）
- ✅ 責任が明確（何をするファイルかすぐわかる）
- ✅ バグが見つけやすい
- ✅ 修正が局所的（他に影響しない）
- ✅ 再利用できる
- ✅ テストが書ける

---

## 🏗️ レイヤードアーキテクチャとは

### 7つの工程（レイヤー）

```
┌─────────────────────────────────────────┐
│  Layer 7: Presentation（表示層）         │  ← routes/
│  リクエストを受け取り、レスポンスを返す    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Layer 6: Presenter（整形層）            │  ← presenters/
│  データを表示用に整形する                 │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Layer 5: Service（サービス層）          │  ← services/
│  ビジネスロジック（計算・判断）           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Layer 4: Validation（検証層）           │  ← validators/
│  入力データのチェック                     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Layer 3: Repository（リポジトリ層）     │  ← data_access/
│  データの取得・保存                      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Layer 2: Data Source（データソース層）  │  ← CSV/SQL
│  実際のデータ保存場所                    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Layer 1: Models（モデル層）             │  ← models/
│  データ構造の定義                        │
└─────────────────────────────────────────┘
```

---

## 📝 各レイヤーの詳細説明

### Layer 1: Models（モデル層）

**役割**: データ構造を定義する  
**場所**: `models/`

```python
# models/shift.py
from dataclasses import dataclass
from datetime import date, time

@dataclass
class Shift:
    """シフトのデータ構造"""
    id: int
    staff_id: str
    date: date
    start_time: time
    end_time: time
    position: str
    
    def duration_hours(self) -> float:
        """勤務時間を計算"""
        delta = datetime.combine(date.min, self.end_time) - \
                datetime.combine(date.min, self.start_time)
        return delta.total_seconds() / 3600
    
    def to_dict(self) -> dict:
        """辞書型に変換"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'position': self.position
        }
```

```python
# models/staff.py
@dataclass
class Staff:
    """スタッフのデータ構造"""
    id: int
    account: str
    last_name: str
    first_name: str
    position: str
    hourly_wage: int
    
    @property
    def full_name(self) -> str:
        """フルネームを取得"""
        return f"{self.last_name} {self.first_name}"
```

**ポイント:**
- データの「形」だけを定義
- ビジネスロジックは入れない（計算は別レイヤー）
- 全レイヤーで使う共通の型

---

### Layer 2: Data Source（データソース層）

**役割**: 実際のデータ保存場所  
**場所**: `data/` フォルダ（CSV）または データベース（SQL）

```
data/
├── shift/
│   └── shift_2025-12.csv       # シフトデータ
├── staff.csv                    # スタッフデータ
└── auth.csv                     # 認証データ
```

**ポイント:**
- このレイヤーは直接触らない
- Repository層（Layer 3）を通してアクセス

---

### Layer 3: Repository（リポジトリ層）

**役割**: データの取得・保存（CRUD操作）  
**場所**: `data_access/`

```python
# data_access/shift_repository.py
from typing import List, Optional
from models.shift import Shift
from datetime import datetime
import csv

class ShiftRepository:
    """シフトデータアクセス"""
    
    def __init__(self):
        self.base_path = 'data/shift'
    
    def find_by_month(self, year: int, month: int) -> List[Shift]:
        """月別シフト取得"""
        path = f"{self.base_path}/shift_{year:04d}-{month:02d}.csv"
        
        if not os.path.exists(path):
            return []
        
        shifts = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                shift = Shift(
                    id=int(row['id']),
                    staff_id=row['staff_id'],
                    date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                    start_time=datetime.strptime(row['start'], '%H:%M').time(),
                    end_time=datetime.strptime(row['end'], '%H:%M').time(),
                    position=row['position']
                )
                shifts.append(shift)
        
        return shifts
    
    def find_by_staff(self, staff_id: str, year: int, month: int) -> List[Shift]:
        """スタッフ別シフト取得"""
        all_shifts = self.find_by_month(year, month)
        return [s for s in all_shifts if s.staff_id == staff_id]
    
    def save(self, shift: Shift) -> None:
        """シフト保存（1件）"""
        # 既存データ読み込み
        month_str = f"{shift.date.year:04d}-{shift.date.month:02d}"
        existing_shifts = self.find_by_month(shift.date.year, shift.date.month)
        
        # 追加または更新
        updated = False
        for i, s in enumerate(existing_shifts):
            if s.id == shift.id:
                existing_shifts[i] = shift
                updated = True
                break
        
        if not updated:
            existing_shifts.append(shift)
        
        # 保存
        self.save_all(month_str, existing_shifts)
    
    def save_all(self, month_str: str, shifts: List[Shift]) -> None:
        """シフト一括保存"""
        path = f"{self.base_path}/shift_{month_str}.csv"
        
        with open(path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'staff_id', 'date', 'start', 'end', 'position']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for shift in shifts:
                writer.writerow({
                    'id': shift.id,
                    'staff_id': shift.staff_id,
                    'date': shift.date.strftime('%Y-%m-%d'),
                    'start': shift.start_time.strftime('%H:%M'),
                    'end': shift.end_time.strftime('%H:%M'),
                    'position': shift.position
                })
    
    def delete(self, shift_id: int, year: int, month: int) -> bool:
        """シフト削除"""
        shifts = self.find_by_month(year, month)
        original_count = len(shifts)
        shifts = [s for s in shifts if s.id != shift_id]
        
        if len(shifts) < original_count:
            month_str = f"{year:04d}-{month:02d}"
            self.save_all(month_str, shifts)
            return True
        
        return False
```

**ポイント:**
- CSV操作はここだけ
- 他のレイヤーはこのクラスを使う
- SQL化する時もこのクラスの中身を変えるだけ

---

### Layer 4: Validation（検証層）

**役割**: 入力データのチェック  
**場所**: `validators/`

```python
# validators/shift_validator.py
from typing import Tuple, List
from models.shift import Shift
from datetime import datetime, time

class ShiftValidator:
    """シフトバリデーション"""
    
    def validate_shift(self, shift: Shift) -> Tuple[bool, List[str]]:
        """シフトデータの妥当性チェック"""
        errors = []
        
        # 必須項目チェック
        if not shift.staff_id:
            errors.append("スタッフIDは必須です")
        
        if not shift.date:
            errors.append("日付は必須です")
        
        if not shift.start_time or not shift.end_time:
            errors.append("開始時刻と終了時刻は必須です")
        
        # 時刻の妥当性チェック
        if shift.start_time and shift.end_time:
            if shift.start_time >= shift.end_time:
                errors.append("終了時刻は開始時刻より後にしてください")
        
        # 勤務時間の上限チェック
        if shift.start_time and shift.end_time:
            duration = shift.duration_hours()
            if duration > 12:
                errors.append("勤務時間は12時間以内にしてください")
            if duration < 1:
                errors.append("勤務時間は1時間以上にしてください")
        
        # 日付の妥当性チェック
        if shift.date:
            # 過去の日付はNG
            if shift.date < datetime.now().date():
                errors.append("過去の日付は登録できません")
            
            # 1年以上先はNG
            max_date = datetime.now().date().replace(year=datetime.now().year + 1)
            if shift.date > max_date:
                errors.append("1年以上先の日付は登録できません")
        
        return len(errors) == 0, errors
    
    def validate_month(self, year: int, month: int) -> Tuple[bool, str]:
        """月の妥当性チェック"""
        if not (1 <= month <= 12):
            return False, "月は1-12の範囲で指定してください"
        
        if year < 2020 or year > 2030:
            return False, "年は2020-2030の範囲で指定してください"
        
        return True, ""
    
    def validate_time_format(self, time_str: str) -> Tuple[bool, str]:
        """時刻フォーマットのチェック"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return True, ""
        except ValueError:
            return False, "時刻はHH:MM形式で入力してください"
```

**ポイント:**
- ビジネスルールのチェック
- エラーメッセージを返す
- 他のレイヤーで使える

---

### Layer 5: Service（サービス層）

**役割**: ビジネスロジック（計算・判断・処理）  
**場所**: `services/`

```python
# services/shift_service.py
from typing import List, Dict
from models.shift import Shift
from data_access.shift_repository import ShiftRepository
from data_access.staff_repository import StaffRepository
from validators.shift_validator import ShiftValidator

class ShiftService:
    """シフト関連のビジネスロジック"""
    
    def __init__(self):
        self.shift_repo = ShiftRepository()
        self.staff_repo = StaffRepository()
        self.validator = ShiftValidator()
    
    def get_monthly_shifts(self, year: int, month: int) -> List[Shift]:
        """月別シフト取得"""
        # バリデーション
        valid, error = self.validator.validate_month(year, month)
        if not valid:
            raise ValueError(error)
        
        # データ取得
        return self.shift_repo.find_by_month(year, month)
    
    def create_shift(self, shift: Shift) -> Shift:
        """シフト作成"""
        # バリデーション
        valid, errors = self.validator.validate_shift(shift)
        if not valid:
            raise ValueError(f"バリデーションエラー: {', '.join(errors)}")
        
        # 重複チェック
        existing = self.shift_repo.find_by_staff(
            shift.staff_id, 
            shift.date.year, 
            shift.date.month
        )
        
        for existing_shift in existing:
            if existing_shift.date == shift.date:
                if self._is_time_overlap(existing_shift, shift):
                    raise ValueError("時間が重複しています")
        
        # 保存
        self.shift_repo.save(shift)
        return shift
    
    def calculate_monthly_hours(self, staff_id: str, year: int, month: int) -> float:
        """月間勤務時間を計算"""
        shifts = self.shift_repo.find_by_staff(staff_id, year, month)
        total_hours = sum(shift.duration_hours() for shift in shifts)
        return round(total_hours, 2)
    
    def calculate_monthly_salary(self, staff_id: str, year: int, month: int) -> int:
        """月間給与を計算"""
        # スタッフ情報取得
        staff = self.staff_repo.find_by_id(staff_id)
        if not staff:
            raise ValueError("スタッフが見つかりません")
        
        # 勤務時間取得
        total_hours = self.calculate_monthly_hours(staff_id, year, month)
        
        # 給与計算
        salary = int(total_hours * staff.hourly_wage)
        return salary
    
    def get_daily_staffing(self, year: int, month: int) -> Dict[str, List[Shift]]:
        """日別人員配置を取得"""
        shifts = self.shift_repo.find_by_month(year, month)
        
        # 日付ごとにグループ化
        daily_shifts = {}
        for shift in shifts:
            date_str = shift.date.strftime('%Y-%m-%d')
            if date_str not in daily_shifts:
                daily_shifts[date_str] = []
            daily_shifts[date_str].append(shift)
        
        return daily_shifts
    
    def check_understaffed_days(self, year: int, month: int, min_staff: int = 3) -> List[str]:
        """人員不足の日をチェック"""
        daily_shifts = self.get_daily_staffing(year, month)
        
        understaffed = []
        for date_str, shifts in daily_shifts.items():
            if len(shifts) < min_staff:
                understaffed.append(date_str)
        
        return understaffed
    
    def _is_time_overlap(self, shift1: Shift, shift2: Shift) -> bool:
        """時間が重複しているかチェック"""
        return not (shift1.end_time <= shift2.start_time or 
                   shift2.end_time <= shift1.start_time)
```

**ポイント:**
- アプリの「脳」の部分
- 複雑な計算・判断をここでやる
- Repository を使ってデータ取得
- Validator を使ってチェック

---

### Layer 6: Presenter（整形層）

**役割**: データを表示用に整形  
**場所**: `presenters/`

```python
# presenters/shift_presenter.py
from typing import List, Dict
from models.shift import Shift
from models.staff import Staff

class ShiftPresenter:
    """シフトデータを表示用に整形"""
    
    def format_for_calendar(self, shifts: List[Shift], staff_list: List[Staff]) -> Dict:
        """カレンダー表示用に整形"""
        # スタッフIDから名前への変換マップ
        staff_map = {s.account: s for s in staff_list}
        
        # 日付ごとにグループ化
        calendar_data = {}
        for shift in shifts:
            date_str = shift.date.strftime('%Y-%m-%d')
            
            if date_str not in calendar_data:
                calendar_data[date_str] = {
                    'date': shift.date.strftime('%m/%d'),
                    'weekday': self._get_weekday_jp(shift.date),
                    'shifts': []
                }
            
            # スタッフ情報を追加
            staff = staff_map.get(shift.staff_id)
            calendar_data[date_str]['shifts'].append({
                'staff_name': staff.full_name if staff else '不明',
                'time_range': f"{shift.start_time.strftime('%H:%M')}-{shift.end_time.strftime('%H:%M')}",
                'duration': f"{shift.duration_hours():.1f}h",
                'position': shift.position
            })
        
        return calendar_data
    
    def format_for_staff_table(self, shifts: List[Shift], staff_list: List[Staff]) -> List[Dict]:
        """スタッフ別テーブル表示用に整形"""
        result = []
        
        for staff in staff_list:
            # このスタッフのシフトを抽出
            staff_shifts = [s for s in shifts if s.staff_id == staff.account]
            
            # 合計時間を計算
            total_hours = sum(s.duration_hours() for s in staff_shifts)
            
            # 給与を計算
            salary = int(total_hours * staff.hourly_wage)
            
            result.append({
                'staff_id': staff.account,
                'staff_name': staff.full_name,
                'position': staff.position,
                'shift_count': len(staff_shifts),
                'total_hours': f"{total_hours:.1f}h",
                'estimated_salary': f"¥{salary:,}",
                'shifts': [
                    {
                        'date': s.date.strftime('%m/%d'),
                        'time': f"{s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')}",
                        'hours': f"{s.duration_hours():.1f}h"
                    }
                    for s in sorted(staff_shifts, key=lambda x: x.date)
                ]
            })
        
        return sorted(result, key=lambda x: x['staff_name'])
    
    def format_for_timeline(self, shifts: List[Shift], date_str: str) -> Dict:
        """タイムライン表示用に整形"""
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_shifts = [s for s in shifts if s.date == target_date]
        
        # 時間軸の作成（8:00-22:00）
        timeline = {
            'date': target_date.strftime('%Y年%m月%d日'),
            'weekday': self._get_weekday_jp(target_date),
            'hours': list(range(8, 23)),
            'staff_timelines': []
        }
        
        for shift in day_shifts:
            timeline['staff_timelines'].append({
                'staff_name': shift.staff_id,  # TODO: 名前に変換
                'start_hour': shift.start_time.hour,
                'end_hour': shift.end_time.hour,
                'duration': shift.duration_hours(),
                'position': shift.position
            })
        
        return timeline
    
    def _get_weekday_jp(self, date) -> str:
        """日本語の曜日を取得"""
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        return weekdays[date.weekday()]
```

**ポイント:**
- 表示用の整形だけをやる
- ビジネスロジックは入れない
- テンプレートで使いやすい形式に変換

---

### Layer 7: Presentation（表示層）

**役割**: HTTPリクエストを受け取り、レスポンスを返す  
**場所**: `routes/`

```python
# routes/admin/shift_manage.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from core.decorators import admin_required
from services.shift_service import ShiftService
from services.staff_service import StaffService
from presenters.shift_presenter import ShiftPresenter
from validators.shift_validator import ShiftValidator

shift_admin_bp = Blueprint('shift_admin', __name__, url_prefix='/admin/shift')

@shift_admin_bp.route('/view/<int:year>/<int:month>')
@admin_required
def view_monthly_shifts(year, month):
    """月別シフト表示"""
    try:
        # サービス層からデータ取得
        shift_service = ShiftService()
        staff_service = StaffService()
        
        shifts = shift_service.get_monthly_shifts(year, month)
        staff_list = staff_service.get_all_staff()
        
        # プレゼンター層で整形
        presenter = ShiftPresenter()
        calendar_data = presenter.format_for_calendar(shifts, staff_list)
        
        # 表示
        return render_template('admin/shift_calendar.html',
                             year=year,
                             month=month,
                             calendar_data=calendar_data)
    
    except ValueError as e:
        flash(f'エラー: {str(e)}', 'error')
        return redirect(url_for('shift_admin.select_month'))

@shift_admin_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_shift():
    """シフト作成"""
    if request.method == 'POST':
        try:
            # フォームデータをモデルに変換
            shift = Shift(
                id=None,  # 新規作成時はNone
                staff_id=request.form['staff_id'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                start_time=datetime.strptime(request.form['start'], '%H:%M').time(),
                end_time=datetime.strptime(request.form['end'], '%H:%M').time(),
                position=request.form['position']
            )
            
            # サービス層で作成（バリデーション込み）
            shift_service = ShiftService()
            created_shift = shift_service.create_shift(shift)
            
            flash('シフトを作成しました', 'success')
            return redirect(url_for('shift_admin.view_monthly_shifts',
                                   year=created_shift.date.year,
                                   month=created_shift.date.month))
        
        except ValueError as e:
            flash(f'エラー: {str(e)}', 'error')
    
    # GET: フォーム表示
    staff_service = StaffService()
    staff_list = staff_service.get_all_staff()
    
    return render_template('admin/shift_create.html',
                         staff_list=staff_list)
```

**ポイント:**
- リクエスト処理だけをやる
- 複雑なロジックは Service 層に任せる
- データ整形は Presenter 層に任せる
- **このファイルはシンプルで短い（50-100行）**

---

## 🔄 データの流れ（実例）

### 例: 管理者がシフトを作成する

```
1. ユーザーがフォーム送信
   POST /admin/shift/create
   ↓
2. Presentation層（routes/admin/shift_manage.py）
   - フォームデータを受け取る
   - Shiftモデルに変換
   ↓
3. Service層（services/shift_service.py）
   - create_shift() を呼ぶ
   ↓
4. Validation層（validators/shift_validator.py）
   - データの妥当性チェック
   - エラーがあれば例外を投げる
   ↓
5. Service層（続き）
   - 重複チェックなどのビジネスロジック
   ↓
6. Repository層（data_access/shift_repository.py）
   - save() を呼ぶ
   ↓
7. Data Source層（data/shift/shift_2025-12.csv）
   - CSVファイルに書き込み
   ↓
8. Repository層
   - 保存完了を返す
   ↓
9. Service層
   - Shiftオブジェクトを返す
   ↓
10. Presentation層
   - 成功メッセージを表示
   - リダイレクト
```

---

## 📊 Before / After 比較

### Before（全部1ファイル）

```python
# routes/admin.py（600行）
@admin_bp.route('/shift/create', methods=['POST'])
def create_shift():
    # データ取得
    staff_id = request.form['staff_id']
    date = request.form['date']
    start = request.form['start']
    end = request.form['end']
    
    # バリデーション
    if not date:
        return "日付は必須です"
    if start >= end:
        return "終了時刻は開始時刻より後にしてください"
    
    # 重複チェック
    existing = pd.read_csv(f'data/shift/shift_{month}.csv')
    for _, row in existing.iterrows():
        if row['staff_id'] == staff_id and row['date'] == date:
            if not (row['end'] <= start or end <= row['start']):
                return "時間が重複しています"
    
    # 保存
    new_shift = pd.DataFrame([{
        'staff_id': staff_id,
        'date': date,
        'start': start,
        'end': end
    }])
    existing = pd.concat([existing, new_shift])
    existing.to_csv(f'data/shift/shift_{month}.csv', index=False)
    
    return redirect('/admin/shift/view')
```

**問題:**
- ❌ 100行以上の長い関数
- ❌ CSV操作が直接書かれている
- ❌ バリデーションロジックが埋もれている
- ❌ 再利用できない
- ❌ テストが書けない

### After（レイヤー分け）

```python
# routes/admin/shift_manage.py（50行）
@shift_admin_bp.route('/create', methods=['POST'])
@admin_required
def create_shift():
    try:
        # モデルに変換
        shift = Shift(
            id=None,
            staff_id=request.form['staff_id'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form['start'], '%H:%M').time(),
            end_time=datetime.strptime(request.form['end'], '%H:%M').time(),
            position=request.form['position']
        )
        
        # サービス層に任せる
        shift_service = ShiftService()
        shift_service.create_shift(shift)
        
        flash('作成しました', 'success')
        return redirect(url_for('shift_admin.view'))
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('shift_admin.create_form'))
```

**メリット:**
- ✅ 短くて読みやすい（20行）
- ✅ 責任が明確
- ✅ エラーハンドリングがシンプル
- ✅ 各レイヤーを個別にテストできる

---

## 🎯 まとめ

### 7つのレイヤー（覚え方）

```
上から下に流れる:
7. Presentation    → リクエストを受け取る
6. Presenter       → 表示用に整形
5. Service         → ビジネスロジック
4. Validation      → チェック
3. Repository      → データ取得・保存
2. Data Source     → 実際のデータ
1. Models          → データ構造の定義
```

### レイヤー分けのルール

1. **上位レイヤーは下位レイヤーを使える**
   - Presentation → Service ✅
   - Service → Repository ✅

2. **下位レイヤーは上位レイヤーを使えない**
   - Repository → Service ❌
   - Service → Presentation ❌

3. **同じレイヤー同士は使える**
   - Service → 別の Service ✅

4. **レイヤーを飛ばさない**
   - Presentation → Service → Repository ✅
   - Presentation → Repository（直接） ❌

### メリットまとめ

- ✅ **わかりやすい**: 各ファイルの責任が明確
- ✅ **変更しやすい**: 影響範囲が限定的
- ✅ **テストしやすい**: 各レイヤーを個別にテスト
- ✅ **再利用できる**: Service や Repository を複数箇所で使える
- ✅ **SQL化が楽**: Repository層だけ変更すればOK

---

次のステップ: 実際にレイヤー分けを実装してみましょう！

