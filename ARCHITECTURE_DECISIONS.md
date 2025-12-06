# アーキテクチャ決定記録 (Architecture Decision Record)

## 現在の技術スタック

### フレームワーク・言語
- **Python 3.x**
- **Flask 2.0.1**
- **Gunicorn 20.1.0** (WSGIサーバー)

### データ管理
- **方式**: CSVファイルベース
- **ライブラリ**: pandas 1.5.3
- **SQL**: 未使用
- **理由**: シンプルな運用、小規模データ、バックアップが容易

### デプロイ環境
- **現在**: GCP App Engine
- **設定ファイル**: app.yaml, Procfile
- **リージョン**: asia-northeast1 (東京)

## 拡張計画

### 規模想定
- **Phase 1** (現在): 1店舗、20-30人
- **Phase 2** (近未来): 4-5店舗、合計80-150人
- **Phase 3** (将来): 公開サービス化、数百店舗〜数千人

### コスト試算

#### Phase 1 (現在)
- **構成**: GCP App Engine Standard
- **月額**: ¥3,000〜¥5,000
- **対応人数**: 50-60人まで余裕

#### Phase 2 (マルチテナント対応)
- **構成**: GCP App Engine (店舗別データ分離)
- **月額**: ¥5,000〜¥8,000
- **実装**: 店舗ID追加、データパス分離
- **期間**: 1-2週間

#### Phase 3 (公開サービス化)
- **構成**: GCP Cloud Run or GKE
- **月額**: ¥30,000〜¥100,000+ (従量制)
- **移行**: コンテナ化済みなら1-2日

## 技術的決定事項

### ✅ 採用する方針

1. **GCPでの継続運用**
   - 理由: 小規模・不定期アクセスに最適
   - コスト効率が高い
   - デプロイが簡単

2. **Docker化（コンテナ化）の実施**
   - 理由: 将来の移行作業を最小化
   - マルチクラウド対応の保険
   - Cloud Run へのスムーズな移行

3. **段階的拡張パス**
   ```
   App Engine → Cloud Run → GKE
   (移行1回、作業時間: 合計3-5日)
   ```

### ❌ 採用しない方針

1. **AWS Lightsail経由の移行**
   - 理由: 2度手間になる
   - Lightsail → EC2/ECS の再移行が必要
   - トータルコストが高い

2. **最初からAWS ECS/Fargate**
   - 理由: 小規模には過剰投資
   - 初期設定が複雑
   - コスト高（月額¥10,000〜¥15,000）

3. **早期のDB移行**
   - 理由: CSVで十分動作している
   - 必要になってから検討
   - コスト増加要因

## クラウドプラットフォーム比較

### GCP App Engine (現在)
- ✅ 従量課金（使わない時は安い）
- ✅ デプロイが簡単
- ✅ コールドスタート対策不要（許容範囲）
- ❌ ベンダーロックイン（ただしコンテナ化で解消可能）

### AWS Lightsail
- ✅ 定額制でわかりやすい
- ✅ 初期設定が簡単
- ❌ スケーリングに限界（最大$160プラン）
- ❌ 大規模化時に再移行必須

### AWS ECS/Fargate
- ✅ 無限のスケーラビリティ
- ✅ AWS エコシステム
- ❌ 小規模には過剰
- ❌ 設定が複雑（VPC、セキュリティグループ等）

## データベース移行の判断基準

### CSV → SQL 移行を検討すべきタイミング

- [ ] 同時アクセスユーザーが50人を超える
- [ ] データの整合性エラーが頻発
- [ ] 複雑な検索クエリが必要になる
- [ ] リアルタイム更新が必要
- [ ] データ量が10,000レコード超

### 推奨DB（移行する場合）
1. **Cloud SQL (PostgreSQL)**: GCP環境なら最適
2. **Amazon RDS**: AWS移行時
3. **Supabase**: PostgreSQL + リアルタイム機能

## Next Steps（優先順位順）

### 1. Docker化（最優先）
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
```

### 2. マルチテナント対応
- 店舗ID機能の追加
- データパスの分離
- 管理画面での店舗切り替え

### 3. Cloud Run への移行（成長時）
```bash
gcloud run deploy shift-system \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated
```

### 4. データベース化（必要になった時）
- Cloud SQL PostgreSQL
- データマイグレーションスクリプト
- ORM導入（SQLAlchemy）

## 参考コスト比較（3年間の総コスト）

| 構成パス | 移行回数 | 総作業時間 | 総コスト |
|---------|---------|-----------|----------|
| **GCP App Engine → Cloud Run** | 1回 | 3日 | ¥450,000 |
| GCP → Lightsail → AWS | 2回 | 15日 | ¥600,000 |
| 最初からAWS ECS | 0回 | 初期7日 | ¥540,000 |

## 結論

**GCP App Engine でスタート → Docker化 → Cloud Run への段階的移行**が最適解。

---

最終更新: 2025-12-06
作成者: Architecture Review

