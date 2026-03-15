# ログイン機能とデコレーター完全ガイド

**目的**: ログイン後のリダイレクトとデコレーターの仕組みを完全に理解する  
**最終更新**: 2025-12-06

---

## 🔐 Part 1: ログイン後のリダイレクト機能

### ❌ 誤解: 各ページに専用のログインページを作る？

```
【誤解のイメージ】

/admin/edit 用のログインページ → ログイン → /admin/edit
/staff/home 用のログインページ → ログイン → /staff/home
/admin/panel 用のログインページ → ログイン → /admin/panel

→ これは間違い！ログインページを何個も作る必要はない
```

### ✅ 正解: 1つのログインページで全て対応

```
【正しいイメージ】

1つのログインページ（/login）
+ nextパラメータ（URLに付ける情報）
= どのページからでも、ログイン後に元のページに戻れる
```

---

## 📝 nextパラメータとは？

### 仕組み

**nextパラメータ**: URLに「ログイン後に戻りたいページ」の情報を付ける

```
例:
/login?next=/admin/edit
        ↑
        この部分が「nextパラメータ」
```

### 動作フロー（図解）

```
シナリオ: ログインしていない状態で /admin/edit にアクセス

Step 1: ユーザーがアクセス
┌──────────────────────┐
│ ブラウザのURL欄      │
│ /admin/edit          │ ← アクセスしたいページ
└──────────────────────┘

Step 2: デコレーターが検知（後で説明）
┌──────────────────────────────────┐
│ @admin_required                  │
│ 「ログインしてないよ！」         │
│ → /login にリダイレクト          │
│   ただし、nextパラメータを追加   │
└──────────────────────────────────┘

Step 3: ログインページにリダイレクト
┌──────────────────────────────┐
│ ブラウザのURL欄              │
│ /login?next=/admin/edit      │ ← nextパラメータ付き
└──────────────────────────────┘

Step 4: ログインフォーム表示
┌──────────────────────────────┐
│ ログインページ               │
│ ┌────────────────────┐       │
│ │ アカウント名        │       │
│ │ [          ]        │       │
│ │ パスワード          │       │
│ │ [          ]        │       │
│ │ [ログイン]          │       │
│ └────────────────────┘       │
│                              │
│ (hidden field)               │
│ next=/admin/edit ← 保持される│
└──────────────────────────────┘

Step 5: ログイン成功
┌──────────────────────────────┐
│ auth.py の login() 関数       │
│ 「next パラメータある？」     │
│ → ある！: /admin/edit         │
│ → そこにリダイレクト          │
└──────────────────────────────┘

Step 6: 元のページに戻る！
┌──────────────────────┐
│ ブラウザのURL欄      │
│ /admin/edit          │ ← 元々アクセスしたかったページ
└──────────────────────┘
```

---

## 💻 実装コード（詳細版）

### 1. デコレーター（@admin_required）

```python
# core/decorators.py
from functools import wraps
from flask import session, redirect, url_for, request

def admin_required(func):
    """管理者専用ページを保護するデコレーター"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ログインチェック
        if session.get('role') != 'admin':
            # ログインしていない、または管理者じゃない
            # → ログインページにリダイレクト
            # 　 ただし、現在のURLを next パラメータとして渡す
            return redirect(url_for('auth.login', next=request.url))
        
        # ログインしている管理者
        # → 元の関数を実行
        return func(*args, **kwargs)
    
    return wrapper
```

**解説:**
```python
request.url
# 現在アクセスしようとしているURL
# 例: http://localhost:5050/admin/edit

url_for('auth.login', next=request.url)
# ログインページのURL + nextパラメータ
# 例: /login?next=http://localhost:5050/admin/edit
```

### 2. ログイン処理

```python
# routes/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash
from urllib.parse import urlparse, urljoin

auth_blueprint = Blueprint("auth", __name__)

def is_safe_url(target):
    """
    リダイレクト先が安全かチェック
    （外部サイトへのリダイレクトを防ぐ）
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    # nextパラメータを取得
    # GETパラメータ（URL） または POSTデータ（フォーム）から取得
    next_url = request.args.get('next') or request.form.get('next')
    
    if request.method == "POST":
        # フォーム送信時の処理
        account = request.form["account"]
        password = request.form["password"]
        auth_data = load_auth_data()

        # 認証チェック
        if account in auth_data and check_password_hash(auth_data[account]["password"], password):
            # ログイン成功！
            # sessionに情報を保存
            session.update({
                "account": account,
                "last_name": auth_data[account]["last_name"],
                "first_name": auth_data[account]["first_name"],
                "role": auth_data[account]["role"],
                "name": f"{auth_data[account]['last_name']} {auth_data[account]['first_name']}"
            })
            
            # nextパラメータがあるか確認
            if next_url and is_safe_url(next_url):
                # ある & 安全 → そこにリダイレクト
                return redirect(next_url)
            
            # nextパラメータがない → デフォルトのホームへ
            if session["role"] == "admin":
                return redirect(url_for("admin.admin_home"))
            else:
                return redirect(url_for("staff.staff_home"))
        else:
            # ログイン失敗
            error = "アカウント名またはパスワードが違います"
            # エラーメッセージと共にログインフォームを再表示
            # nextパラメータも保持
            return render_template("login.html", error=error, next=next_url)
    
    # GET: ログインフォーム表示
    # nextパラメータをテンプレートに渡す
    return render_template("login.html", next=next_url)
```

### 3. ログインフォーム（HTML）

```html
<!-- templates/login.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ログイン</title>
</head>
<body>
    <h2>ログイン</h2>
    
    {% if error %}
    <p style="color: red;">{{ error }}</p>
    {% endif %}
    
    <form method="POST" action="{{ url_for('auth.login') }}">
        <!-- nextパラメータをhiddenフィールドで保持 -->
        <!-- POSTリクエストでもnextの情報を送る -->
        {% if next %}
        <input type="hidden" name="next" value="{{ next }}">
        {% endif %}
        
        <div>
            <label>アカウント名:</label>
            <input type="text" name="account" required>
        </div>
        
        <div>
            <label>パスワード:</label>
            <input type="password" name="password" required>
        </div>
        
        <button type="submit">ログイン</button>
    </form>
</body>
</html>
```

**ポイント:**
- `<input type="hidden" name="next" value="{{ next }}">` で next の値を保持
- ユーザーには見えないが、POSTリクエストで送られる

### 4. 保護されたページ

```python
# routes/admin/shift_manage.py
from flask import Blueprint, render_template
from core.decorators import admin_required

shift_admin_bp = Blueprint('shift_admin', __name__, url_prefix='/admin/shift')

@shift_admin_bp.route('/edit')
@admin_required  # ← このデコレーターが保護する
def edit_shift():
    """シフト編集ページ（管理者専用）"""
    # この関数が実行される時点で、
    # ログイン済み & 管理者であることが保証されている
    return render_template('admin/shift_edit.html')
```

---

## 🎭 Part 2: デコレーターとは？

### デコレーターの基本

**デコレーター**: 関数を「装飾」して、機能を追加する仕組み

```python
# デコレーターなし
def hello():
    print("Hello!")

hello()  # → "Hello!" が表示される

# デコレーターあり
@admin_required  # ← これがデコレーター
def hello():
    print("Hello!")

hello()  # → まず @admin_required が実行される
        #    → ログインチェック
        #    → OKなら "Hello!" が表示される
```

### デコレーターの仕組み（詳細）

#### ステップ1: デコレーターなしの場合

```python
# routes/admin/home.py
def admin_home():
    # ログインチェック（毎回書く必要がある）
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    # 実際の処理
    return render_template('admin_home.html')
```

**問題点:**
- すべての管理者ページで同じコードを書く必要がある
- 書き忘れると、保護されないページができてしまう
- 変更したい時、すべてのページを修正する必要がある

#### ステップ2: デコレーターを使う

```python
# routes/admin/home.py
@admin_required  # ← この1行を追加するだけ
def admin_home():
    # ログインチェックのコードは不要！
    # 実際の処理だけを書く
    return render_template('admin_home.html')
```

**メリット:**
- ログインチェックのコードが1箇所（デコレーター）に集約
- 書き忘れが防げる
- 変更が簡単（デコレーターだけ修正すればOK）

---

## 🔍 デコレーターの動作を詳しく見る

### デコレーターの定義

```python
# core/decorators.py
from functools import wraps
from flask import session, redirect, url_for, request

def admin_required(func):
    """
    管理者専用デコレーター
    
    引数:
        func: 装飾される関数（例: admin_home関数）
    
    返り値:
        wrapper: funcをラップした新しい関数
    """
    
    @wraps(func)  # ← funcのメタデータ（名前など）を保持
    def wrapper(*args, **kwargs):
        """
        実際に実行される関数
        
        引数:
            *args: 元の関数の位置引数
            **kwargs: 元の関数のキーワード引数
        """
        
        # 【検知1】ログイン状態をチェック
        if session.get('role') != 'admin':
            # ログインしていない、または管理者じゃない
            
            # 【検知2】現在のURLを取得
            current_url = request.url
            # 例: http://localhost:5050/admin/edit
            
            # 【検知3】ログインページにリダイレクト
            # nextパラメータに現在のURLを付ける
            return redirect(url_for('auth.login', next=current_url))
        
        # ログインしている管理者
        # → 元の関数を実行
        return func(*args, **kwargs)
    
    return wrapper
```

### デコレーターが何を検知するか

```python
@admin_required  # ← このデコレーター
def admin_home():
    return render_template('admin_home.html')

# 上のコードは、実際にはこういう意味：
# admin_home = admin_required(admin_home)
```

#### 検知1: ログイン状態

```python
if session.get('role') != 'admin':
    # sessionは Flask が管理するユーザー情報
    # ログイン時に session['role'] = 'admin' が設定される
    # これをチェックすることで、ログイン済みか判定
```

#### 検知2: 現在のURL

```python
request.url
# Flaskの request オブジェクトから現在のURLを取得
# request は Flask が自動的に提供する
# 
# 例:
# ユーザーが /admin/edit にアクセス
# → request.url = "http://localhost:5050/admin/edit"
```

#### 検知3: リダイレクト先

```python
url_for('auth.login', next=current_url)
# url_for: Flaskの関数、ルート名からURLを生成
# 
# 例:
# url_for('auth.login') → "/login"
# url_for('auth.login', next='/admin/edit') → "/login?next=/admin/edit"
```

---

## 🎬 実行フロー（ステップバイステップ）

### シナリオ: ログインしていない状態で /admin/edit にアクセス

```python
# Step 1: ユーザーがアクセス
# ブラウザ → Flask: GET /admin/edit

# Step 2: Flaskがルーティング
@admin_bp.route('/edit')
@admin_required  # ← ここが実行される
def edit_shift():
    return render_template('edit.html')

# Step 3: デコレーターが実行される
# admin_required の wrapper 関数が呼ばれる

def wrapper(*args, **kwargs):
    # Step 4: ログインチェック
    if session.get('role') != 'admin':
        # session = {} （ログインしていない）
        # session.get('role') = None
        # None != 'admin' → True
        
        # Step 5: 現在のURLを取得
        current_url = request.url
        # = "http://localhost:5050/admin/edit"
        
        # Step 6: リダイレクト
        return redirect(url_for('auth.login', next=current_url))
        # = redirect("/login?next=http://localhost:5050/admin/edit")
    
    # この部分は実行されない（ログインしていないので）
    return func(*args, **kwargs)

# Step 7: ブラウザがリダイレクト
# ブラウザ → Flask: GET /login?next=http://localhost:5050/admin/edit

# Step 8: ログインページ表示
@auth_blueprint.route("/login")
def login():
    next_url = request.args.get('next')
    # = "http://localhost:5050/admin/edit"
    
    return render_template("login.html", next=next_url)
    # テンプレートに next を渡す

# Step 9: ユーザーがログイン
# ブラウザ → Flask: POST /login
# form data: account=admin, password=***, next=http://localhost:5050/admin/edit

# Step 10: 認証成功
if account in auth_data and check_password_hash(...):
    session.update({
        "role": "admin",
        ...
    })
    
    # Step 11: nextパラメータをチェック
    if next_url and is_safe_url(next_url):
        return redirect(next_url)
        # = redirect("http://localhost:5050/admin/edit")
        #   ↑ 元のページに戻る！

# Step 12: ブラウザがリダイレクト
# ブラウザ → Flask: GET /admin/edit

# Step 13: 再度デコレーターが実行される
@admin_required
def edit_shift():
    ...

def wrapper(*args, **kwargs):
    # Step 14: ログインチェック
    if session.get('role') != 'admin':
        # session = {'role': 'admin', ...} （ログイン済み）
        # session.get('role') = 'admin'
        # 'admin' != 'admin' → False
        # このif文の中は実行されない
    
    # Step 15: 元の関数を実行
    return func(*args, **kwargs)
    # = edit_shift() が実行される

# Step 16: ページ表示
return render_template('edit.html')
# ブラウザにHTMLが返される
```

---

## 📝 複数のデコレーターを作る

### 権限レベル別のデコレーター

```python
# core/decorators.py

def login_required(func):
    """ログイン必須（スタッフまたは管理者）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'account' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return func(*args, **kwargs)
    return wrapper

def staff_required(func):
    """スタッフ専用（管理者もOK）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('role') not in ['staff', 'admin']:
            return redirect(url_for('auth.login', next=request.url))
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    """管理者専用"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth.login', next=request.url))
        return func(*args, **kwargs)
    return wrapper
```

### 使い分け

```python
# 誰でも見れる（デコレーターなし）
@public_bp.route('/info')
def public_info():
    return render_template('info.html')

# ログインが必要
@staff_bp.route('/home')
@login_required
def staff_home():
    return render_template('staff_home.html')

# スタッフ専用
@staff_bp.route('/request')
@staff_required
def request_shift():
    return render_template('request.html')

# 管理者専用
@admin_bp.route('/manage')
@admin_required
def manage_staff():
    return render_template('manage.html')
```

---

## 🎯 まとめ

### ログイン後のリダイレクト

```
1つのログインページ（/login）
+ nextパラメータ（URLに情報を付ける）
= どのページからでも元のページに戻れる

【重要】各ページ専用のログインページは作らない！
```

### デコレーターとは

```
関数を「装飾」して機能を追加する仕組み

@admin_required  ← この1行を追加するだけ
def admin_home():
    ...

= ログインチェックを自動で追加
```

### デコレーターが検知すること

```
1. ログイン状態（session をチェック）
2. 現在のURL（request.url を取得）
3. リダイレクト先（url_for で生成）
```

### 動作の流れ

```
1. ユーザーが保護されたページにアクセス
   ↓
2. デコレーターが検知
   ↓
3. ログインしていない → /login?next=元のURL にリダイレクト
   ↓
4. ログインフォーム表示（nextを保持）
   ↓
5. ログイン成功
   ↓
6. next パラメータをチェック
   ↓
7. 元のページにリダイレクト
   ↓
8. 再度デコレーターが検知
   ↓
9. ログイン済み → ページ表示
```

---

次のステップ: 実際に実装してみましょう！

