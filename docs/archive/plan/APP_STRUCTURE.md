# アプリの構造とフロー完全ガイド

**最終更新**: 2025-12-06  
**目的**: このアプリがどう動いているかを完全に理解する

---

## 🎯 このアプリは何をするアプリ？

**カフェのシフト管理＋業務情報共有アプリ**

- スタッフがシフト希望を提出
- 管理者がシフトを作成・編集
- 全員がシフトを閲覧
- マニュアル、メモ、在庫管理などの業務情報を共有

---

## 👥 ユーザーの種類（3種類）

```
1. 👤 一般訪問者（ログインなし）
   → 限定的な情報のみ閲覧可能

2. 👔 スタッフ（ログイン必要）
   → シフト希望提出、自分のシフト確認

3. 👑 管理者（admin）
   → 全ての機能が使える
```

---

## 🔐 認証の仕組み

### ログインの流れ

```
1. ユーザーが /login にアクセス
2. アカウント名とパスワードを入力
3. auth.csv と照合
4. 成功したら session に情報を保存:
   - account (アカウント名)
   - name (表示名)
   - role ("admin" または "staff")
5. role に応じてリダイレクト:
   - admin → /admin/home
   - staff → /staff/home
```

### 認証チェックのコード

```python
# routes/auth.py (24-37行目)
if account in auth_data and check_password_hash(...):
    session.update({
        "account": account,
        "role": auth_data[account]["role"],  # ← "admin" or "staff"
        "name": "..."
    })
    
    if session["role"] == "admin":
        return redirect(url_for("admin.admin_home"))  # 管理者ホーム
    else:
        return redirect(url_for("staff.staff_home"))  # スタッフホーム
```

---

## 📁 13個の機能モジュール（Blueprint）

### 起動ファイル: `app.py`

全ての機能モジュールを読み込んで起動する

```python
from routes.auth import auth_blueprint          # 認証
from routes.admin import admin_blueprint        # 管理者機能
from routes.staff import staff_blueprint        # スタッフ機能
from routes.stock import stock_bp               # 在庫管理
from routes.manual import manual_bp             # マニュアル
from routes.shift_public import shift_public_bp # シフト閲覧（公開）
from routes.manual_memo import kitchen_memo_bp  # 仕込みメモ
from routes.order_memo import order_memo_bp     # 発注メモ
from routes.notice_memo import notice_memo_bp   # お知らせメモ
from routes.daily_shift import daily_shift_bp   # 日別シフト
from routes.exclude_api import exclude_api      # 除外時間API
from routes.monthly_shift import monthly_shift_bp # 月別シフト

# 合計: 13個のBlueprint
```

---

## 🗺️ 全エンドポイントマップ（権限別）

### ⚪ レベル0: 誰でも見れる（ログイン不要）

| URL | ファイル | 機能 |
|-----|---------|------|
| `/` | `routes/auth.py` | トップページ |
| `/login` | `routes/auth.py` | ログイン画面 |
| `/shift/view` | `routes/shift_public.py` | シフト表（閲覧専用）|
| `/shift/graph/readonly` | `routes/shift_public.py` | シフト人数グラフ |
| `/stock` | `routes/stock.py` | ドリンク管理 |
| `/stock/alert` | `routes/stock.py` | 在庫アラート |
| `/manual/view` | `routes/manual.py` | マニュアル閲覧 |
| `/manual/memo/kitchen/` | `routes/manual_memo.py` | 仕込みメモ |
| `/manual/memo/order/` | `routes/order_memo.py` | 発注メモ |
| `/manual/memo/notice/` | `routes/notice_memo.py` | お知らせメモ |
| `/monthly_shift/<month>` | `routes/monthly_shift.py` | 月別シフト表 |

### 🟢 レベル1: スタッフ（ログイン必要）

| URL | ファイル | 機能 |
|-----|---------|------|
| `/staff/home` | `routes/staff.py` | スタッフホーム |
| `/staff/submit` | `routes/staff.py` | シフト希望提出 |
| `/staff/view` | `routes/staff.py` | 自分のシフト確認 |
| `/staff/graph` | `routes/staff.py` | 自分の勤務グラフ |

### 🔴 レベル2: 管理者専用（admin）

| URL | ファイル | 機能 |
|-----|---------|------|
| `/admin/home` | `routes/admin.py` | 管理者ホーム |
| `/admin/edit` | `routes/admin.py` | シフト編集 |
| `/admin/import` | `routes/admin.py` | シフト希望インポート |
| `/admin/export` | `routes/admin.py` | シフトエクスポート |
| `/admin/panel` | `routes/admin.py` | スタッフ管理パネル |
| `/admin/add_staff` | `routes/admin.py` | スタッフ追加 |
| `/manual/upload` | `routes/manual.py` | マニュアルアップロード |
| `/manual/upload_image` | `routes/manual.py` | 画像アップロード |
| `/exclude/api/...` | `routes/exclude_api.py` | 除外時間API |
| `/daily_shift/...` | `routes/daily_shift.py` | 日別シフト管理 |

---

## 🔄 実際のユーザーフロー

### シナリオ1: 一般訪問者（バイトの友達など）

```
1. http://localhost:5050/ にアクセス
   ↓
2. トップページ表示（public_home.html）
   ↓
3. 「シフト表」をクリック
   ↓
4. /shift/view で全員のシフト表を閲覧（ログイン不要）
```

### シナリオ2: スタッフがシフト希望を提出

```
1. /login にアクセス
   ↓
2. アカウント名とパスワード入力
   ↓
3. 認証成功 → /staff/home にリダイレクト
   ↓
4. 「シフト希望提出」をクリック
   ↓
5. /staff/submit で希望シフトを入力
   ↓
6. 保存 → data/shift_request/shift_request_YYYY-MM.csv に保存
```

### シナリオ3: 管理者がシフトを作成

```
1. /login にアクセス
   ↓
2. adminアカウントでログイン
   ↓
3. 認証成功 → /admin/home にリダイレクト
   ↓
4. 「シフト編集」をクリック
   ↓
5. /admin/edit で月を選択
   ↓
6. スタッフ希望をインポート（/admin/import）
   ↓
7. シフトを編集・調整
   ↓
8. 保存 → data/shift/shift_YYYY-MM.csv に保存
   ↓
9. 全スタッフが /shift/view で確認可能に
```

---

## 📂 データの保存場所

### CSV ファイル構造

```
data/
├── shift/                          # 確定シフト
│   └── shift_2025-12.csv          # 月別
│
├── shift_request/                  # シフト希望
│   └── shift_request_2025-12.csv
│
├── imported_requests/              # インポート済み希望
│   └── imported_requests_2025-12.csv
│
├── notes/                          # メモ
│   └── notes_2025-12.csv
│
├── exclude_time/                   # 除外時間
│   └── exclude_time_2025-07.csv
│
├── manuals/                        # マニュアル
│   ├── categories.csv
│   ├── Kitchen/
│   ├── Top/
│   └── Others/
│
├── stock.csv                       # 在庫データ
└── stock_alert.csv                 # 在庫アラート

auth.csv                            # アカウント情報
staff.csv                           # スタッフ情報
```

---

## 🧩 各ファイルの役割

### コア（必須）

| ファイル | 役割 | 重要度 |
|---------|------|--------|
| `app.py` | アプリ起動、全Blueprint登録 | ⭐⭐⭐⭐⭐ |
| `routes/auth.py` | 認証、ログイン/ログアウト | ⭐⭐⭐⭐⭐ |
| `routes/admin.py` | 管理者機能（シフト編集など） | ⭐⭐⭐⭐⭐ |
| `routes/staff.py` | スタッフ機能（希望提出など） | ⭐⭐⭐⭐⭐ |
| `routes/shift_public.py` | シフト閲覧（公開） | ⭐⭐⭐⭐⭐ |

### 業務支援機能

| ファイル | 役割 | 重要度 |
|---------|------|--------|
| `routes/manual.py` | マニュアル管理 | ⭐⭐⭐ |
| `routes/manual_memo.py` | 仕込みメモ | ⭐⭐⭐ |
| `routes/order_memo.py` | 発注メモ | ⭐⭐⭐ |
| `routes/notice_memo.py` | お知らせメモ | ⭐⭐⭐ |
| `routes/stock.py` | 在庫管理 | ⭐⭐ |

### サポート機能

| ファイル | 役割 | 重要度 |
|---------|------|--------|
| `routes/daily_shift.py` | 日別シフト表示 | ⭐⭐⭐⭐ |
| `routes/monthly_shift.py` | 月別シフト表示 | ⭐⭐⭐⭐ |
| `routes/exclude_api.py` | 除外時間API | ⭐⭐⭐ |

### ユーティリティ（裏方）

| ファイル | 役割 |
|---------|------|
| `utils/csv_utils.py` | CSV読み書き |
| `utils/csv_handler.py` | データ読み込み |
| `utils/staff_utils.py` | スタッフデータ処理 |
| `utils/date_utils.py` | 日付処理 |
| `utils/graph_utils.py` | グラフ生成 |
| `utils/shift_utils.py` | シフト計算 |

---

## 🔧 権限チェックの実装

### パターン1: session チェック（現在の実装）

```python
# routes/admin.py
@admin_blueprint.route("/admin/home")
def admin_home():
    if session.get("role") != "admin":  # ← 管理者チェック
        return redirect(url_for("auth.login"))
    
    # 管理者のみアクセス可能
    return render_template("admin_home.html", ...)
```

### パターン2: デコレーター（一部で使用）

```python
# routes/manual.py
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'account' not in session or session.get('account') != 'admin':
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

@manual_bp.route('/upload')
@login_required  # ← デコレーターで保護
def upload_manual():
    ...
```

---

## 📊 データの流れ

### シフト希望提出の例

```
1. スタッフがフォーム入力
   ↓ (POST /staff/submit)
2. routes/staff.py が受け取る
   ↓
3. utils/csv_utils.py の save_shift_requests() を呼ぶ
   ↓
4. data/shift_request/shift_request_YYYY-MM.csv に保存
   ↓
5. 管理者が /admin/import でインポート
   ↓
6. data/imported_requests/ にコピー
   ↓
7. 管理者が /admin/edit でシフト作成
   ↓
8. data/shift/shift_YYYY-MM.csv に保存
   ↓
9. 全員が /shift/view で閲覧可能
```

---

## 🎯 まとめ

### このアプリの核心

1. **認証**: auth.csv でアカウント管理、session で状態管理
2. **権限**: admin / staff / 一般訪問者の3レベル
3. **データ**: 全てCSVファイル（data/ フォルダ）
4. **構成**: 13個のBlueprint（機能モジュール）
5. **フロー**: スタッフ希望 → 管理者編集 → 全員閲覧

### 複雑に感じる理由

- ✅ **機能が多い**（13個のBlueprint、72エンドポイント）
- ✅ **ファイルが多い**（routes/ 13個、utils/ 9個）
- ⚠️ **命名が統一されていない**（admin_blueprint, stock_bp, shift_public_bp...）
- ⚠️ **権限チェックの方法がバラバラ**（session チェック、デコレーター）
- ⚠️ **データアクセスが散在**（routes/ でもCSV操作）

---

次のステップ: このアプリを**もっとわかりやすく整理**しましょう！

