# 📚 ドキュメントインデックス

シフト管理システムの全ドキュメント一覧です。目的別に整理されています。

**最終更新**: 2026-03-15

---

## 🚀 はじめに

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| [`README.md`](./README.md) | プロジェクト概要、セットアップ、機能一覧 | **全員（最初に必読）** |
| [`PLAN.md`](./PLAN.md) | 開発の全体計画、進捗状況、次のステップ | **プロジェクト管理者、開発リーダー** |
| [`TASKS.md`](./TASKS.md) | 実装済み/未実装機能の詳細リスト | **開発者** |
| `INDEX.md` (このファイル) | 全ドキュメントのインデックス | **迷った人** |

---

## 📖 カテゴリ別ドキュメント

### 🎓 getting-started/ - 初心者向けガイド

開発を始めるための基本情報。

| ドキュメント | 内容 | いつ読む？ |
|-------------|------|-----------|
| [`docs/getting-started/DEVELOPMENT_GUIDE.md`](./docs/getting-started/DEVELOPMENT_GUIDE.md) | 機能開発の実践ガイド（Flask起動、レイヤー実装） | 初めて機能開発する時 |
| [`docs/getting-started/GIT_GUIDE.md`](./docs/getting-started/GIT_GUIDE.md) | Git操作ガイド（コミット、ブランチ、戻す方法） | Git使い方を確認したい時 |

---

### 🏗️ architecture/ - アーキテクチャ設計

システムの構造と設計思想。

| ドキュメント | 内容 | いつ読む？ | 重要度 |
|-------------|------|-----------|--------|
| [`docs/architecture/SYSTEM_DIAGRAMS.md`](./docs/architecture/SYSTEM_DIAGRAMS.md) | システム全体の図解（Mermaid） | 視覚的に理解したい時 | ⭐⭐⭐⭐⭐ |
| [`docs/architecture/LAYERED_ARCHITECTURE.md`](./docs/architecture/LAYERED_ARCHITECTURE.md) | 7層アーキテクチャの完全ガイド（29KB） | コードを書く前に必読 | ⭐⭐⭐⭐⭐ |
| [`docs/architecture/APP_STRUCTURE.md`](./docs/architecture/APP_STRUCTURE.md) | システム全体の構造と動作フロー | 全体像を把握したい時 | ⭐⭐⭐⭐ |
| [`docs/architecture/LOGIN_AND_DECORATORS.md`](./docs/architecture/LOGIN_AND_DECORATORS.md) | ログイン機能とデコレーターの詳細（19KB） | 認証機能を触る時 | ⭐⭐⭐⭐⭐ |

---

### 📊 planning/ - 計画・分析・意思決定

技術選定、機能分析、アーキテクチャ決定の記録。

| ドキュメント | 内容 | いつ読む？ |
|-------------|------|-----------|
| [`docs/planning/ARCHITECTURE_DECISIONS.md`](./docs/planning/ARCHITECTURE_DECISIONS.md) | 技術スタック選定理由、GCP vs AWS比較 | 技術選定を判断する時 |
| [`docs/planning/FEATURE_ANALYSIS.md`](./docs/planning/FEATURE_ANALYSIS.md) | 全機能（72エンドポイント）の需要分析 | 機能の優先度を決める時 |
| [`docs/planning/USER_FLOW_MAPPING.md`](./docs/planning/USER_FLOW_MAPPING.md) | ユーザーフローと権限マッピング | 権限設計・UI設計する時 |

---

### 🔄 migration/ - 移行計画

データベース移行、リファクタリング、技術刷新の計画。

| ドキュメント | 内容 | いつ読む？ |
|-------------|------|-----------|
| [`docs/migration/MIGRATION_TO_SQL.md`](./docs/migration/MIGRATION_TO_SQL.md) | CSV → SQL移行の詳細計画（Cloud SQL / BigQuery） | 本格的にSQL化する時 |
| [`docs/migration/SUPABASE_SETUP.md`](./docs/migration/SUPABASE_SETUP.md) | Supabase（無料PostgreSQL）セットアップ手順 | 無料でSQL化を試したい時 |
| [`docs/migration/REACT_INTEGRATION.md`](./docs/migration/REACT_INTEGRATION.md) | React統合計画とアーキテクチャ移行 | フロントエンドを刷新する時 |
| [`docs/migration/REFACTORING_PLAN.md`](./docs/migration/REFACTORING_PLAN.md) | コード整理・リファクタリング計画 | コードを整理する時 |

---

### 🗄️ archive/ - 古いドキュメント

過去のチャット履歴、開発メモ、旧フォルダ。

| ドキュメント | 内容 |
|-------------|------|
| [`docs/archive/CHAT_HISTORY_2025-12-06.md`](./docs/archive/CHAT_HISTORY_2025-12-06.md) | 2025年12月のチャット履歴（技術選定の議論） |
| [`docs/archive/memo_2026-02-22.md`](./docs/archive/memo_2026-02-22.md) | 2026年2月の開発メモ（UI改善案） |
| [`docs/archive/plan_README.md`](./docs/archive/plan_README.md) | 旧plan/フォルダのREADME |
| `docs/archive/plan/` | 旧plan/フォルダの全ファイル（バックアップ） |

---

## 🎯 目的別の読み方ガイド

### 🆕 初めてプロジェクトに参加する人

```
1. README.md                        - プロジェクト概要を理解
2. docs/architecture/SYSTEM_DIAGRAMS.md  - 図で全体像を把握
3. docs/getting-started/DEVELOPMENT_GUIDE.md - 開発環境のセットアップ
4. TASKS.md                         - 現在の実装状況を確認
5. docs/architecture/LAYERED_ARCHITECTURE.md - コードの書き方を学ぶ
```

**所要時間**: 2-3時間

---

### 💻 機能開発をする人

```
1. TASKS.md                         - 何を実装するか確認
2. docs/architecture/SYSTEM_DIAGRAMS.md  - 処理フローを図で確認
3. docs/architecture/LAYERED_ARCHITECTURE.md - アーキテクチャルールを理解
4. docs/getting-started/DEVELOPMENT_GUIDE.md - 実装方法を確認
5. docs/getting-started/GIT_GUIDE.md - コミット方法を確認
```

**所要時間**: 1時間

---

### 🔐 認証機能を触る人

```
1. docs/architecture/SYSTEM_DIAGRAMS.md      - 認証フローの図を確認
2. docs/architecture/LOGIN_AND_DECORATORS.md - 認証の仕組みを理解
3. docs/planning/USER_FLOW_MAPPING.md        - 権限マトリクスを確認
4. docs/architecture/APP_STRUCTURE.md        - 全体フローを把握
```

**所要時間**: 1-2時間

---

### 🗄️ SQL移行を検討する人

```
1. docs/planning/FEATURE_ANALYSIS.md    - どの機能をSQL化すべきか判断
2. docs/migration/SUPABASE_SETUP.md     - 無料で始める方法を確認
3. docs/migration/MIGRATION_TO_SQL.md   - 本格的な移行計画を理解
4. docs/planning/ARCHITECTURE_DECISIONS.md - コストと技術選定を理解
```

**所要時間**: 2-3時間

---

### 🎨 React統合を検討する人

```
1. docs/migration/REACT_INTEGRATION.md  - React統合の3つのアプローチ
2. docs/architecture/LAYERED_ARCHITECTURE.md - 既存アーキテクチャの理解
3. TASKS.md (フェーズ4B参照)           - 実装済みのReact機能を確認
```

**所要時間**: 1-2時間

---

### 📊 プロジェクト全体を把握したい人（PM、意思決定者）

```
1. README.md                            - 全体概要
2. PLAN.md                              - 開発計画と進捗
3. docs/planning/FEATURE_ANALYSIS.md    - 機能の需要分析
4. docs/planning/ARCHITECTURE_DECISIONS.md - 技術決定の根拠
5. docs/architecture/SYSTEM_DIAGRAMS.md - システム構造の可視化
```

**所要時間**: 1-2時間

---

## 📁 フォルダ構造

```
shift_auth_system_prototype/
│
├── README.md                    # プロジェクトのエントランス
├── PLAN.md                      # 開発計画と進捗
├── INDEX.md                     # このファイル（ドキュメントインデックス）
├── TASKS.md                     # タスク管理
│
├── docs/                        # 📚 全てのドキュメント
│   ├── getting-started/         # 🚀 初心者向けガイド
│   │   ├── DEVELOPMENT_GUIDE.md
│   │   └── GIT_GUIDE.md
│   │
│   ├── architecture/            # 🏗️ アーキテクチャ設計
│   │   ├── SYSTEM_DIAGRAMS.md
│   │   ├── LAYERED_ARCHITECTURE.md
│   │   ├── APP_STRUCTURE.md
│   │   └── LOGIN_AND_DECORATORS.md
│   │
│   ├── planning/                # 📊 計画・分析
│   │   ├── ARCHITECTURE_DECISIONS.md
│   │   ├── FEATURE_ANALYSIS.md
│   │   └── USER_FLOW_MAPPING.md
│   │
│   ├── migration/               # 🔄 移行計画
│   │   ├── MIGRATION_TO_SQL.md
│   │   ├── SUPABASE_SETUP.md
│   │   ├── REACT_INTEGRATION.md
│   │   └── REFACTORING_PLAN.md
│   │
│   └── archive/                 # 🗄️ 古いドキュメント
│       ├── CHAT_HISTORY_2025-12-06.md
│       ├── memo_2026-02-22.md
│       ├── plan_README.md
│       └── plan/ (旧planフォルダ)
│
├── app.py                       # メインアプリケーション
├── models/                      # データモデル
├── data_access/                 # リポジトリ
├── services/                    # ビジネスロジック
├── routes/                      # ルーティング
├── templates/                   # HTMLテンプレート
├── static/                      # 静的ファイル
├── frontend/                    # React (Vite)
├── data/                        # CSVデータ
└── old/                         # 旧コード
```

---

## 🔍 キーワード検索ガイド

探しているものがわからない時は、このキーワードで探してください：

| キーワード | 見るべきドキュメント |
|-----------|---------------------|
| **セットアップ** | README.md → docs/getting-started/DEVELOPMENT_GUIDE.md |
| **レイヤー** | docs/architecture/LAYERED_ARCHITECTURE.md |
| **図・ダイアグラム** | docs/architecture/SYSTEM_DIAGRAMS.md |
| **認証・ログイン** | docs/architecture/LOGIN_AND_DECORATORS.md |
| **権限・デコレーター** | docs/architecture/LOGIN_AND_DECORATORS.md |
| **SQL移行** | docs/migration/SUPABASE_SETUP.md → docs/migration/MIGRATION_TO_SQL.md |
| **React** | docs/migration/REACT_INTEGRATION.md |
| **コスト** | docs/planning/ARCHITECTURE_DECISIONS.md |
| **機能一覧** | docs/planning/FEATURE_ANALYSIS.md |
| **Git使い方** | docs/getting-started/GIT_GUIDE.md |
| **タスク** | TASKS.md |
| **開発計画** | PLAN.md |

---

## 📊 ドキュメントサイズ一覧

大きいドキュメントは読むのに時間がかかります。

| サイズ | ドキュメント | 読了時間 |
|-------|-------------|----------|
| **29KB** | docs/architecture/LAYERED_ARCHITECTURE.md | 30-40分 |
| **19KB** | docs/architecture/LOGIN_AND_DECORATORS.md | 20-30分 |
| **15KB** | docs/migration/REACT_INTEGRATION.md | 15-20分 |
| **14KB** | docs/migration/REFACTORING_PLAN.md | 15-20分 |
| **14KB** | docs/planning/USER_FLOW_MAPPING.md | 15-20分 |
| **11KB** | docs/planning/FEATURE_ANALYSIS.md | 10-15分 |
| **11KB** | docs/migration/MIGRATION_TO_SQL.md | 10-15分 |
| **11KB** | docs/architecture/APP_STRUCTURE.md | 10-15分 |
| **10KB** | docs/getting-started/DEVELOPMENT_GUIDE.md | 10分 |
| **7-8KB** | その他 | 5-10分 |

---

## 🎯 状況別おすすめパス

### 「今すぐ開発を始めたい」

```
1. README.md (5分)
2. docs/architecture/SYSTEM_DIAGRAMS.md (10分) - 図で理解
3. docs/getting-started/DEVELOPMENT_GUIDE.md (10分)
4. TASKS.md (5分) - 何を作るか決める
```

**合計30分** → 開発開始！

---

### 「アーキテクチャをしっかり理解したい」

```
1. docs/architecture/SYSTEM_DIAGRAMS.md (10分) - 全体像
2. docs/architecture/LAYERED_ARCHITECTURE.md (40分) - 詳細
3. docs/architecture/APP_STRUCTURE.md (15分) - 動作フロー
4. docs/architecture/LOGIN_AND_DECORATORS.md (30分) - 認証
```

**合計1時間35分** → 完全理解！

---

### 「技術選定の背景を知りたい」

```
1. docs/planning/ARCHITECTURE_DECISIONS.md (10分) - 技術決定
2. docs/planning/FEATURE_ANALYSIS.md (15分) - 機能分析
3. docs/archive/CHAT_HISTORY_2025-12-06.md (任意) - 議論の記録
```

**合計25分** → 判断材料が揃う！

---

### 「過去の経緯を知りたい」

```
1. docs/archive/CHAT_HISTORY_2025-12-06.md - 2025年12月の技術選定議論
2. docs/archive/memo_2026-02-22.md - 2026年2月のUI改善案メモ
3. TASKS.md - 実装履歴を確認
```

---

## 💡 Tips

### ドキュメントの更新ルール

- **README.md**: プロジェクト概要が変わった時に更新
- **PLAN.md**: フェーズが進んだ時、大きなマイルストーンごとに更新
- **TASKS.md**: 機能を実装したら即座に更新
- **INDEX.md**: ドキュメントを追加/削除した時に更新

### 迷った時は

1. まず `INDEX.md` (このファイル) を見る
2. それでもわからなければ `README.md` を見る
3. 開発計画を知りたければ `PLAN.md` を見る

### GitHubで見る

このプロジェクトはGitHub上でも閲覧できます。Markdown + Mermaid図が自動レンダリングされます。

---

## 📝 ドキュメント作成のルール

新しいドキュメントを作成する際は、以下を守ってください：

1. **適切なフォルダに配置**
   - 初心者向け → `docs/getting-started/`
   - 設計書 → `docs/architecture/`
   - 計画書 → `docs/planning/`
   - 移行計画 → `docs/migration/`
   - 古いもの → `docs/archive/`

2. **INDEX.md を更新**
   - 新しいドキュメントを追加したら必ず INDEX.md に追記

3. **ファイル名規則**
   - 大文字アンダースコア（例: `MY_DOCUMENT.md`）
   - 日付付きアーカイブ（例: `memo_2026-03-15.md`）

4. **先頭にメタ情報**
   ```markdown
   # タイトル
   
   **作成日**: YYYY-MM-DD
   **更新日**: YYYY-MM-DD
   **対象者**: 開発者 / PM / 全員
   ```

---

## 🔗 外部リソース

- **GitHubリポジトリ**: (設定されている場合)
- **Mermaid Live Editor**: https://mermaid.live/ （図の編集）
- **Supabase**: https://supabase.com （無料PostgreSQL）

---

最終更新: 2026-03-15  
管理者: プロジェクトチーム
