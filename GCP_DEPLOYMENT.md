# GCP App Engine デプロイ手順

## 前提条件
- Google Cloud Platform アカウント
- Google Cloud SDK がインストール済み
- プロジェクトが作成済み

## 1. Google Cloud SDK のセットアップ

```bash
# Google Cloud SDK のインストール（未インストールの場合）
# https://cloud.google.com/sdk/docs/install

# 認証
gcloud auth login

# プロジェクトの設定
gcloud config set project YOUR_PROJECT_ID
```

## 2. 必要なAPIの有効化

```bash
# App Engine API
gcloud services enable appengine.googleapis.com

# Cloud Storage API
gcloud services enable storage.googleapis.com
```

## 3. Cloud Storage バケットの作成

```bash
# バケットを作成（一意の名前が必要）
gsutil mb gs://shift-auth-system-data-YOUR_PROJECT_ID

# バケットを公開（必要に応じて）
gsutil iam ch allUsers:objectViewer gs://shift-auth-system-data-YOUR_PROJECT_ID
```

## 4. サービスアカウントキーの設定

```bash
# サービスアカウントキーを作成
gcloud iam service-accounts create shift-auth-system \
    --display-name="Shift Auth System Service Account"

# キーファイルをダウンロード
gcloud iam service-accounts keys create key.json \
    --iam-account=shift-auth-system@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 環境変数に設定
export GOOGLE_APPLICATION_CREDENTIALS="key.json"
```

## 5. アプリケーションのデプロイ

```bash
# アプリケーションをデプロイ
gcloud app deploy

# デプロイ後のURLを確認
gcloud app browse
```

## 6. データの移行

### ローカルデータをCloud Storageにアップロード

```bash
# dataフォルダ全体をアップロード
gsutil -m cp -r data/* gs://shift-auth-system-data-YOUR_PROJECT_ID/data/
```

## 7. 環境変数の設定

App Engine コンソールで以下の環境変数を設定：

```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
BUCKET_NAME=shift-auth-system-data-YOUR_PROJECT_ID
```

## 8. トラブルシューティング

### よくある問題

1. **権限エラー**
   ```bash
   # サービスアカウントに権限を付与
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:shift-auth-system@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/storage.admin"
   ```

2. **ファイルが見つからない**
   - Cloud Storage にデータが正しくアップロードされているか確認
   - バケット名が正しく設定されているか確認

3. **メモリ不足**
   - app.yaml の instance_class を F2 または F4 に変更

## 9. 監視とログ

```bash
# ログの確認
gcloud app logs tail

# インスタンスの確認
gcloud app instances list
```

## 10. カスタムドメインの設定（オプション）

```bash
# カスタムドメインをマッピング
gcloud app domain-mappings create YOUR_DOMAIN
```

## 注意事項

- 本番環境では適切なセキュリティ設定を行ってください
- 定期的なバックアップを設定してください
- コスト監視を設定してください 