# CSV → SQL 移行計画

## 背景
- 現在: CSVファイルベースのデータ管理
- 課題: 同時アクセス、データ整合性、検索性能
- 目標: SQL化によるスケーラビリティ向上 + SQL学習の実践

## 移行方針

### 選択肢の比較

| 項目 | Cloud SQL | BigQuery | ハイブリッド |
|------|-----------|----------|-------------|
| **用途** | OLTP（トランザクション） | OLAP（分析） | 両方 |
| **適性** | ✅ 最適 | ⚠️ 過剰 | ✅ 理想的 |
| **コスト** | ¥10,000/月 | ¥500/月 | ¥10,500/月 |
| **学習** | SQL基礎 | BigQuery SQL | 両方 |
| **パフォーマンス** | リアルタイム◎ | バッチ◎ | 用途別◎ |

### 🎯 推奨: ハイブリッド構成

```
┌──────────────────────────────────┐
│  Flask アプリケーション           │
└────────┬─────────────────────────┘
         │
         ├─→ Cloud SQL (PostgreSQL)
         │   ├─ shifts テーブル
         │   ├─ staff テーブル
         │   ├─ shift_requests テーブル
         │   └─ auth テーブル
         │
         └─→ BigQuery (分析・レポート)
             ├─ shifts_analysis (日次同期)
             ├─ monthly_reports
             └─ staff_statistics
```

## Phase 1: Cloud SQL セットアップ

### 1.1 Cloud SQL インスタンス作成

```bash
# PostgreSQL インスタンス作成
gcloud sql instances create shift-system-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=asia-northeast1 \
    --storage-type=SSD \
    --storage-size=10GB

# データベース作成
gcloud sql databases create shift_db \
    --instance=shift-system-db

# ユーザー作成
gcloud sql users create shift_user \
    --instance=shift-system-db \
    --password=SECURE_PASSWORD
```

### 1.2 スキーマ設計

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

-- シフト希望テーブル
CREATE TABLE shift_requests (
    id SERIAL PRIMARY KEY,
    staff_id VARCHAR(50) REFERENCES staff(staff_id),
    date DATE NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    preferred_time VARCHAR(50),
    note TEXT,
    store_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 除外時間テーブル
CREATE TABLE exclude_times (
    id SERIAL PRIMARY KEY,
    staff_id VARCHAR(50) REFERENCES staff(staff_id),
    date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    reason TEXT,
    store_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- メモテーブル
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    note_type VARCHAR(50),  -- 'kitchen', 'order', 'notice'
    date DATE,
    content TEXT,
    store_id VARCHAR(50),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_shifts_date ON shifts(date);
CREATE INDEX idx_shifts_staff ON shifts(staff_id);
CREATE INDEX idx_shifts_store ON shifts(store_id);
CREATE INDEX idx_shift_requests_date ON shift_requests(date);
```

### 1.3 依存関係追加

```txt
# requirements.txt に追加
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23
alembic==1.13.0  # マイグレーションツール
```

### 1.4 データベース接続設定

```python
# utils/db_connection.py (新規作成)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 環境変数から接続情報取得
DB_USER = os.environ.get("DB_USER", "shift_user")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME", "shift_db")
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")

# GCP App Engine 環境では Unix socket 接続
if os.environ.get('GAE_ENV', '').startswith('standard'):
    db_socket_dir = "/cloudsql"
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={db_socket_dir}/{INSTANCE_CONNECTION_NAME}"
else:
    # ローカル開発環境では TCP 接続
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 1.5 モデル定義

```python
# models/staff.py (新規作成)
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from utils.db_connection import Base

class Staff(Base):
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    store_id = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## Phase 2: CSVデータのマイグレーション

### 2.1 マイグレーションスクリプト

```python
# scripts/migrate_csv_to_sql.py
import pandas as pd
from utils.db_connection import engine
from models import Staff, Auth, Shift, ShiftRequest

def migrate_staff():
    """staff.csv → staff テーブル"""
    df = pd.read_csv('staff.csv')
    df.to_sql('staff', engine, if_exists='append', index=False)
    print(f"Migrated {len(df)} staff records")

def migrate_auth():
    """auth.csv → auth テーブル"""
    df = pd.read_csv('auth.csv')
    df.to_sql('auth', engine, if_exists='append', index=False)
    print(f"Migrated {len(df)} auth records")

def migrate_shifts():
    """data/shift/*.csv → shifts テーブル"""
    import glob
    for file in glob.glob('data/shift/*.csv'):
        df = pd.read_csv(file)
        # 店舗IDをファイル名から抽出するなど
        df.to_sql('shifts', engine, if_exists='append', index=False)
        print(f"Migrated {file}")

if __name__ == "__main__":
    migrate_staff()
    migrate_auth()
    migrate_shifts()
```

## Phase 3: アプリケーションコード修正

### 3.1 CSV読み込みをSQL化

**Before (CSV):**
```python
# routes/staff.py
def get_shifts():
    df = pd.read_csv('data/shift/shift_2025-12.csv')
    return df
```

**After (SQL):**
```python
# routes/staff.py
from sqlalchemy import select
from models import Shift
from utils.db_connection import get_db

def get_shifts():
    db = next(get_db())
    query = select(Shift).where(Shift.date >= '2025-12-01')
    result = db.execute(query)
    return result.fetchall()
```

### 3.2 段階的移行（リスク軽減）

```python
# utils/data_access.py
import os

USE_SQL = os.environ.get('USE_SQL', 'False') == 'True'

def get_shifts(date):
    if USE_SQL:
        # SQL から取得
        return get_shifts_from_sql(date)
    else:
        # CSV から取得（既存コード）
        return get_shifts_from_csv(date)
```

## Phase 4: BigQuery 連携（分析用）

### 4.1 BigQuery データセット作成

```bash
# データセット作成
bq mk --dataset --location=asia-northeast1 shift_analytics

# テーブル作成（Cloud SQL と同じスキーマ）
bq mk --table shift_analytics.shifts_analysis \
    staff_id:STRING,date:DATE,time_slot:STRING,store_id:STRING
```

### 4.2 定期同期（Cloud Scheduler + Cloud Functions）

```python
# functions/sync_to_bigquery.py
from google.cloud import bigquery
import pandas as pd
from utils.db_connection import engine

def sync_shifts_to_bigquery(request):
    # Cloud SQL からデータ取得
    query = """
        SELECT * FROM shifts 
        WHERE updated_at > NOW() - INTERVAL '1 day'
    """
    df = pd.read_sql(query, engine)
    
    # BigQuery へアップロード
    client = bigquery.Client()
    table_id = "project.shift_analytics.shifts_analysis"
    
    job = client.load_table_from_dataframe(df, table_id)
    job.result()
    
    return f"Synced {len(df)} records"
```

### 4.3 分析クエリ例

```sql
-- BigQuery: 月次レポート
SELECT 
  staff_id,
  store_id,
  DATE_TRUNC(date, MONTH) as month,
  COUNT(*) as shift_count,
  SUM(TIMESTAMP_DIFF(end_time, start_time, HOUR)) as total_hours,
  AVG(TIMESTAMP_DIFF(end_time, start_time, HOUR)) as avg_hours_per_shift
FROM `project.shift_analytics.shifts_analysis`
WHERE date >= '2025-01-01'
GROUP BY staff_id, store_id, month
ORDER BY month DESC, shift_count DESC;

-- スタッフランキング（BigQueryの分析関数を活用）
SELECT 
  staff_id,
  shift_count,
  RANK() OVER (PARTITION BY store_id ORDER BY shift_count DESC) as rank_in_store,
  PERCENT_RANK() OVER (ORDER BY shift_count DESC) as percentile
FROM (
  SELECT staff_id, store_id, COUNT(*) as shift_count
  FROM `project.shift_analytics.shifts_analysis`
  GROUP BY staff_id, store_id
);
```

## コスト試算

### Cloud SQL
```
db-f1-micro（0.6GB RAM, 共有CPU）
- 月額: ¥10,000
- ストレージ: ¥100/月（10GB）
```

### BigQuery
```
- ストレージ: ¥500/月（10GB想定）
- クエリ: ¥0.6/GB
  └─ 月100GBスキャン想定: ¥60
合計: ¥560/月
```

### 合計
```
¥10,660/月（CSV時代は¥0）
```

## タイムライン

| Week | タスク | 所要時間 |
|------|--------|----------|
| 1 | Cloud SQL セットアップ、スキーマ設計 | 8h |
| 2 | モデル定義、接続設定 | 8h |
| 3 | CSVマイグレーションスクリプト作成 | 8h |
| 4 | データマイグレーション実行・検証 | 8h |
| 5-6 | アプリコード修正（段階的） | 16h |
| 7 | テスト・デバッグ | 8h |
| 8 | BigQuery 連携（オプション） | 8h |

**合計: 64時間（約2ヶ月、週末作業想定）**

## リスクと対策

### リスク1: データ移行の失敗
**対策**: 
- CSV バックアップ保持
- 段階的移行（フラグで切り替え）
- ロールバック手順の準備

### リスク2: パフォーマンス劣化
**対策**:
- 適切なインデックス設定
- クエリ最適化
- コネクションプーリング

### リスク3: コスト超過
**対策**:
- 最小インスタンス（db-f1-micro）でスタート
- BigQuery は分析時のみ使用
- コスト監視アラート設定

## Next Steps

1. ✅ この移行計画をレビュー
2. ⬜ Cloud SQL インスタンス作成
3. ⬜ スキーマ設計の詳細化
4. ⬜ マイグレーションスクリプト実装
5. ⬜ テスト環境での検証

---

作成日: 2025-12-06

