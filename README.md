# Shift Authentication System Prototype

シフト管理システムのプロトタイプ（レイヤードアーキテクチャ版）

## 主な実装済み機能

- ✅ **認証システム**: ログイン・ログアウト、管理者・スタッフの権限管理
- ✅ **スタッフ管理**: 一覧表示、新規追加
- ✅ **シフト管理**: 月別カレンダー表示、追加、編集、削除
- ✅ **シフト希望提出**: スタッフがシフト希望を提出・閲覧・削除
- ✅ **シフト希望インポート**: 管理者がシフト希望を確認・承認・却下
- ✅ **給料計算**: 月別給料明細の表示

詳細な機能リストは [`TASKS.md`](./TASKS.md) を参照してください。

## プロジェクト構造

```
shift_auth_system_prototype_gcp/
├── app.py                      # メインアプリケーション
├── requirements.txt            # Python依存関係
├── .env.example               # 環境変数テンプレート
├── .gitignore                 # Git除外設定
│
├── core/                      # コア機能
│   └── decorators.py         # 認証デコレーター
│
├── models/                    # データモデル
│   ├── shift.py              # シフトモデル
│   ├── shift_request.py      # シフト希望モデル
│   ├── staff.py              # スタッフモデル
│   └── auth.py               # 認証モデル
│
├── data_access/              # データアクセス層（Repository）
│   ├── shift_repository.py   # シフトデータアクセス
│   ├── shift_request_repository.py  # シフト希望データアクセス
│   ├── staff_repository.py   # スタッフデータアクセス
│   └── auth_repository.py    # 認証データアクセス
│
├── validators/               # バリデーション層
│   ├── shift_validator.py    # シフトバリデーション
│   ├── shift_request_validator.py   # シフト希望バリデーション
│   └── staff_validator.py    # スタッフバリデーション
│
├── services/                 # サービス層（ビジネスロジック）
│   ├── shift_service.py      # シフトサービス
│   ├── shift_request_service.py     # シフト希望サービス
│   └── staff_service.py      # スタッフサービス
│
├── presenters/               # プレゼンター層（表示整形）
│   └── shift_presenter.py    # シフトプレゼンター
│
├── routes/                   # ルーティング層（Presentation）
│   ├── auth.py              # 認証ルート
│   ├── admin.py             # 管理者ルート
│   └── staff.py             # スタッフルート
│
├── templates/               # HTMLテンプレート
├── static/                  # 静的ファイル（CSS, JS）
├── data/                    # CSVデータ
│   ├── shift/              # シフトデータ（月別）
│   ├── shift_request/      # シフト希望データ（月別）
│   ├── staff.csv           # スタッフマスタ
│   └── auth.csv            # 認証情報
│
├── plan/                    # 設計書
│   ├── LAYERED_ARCHITECTURE.md
│   ├── APP_STRUCTURE.md
│   └── ...
│
└── old/                     # 旧ファイル（参照用）
```

## セットアップ

### 1. 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
cp .env.example .env
# .env ファイルを編集して必要な値を設定
```

### 4. アプリケーションの起動

**⚠️ 重要**: Flaskは**必ず手動で起動**してください。チャット（AI）に起動させないこと。

```bash
python3 app.py
```

ブラウザで http://localhost:5050 にアクセス

**停止方法**: ターミナルで **Ctrl + C**

## アーキテクチャ

このプロジェクトは7層のレイヤードアーキテクチャを採用しています：

1. **Models**: データ構造の定義
2. **Data Source**: データの物理的な格納場所（CSV, 将来的にSQL）
3. **Repository**: データアクセスの抽象化
4. **Validation**: 入力データの検証
5. **Service**: ビジネスロジック
6. **Presenter**: 表示用データの整形
7. **Presentation**: ルーティングとHTTPハンドリング

詳細は `plan/LAYERED_ARCHITECTURE.md` を参照してください。

## 開発ガイド

### 新しい機能を追加する場合

1. **Models**: データモデルを定義
2. **Repository**: データアクセスロジックを実装
3. **Validator**: バリデーションルールを追加
4. **Service**: ビジネスロジックを実装
5. **Presenter**: 表示用整形ロジックを追加
6. **Routes**: エンドポイントを作成
7. **Git commit**: 実装後は必ずGitにコミットすること ⚠️

下位レイヤーから上位レイヤーへ順に実装することを推奨します。

### 開発フロー（必須）

機能実装後は**必ず以下の手順でGitにコミット**してください：

```bash
# 1. 変更を確認
git status
git diff

# 2. ステージング
git add .

# 3. コミット（わかりやすいメッセージで）
git commit -m "feat: 機能の説明"
# 例: git commit -m "feat: シフト削除機能を実装"
# 例: git commit -m "feat: シフト編集機能を追加"
# 例: git commit -m "fix: シフト表示のバグを修正"

# 4. GitHubにプッシュ
git push origin main
```

**⚠️ 重要**: このプロジェクトでは、機能実装やバグ修正を行った際は**必ずGitにコミット**することを義務付けます。バージョン管理を徹底することで、変更履歴の追跡とロールバックを可能にします。

詳細なGit操作については `GIT_GUIDE.md` を参照してください。

## 📚 ドキュメント一覧

このプロジェクトには目的別に整理された15個のドキュメントがあります。

### 🎯 まず読むべき文書

| ドキュメント | 内容 | 読むべき人 |
|-------------|------|-----------|
| `README.md` (このファイル) | プロジェクト概要、セットアップ手順 | 全員（最初に必読） |
| `TASKS.md` | 実装済み/未実装機能のリスト | 開発者、プロジェクト管理者 |
| `DEVELOPMENT_GUIDE.md` | 機能開発の実践ガイド | 機能を追加する人 |

### 🏗️ アーキテクチャ設計

| ドキュメント | 内容 | 読むべき人 |
|-------------|------|-----------|
| `SYSTEM_DIAGRAMS.md` ⭐ | レイヤー構造・処理フローの図解（Mermaid） | 視覚的に理解したい人 |
| `plan/LAYERED_ARCHITECTURE.md` ⭐ | 7層アーキテクチャの完全ガイド（29KB） | コードを書く人全員 |
| `plan/APP_STRUCTURE.md` | システム全体の構造と動作フロー | システム全体を理解したい人 |

### 🔐 認証・権限管理

| ドキュメント | 内容 | 読むべき人 |
|-------------|------|-----------|
| `plan/LOGIN_AND_DECORATORS.md` ⭐ | ログイン機能とデコレーターの詳細解説（19KB） | 認証機能を触る人 |
| `plan/USER_FLOW_MAPPING.md` | ユーザーフローと権限マッピング | UI/UX設計、権限設計する人 |

### 📊 データベース・SQL移行

| ドキュメント | 内容 | 読むべき人 |
|-------------|------|-----------|
| `plan/MIGRATION_TO_SQL.md` | CSV → SQL 移行計画 | DB移行を検討する人 |
| `plan/SUPABASE_SETUP.md` | Supabase（無料PostgreSQL）セットアップ | 無料でSQL化したい人 |

### 📈 機能分析・将来計画

| ドキュメント | 内容 | 読むべき人 |
|-------------|------|-----------|
| `plan/FEATURE_ANALYSIS.md` | 全機能（72エンドポイント）の分析 | 機能の優先度を判断する人 |
| `plan/ARCHITECTURE_DECISIONS.md` | 技術スタック選定理由 | 技術選定・コスト判断する人 |
| `plan/REFACTORING_PLAN.md` | コード整理計画 | リファクタリングを検討する人 |
| `plan/REACT_INTEGRATION.md` ⭐ | React統合計画とアーキテクチャ移行 | フロントエンド刷新する人 |

### 🔧 運用・Git管理

| ドキュメント | 内容 | 読むべき人 |
|-------------|------|-----------|
| `GIT_GUIDE.md` | Git操作ガイド | Git初心者、復習したい人 |
| `plan/README.md` | plan/フォルダのインデックス | GCP作業する人 |

### 🎯 読む順番（推奨）

#### 初めての人
```
1. README.md (このファイル) - 全体概要
2. SYSTEM_DIAGRAMS.md - 図で理解する（視覚的）
3. TASKS.md - 現状把握
4. plan/LAYERED_ARCHITECTURE.md - コードの書き方
5. DEVELOPMENT_GUIDE.md - 開発手順
```

#### 機能開発する人
```
1. TASKS.md - 何を実装するか確認
2. SYSTEM_DIAGRAMS.md - 処理フローを図で確認
3. plan/LAYERED_ARCHITECTURE.md - アーキテクチャ理解
4. DEVELOPMENT_GUIDE.md - 実装方法
5. GIT_GUIDE.md - コミット方法
```

#### 認証機能を触る人
```
1. SYSTEM_DIAGRAMS.md - 認証フローの図
2. plan/LOGIN_AND_DECORATORS.md - 認証の仕組み
3. plan/USER_FLOW_MAPPING.md - 権限マトリクス
4. plan/APP_STRUCTURE.md - 全体フロー
```

#### SQL移行を検討する人
```
1. plan/FEATURE_ANALYSIS.md - どの機能をSQL化すべきか
2. plan/SUPABASE_SETUP.md - 無料で始める方法
3. plan/MIGRATION_TO_SQL.md - 本格的な移行計画
4. plan/ARCHITECTURE_DECISIONS.md - コスト判断
```

## デプロイ

### GCP App Engine へのデプロイ

```bash
gcloud app deploy
```

詳細は `old/GCP_DEPLOYMENT.md` を参照してください。

## ライセンス

Private Project

