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
開発計画と進捗は [`PLAN.md`](./PLAN.md) を参照してください。  
全ドキュメント一覧は [`INDEX.md`](./INDEX.md) を参照してください。

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
├── docs/                    # ドキュメント
│   ├── getting-started/    # 開発ガイド
│   ├── architecture/       # アーキテクチャ設計
│   ├── planning/           # 計画・分析
│   ├── migration/          # 移行計画
│   └── archive/            # 古いドキュメント
│
└── old/                     # 旧コード（参照用）
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

詳細は [`docs/architecture/LAYERED_ARCHITECTURE.md`](./docs/architecture/LAYERED_ARCHITECTURE.md) を参照してください。

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

詳細なGit操作については [`docs/getting-started/GIT_GUIDE.md`](./docs/getting-started/GIT_GUIDE.md) を参照してください。

## 📚 ドキュメント

### 🎯 まず読むべき文書

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| `README.md` (このファイル) | プロジェクト概要、セットアップ手順 | **全員（最初に必読）** |
| [`PLAN.md`](./PLAN.md) | 開発の全体計画、進捗状況、次のステップ | プロジェクト管理者 |
| [`TASKS.md`](./TASKS.md) | 実装済み/未実装機能の詳細リスト | 開発者 |
| [`INDEX.md`](./INDEX.md) | 全ドキュメントのインデックス | 迷った時に見る |

### 📖 詳細ドキュメント

詳細なドキュメントは `docs/` フォルダに整理されています：

```
docs/
├── getting-started/         # 🚀 初心者向けガイド
│   ├── DEVELOPMENT_GUIDE.md  # 機能開発の実践ガイド
│   └── GIT_GUIDE.md          # Git操作ガイド
│
├── architecture/            # 🏗️ アーキテクチャ設計
│   ├── SYSTEM_DIAGRAMS.md    # システム図解（Mermaid）⭐
│   ├── LAYERED_ARCHITECTURE.md  # 7層アーキテクチャ完全ガイド ⭐
│   ├── APP_STRUCTURE.md      # システム全体の構造
│   └── LOGIN_AND_DECORATORS.md  # 認証の詳細 ⭐
│
├── planning/                # 📊 計画・分析
│   ├── ARCHITECTURE_DECISIONS.md  # 技術選定理由
│   ├── FEATURE_ANALYSIS.md   # 全機能の需要分析
│   └── USER_FLOW_MAPPING.md  # ユーザーフローと権限
│
├── migration/               # 🔄 移行計画
│   ├── MIGRATION_TO_SQL.md   # SQL移行計画
│   ├── SUPABASE_SETUP.md     # Supabase無料セットアップ
│   ├── REACT_INTEGRATION.md  # React統合計画 ⭐
│   └── REFACTORING_PLAN.md   # リファクタリング計画
│
└── archive/                 # 🗄️ 古いドキュメント
```

⭐マークは特に重要なドキュメントです。

全ドキュメントの詳細は [`INDEX.md`](./INDEX.md) を参照してください。

### 🎯 読む順番（推奨）

#### 初めての人
```
1. README.md (このファイル) - 全体概要
2. docs/architecture/SYSTEM_DIAGRAMS.md - 図で理解
3. TASKS.md - 現状把握
4. docs/getting-started/DEVELOPMENT_GUIDE.md - 開発手順
```

#### 機能開発する人
```
1. TASKS.md - 何を実装するか確認
2. docs/architecture/LAYERED_ARCHITECTURE.md - アーキテクチャ理解
3. docs/getting-started/DEVELOPMENT_GUIDE.md - 実装方法
```

詳しい目的別ガイドは [`INDEX.md`](./INDEX.md) を参照してください。

## デプロイ

### GCP App Engine へのデプロイ

```bash
gcloud app deploy
```

詳細は [`old/GCP_DEPLOYMENT.md`](./old/GCP_DEPLOYMENT.md) を参照してください。

## ライセンス

Private Project

