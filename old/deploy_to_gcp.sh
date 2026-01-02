#!/bin/bash

# GCP App Engine デプロイスクリプト

set -e

echo "🚀 GCP App Engine デプロイを開始します..."

# プロジェクトIDの確認
if [ -z "$1" ]; then
    echo "❌ プロジェクトIDを指定してください"
    echo "使用方法: ./deploy_to_gcp.sh YOUR_PROJECT_ID"
    exit 1
fi

PROJECT_ID=$1
BUCKET_NAME="shift-auth-system-data-$PROJECT_ID"

echo "📋 プロジェクトID: $PROJECT_ID"
echo "📦 バケット名: $BUCKET_NAME"

# 1. プロジェクトの設定
echo "🔧 プロジェクトを設定中..."
gcloud config set project $PROJECT_ID

# 2. 必要なAPIを有効化
echo "🔌 APIを有効化中..."
gcloud services enable appengine.googleapis.com
gcloud services enable storage.googleapis.com

# 3. Cloud Storage バケットを作成
echo "📦 Cloud Storage バケットを作成中..."
gsutil mb gs://$BUCKET_NAME || echo "バケットは既に存在します"

# 4. サービスアカウントを作成
echo "👤 サービスアカウントを作成中..."
gcloud iam service-accounts create shift-auth-system \
    --display-name="Shift Auth System Service Account" \
    || echo "サービスアカウントは既に存在します"

# 5. サービスアカウントキーを作成
echo "🔑 サービスアカウントキーを作成中..."
gcloud iam service-accounts keys create key.json \
    --iam-account=shift-auth-system@$PROJECT_ID.iam.gserviceaccount.com \
    || echo "キーファイルは既に存在します"

# 6. 権限を付与
echo "🔐 権限を付与中..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:shift-auth-system@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# 7. データをアップロード
echo "📤 データをアップロード中..."
if [ -d "data" ]; then
    gsutil -m cp -r data/* gs://$BUCKET_NAME/data/
    echo "✅ データのアップロードが完了しました"
else
    echo "⚠️  dataフォルダが見つかりません"
fi

# 8. アプリケーションをデプロイ
echo "🚀 アプリケーションをデプロイ中..."
gcloud app deploy --quiet

# 9. デプロイ完了
echo "✅ デプロイが完了しました！"
echo "🌐 アプリケーションURL:"
gcloud app browse --no-launch-browser

echo ""
echo "📋 次のステップ:"
echo "1. ブラウザでアプリケーションにアクセス"
echo "2. 管理者アカウントでログイン"
echo "3. データが正しく表示されることを確認"
echo ""
echo "🔧 トラブルシューティング:"
echo "- ログの確認: gcloud app logs tail"
echo "- インスタンスの確認: gcloud app instances list"
echo "- バケットの確認: gsutil ls gs://$BUCKET_NAME/" 