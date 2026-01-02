# Shift Authentication System Prototype

シフト管理システムのプロトタイプ（レイヤードアーキテクチャ版）

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
│   ├── staff.py              # スタッフモデル
│   └── auth.py               # 認証モデル
│
├── data_access/              # データアクセス層（Repository）
│   ├── shift_repository.py   # シフトデータアクセス
│   ├── staff_repository.py   # スタッフデータアクセス
│   └── auth_repository.py    # 認証データアクセス
│
├── validators/               # バリデーション層
│   ├── shift_validator.py    # シフトバリデーション
│   └── staff_validator.py    # スタッフバリデーション
│
├── services/                 # サービス層（ビジネスロジック）
│   ├── shift_service.py      # シフトサービス
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

```bash
python3 app.py
```

ブラウザで http://localhost:5050 にアクセス

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

下位レイヤーから上位レイヤーへ順に実装することを推奨します。

## デプロイ

### GCP App Engine へのデプロイ

```bash
gcloud app deploy
```

詳細は `old/GCP_DEPLOYMENT.md` を参照してください。

## ライセンス

Private Project

