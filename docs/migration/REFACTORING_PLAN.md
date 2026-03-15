# アプリ整理計画（リファクタリング）

**目的**: わかりやすく、管理しやすいコードにする  
**方針**: Repository パターンとか難しいことは後回し。まずは「見ただけでわかる構造」に

---

## 🎯 改善したいこと（あなたの要望）

1. ✅ **機能別・動作段階でファイルを分けたい**
2. ✅ **権限管理を明確にしたい**（管理者専用、ログイン必須、公開）
3. ✅ **アカウント管理をやりやすくしたい**
4. ✅ **アプリの動作を理解しやすくしたい**

---

## 📁 新しいフォルダ構成（提案）

### Before（現状）

```
shift_auth_system_prototype_gcp/
├── app.py
├── routes/                    # 全部ここに混在（13ファイル）
│   ├── auth.py
│   ├── admin.py
│   ├── staff.py
│   ├── shift_public.py
│   ├── manual.py
│   ├── stock.py
│   ├── manual_memo.py
│   ├── order_memo.py
│   ├── notice_memo.py
│   ├── daily_shift.py
│   ├── monthly_shift.py
│   ├── monthly_shift_chart.py
│   └── exclude_api.py
├── utils/                     # ユーティリティ（9ファイル）
│   ├── csv_utils.py
│   ├── csv_handler.py
│   ├── data_utils.py
│   ├── staff_utils.py
│   ├── date_utils.py
│   ├── graph_utils.py
│   ├── shift_utils.py
│   ├── lock_utils.py
│   └── exclude_time_utils.py
└── data/                      # データフォルダ
```

**問題点:**
- routes/ に13ファイルが混在
- 権限レベルがファイル名からわからない
- 機能ごとの分類が不明確

### After（提案）

```
shift_auth_system_prototype_gcp/
├── app.py                              # メインアプリ（シンプルに）
│
├── core/                               # 🔵 コア機能（認証・共通）
│   ├── __init__.py
│   ├── auth.py                         # 認証（ログイン/ログアウト）
│   ├── decorators.py                   # 権限チェック用デコレーター
│   └── account_manager.py              # アカウント管理（新規作成）
│
├── routes/                             # 🎯 ルーティング（権限別に整理）
│   │
│   ├── public/                         # ⚪ 誰でも見れる
│   │   ├── __init__.py
│   │   ├── home.py                     # トップページ
│   │   ├── shift_view.py               # シフト閲覧
│   │   ├── info.py                     # 業務情報（メモ・マニュアル閲覧）
│   │   └── stock_view.py               # 在庫閲覧
│   │
│   ├── staff/                          # 🟢 スタッフ専用
│   │   ├── __init__.py
│   │   ├── home.py                     # スタッフホーム
│   │   ├── shift_request.py            # シフト希望提出
│   │   └── my_shift.py                 # 自分のシフト確認
│   │
│   └── admin/                          # 🔴 管理者専用
│       ├── __init__.py
│       ├── home.py                     # 管理者ホーム
│       ├── shift_manage.py             # シフト管理
│       ├── staff_manage.py             # スタッフ管理
│       ├── account_manage.py           # アカウント管理（新規）
│       ├── manual_manage.py            # マニュアル管理
│       └── stock_manage.py             # 在庫管理
│
├── services/                           # 📊 ビジネスロジック層（新規）
│   ├── __init__.py
│   ├── shift_service.py                # シフト関連の処理
│   ├── staff_service.py                # スタッフ関連の処理
│   ├── account_service.py              # アカウント関連の処理
│   └── graph_service.py                # グラフ生成
│
├── data_access/                        # 💾 データアクセス層（新規）
│   ├── __init__.py
│   ├── csv_handler.py                  # CSV読み書き統一
│   ├── shift_data.py                   # シフトデータ
│   ├── staff_data.py                   # スタッフデータ
│   └── auth_data.py                    # 認証データ
│
├── utils/                              # 🔧 ユーティリティ
│   ├── __init__.py
│   ├── date_helpers.py                 # 日付処理
│   ├── validators.py                   # バリデーション
│   └── formatters.py                   # フォーマット
│
├── data/                               # 📁 データ（変更なし）
└── templates/                          # 📄 HTML（変更なし）
```

---

## 🔐 権限管理の統一

### 現状の問題

```python
# routes/admin.py
if session.get("role") != "admin":  # ← バラバラ
    return redirect(url_for("auth.login"))

# routes/manual.py
if 'account' not in session or session.get('account') != 'admin':  # ← 別の書き方
    return redirect(url_for('auth.login'))
```

### 改善後（デコレーターで統一）

```python
# core/decorators.py（新規作成）
from functools import wraps
from flask import session, redirect, url_for

def login_required(func):
    """ログイン必須（スタッフ以上）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'account' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    """管理者専用"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

def staff_or_admin(func):
    """スタッフまたは管理者"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('role') not in ['staff', 'admin']:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper
```

### 使い方

```python
# routes/admin/shift_manage.py
from core.decorators import admin_required

@admin_bp.route('/shift/edit')
@admin_required  # ← これだけでOK！
def edit_shift():
    # 管理者のみアクセス可能
    ...

# routes/staff/shift_request.py
from core.decorators import login_required

@staff_bp.route('/shift/request')
@login_required  # ← スタッフ以上
def request_shift():
    ...
```

**メリット:**
- ✅ コードを見ただけで権限がわかる
- ✅ 書き方が統一される
- ✅ 変更が一箇所で済む

---

## 👤 アカウント管理の改善

### 現状の問題

- アカウント追加・削除の機能がない
- auth.csv を直接編集する必要がある
- パスワード変更ができない

### 改善案: アカウント管理画面を追加

```python
# core/account_manager.py（新規作成）
from werkzeug.security import generate_password_hash
import csv

class AccountManager:
    """アカウント管理クラス"""
    
    def __init__(self):
        self.auth_file = 'auth.csv'
        self.staff_file = 'staff.csv'
    
    def create_account(self, account, password, last_name, first_name, role='staff'):
        """新規アカウント作成"""
        password_hash = generate_password_hash(password)
        
        # auth.csv に追加
        with open(self.auth_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([account, last_name, first_name, role, 0, password_hash])
        
        return True
    
    def delete_account(self, account):
        """アカウント削除"""
        # auth.csv から削除
        ...
    
    def change_password(self, account, new_password):
        """パスワード変更"""
        password_hash = generate_password_hash(new_password)
        ...
    
    def list_all_accounts(self):
        """全アカウント一覧"""
        ...
    
    def update_role(self, account, new_role):
        """権限変更"""
        ...
```

### 管理者画面を追加

```python
# routes/admin/account_manage.py（新規作成）
from flask import Blueprint, render_template, request, redirect
from core.decorators import admin_required
from core.account_manager import AccountManager

account_admin_bp = Blueprint('account_admin', __name__, url_prefix='/admin/accounts')

@account_admin_bp.route('/')
@admin_required
def list_accounts():
    """アカウント一覧"""
    manager = AccountManager()
    accounts = manager.list_all_accounts()
    return render_template('admin/account_list.html', accounts=accounts)

@account_admin_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_account():
    """アカウント作成"""
    if request.method == 'POST':
        manager = AccountManager()
        manager.create_account(
            account=request.form['account'],
            password=request.form['password'],
            last_name=request.form['last_name'],
            first_name=request.form['first_name'],
            role=request.form['role']
        )
        return redirect('/admin/accounts')
    
    return render_template('admin/account_create.html')

@account_admin_bp.route('/delete/<account>', methods=['POST'])
@admin_required
def delete_account(account):
    """アカウント削除"""
    manager = AccountManager()
    manager.delete_account(account)
    return redirect('/admin/accounts')

@account_admin_bp.route('/change_password/<account>', methods=['GET', 'POST'])
@admin_required
def change_password(account):
    """パスワード変更"""
    if request.method == 'POST':
        manager = AccountManager()
        manager.change_password(account, request.form['new_password'])
        return redirect('/admin/accounts')
    
    return render_template('admin/change_password.html', account=account)
```

---

## 📊 データアクセス層の統一

### 現状の問題

```python
# routes/ で直接CSV操作
import csv
with open('data/shift/shift_2025-12.csv') as f:
    ...

# utils/csv_utils.py
def load_shifts(month):
    ...

# utils/csv_handler.py
def load_shifts(month):  # ← 同じ名前の関数が複数！
    ...
```

### 改善後（data_access/ に統一）

```python
# data_access/shift_data.py
class ShiftData:
    """シフトデータアクセス"""
    
    def __init__(self):
        self.base_path = 'data/shift'
    
    def get_by_month(self, month):
        """月別シフト取得"""
        path = f"{self.base_path}/shift_{month}.csv"
        return self._read_csv(path)
    
    def save(self, month, shifts):
        """シフト保存"""
        path = f"{self.base_path}/shift_{month}.csv"
        self._write_csv(path, shifts)
    
    def _read_csv(self, path):
        """CSV読み込み（内部メソッド）"""
        ...
    
    def _write_csv(self, path, data):
        """CSV書き込み（内部メソッド）"""
        ...

# data_access/staff_data.py
class StaffData:
    """スタッフデータアクセス"""
    ...

# data_access/auth_data.py
class AuthData:
    """認証データアクセス"""
    ...
```

### 使い方

```python
# routes/admin/shift_manage.py
from data_access.shift_data import ShiftData

@admin_bp.route('/shift/edit')
@admin_required
def edit_shift():
    shift_data = ShiftData()
    shifts = shift_data.get_by_month('2025-12')  # ← シンプル！
    ...
```

---

## 🎯 移行ステップ（段階的に）

### Phase 1: 権限管理の統一（1-2日）

1. `core/decorators.py` 作成
2. 全ての routes/ で `@admin_required` などを使うように変更
3. テスト

**変更ファイル数**: 約13ファイル  
**難易度**: ⭐⭐☆☆☆（簡単）

### Phase 2: アカウント管理機能追加（2-3日）

1. `core/account_manager.py` 作成
2. `routes/admin/account_manage.py` 作成
3. 管理画面テンプレート作成
4. テスト

**変更ファイル数**: 約5ファイル（新規）  
**難易度**: ⭐⭐⭐☆☆（普通）

### Phase 3: フォルダ再構成（3-5日）

1. routes/ を public/, staff/, admin/ に分割
2. ファイル移動とimport修正
3. テスト

**変更ファイル数**: 約20ファイル  
**難易度**: ⭐⭐⭐⭐☆（やや難しい）

### Phase 4: データアクセス層統一（5-7日）

1. `data_access/` フォルダ作成
2. CSV操作を統一
3. routes/ から直接CSV操作を削除
4. テスト

**変更ファイル数**: 約30ファイル  
**難易度**: ⭐⭐⭐⭐⭐（難しい）

---

## 📋 優先度

### 今すぐやるべき（効果大、工数小）

1. ✅ **Phase 1: 権限管理の統一**
   - 効果: コードがわかりやすくなる
   - 工数: 1-2日
   - リスク: 低

2. ✅ **Phase 2: アカウント管理機能**
   - 効果: 管理が楽になる
   - 工数: 2-3日
   - リスク: 低

### 余裕があればやる（効果中、工数大）

3. ⚠️ **Phase 3: フォルダ再構成**
   - 効果: 構造がわかりやすくなる
   - 工数: 3-5日
   - リスク: 中（import修正が多い）

### SQL化と同時にやる（効果大、工数大）

4. 🔄 **Phase 4: データアクセス層統一**
   - 効果: SQL化が楽になる
   - 工数: 5-7日
   - リスク: 高（大規模変更）

---

## 🎯 推奨アプローチ

### まずはこれだけ！

```
1. Phase 1（権限管理の統一）
   ↓
2. Phase 2（アカウント管理機能）
   ↓
3. ここでSQL化を検討
   ↓
4. SQL化と同時に Phase 4（データアクセス層統一）
```

**Phase 3（フォルダ再構成）は省略してもOK**  
→ Phase 1, 2 だけでもかなり改善される

---

## 📝 次のステップ

1. **このプランを確認する**
2. **どこから始めるか決める**
3. **実装開始**

どうしますか？

