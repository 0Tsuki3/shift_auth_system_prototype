# シフト管理システム - GCP作業用フォルダ

## 📌 このフォルダについて

**作成日**: 2025-12-06  
**目的**: GCPデプロイ・SQL化などの作業用環境

元フォルダから最新のコードと全ドキュメントをコピーしました。

## 📚 重要なドキュメント

### 必読ドキュメント（今日作成）

1. **[CHAT_HISTORY_2025-12-06.md](./CHAT_HISTORY_2025-12-06.md)**  
   今日の会話の完全な記録。全ての意思決定が記載されています。

2. **[ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md)**  
   アーキテクチャ決定記録（ADR）。技術スタック、プラットフォーム選定の理由など。

3. **[FEATURE_ANALYSIS.md](./FEATURE_ANALYSIS.md)**  
   全機能（72エンドポイント）の分析と需要判断。

4. **[MIGRATION_TO_SQL.md](./MIGRATION_TO_SQL.md)**  
   CSV → SQL への移行計画。スキーマ設計、マイグレーション手順など。

5. **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)**  
   Supabase（無料PostgreSQL）のセットアップガイド。

6. **[REACT_INTEGRATION.md](./REACT_INTEGRATION.md)** 🆕  
   React統合計画。スプレッドシート形式UI実装と将来のアーキテクチャ移行。

7. **[WORKSPACE_INFO.md](./WORKSPACE_INFO.md)**  
   このワークスペースの簡易情報。

### 既存ドキュメント

- **[GCP_DEPLOYMENT.md](./GCP_DEPLOYMENT.md)** - GCPデプロイ手順
- **[shift_exclude_time_instructions.md](./shift_exclude_time_instructions.md)** - 除外時間機能

## 🚀 クイックスタート

### ローカルで起動

```bash
# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# アプリ起動
python main.py

# ブラウザで開く
open http://localhost:8080
```

### ログイン情報

```
管理者アカウント:
- アカウント: admin
- パスワード: （auth.csv参照）
```

## 📊 現在の状態

### 動作状況
- ✅ **完全に動作中**
- ✅ Python 3.13.7
- ✅ Flask 2.0.1
- ✅ 全機能が利用可能

### データ状況
- ✅ 2025年9月まで実績データあり（135件のシフト）
- ⚠️ 10月以降はほぼ空
- 👤 スタッフ: 1人（中村 元）

### 技術スタック
```
Backend:
- Python 3.13
- Flask 2.0.1
- Gunicorn 20.1.0
- pandas 1.5.3

Data:
- CSV ファイル（現状）
- SQL なし（今後移行予定）

Deploy:
- GCP App Engine
- ポート: 8080
```

## 🎯 次のアクション

### Option 1: SQL化（推奨）

**Supabase無料プラン**を使う（コスト増加なし）

```bash
# 1. Supabaseアカウント作成
https://supabase.com

# 2. セットアップガイド参照
cat SUPABASE_SETUP.md

# 3. マイグレーション実行
python scripts/migrate_to_supabase.py
```

**期間**: 2-3週間  
**コスト**: ¥3,000/月（変わらず）

### Option 2: GCPにデプロイ

```bash
# GCP認証
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# デプロイ
gcloud app deploy

# 確認
gcloud app browse
```

**期間**: 数時間  
**コスト**: ¥3,000/月程度

### Option 3: そのまま使う

現状のままローカルで使い続ける（無料）

## 💰 コスト試算

### 現状（CSV）
```
GCP App Engine: ¥3,000/月
データベース: ¥0（CSV）
合計: ¥3,000/月
```

### SQL化後（Supabase無料）
```
GCP App Engine: ¥3,000/月
Supabase: ¥0（無料プラン）
合計: ¥3,000/月
```

### SQL化後（Cloud SQL）
```
GCP App Engine: ¥3,000/月
Cloud SQL (f1-micro): ¥1,780/月
合計: ¥4,780/月
```

### マルチテナント（4-5店舗）
```
GCP App Engine: ¥5,000/月
Supabase: ¥0
合計: ¥5,000/月
```

## 🏗️ プロジェクト構成

```
.
├── app.py                  # Flaskアプリケーション本体
├── main.py                 # エントリーポイント
├── requirements.txt        # 依存関係
├── app.yaml               # GCP App Engine設定
├── Procfile               # Heroku/Render設定
│
├── routes/                # ルート定義
│   ├── auth.py           # 認証
│   ├── admin.py          # 管理者機能
│   ├── staff.py          # スタッフ機能
│   ├── daily_shift.py    # 日次シフト
│   ├── monthly_shift.py  # 月次シフト
│   ├── shift_public.py   # 公開シフト
│   ├── manual.py         # マニュアル
│   ├── manual_memo.py    # キッチンメモ
│   ├── order_memo.py     # 発注メモ
│   ├── notice_memo.py    # お知らせ
│   ├── stock.py          # 在庫管理
│   └── exclude_api.py    # 除外時間API
│
├── utils/                # ユーティリティ
│   ├── csv_utils.py      # CSV操作
│   ├── staff_utils.py    # スタッフ管理
│   ├── shift_utils.py    # シフト計算
│   ├── date_utils.py     # 日付処理
│   ├── graph_utils.py    # グラフ生成
│   └── exclude_time_utils.py
│
├── templates/            # HTMLテンプレート（47ファイル）
├── static/               # 静的ファイル（CSS等）
├── data/                 # データファイル（CSV）
│   ├── shift/           # 確定シフト
│   ├── shift_request/   # シフト希望
│   ├── notes/           # メモ
│   ├── manuals/         # マニュアル
│   └── exclude_time/    # 除外時間
│
└── google-cloud-sdk/    # GCP SDK
```

## 📈 機能一覧

### コア機能（⭐⭐⭐⭐⭐）
- シフト希望提出
- シフト編集・確定
- シフト閲覧
- スタッフ管理
- セグメント表示（人員配置の可視化）

### 差別化機能（⭐⭐⭐⭐）
- グラフ可視化（タイムライン）
- 除外時間管理
- 人件費計算
- カレンダーダウンロード（iCal形式）

### 付加機能（⭐⭐⭐）
- マニュアル管理
- メモ機能（仕込み・発注・お知らせ）
- 在庫管理

詳細は [FEATURE_ANALYSIS.md](./FEATURE_ANALYSIS.md) 参照

## 🔒 セキュリティ

### 認証
- パスワードハッシュ化（pbkdf2:sha256）
- セッション管理
- ロール分離（admin/staff）

### データ
- CSVファイルベース（ローカル）
- バックアップ推奨

## 🐛 トラブルシューティング

### アプリが起動しない

```bash
# 仮想環境の確認
which python
# → venv/bin/python と表示されるべき

# 依存関係の再インストール
pip install -r requirements.txt --force-reinstall
```

### ポートが使用中

```bash
# ポート8080を使っているプロセスを確認
lsof -i :8080

# 強制終了
kill -9 PID
```

### データが表示されない

```bash
# data/ フォルダの確認
ls -lh data/shift/

# 権限の確認
chmod -R 755 data/
```

## 📞 サポート

このプロジェクトの全ての意思決定と議論は **[CHAT_HISTORY_2025-12-06.md](./CHAT_HISTORY_2025-12-06.md)** に記録されています。

疑問があればまずこのファイルを確認してください。

---

**最終更新**: 2025-12-06  
**バージョン**: 開発版（SQL移行前）  
**ステータス**: ✅ 動作確認済み

