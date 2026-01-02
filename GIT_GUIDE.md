# Git 使い方ガイド（後で戻れるように）

## 🚀 よく使うコマンド（これだけ覚えればOK）

### 毎回使うコマンド

```bash
# 1. 状態確認
git status

# 2. 変更を保存（commit）
git add .
git commit -m "feat: Models層を実装"

# 3. リモートに送信（push）
git push origin main
```

### 振り返り用コマンド

```bash
# コミット履歴を見る（シンプル）
git log --oneline

# コミット履歴を見る（グラフ付き）
git log --oneline --graph --all

# 最近5件だけ見る
git log --oneline -5
```

### 戻るコマンド

```bash
# 特定のコミットに戻る（一時的に確認）
git checkout abc1234

# mainに戻る
git checkout main

# 完全に戻す（⚠️変更破棄）
git reset --hard abc1234
```

---

## 📋 基本的な流れ

### 1. 現在の状態を確認
```bash
git status
```
- 変更されたファイルが表示されます
- 赤色 = まだステージングされていない
- 緑色 = ステージング済み（コミット準備完了）

### 2. 変更をステージングに追加
```bash
# 全ての変更を追加
git add .

# 特定のファイルだけ追加
git add models/shift.py
git add models/staff.py

# フォルダごと追加
git add models/
```

### 3. コミット（セーブポイント作成）
```bash
# コミットメッセージ付きで保存
git commit -m "Models層を実装"

# 複数行のメッセージ
git commit -m "Models層を実装

- Shiftモデルを追加
- Staffモデルを追加
- Authモデルを追加"
```

### 4. リモートにプッシュ（オプション）
```bash
git push origin main
```

---

## 🔄 後で戻る方法

### コミット履歴を確認
```bash
# シンプルな履歴表示
git log --oneline

# 詳細な履歴表示
git log

# グラフィカルな履歴表示
git log --oneline --graph --all
```

出力例：
```
abc1234 Models層を実装
def5678 Repository層を実装
ghi9012 環境整備完了
```

### 特定のコミットに戻る

#### 一時的に確認するだけ（変更は保持）
```bash
git checkout abc1234
```
戻すには：
```bash
git checkout main
```

#### 完全に戻す（変更を破棄）
```bash
# ⚠️ 注意：これは元に戻せません
git reset --hard abc1234
```

#### 安全に戻す（新しいコミットとして戻す）
```bash
# 推奨：履歴を残したまま戻す
git revert abc1234
```

---

## 🌿 ブランチを使った安全な開発

### ブランチとは
別の作業ラインを作って、メインを壊さずに実験できる機能

```
main ───●───●───●───●
         \
          ●───●  feature/models
```

### ブランチの基本操作

#### 新しいブランチを作成して移動
```bash
# ブランチ作成 + 移動
git checkout -b feature/models

# または（Git 2.23以降）
git switch -c feature/models
```

#### ブランチ一覧を確認
```bash
git branch
```

#### ブランチを切り替え
```bash
git checkout main
git checkout feature/models
```

#### ブランチをマージ
```bash
# mainに戻る
git checkout main

# feature/modelsの変更をmainに統合
git merge feature/models
```

#### ブランチを削除
```bash
# マージ済みのブランチを削除
git branch -d feature/models

# 強制削除
git branch -D feature/models
```

---

## 📦 推奨ワークフロー（このプロジェクト用）

### レイヤーごとにコミット
```bash
# 1. Models層
git add models/
git commit -m "feat: Models層を実装"

# 2. Repository層
git add data_access/
git commit -m "feat: Repository層を実装"

# 3. Validators層
git add validators/
git commit -m "feat: Validators層を実装"

# 4. Services層
git add services/
git commit -m "feat: Services層を実装"

# 5. Presenters層
git add presenters/
git commit -m "feat: Presenters層を実装"

# 6. Core層
git add core/
git commit -m "feat: Core層（decorators）を実装"

# 7. Routes層
git add routes/
git commit -m "feat: Routes層を実装"

# 8. アプリケーション本体
git add app.py
git commit -m "feat: メインアプリケーションを作成"
```

### 安全なブランチ戦略
```bash
# 環境整備完了時点でコミット
git add .gitignore requirements.txt README.md
git commit -m "chore: プロジェクト環境整備"

# 新しい機能を実装する時
git checkout -b feature/layered-architecture

# 各レイヤーを実装してコミット
git add models/
git commit -m "feat: Models層を実装"

git add data_access/
git commit -m "feat: Repository層を実装"

# 全て完了したらmainにマージ
git checkout main
git merge feature/layered-architecture
```

---

## 🔍 よく使うコマンド

### 変更を確認
```bash
# 何が変わったか見る
git diff

# ステージング済みの変更を見る
git diff --staged

# 特定のファイルの変更を見る
git diff models/shift.py
```

### 間違えた時の対処

#### まだコミットしていない変更を取り消す
```bash
# 特定のファイルの変更を取り消す
git checkout -- models/shift.py

# 全ての変更を取り消す（⚠️注意）
git checkout -- .
```

#### ステージングを取り消す（変更は残す）
```bash
git reset HEAD models/shift.py
```

#### 直前のコミットメッセージを修正
```bash
git commit --amend -m "新しいメッセージ"
```

#### 直前のコミットにファイルを追加
```bash
# ファイルを追加
git add forgotten_file.py

# 直前のコミットに統合
git commit --amend --no-edit
```

---

## 📝 コミットメッセージのルール

### プレフィックスを使う
```
feat:     新機能
fix:      バグ修正
refactor: リファクタリング
docs:     ドキュメント
chore:    環境整備、雑務
test:     テスト追加
style:    コードフォーマット
```

### 例
```bash
git commit -m "feat: Shiftモデルにduration_hours()メソッドを追加"
git commit -m "fix: ShiftRepositoryのfind_by_month()のバグ修正"
git commit -m "refactor: Services層のエラーハンドリングを改善"
git commit -m "docs: README.mdにセットアップ手順を追加"
git commit -m "chore: .gitignoreに__pycache__を追加"
```

---

## 🚨 緊急時の対処

### 全部めちゃくちゃになった時
```bash
# 全ての変更を破棄して最後のコミットに戻る
git reset --hard HEAD

# 特定のコミットまで戻る
git reset --hard abc1234
```

### プッシュした後に戻したい時
```bash
# ⚠️ 他の人と共有している場合は使わない
git push --force

# 推奨：新しいコミットとして取り消す
git revert HEAD
git push
```

### 削除したファイルを復元
```bash
# 最後のコミットから復元
git checkout HEAD -- models/shift.py

# 特定のコミットから復元
git checkout abc1234 -- models/shift.py
```

---

## 🎯 このプロジェクトでの推奨戦略

1. **環境整備後にコミット**
   ```bash
   git add .gitignore requirements.txt README.md
   git commit -m "chore: プロジェクト環境整備"
   ```

2. **各レイヤー完成時にコミット**
   - 動作確認してからコミット
   - 1レイヤー = 1コミット

3. **定期的にプッシュ**（リモートがある場合）
   ```bash
   git push origin main
   ```

4. **大きな変更前はブランチを切る**
   ```bash
   git checkout -b feature/new-feature
   ```

5. **こまめにコミット**
   - 「後で戻れるポイント」を増やす
   - コミットは無料、ためらわない

---

## 📊 Git状態の確認

### 現在の状態を一目で確認
```bash
# 状態確認
git status

# 最近のコミット5件
git log --oneline -5

# ブランチ一覧
git branch

# リモートの状態
git remote -v
```

これで安全に開発を進められます！

