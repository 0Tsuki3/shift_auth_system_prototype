# 🚀 機能開発ガイド

## 🔧 開発環境の起動

### Flask起動（必須）

**⚠️ 重要**: Flaskは**必ず手動で起動**してください。チャット（AI）に起動させないこと。

```bash
cd /Users/tsukasa/my_code/owns/shift_auth_system_prototype
python3 app.py
```

- **起動確認**: `http://localhost:5050` にアクセス
- **停止方法**: ターミナルで **Ctrl + C**
- **注意**: AIに起動させるとCtrl+Cで停止できなくなります

### React開発サーバー（フロントエンド開発時のみ）

```bash
cd /Users/tsukasa/my_code/owns/shift_auth_system_prototype/frontend
npm run dev
```

- **開発用URL**: `http://localhost:5173` （Viteの開発サーバー）
- **本番ビルド**: `npm run build` → `../static/js/shift-editor/` に出力

---

## レイヤードアーキテクチャでの開発手順

### 🎯 開発の流れ（トップダウン設計 → ボトムアップ実装）

---

## ステップ1: 設計（紙とペン、または頭の中）

### 1-1. URL設計
```
何を作る？ → 「管理者がシフトを追加する機能」

どんなURL？
  GET  /admin/shifts/add/<month>  → 追加フォーム表示
  POST /admin/shifts/add/<month>  → データ保存
```

### 1-2. 画面設計
```
入力項目は？
  - スタッフ選択（ドロップダウン）
  - 日付（カレンダー）
  - 開始時刻（HH:MM）
  - 終了時刻（HH:MM）
  - 保存ボタン
```

### 1-3. データ設計
```
必要なデータは？
  - Shiftモデル（既にある✅）
  - Staffリスト（既にある✅）
  
バリデーションは？
  - 必須項目チェック（既にある✅）
  - 時刻の妥当性（既にある✅）
```

---

## ステップ2: 実装（下から上へ）

### 層1: Models ← 既にある✅
```python
# models/shift.py
# → もう完成してる！
```

### 層2: Repository ← 既にある✅
```python
# data_access/shift_repository.py
# → add_shift() メソッドがある！
```

### 層3: Validator ← 既にある✅
```python
# validators/shift_validator.py
# → validate_shift_entry() がある！
```

### 層4: Service ← 既にある✅
```python
# services/shift_service.py
# → create_shift() メソッドがある！
```

### 層5: Presenter ← 必要なし
```
（今回は表示整形が不要）
```

### 層6: Routes ← ここを書く！
```python
# routes/admin.py

@admin_bp.route('/shifts/add/<month>', methods=['GET', 'POST'])
@admin_required
def add_shift(month):
    """シフト追加"""
    if request.method == 'POST':
        # フォームからデータ取得
        shift_data = {
            'account': request.form.get('account'),
            'date': request.form.get('date'),
            'start': request.form.get('start'),
            'end': request.form.get('end')
        }
        
        try:
            # Serviceを呼ぶ
            shift_service.create_shift(month, shift_data)
            flash('シフトを追加しました', 'success')
            return redirect(url_for('admin.view_shifts', month=month))
        except ValueError as e:
            flash(str(e), 'error')
    
    # GETの場合：フォーム表示
    staff_list = staff_service.get_all_staff()
    return render_template('admin_add_shift.html', 
                         month=month, 
                         staff_list=staff_list)
```

### 層7: HTML ← ここも書く！
```html
<!-- templates/admin_add_shift.html -->
{% extends "base.html" %}

{% block content %}
<div class="card">
    <h2>シフト追加 - {{ month }}</h2>
    
    <form method="POST">
        <div class="form-group">
            <label>スタッフ</label>
            <select name="account" required>
                {% for staff in staff_list %}
                    <option value="{{ staff.account }}">
                        {{ staff.full_name }}
                    </option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label>日付</label>
            <input type="date" name="date" required>
        </div>
        
        <div class="form-group">
            <label>開始時刻</label>
            <input type="time" name="start" required>
        </div>
        
        <div class="form-group">
            <label>終了時刻</label>
            <input type="time" name="end" required>
        </div>
        
        <button type="submit" class="btn btn-primary">
            追加
        </button>
    </form>
</div>
{% endblock %}
```

---

## 📊 開発の流れ（まとめ）

```
設計フェーズ（上から）:
  URL → 画面 → データ
  ↓
実装フェーズ（下から）:
  Models → Repository → Validator → Service
  → Presenter → Routes → HTML
```

---

## 🎓 実践：次の機能を作ってみよう

### 初級: シフト追加機能
- 上記の例を参考に実装
- 既存の層を使うだけ（Routes + HTMLのみ）

### 中級: シフト編集機能
- シフトIDで特定のシフトを編集
- RoutesでShiftService.update_shift()を呼ぶ

### 上級: 月別シフト統計
- 月全体の統計を表示
- Presenterで集計ロジックを実装

---

## 💡 コーディングのコツ

### ✅ DO（やるべきこと）
1. **下の層から順番に作る**
   - Models → Repository → ... → Routes
   
2. **各層の役割を守る**
   - Routes: リクエスト処理だけ
   - Service: ビジネスロジックだけ
   - Repository: データアクセスだけ

3. **既存のコードを真似る**
   - 似た機能を参考にする
   - パターンを守る

### ❌ DON'T（やってはいけないこと）
1. **層をスキップしない**
   - Routes → Repository は❌
   - Routes → Service → Repository が正解✅

2. **層を混ぜない**
   - Routesにデータアクセスを書かない
   - ServiceにHTMLを書かない

3. **一度に全部作らない**
   - 1機能ずつ、1層ずつ

---

## 🔍 デバッグのコツ

問題が起きたら、下から確認:

```
1. Models: データ構造は正しい？
   ↓
2. Repository: CSVの読み書きは動く？
   ↓
3. Validator: バリデーションは通る？
   ↓
4. Service: ロジックは正しい？
   ↓
5. Routes: リクエスト処理は合ってる？
   ↓
6. HTML: フォームは正しい？
```

---

## 🎯 練習問題

以下の機能を順番に実装してみてください：

### 1. シフト追加（初級）
- URL: `/admin/shifts/add/<month>`
- 必要な層: Routes + HTML のみ
- 難易度: ⭐

### 2. シフト削除（初級）
- URL: `/admin/shifts/delete/<month>/<shift_id>`
- 必要な層: Routes のみ（リダイレクトだけ）
- 難易度: ⭐

### 3. シフト編集（中級）✅ 実装済み (2026-02-22)
- URL: `/admin/shifts/edit/<month>/<shift_id>`
- 必要な層: Routes + HTML
- 難易度: ⭐⭐

### 4. スタッフ別月間統計（上級）
- URL: `/admin/stats/<month>`
- 必要な層: Presenter + Routes + HTML
- 難易度: ⭐⭐⭐

---

## 📚 参考になるファイル

既存の実装を参考にしてください：

### 基本的なCRUD操作
- **スタッフ追加**: `routes/admin.py` の `add_staff()`
- **シフト追加**: `routes/admin.py` の `add_shift()`
- **シフト編集**: `routes/admin.py` の `edit_shift()`
- **シフト削除**: `routes/admin.py` の `delete_shift()`
- **シフト表示**: `routes/admin.py` の `view_shifts()`

### 完全な機能実装例（全7層）
- **シフト希望提出機能**: 
  - Model: `models/shift_request.py`
  - Repository: `data_access/shift_request_repository.py`
  - Validator: `validators/shift_request_validator.py`
  - Service: `services/shift_request_service.py`
  - Routes: `routes/staff.py` の `submit_request()`, `view_requests()`, `delete_request()`
  - Templates: `templates/staff_submit_request.html`, `templates/staff_view_requests.html`

### HTMLフォーム
- **追加フォーム**: `templates/admin_add_staff.html`, `templates/staff_submit_request.html`
- **一覧表示**: `templates/admin_shifts_calendar.html`, `templates/staff_view_requests.html`

---

## 🎉 実装したらやること

1. **動作確認**
   - ブラウザで実際に試す
   
2. **Git コミット**
   ```bash
   git add .
   git commit -m "feat: シフト追加機能を実装"
   ```

3. **次の機能へ！**

---

質問があればいつでも聞いてください！

