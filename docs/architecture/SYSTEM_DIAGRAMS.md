# システム構造図

このドキュメントでは、シフト認証システムの構造と処理フローを視覚的に説明します。

## 目次

1. [レイヤードアーキテクチャ全体図](#レイヤードアーキテクチャ全体図)
2. [シフト管理機能の処理フロー](#シフト管理機能の処理フロー)
3. [シフト追加処理の詳細フロー](#シフト追加処理の詳細フロー)
4. [モジュール依存関係図](#モジュール依存関係図)
5. [認証フローの図](#認証フローの図)

---

## レイヤードアーキテクチャ全体図

このシステムは7層のレイヤードアーキテクチャを採用しています。各レイヤーは下位レイヤーのみに依存します。

```mermaid
graph TB
    subgraph Layer7["🌐 Layer 7: Presentation (Routes)"]
        style Layer7 fill:#e3f2fd
        A1[routes/admin.py<br/>管理者機能]
        A2[routes/staff.py<br/>スタッフ機能]
        A3[routes/auth.py<br/>認証機能]
    end
    
    subgraph Layer6["🎨 Layer 6: Presenter (表示整形)"]
        style Layer6 fill:#fff3e0
        B1[shift_presenter.py<br/>カレンダー表示整形]
    end
    
    subgraph Layer5["⚙️ Layer 5: Service (ビジネスロジック)"]
        style Layer5 fill:#e8f5e9
        C1[shift_service.py<br/>シフト処理]
        C2[staff_service.py<br/>スタッフ処理]
        C3[shift_request_service.py<br/>シフト希望処理]
    end
    
    subgraph Layer4["✅ Layer 4: Validator (バリデーション)"]
        style Layer4 fill:#fce4ec
        D1[shift_validator.py<br/>シフト検証]
        D2[staff_validator.py<br/>スタッフ検証]
        D3[shift_request_validator.py<br/>シフト希望検証]
    end
    
    subgraph Layer3["💾 Layer 3: Repository (データアクセス)"]
        style Layer3 fill:#f3e5f5
        E1[shift_repository.py<br/>シフトCRUD]
        E2[staff_repository.py<br/>スタッフCRUD]
        E3[auth_repository.py<br/>認証CRUD]
        E4[shift_request_repository.py<br/>シフト希望CRUD]
    end
    
    subgraph Layer2["📦 Layer 2: Model (データ構造)"]
        style Layer2 fill:#e0f2f1
        F1[shift.py<br/>Shift]
        F2[staff.py<br/>Staff]
        F3[auth.py<br/>User]
        F4[shift_request.py<br/>ShiftRequest]
    end
    
    subgraph Layer1["📂 Layer 1: Data Source"]
        style Layer1 fill:#eceff1
        G1[(data/shift/*.csv)]
        G2[(data/staff.csv)]
        G3[(data/auth.csv)]
        G4[(data/shift_request/*.csv)]
    end
    
    A1 --> B1
    A1 --> C1
    A2 --> C1
    A2 --> C2
    A2 --> C3
    A3 --> E3
    
    B1 --> C1
    
    C1 --> D1
    C1 --> E1
    C2 --> D2
    C2 --> E2
    C3 --> D3
    C3 --> E4
    
    E1 --> F1
    E2 --> F2
    E3 --> F3
    E4 --> F4
    
    E1 --> G1
    E2 --> G2
    E3 --> G3
    E4 --> G4
```

**ポイント**:
- 上位レイヤーは下位レイヤーに依存（逆は禁止）
- 各レイヤーは明確な責務を持つ
- Presentationレイヤーは認証デコレーター（`@login_required`, `@admin_required`）で保護

---

## シフト管理機能の処理フロー

シフト一覧表示とシフト追加の処理フローを示します。

```mermaid
flowchart TB
    subgraph Presentation["📱 Presentation Layer (routes/admin.py)"]
        route_list["/shift/list<br/>shift_list()<br/>月別シフト一覧"]
        route_add["/shift/add<br/>shift_add()<br/>シフト追加"]
        route_edit["/shift/edit<br/>shift_edit()<br/>シフト編集"]
        route_delete["/shift/delete<br/>shift_delete()<br/>シフト削除"]
    end
    
    subgraph Presenter["🎨 Presenter Layer"]
        format_calendar["shift_presenter.py<br/>format_calendar_view()<br/>カレンダー形式に整形"]
    end
    
    subgraph Service["⚙️ Service Layer (shift_service.py)"]
        get_shifts["get_shifts_by_month()<br/>月別シフト取得"]
        add_shift["add_shift()<br/>シフト追加"]
        update_shift["update_shift()<br/>シフト更新"]
        delete_shift["delete_shift()<br/>シフト削除"]
    end
    
    subgraph Validator["✅ Validator Layer"]
        validate_shift["shift_validator.py<br/>validate_shift_data()<br/>シフトデータ検証"]
        validate_date["validate_date_format()<br/>日付形式検証"]
    end
    
    subgraph Repository["💾 Repository Layer"]
        repo_get["shift_repository.py<br/>get_by_month()<br/>月別データ取得"]
        repo_save["save()<br/>新規保存"]
        repo_update["update()<br/>更新"]
        repo_delete["delete()<br/>削除"]
    end
    
    subgraph DataSource["📂 Data Source"]
        csv[("data/shift/shift_YYYY-MM.csv")]
    end
    
    %% シフト一覧の流れ
    route_list --> get_shifts
    get_shifts --> repo_get
    repo_get --> csv
    csv -.データ返却.-> repo_get
    repo_get -.Shiftオブジェクト.-> get_shifts
    get_shifts -.シフトリスト.-> format_calendar
    format_calendar -.カレンダーデータ.-> route_list
    
    %% シフト追加の流れ
    route_add --> validate_shift
    validate_shift -.OK.-> add_shift
    add_shift --> repo_save
    repo_save --> csv
    
    %% シフト編集の流れ
    route_edit --> validate_shift
    validate_shift -.OK.-> update_shift
    update_shift --> repo_update
    repo_update --> csv
    
    %% シフト削除の流れ
    route_delete --> delete_shift
    delete_shift --> repo_delete
    repo_delete --> csv
    
    style route_list fill:#bbdefb
    style route_add fill:#c8e6c9
    style route_edit fill:#fff9c4
    style route_delete fill:#ffccbc
```

**処理の流れ**:
1. **取得**: Routes → Service → Repository → CSV → 逆順で返却 → Presenter → Routes
2. **追加/編集**: Routes → Validator → Service → Repository → CSV
3. **削除**: Routes → Service → Repository → CSV

---

## シフト追加処理の詳細フロー

ユーザーがシフトを追加する際の時系列フローを示します。

```mermaid
sequenceDiagram
    actor User as 👤 管理者
    participant Route as routes/admin.py<br/>shift_add()
    participant Valid as shift_validator.py<br/>validate_shift_data()
    participant Service as shift_service.py<br/>add_shift()
    participant StaffRepo as staff_repository.py<br/>get_by_id()
    participant ShiftRepo as shift_repository.py<br/>save()
    participant CSV as 📂 CSV File
    
    User->>Route: POST /shift/add<br/>{date, staff_id, start, end}
    
    Note over Route: 1. バリデーション
    Route->>Valid: validate_shift_data(form_data)
    
    alt データ不正
        Valid-->>Route: ValidationError
        Route-->>User: ❌ エラーメッセージ表示
    else データ正常
        Valid-->>Route: ✅ OK
        
        Note over Route: 2. ビジネスロジック実行
        Route->>Service: add_shift(shift_data)
        
        Note over Service: スタッフ存在確認
        Service->>StaffRepo: get_by_id(staff_id)
        StaffRepo-->>Service: Staff or None
        
        alt スタッフ不在
            Service-->>Route: ValueError("スタッフが存在しません")
            Route-->>User: ❌ エラー表示
        else スタッフ存在
            Note over Service: 3. データ保存
            Service->>ShiftRepo: save(shift)
            ShiftRepo->>CSV: 該当月のCSVに書き込み
            CSV-->>ShiftRepo: ✅ 保存成功
            ShiftRepo-->>Service: shift_id
            Service-->>Route: ✅ 追加成功
            
            Note over Route: 4. リダイレクト
            Route-->>User: 🔄 redirect("/shift/list")
        end
    end
```

**エラーハンドリング**:
- バリデーションエラー → フォームに戻る
- スタッフ不在エラー → エラーメッセージ表示
- CSV書き込みエラー → 500エラー

---

## モジュール依存関係図

各Pythonファイル間の依存関係を示します。

```mermaid
classDiagram
    %% Presentation Layer
    class RoutesAdmin {
        +shift_list()
        +shift_add()
        +shift_edit()
        +shift_delete()
        +staff_list()
        +staff_add()
        +salary_list()
    }
    
    class RoutesStaff {
        +my_shift()
        +my_salary()
    }
    
    class RoutesAuth {
        +login()
        +logout()
    }
    
    %% Presenter Layer
    class ShiftPresenter {
        +format_calendar_view(shifts, year, month)
        +format_shift_detail(shift)
    }
    
    %% Service Layer
    class ShiftService {
        -validator: ShiftValidator
        -shift_repo: ShiftRepository
        -staff_repo: StaffRepository
        +get_shifts_by_month(year, month)
        +add_shift(shift_data)
        +update_shift(shift_id, data)
        +delete_shift(shift_id, year_month)
    }
    
    class StaffService {
        -validator: StaffValidator
        -staff_repo: StaffRepository
        +get_all_staff()
        +add_staff(staff_data)
    }
    
    %% Validator Layer
    class ShiftValidator {
        +validate_shift_data(data)
        +validate_date_format(date_str)
        +validate_time_format(time_str)
    }
    
    class StaffValidator {
        +validate_staff_data(data)
        +validate_hourly_wage(wage)
    }
    
    %% Repository Layer
    class ShiftRepository {
        +get_by_month(year, month)
        +get_by_id(shift_id, year_month)
        +save(shift)
        +update(shift_id, year_month, data)
        +delete(shift_id, year_month)
    }
    
    class StaffRepository {
        +get_all()
        +get_by_id(staff_id)
        +save(staff)
    }
    
    class AuthRepository {
        +get_by_username(username)
        +verify_password(username, password)
    }
    
    %% 依存関係
    RoutesAdmin --> ShiftService
    RoutesAdmin --> StaffService
    RoutesAdmin --> ShiftPresenter
    
    RoutesStaff --> ShiftService
    
    RoutesAuth --> AuthRepository
    
    ShiftService --> ShiftValidator
    ShiftService --> ShiftRepository
    ShiftService --> StaffRepository
    
    StaffService --> StaffValidator
    StaffService --> StaffRepository
    
    ShiftPresenter --> ShiftService
```

**依存の方向**:
- Routes → Service/Presenter
- Service → Validator + Repository
- Presenter → Service
- Repository → CSV（図示省略）

---

## 認証フローの図

ログインから保護されたページへのアクセスまでのフロー。

```mermaid
sequenceDiagram
    actor User as 👤 ユーザー
    participant Browser as 🌐 ブラウザ
    participant Auth as routes/auth.py<br/>login()
    participant AuthRepo as auth_repository.py
    participant Session as Flask Session
    participant Admin as routes/admin.py<br/>@admin_required
    
    Note over User,Admin: ログイン処理
    User->>Browser: ログインフォーム送信
    Browser->>Auth: POST /login<br/>{username, password}
    
    Auth->>AuthRepo: verify_password(username, password)
    AuthRepo->>AuthRepo: パスワードハッシュ検証
    
    alt 認証失敗
        AuthRepo-->>Auth: False
        Auth-->>Browser: ❌ "ユーザー名またはパスワードが違います"
        Browser-->>User: エラー表示
    else 認証成功
        AuthRepo-->>Auth: True + User情報
        Auth->>Session: session['user_id'] = user_id<br/>session['role'] = role
        Session-->>Auth: ✅ セッション保存
        Auth-->>Browser: 🔄 redirect("/shift/list")
        Browser-->>User: ✅ ログイン成功
    end
    
    Note over User,Admin: 保護されたページへのアクセス
    User->>Browser: /shift/list にアクセス
    Browser->>Admin: GET /shift/list
    
    Note over Admin: @login_required デコレーター
    Admin->>Session: session.get('user_id')
    
    alt セッションなし
        Session-->>Admin: None
        Admin-->>Browser: 🔄 redirect("/login")
        Browser-->>User: ログインページへ
    else セッションあり
        Session-->>Admin: user_id
        
        Note over Admin: @admin_required デコレーター
        Admin->>Session: session.get('role')
        
        alt 管理者ではない
            Session-->>Admin: role = 'staff'
            Admin-->>Browser: ❌ 403 Forbidden
            Browser-->>User: "管理者権限が必要です"
        else 管理者
            Session-->>Admin: role = 'admin'
            Admin->>Admin: shift_list() 実行
            Admin-->>Browser: ✅ シフト一覧HTML
            Browser-->>User: ページ表示
        end
    end
```

**認証の仕組み**:
1. **ログイン**: パスワードハッシュ検証 → セッションに保存
2. **@login_required**: セッション確認 → なければログインページへ
3. **@admin_required**: ロール確認 → 管理者でなければ403エラー

詳細は [`LOGIN_AND_DECORATORS.md`](./LOGIN_AND_DECORATORS.md) を参照。

---

## 補足情報

### ダイアグラムの読み方

| 記号 | 意味 |
|------|------|
| `-->` | 実線矢印（直接呼び出し） |
| `-.->` | 点線矢印（データ返却） |
| `subgraph` | レイヤーやモジュールのグループ |
| `actor` | 人間のユーザー |
| `alt/else/end` | 条件分岐 |

### 関連ドキュメント

- **アーキテクチャ詳細**: [`LAYERED_ARCHITECTURE.md`](./LAYERED_ARCHITECTURE.md)
- **開発ガイド**: [`../getting-started/DEVELOPMENT_GUIDE.md`](../getting-started/DEVELOPMENT_GUIDE.md)
- **認証の仕組み**: [`LOGIN_AND_DECORATORS.md`](./LOGIN_AND_DECORATORS.md)
- **全体構造**: [`APP_STRUCTURE.md`](./APP_STRUCTURE.md)

---

## Mermaid図の編集方法

これらの図はMarkdown内にMermaid記法で記述されています。

- **オンラインエディタ**: [Mermaid Live Editor](https://mermaid.live/)
- **VSCode拡張**: Mermaid Preview
- **GitHub**: 自動レンダリング対応

図を更新したい場合は、このファイルを直接編集してください。
