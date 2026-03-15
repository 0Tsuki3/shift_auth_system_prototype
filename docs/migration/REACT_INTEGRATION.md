# React統合計画

**最終更新**: 2026-02-23

## 概要

スプレッドシート形式のシフト編集画面を実装するため、Reactを導入します。
段階的なアプローチを採用し、必要に応じてアーキテクチャを進化させます。

---

## 採用アプローチ

### ✅ **フェーズ1: ハイブリッド構成（現在）**

**目的**: 最速で価値を提供し、運用で評価する

```
┌─────────────────────────────────────┐
│         Flask Application           │
│  ┌─────────────────────────────┐   │
│  │  既存機能（Jinja2）          │   │
│  │  - ログイン                  │   │
│  │  - スタッフ管理              │   │
│  │  - 給料計算 etc.             │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  REST API（新規）            │   │
│  │  - /api/shift-requests/*    │   │
│  │  - /api/staff               │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  React SPA（新規）           │   │
│  │  - スプレッドシート編集      │   │
│  │  (static/js/shift-editor/)  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**メリット**:
- ✅ 既存コードをほぼ変更しない
- ✅ デプロイが簡単（1箇所のみ）
- ✅ 認証がそのまま使える（Flask Session）
- ✅ GCP App Engineで追加設定不要

**制約**:
- ⚠️ フロント・バックが同一デプロイ単位
- ⚠️ 大規模スケールには向かない

---

### 🚀 **フェーズ2: 完全分離構成（将来）**

**移行タイミング**（以下のいずれかが発生したとき）:
- [ ] 同時編集が頻発する（複数管理者の競合）
- [ ] レスポンスが遅くなる（スタッフ30人超）
- [ ] モバイルアプリを作る必要が出る
- [ ] 外部サービスとのAPI連携が必要になる
- [ ] SQL移行が完了している

```
┌──────────────────┐      ┌──────────────────┐
│   Flask API      │      │   React SPA      │
│   (Cloud Run)    │◄─────│ (Firebase/GCS)   │
│                  │ CORS │                  │
│  /api/*          │      │  スプレッド編集  │
└──────────────────┘      └──────────────────┘
```

**メリット**:
- ✅ フロント・バックの独立スケール
- ✅ フロントエンドのCDN配信（高速化）
- ✅ 複数クライアント対応（Web/Mobile）
- ✅ チーム分業しやすい

**追加コスト**:
- ⚠️ CORS設定が必要
- ⚠️ 認証方式の変更（Cookie → JWT検討）
- ⚠️ デプロイが2箇所になる
- ⚠️ インフラコスト増（Cloud Run + Firebase）

**移行工数**: 2-3日程度
- Day 1: Flask CORS設定 + React環境変数化
- Day 2: GCPデプロイ設定（Cloud Run + Firebase）
- Day 3: 動作確認 + ドキュメント更新

---

## フェーズ1: 実装詳細

### 1. プロジェクト構造

```
shift_auth_system_prototype/
├── app.py                      # Flask本体
├── requirements.txt            # Python依存関係
│
├── frontend/                   # Reactプロジェクト（新規）
│   ├── package.json
│   ├── vite.config.js         # ビルド先: ../static/js/shift-editor/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SpreadsheetEditor.jsx
│   │   │   ├── ShiftCell.jsx
│   │   │   └── EditModal.jsx
│   │   └── main.jsx
│   └── index.html
│
├── static/
│   ├── css/
│   └── js/
│       └── shift-editor/      # Reactビルド出力先
│           ├── index.js
│           └── assets/
│
├── templates/
│   ├── admin_shift_requests.html        # 既存
│   └── admin_shift_editor_spa.html      # 新規（Reactホスト）
│
└── routes/
    └── admin.py               # API追加
```

---

### 2. Flask側の変更

#### 2.1 新規エンドポイント（routes/admin.py）

```python
from flask import Blueprint, jsonify, request, render_template
from core.decorators import login_required, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ============================
# React SPA ホストページ
# ============================
@admin_bp.route('/shift-editor/<month>')
@login_required
@admin_required
def shift_editor_spa(month):
    """Reactベースのスプレッドシート編集画面"""
    return render_template('admin_shift_editor_spa.html', month=month)


# ============================
# REST API（JSON）
# ============================
@admin_bp.route('/api/shift-requests/<month>', methods=['GET'])
@login_required
@admin_required
def api_shift_requests_list(month):
    """指定月のシフト希望一覧を取得"""
    try:
        requests = shift_request_service.get_requests_by_month(month)
        staff_dict = {s.id: s for s in staff_service.get_all_staff()}
        
        result = []
        for req in requests:
            staff = staff_dict.get(req.staff_id)
            result.append({
                'id': req.id,
                'staff_id': req.staff_id,
                'staff_name': staff.name if staff else '不明',
                'position': staff.position if staff else '',
                'date': req.date.isoformat(),
                'start': req.start.strftime('%H:%M'),
                'end': req.end.strftime('%H:%M'),
                'duration_hours': req.duration_hours(),
                'type': req.type,
                'note': req.note,
                'is_read': req.is_read,
                'created_at': req.created_at.isoformat() if req.created_at else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/shift-requests/<request_id>', methods=['PATCH'])
@login_required
@admin_required
def api_shift_request_update(request_id):
    """シフト希望を更新"""
    try:
        data = request.get_json()
        
        # バリデーション（既存のvalidatorを使用）
        # 更新処理（既存のserviceを使用）
        
        return jsonify({'message': 'Updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@admin_bp.route('/api/shift-requests/<request_id>/read', methods=['PATCH'])
@login_required
@admin_required
def api_shift_request_toggle_read(request_id):
    """既読/未読をトグル"""
    try:
        # 実装は既存のロジックを流用
        return jsonify({'message': 'Toggled'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@admin_bp.route('/api/staff', methods=['GET'])
@login_required
@admin_required
def api_staff_list():
    """スタッフ一覧を取得"""
    try:
        staff_list = staff_service.get_all_staff()
        result = [{
            'id': s.id,
            'name': s.name,
            'position': s.position,
            'hourly_wage': s.hourly_wage
        } for s in staff_list]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### 2.2 Reactホストテンプレート（templates/admin_shift_editor_spa.html）

```html
{% extends "base.html" %}

{% block title %}シフト希望編集 - {{ month }}{% endblock %}

{% block content %}
<!-- Reactアプリのマウント先 -->
<div id="root" data-month="{{ month }}"></div>

<!-- ビルド済みReactアプリ -->
<script type="module" src="{{ url_for('static', filename='js/shift-editor/index.js') }}"></script>
{% endblock %}
```

---

### 3. React側の実装

#### 3.1 セットアップ

```bash
# プロジェクトルートで実行
mkdir frontend
cd frontend

# Viteプロジェクト作成
npm create vite@latest . -- --template react
npm install

# 追加パッケージ
npm install axios date-fns
```

#### 3.2 vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static/js/shift-editor',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5050',
        changeOrigin: true
      }
    }
  }
})
```

#### 3.3 コンポーネント例（SpreadsheetEditor.jsx）

```jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import { format, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns'
import { ja } from 'date-fns/locale'

export function SpreadsheetEditor({ month }) {
  const [requests, setRequests] = useState([])
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [month])

  const fetchData = async () => {
    try {
      const [reqRes, staffRes] = await Promise.all([
        axios.get(`/api/shift-requests/${month}`),
        axios.get(`/api/staff`)
      ])
      
      setRequests(reqRes.data)
      setStaff(staffRes.data)
    } catch (error) {
      console.error('データ取得エラー:', error)
    } finally {
      setLoading(false)
    }
  }

  // 日付リストを生成
  const monthDate = new Date(month + '-01')
  const days = eachDayOfInterval({
    start: startOfMonth(monthDate),
    end: endOfMonth(monthDate)
  })

  // スタッフごとにリクエストをグループ化
  const requestsByStaff = staff.reduce((acc, s) => {
    acc[s.id] = requests.filter(r => r.staff_id === s.id)
    return acc
  }, {})

  const toggleRead = async (requestId) => {
    try {
      await axios.patch(`/api/shift-requests/${requestId}/read`)
      fetchData() // リフレッシュ
    } catch (error) {
      console.error('更新エラー:', error)
    }
  }

  if (loading) return <div>読み込み中...</div>

  return (
    <div className="spreadsheet-container">
      {/* ヘッダー：日付 */}
      <div className="spreadsheet-header">
        <div className="staff-name-column">スタッフ</div>
        {days.map(day => (
          <div key={day} className="date-column">
            {format(day, 'M/d', { locale: ja })}
            <br />
            {format(day, 'E', { locale: ja })}
          </div>
        ))}
      </div>

      {/* ボディ：スタッフ × 日付 */}
      {staff.map(s => (
        <div key={s.id} className="staff-row">
          <div className="staff-name-column">
            <strong>{s.name}</strong>
            <div className="position">{s.position}</div>
          </div>
          {days.map(day => {
            const dayStr = format(day, 'yyyy-MM-dd')
            const req = requestsByStaff[s.id]?.find(r => r.date === dayStr)
            
            return (
              <div 
                key={dayStr} 
                className={`shift-cell ${req ? 'has-request' : ''} ${req?.is_read ? 'read' : 'unread'}`}
                onClick={() => req && toggleRead(req.id)}
              >
                {req ? (
                  <>
                    <div className="time">
                      {req.start} - {req.end}
                    </div>
                    {req.note && <div className="note">💬</div>}
                    <div className="status">
                      {req.is_read ? '✓' : '未読'}
                    </div>
                  </>
                ) : (
                  <div className="empty">─</div>
                )}
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}
```

---

### 4. 開発フロー

#### 開発時

```bash
# Terminal 1: Flask起動
source venv/bin/activate
python app.py

# Terminal 2: Vite開発サーバー
cd frontend
npm run dev
```

→ http://localhost:5173 でReactアプリを開発（Flaskへプロキシ）

#### ビルド

```bash
cd frontend
npm run build
# → static/js/shift-editor/ に出力
```

#### デプロイ

```bash
# ビルド
cd frontend && npm run build && cd ..

# Git commit
git add .
git commit -m "feat: Reactスプレッドシート編集画面を実装"
git push origin main

# GCP App Engine デプロイ
gcloud app deploy
```

---

### 5. GCP App Engine設定

**app.yaml** （変更不要）

```yaml
runtime: python39
entrypoint: gunicorn -b :$PORT app:app

handlers:
  # 静的ファイル（React含む）
  - url: /static
    static_dir: static
    secure: always
  
  # その他はFlaskへ
  - url: /.*
    script: auto
    secure: always
```

**ビルド済みファイルをGitに含める**:
- `static/js/shift-editor/` をコミット対象に
- `.gitignore` で `frontend/node_modules/` は除外

---

## フェーズ2: 完全分離構成への移行（将来）

### 移行時の変更点

#### 1. Flask側

```python
# requirements.txt に追加
flask-cors==4.0.0

# app.py
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # CORS設定
    CORS(app, 
         origins=['https://your-frontend.web.app'],  # Firebaseドメイン
         supports_credentials=True)  # Cookie認証継続
    
    # 以下は既存のまま
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    ...
```

#### 2. React側

```javascript
// .env.production
VITE_API_URL=https://your-api.run.app

// api.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true  // Cookie送信
})

export default api
```

#### 3. デプロイ

```bash
# Flask → Cloud Run
gcloud run deploy shift-api \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated

# React → Firebase Hosting
cd frontend
npm run build
firebase deploy --only hosting
```

---

## まとめ

### 現在の方針
- ✅ **アプローチ1（ハイブリッド構成）** で実装開始
- ✅ まずは動くものを作り、価値を確認
- ✅ 運用しながら必要性を評価

### 将来の選択肢
- 🔄 スケールが必要になったら **アプローチ3（完全分離）** へ移行
- 🔄 移行コストは低い（2-3日）
- 🔄 段階的な進化が可能

### 次のステップ
1. フロントエンドプロジェクトのセットアップ
2. Flask API実装
3. Reactスプレッドシート画面実装
4. デプロイテスト

**詳細な実装タスクは `TASKS.md` のフェーズ4Bを参照**
