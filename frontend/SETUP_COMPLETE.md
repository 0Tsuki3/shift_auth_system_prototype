# React/Vite セットアップ完了 ✅

**完了日**: 2026-02-23

## ✅ セットアップ済み項目

### 1. Vite + React環境
- ✅ Vite 7.3.1
- ✅ React 19.2.0
- ✅ ESLint設定

### 2. 追加パッケージ
- ✅ `axios` (^1.13.5) - HTTP通信
- ✅ `date-fns` (^4.1.0) - 日付処理

### 3. ビルド設定 (`vite.config.js`)
- ✅ 出力先: `../static/js/shift-editor/`
- ✅ エントリーポイント: `index.js`
- ✅ ビルドテスト成功

### 4. 開発サーバー設定
- ✅ Flask API プロキシ設定
  - `/api` → `http://localhost:5050`
  - `/admin` → `http://localhost:5050`

### 5. Git設定
- ✅ `.gitignore` に `node_modules/` 追加

---

## 🎯 次のステップ（次のチャットで実装）

### **重要**: 次のチャットで以下のファイルを見せてください
1. `README.md`
2. `TASKS.md`
3. `plan/REACT_INTEGRATION.md` ⭐ **（必須）**

これで全ての実装詳細とコンテキストが分かります！

---

### ステップ1: Flask API実装

**ファイル**: `routes/admin.py`

実装するAPI:
- `GET /api/shift-requests/<month>` - シフト希望一覧
- `GET /api/staff` - スタッフ一覧
- `PATCH /api/shift-requests/<id>` - 更新
- `PATCH /api/shift-requests/<id>/read` - 既読トグル

詳細は `plan/REACT_INTEGRATION.md` の「2.1 新規エンドポイント」参照

---

### ステップ2: React コンポーネント実装

**ファイル**: `frontend/src/components/SpreadsheetEditor.jsx`

実装する機能:
- スタッフ × 日付のグリッド表示
- セルクリック → 編集モーダル
- 未読/既読トグル
- 色分け表示

サンプルコードは `plan/REACT_INTEGRATION.md` の「3.3 コンポーネント例」参照

---

### ステップ3: Flask テンプレート作成

**ファイル**: `templates/admin_shift_editor_spa.html`

Reactアプリをホストするテンプレート

---

## 🚀 開発フロー

### 開発時（2つのターミナル）

**⚠️ 重要**: Flask/Viteは**必ず手動で起動**してください。チャット（AI）に起動させないこと。

**Terminal 1: Flask**
```bash
cd /Users/tsukasa/my_code/owns/shift_auth_system_prototype
python3 app.py
# → http://localhost:5050
# 停止: Ctrl + C
```

**Terminal 2: Vite（フロントエンド開発時のみ）**
```bash
cd /Users/tsukasa/my_code/owns/shift_auth_system_prototype/frontend
npm run dev
# → http://localhost:5173
# 停止: Ctrl + C
```

### ビルド（本番用）

```bash
cd frontend
npm run build
# → ../static/js/shift-editor/ に出力
```

---

## 📁 プロジェクト構造

```
shift_auth_system_prototype/
├── frontend/               # Reactプロジェクト
│   ├── src/
│   │   ├── App.jsx        # ✅ セットアップ完了テスト画面
│   │   ├── components/    # ← ここにコンポーネント作成
│   │   └── main.jsx
│   ├── vite.config.js     # ✅ ビルド設定済み
│   └── package.json       # ✅ 依存関係インストール済み
│
├── static/js/shift-editor/  # Reactビルド出力先
│   ├── index.js           # ✅ ビルド成功
│   └── assets/
│
└── routes/admin.py        # ← Flask API実装箇所
```

---

## 🐛 トラブルシューティング

### ビルドが失敗する
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 開発サーバーが起動しない
```bash
# ポート確認
lsof -i :5173
# 強制終了
kill -9 PID
```

### Flaskとの通信がうまくいかない
- Flask側のCORS設定は不要（同一オリジン）
- プロキシ設定は `vite.config.js` で設定済み
- Flask が http://localhost:5050 で起動しているか確認

---

## 📚 参考ドキュメント

- **実装詳細**: `plan/REACT_INTEGRATION.md` ⭐
- **タスク一覧**: `TASKS.md` のフェーズ4B
- **プロジェクト概要**: `README.md`

---

**セットアップ完了！次のチャットで実装を進めましょう 🚀**
