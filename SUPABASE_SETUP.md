# Supabase セットアップガイド（無料プラン）

## なぜSupabase？

- ✅ **完全無料**: 500MB、無制限リクエスト
- ✅ **PostgreSQL**: 標準的なSQL、Cloud SQLと互換性高い
- ✅ **簡単セットアップ**: 5分で開始
- ✅ **認証機能付き**: Row Level Security（RLS）が強力
- ✅ **将来の移行が楽**: PostgreSQLなのでCloud SQLへも簡単

## セットアップ手順

### 1. Supabaseアカウント作成

```
1. https://supabase.com にアクセス
2. "Start your project" をクリック
3. GitHubアカウントでサインアップ（推奨）
```

### 2. プロジェクト作成

```
1. "New Project" をクリック
2. 設定:
   - Name: shift-auth-system
   - Database Password: 強力なパスワード（メモ！）
   - Region: Northeast Asia (Tokyo)
3. "Create new project" をクリック
```

### 3. データベース接続情報取得

```
1. Project Settings → Database
2. "Connection string" をコピー
   例: postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres
```

### 4. テーブル作成

SupabaseのSQL Editorで実行:

```sql
-- スタッフテーブル
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    staff_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    store_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 認証テーブル
CREATE TABLE auth (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    store_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- シフトテーブル
CREATE TABLE shifts (
    id SERIAL PRIMARY KEY,
    staff_id VARCHAR(50) REFERENCES staff(staff_id),
    date DATE NOT NULL,
    time_slot VARCHAR(50),
    start_time TIME,
    end_time TIME,
    position VARCHAR(50),
    store_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(staff_id, date, time_slot)
);

-- インデックス
CREATE INDEX idx_shifts_date ON shifts(date);
CREATE INDEX idx_shifts_staff ON shifts(staff_id);
CREATE INDEX idx_shifts_store ON shifts(store_id);
```

### 5. アプリケーション設定

#### 5.1 環境変数設定

```bash
# .env ファイル作成
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres
```

#### 5.2 requirements.txt 更新

```txt
# 既存のライブラリに追加
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23
supabase==2.3.0  # オプション: Supabase Python SDK
```

#### 5.3 データベース接続

```python
# utils/db_connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 6. CSVデータ移行

```python
# scripts/migrate_to_supabase.py
import pandas as pd
from sqlalchemy import create_engine
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# スタッフデータ
df_staff = pd.read_csv('staff.csv')
df_staff.to_sql('staff', engine, if_exists='append', index=False)
print(f"✅ Migrated {len(df_staff)} staff records")

# 認証データ
df_auth = pd.read_csv('auth.csv')
df_auth.to_sql('auth', engine, if_exists='append', index=False)
print(f"✅ Migrated {len(df_auth)} auth records")

# シフトデータ
import glob
for file in glob.glob('data/shift/*.csv'):
    df = pd.read_csv(file)
    df.to_sql('shifts', engine, if_exists='append', index=False)
    print(f"✅ Migrated {file}")
```

### 7. アプリケーションコード更新

#### Before (CSV):
```python
# routes/admin.py
def get_all_shifts():
    df = pd.read_csv('data/shift/shift_2025-12.csv')
    return df.to_dict('records')
```

#### After (Supabase/SQL):
```python
# routes/admin.py
from utils.db_connection import get_db
from sqlalchemy import select
from models import Shift

def get_all_shifts():
    db = next(get_db())
    result = db.query(Shift).filter(
        Shift.date >= '2025-12-01',
        Shift.date < '2026-01-01'
    ).all()
    return [shift.__dict__ for shift in result]
```

## Supabase Dashboard の活用

### 1. Table Editor
- GUIでデータ確認・編集
- CSVインポート/エクスポート

### 2. SQL Editor
- SQLクエリを直接実行
- クエリを保存・共有

### 3. Database
- テーブル構造確認
- インデックス管理
- リレーション確認

### 4. Logs
- クエリパフォーマンス確認
- エラーログ確認

## 無料プランの制限

```
✅ 500 MB データベース
   → 50-60人規模なら十分（数年分のシフトデータでも余裕）

✅ 2 GB 帯域/月
   → 月数千リクエスト程度なら問題なし

✅ 無制限 API リクエスト
   → 制限なし！

⚠️  2つまでプロジェクト
   → 本番・開発で2つ使える

⚠️  7日間のバックアップ保持
   → 定期的にエクスポート推奨
```

## コスト試算

### 無料プランで足りる期間

```
想定:
- スタッフ: 60人
- 月間シフト: 1,800件（60人 × 30日）
- 1レコード: 約0.5KB

計算:
- 1ヶ月: 0.9 MB
- 1年: 10.8 MB
- 10年: 108 MB

→ 500MBあれば40年以上使える！
```

### 有料プランへのアップグレード時期

```
Pro プラン ($25/月 = ¥3,750) にアップグレードが必要なのは:
- データが500MB超える時（数十店舗展開時）
- 帯域が2GB/月超える時（月数万リクエスト）
```

## 将来の移行パス

### Supabase → Cloud SQL への移行

```bash
# 1. Supabaseからデータをエクスポート
pg_dump -h db.xxx.supabase.co -U postgres -d postgres > backup.sql

# 2. Cloud SQLにインポート
gcloud sql import sql INSTANCE_NAME gs://BUCKET/backup.sql

# 3. 接続文字列を変更するだけ
DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/instance
```

**移行時間: 1時間程度**

## BigQuery連携（オプション）

```python
# Supabase → BigQuery 同期
from google.cloud import bigquery
import pandas as pd
from utils.db_connection import engine

def sync_to_bigquery():
    # Supabaseからデータ取得
    df = pd.read_sql("SELECT * FROM shifts", engine)
    
    # BigQueryへアップロード
    client = bigquery.Client()
    df.to_gbq('dataset.shifts', project_id='project')
```

## トラブルシューティング

### 接続エラー
```python
# SSL証明書エラーが出る場合
DATABASE_URL = "postgresql://...?sslmode=require"
```

### パフォーマンス改善
```sql
-- インデックス追加
CREATE INDEX idx_custom ON table_name(column_name);

-- EXPLAIN で確認
EXPLAIN ANALYZE SELECT * FROM shifts WHERE date = '2025-12-06';
```

## まとめ

**Supabase 無料プランで十分！**

- ✅ コスト: ¥0/月
- ✅ セットアップ: 30分
- ✅ PostgreSQL: 標準SQL学習に最適
- ✅ 将来性: Cloud SQLへ簡単移行可能

---

作成日: 2025-12-06
推奨: まずSupabaseで無料スタート！

