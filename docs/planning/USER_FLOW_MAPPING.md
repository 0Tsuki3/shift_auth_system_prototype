# ユーザーフロー・権限マッピング

**目的**: ユーザーの状態別にできること・ページ遷移を可視化する  
**最終更新**: 2025-12-06

---

## 🎭 ユーザーの種類と権限

```mermaid
graph TD
    A[訪問者] --> B{ログイン}
    B -->|管理者| C[👑 管理者<br/>role: admin]
    B -->|スタッフ| D[👔 スタッフ<br/>role: staff]
    B -->|失敗| A
    
    C --> E[全機能アクセス可能]
    D --> F[限定機能のみ]
    A --> G[公開情報のみ閲覧]
    
    style C fill:#ff6b6b
    style D fill:#4ecdc4
    style A fill:#95e1d3
```

---

## 📊 権限マトリクス

| 機能カテゴリ | 機能 | 👤 訪問者 | 👔 スタッフ | 👑 管理者 |
|-------------|------|----------|-----------|----------|
| **認証** | ログイン | ✅ | ✅ | ✅ |
| | ログアウト | - | ✅ | ✅ |
| **シフト閲覧** | 全体シフト表 | ✅ | ✅ | ✅ |
| | 自分のシフト | - | ✅ | ✅ |
| | シフト人数グラフ | ✅ | ✅ | ✅ |
| **シフト管理** | シフト希望提出 | - | ✅ | ✅ |
| | シフト編集 | - | - | ✅ |
| | シフト希望インポート | - | - | ✅ |
| | シフト確定 | - | - | ✅ |
| **スタッフ管理** | スタッフ一覧 | - | - | ✅ |
| | スタッフ追加 | - | - | ✅ |
| | スタッフ編集 | - | - | ✅ |
| | スタッフ削除 | - | - | ✅ |
| **アカウント管理** | アカウント作成 | - | - | ✅ |
| | アカウント削除 | - | - | ✅ |
| | パスワード変更 | - | - | ✅ |
| **業務情報** | マニュアル閲覧 | ✅ | ✅ | ✅ |
| | マニュアル編集 | - | - | ✅ |
| | 仕込みメモ閲覧 | ✅ | ✅ | ✅ |
| | 仕込みメモ編集 | - | - | ✅ |
| | 発注メモ閲覧 | ✅ | ✅ | ✅ |
| | 発注メモ編集 | - | - | ✅ |
| | お知らせ閲覧 | ✅ | ✅ | ✅ |
| | お知らせ編集 | - | - | ✅ |
| **在庫管理** | 在庫確認 | ✅ | ✅ | ✅ |
| | 在庫更新 | - | ✅ | ✅ |
| | 在庫アラート設定 | - | - | ✅ |

---

## 🗺️ ページ遷移図（全体）

```mermaid
graph TB
    Start([トップページ<br/>/]) --> Login{ログイン?}
    
    Login -->|いいえ| PublicArea[公開エリア]
    Login -->|スタッフ| StaffArea[スタッフエリア]
    Login -->|管理者| AdminArea[管理者エリア]
    
    PublicArea --> P1[シフト閲覧]
    PublicArea --> P2[マニュアル閲覧]
    PublicArea --> P3[メモ閲覧]
    PublicArea --> P4[在庫確認]
    
    StaffArea --> S1[シフト希望提出]
    StaffArea --> S2[自分のシフト確認]
    StaffArea --> S3[勤務グラフ]
    StaffArea --> S4[在庫更新]
    
    AdminArea --> A1[シフト編集]
    AdminArea --> A2[スタッフ管理]
    AdminArea --> A3[アカウント管理]
    AdminArea --> A4[マニュアル管理]
    AdminArea --> A5[全データ管理]
    
    P1 --> |ログイン必要な操作| LoginPage[/login]
    P2 --> |編集| LoginPage
    S1 --> |管理者機能| LoginPage
    
    LoginPage --> |認証成功| ReturnPage[元のページ]
    
    style PublicArea fill:#95e1d3
    style StaffArea fill:#4ecdc4
    style AdminArea fill:#ff6b6b
    style LoginPage fill:#ffd93d
```

---

## 🔄 ユーザーフロー（訪問者）

```mermaid
graph LR
    A[トップページ] --> B{何をする?}
    
    B -->|シフト確認| C[シフト表]
    B -->|マニュアル| D[マニュアル閲覧]
    B -->|メモ確認| E[メモ閲覧]
    B -->|在庫確認| F[在庫一覧]
    
    C --> G[カレンダー表示]
    C --> H[グラフ表示]
    
    D --> I[カテゴリ選択]
    I --> J[マニュアル詳細]
    
    E --> K[仕込みメモ]
    E --> L[発注メモ]
    E --> M[お知らせ]
    
    F --> N[ドリンク在庫]
    F --> O[アラート確認]
    
    style A fill:#95e1d3
    style C fill:#95e1d3
    style D fill:#95e1d3
    style E fill:#95e1d3
    style F fill:#95e1d3
```

---

## 🔄 ユーザーフロー（スタッフ）

```mermaid
graph TB
    A[ログイン] --> B[スタッフホーム]
    
    B --> C{何をする?}
    
    C -->|シフト希望| D[希望提出フォーム]
    D --> D1[日付選択]
    D1 --> D2[時間入力]
    D2 --> D3[確認]
    D3 --> D4[提出完了]
    
    C -->|自分のシフト| E[シフト確認]
    E --> E1[カレンダー表示]
    E --> E2[月別表示]
    
    C -->|勤務状況| F[グラフ表示]
    F --> F1[月別勤務時間]
    F --> F2[予定給与]
    
    C -->|在庫管理| G[在庫更新]
    G --> G1[数量入力]
    G1 --> G2[保存]
    
    C -->|公開情報| H[公開ページへ]
    H --> I[マニュアル/メモ]
    
    style A fill:#4ecdc4
    style B fill:#4ecdc4
    style D4 fill:#6bcf7f
    style G2 fill:#6bcf7f
```

---

## 🔄 ユーザーフロー（管理者）

```mermaid
graph TB
    A[ログイン] --> B[管理者ホーム]
    
    B --> C{管理項目}
    
    C -->|シフト管理| D[シフト管理]
    D --> D1[シフト編集]
    D --> D2[希望インポート]
    D --> D3[確定・公開]
    D --> D4[エクスポート]
    
    C -->|スタッフ管理| E[スタッフ管理]
    E --> E1[一覧表示]
    E --> E2[追加]
    E --> E3[編集]
    E --> E4[削除]
    
    C -->|アカウント管理| F[アカウント管理]
    F --> F1[一覧表示]
    F --> F2[新規作成]
    F --> F3[パスワード変更]
    F --> F4[権限変更]
    F --> F5[削除]
    
    C -->|マニュアル管理| G[マニュアル管理]
    G --> G1[アップロード]
    G --> G2[編集]
    G --> G3[カテゴリ管理]
    
    C -->|メモ管理| H[メモ管理]
    H --> H1[仕込みメモ編集]
    H --> H2[発注メモ編集]
    H --> H3[お知らせ編集]
    
    C -->|在庫管理| I[在庫管理]
    I --> I1[在庫更新]
    I --> I2[アラート設定]
    
    C -->|データ管理| J[データ管理]
    J --> J1[バックアップ]
    J --> J2[インポート]
    J --> J3[エクスポート]
    
    style A fill:#ff6b6b
    style B fill:#ff6b6b
    style D3 fill:#6bcf7f
    style F2 fill:#6bcf7f
    style G1 fill:#6bcf7f
```

---

## 📍 エンドポイントマップ（URL別）

### 公開エリア（認証不要）

```mermaid
graph LR
    A[/] --> B[トップページ]
    C[/login] --> D[ログイン]
    E[/shift/view] --> F[シフト表]
    G[/shift/graph/readonly] --> H[グラフ]
    I[/manual/view] --> J[マニュアル]
    K[/manual/memo/kitchen] --> L[仕込みメモ]
    M[/manual/memo/order] --> N[発注メモ]
    O[/manual/memo/notice] --> P[お知らせ]
    Q[/stock] --> R[在庫]
    S[/monthly_shift/YYYY-MM] --> T[月別シフト]
    
    style B fill:#95e1d3
    style D fill:#ffd93d
    style F fill:#95e1d3
    style H fill:#95e1d3
    style J fill:#95e1d3
    style L fill:#95e1d3
    style N fill:#95e1d3
    style P fill:#95e1d3
    style R fill:#95e1d3
    style T fill:#95e1d3
```

### スタッフエリア（ログイン必要）

```mermaid
graph LR
    A[/staff/home] --> B[ホーム]
    C[/staff/submit] --> D[シフト希望提出]
    E[/staff/view] --> F[自分のシフト]
    G[/staff/graph] --> H[勤務グラフ]
    I[/staff/upload] --> J[ファイルアップロード]
    
    style B fill:#4ecdc4
    style D fill:#4ecdc4
    style F fill:#4ecdc4
    style H fill:#4ecdc4
    style J fill:#4ecdc4
```

### 管理者エリア（admin権限必要）

```mermaid
graph TB
    A[/admin/home] --> B[管理者ホーム]
    
    C[/admin/edit] --> D[シフト編集]
    E[/admin/import] --> F[希望インポート]
    G[/admin/export] --> H[エクスポート]
    
    I[/admin/panel] --> J[スタッフ管理]
    K[/admin/add_staff] --> L[スタッフ追加]
    
    M[/admin/accounts] --> N[アカウント管理]
    O[/admin/accounts/create] --> P[アカウント作成]
    Q[/admin/accounts/delete] --> R[アカウント削除]
    
    S[/manual/upload] --> T[マニュアルアップロード]
    U[/manual/upload_image] --> V[画像アップロード]
    
    W[/exclude/api/*] --> X[除外時間API]
    
    style B fill:#ff6b6b
    style D fill:#ff6b6b
    style F fill:#ff6b6b
    style H fill:#ff6b6b
    style J fill:#ff6b6b
    style L fill:#ff6b6b
    style N fill:#ff6b6b
    style P fill:#ff6b6b
    style R fill:#ff6b6b
    style T fill:#ff6b6b
    style V fill:#ff6b6b
    style X fill:#ff6b6b
```

---

## 🔐 認証フロー

```mermaid
sequenceDiagram
    participant U as ユーザー
    participant B as ブラウザ
    participant S as サーバー
    participant D as データベース
    
    U->>B: /admin/edit にアクセス
    B->>S: GET /admin/edit
    S->>S: デコレーター: ログインチェック
    S->>S: session['role'] != 'admin'
    S-->>B: リダイレクト /login?next=/admin/edit
    
    B->>U: ログインフォーム表示
    U->>B: アカウント・パスワード入力
    B->>S: POST /login (+ next=/admin/edit)
    
    S->>D: 認証情報確認
    D-->>S: OK
    
    S->>S: session に保存
    S-->>B: リダイレクト /admin/edit
    
    B->>S: GET /admin/edit
    S->>S: デコレーター: ログインチェック
    S->>S: session['role'] == 'admin' ✓
    S-->>B: ページ表示
    B->>U: シフト編集画面
```

---

## 🎯 状態遷移図（ログイン状態）

```mermaid
stateDiagram-v2
    [*] --> 未ログイン
    
    未ログイン --> ログイン試行: /login にアクセス
    ログイン試行 --> ログイン済み_スタッフ: 認証成功（staff）
    ログイン試行 --> ログイン済み_管理者: 認証成功（admin）
    ログイン試行 --> 未ログイン: 認証失敗
    
    ログイン済み_スタッフ --> 未ログイン: ログアウト
    ログイン済み_管理者 --> 未ログイン: ログアウト
    
    未ログイン --> 未ログイン: 公開ページ閲覧
    ログイン済み_スタッフ --> ログイン済み_スタッフ: スタッフ機能利用
    ログイン済み_管理者 --> ログイン済み_管理者: 管理者機能利用
    
    note right of 未ログイン
        公開ページのみ閲覧可能
        - シフト表
        - マニュアル
        - メモ
        - 在庫
    end note
    
    note right of ログイン済み_スタッフ
        スタッフ機能
        - シフト希望提出
        - 自分のシフト確認
        - 在庫更新
    end note
    
    note right of ログイン済み_管理者
        全機能利用可能
        - シフト編集
        - スタッフ管理
        - アカウント管理
        - マニュアル管理
    end note
```

---

## 🎬 シナリオベースのフロー

### シナリオ1: スタッフがシフト希望を提出

```mermaid
graph TD
    A[スタッフがログイン] --> B[スタッフホーム]
    B --> C[シフト希望提出をクリック]
    C --> D[月選択画面]
    D --> E[希望フォーム表示]
    E --> F[日付と時間を入力]
    F --> G[確認画面]
    G --> H{OK?}
    H -->|修正| F
    H -->|提出| I[CSV保存]
    I --> J[完了メッセージ]
    J --> K[ホームに戻る]
    
    style A fill:#4ecdc4
    style I fill:#6bcf7f
    style J fill:#6bcf7f
```

### シナリオ2: 管理者がシフトを作成

```mermaid
graph TD
    A[管理者ログイン] --> B[管理者ホーム]
    B --> C[シフト編集をクリック]
    C --> D[月選択]
    D --> E[編集画面表示]
    
    E --> F[スタッフ希望をインポート]
    F --> G[CSVから読み込み]
    G --> H[希望を自動配置]
    
    H --> I[手動で調整]
    I --> J{確認}
    J -->|修正| I
    J -->|OK| K[CSV保存]
    
    K --> L[確定・公開]
    L --> M[全員がシフト閲覧可能に]
    
    style A fill:#ff6b6b
    style K fill:#6bcf7f
    style L fill:#6bcf7f
    style M fill:#6bcf7f
```

### シナリオ3: 訪問者がシフトを確認

```mermaid
graph TD
    A[トップページ] --> B[シフト表をクリック]
    B --> C[全体シフト表示]
    C --> D{表示形式選択}
    D -->|カレンダー| E[カレンダービュー]
    D -->|グラフ| F[人数グラフ]
    D -->|タイムライン| G[タイムラインビュー]
    
    E --> H[日付クリック]
    H --> I[その日の詳細]
    
    F --> J[日別人数確認]
    
    G --> K[時間別配置確認]
    
    style A fill:#95e1d3
    style C fill:#95e1d3
```

---

## 📝 エンドポイント一覧表（詳細版）

| URL | メソッド | 権限 | 機能 | ファイル |
|-----|---------|------|------|---------|
| `/` | GET | 公開 | トップページ | `routes/auth.py` |
| `/login` | GET/POST | 公開 | ログイン | `routes/auth.py` |
| `/logout` | GET | ログイン必要 | ログアウト | `routes/auth.py` |
| `/staff/home` | GET | スタッフ | ホーム | `routes/staff.py` |
| `/staff/submit` | GET/POST | スタッフ | シフト希望提出 | `routes/staff.py` |
| `/staff/view` | GET | スタッフ | 自分のシフト | `routes/staff.py` |
| `/staff/graph` | GET | スタッフ | 勤務グラフ | `routes/staff.py` |
| `/admin/home` | GET | 管理者 | 管理者ホーム | `routes/admin.py` |
| `/admin/edit` | GET/POST | 管理者 | シフト編集 | `routes/admin.py` |
| `/admin/import` | GET/POST | 管理者 | 希望インポート | `routes/admin.py` |
| `/admin/export` | GET | 管理者 | エクスポート | `routes/admin.py` |
| `/admin/panel` | GET | 管理者 | スタッフ管理 | `routes/admin.py` |
| `/admin/add_staff` | GET/POST | 管理者 | スタッフ追加 | `routes/admin.py` |
| `/shift/view` | GET | 公開 | シフト表 | `routes/shift_public.py` |
| `/shift/graph/readonly` | GET | 公開 | グラフ | `routes/shift_public.py` |
| `/manual/view` | GET | 公開 | マニュアル閲覧 | `routes/manual.py` |
| `/manual/upload` | GET/POST | 管理者 | アップロード | `routes/manual.py` |
| `/stock` | GET/POST | 公開 | 在庫管理 | `routes/stock.py` |
| `/stock/alert` | GET | 公開 | アラート | `routes/stock.py` |

---

## 🎯 まとめ

### 図の見方

- 🟢 **緑**: 公開（誰でも見れる）
- 🔵 **青**: スタッフ（ログイン必要）
- 🔴 **赤**: 管理者（admin権限必要）
- 🟡 **黄**: 認証関連

### 活用方法

1. **開発時**: 実装する機能の位置づけを確認
2. **レビュー時**: 権限設定の漏れをチェック
3. **説明時**: 新メンバーへの説明資料
4. **設計時**: 新機能の追加位置を検討

---

**VSCodeで図を表示するには**:
- 拡張機能「Markdown Preview Mermaid Support」をインストール
- このファイルをプレビュー（Cmd+Shift+V）で表示

**GitHubでも自動表示されます**:
- このファイルをプッシュするだけ
- 図が自動的にレンダリングされます

