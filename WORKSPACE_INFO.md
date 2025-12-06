# ワークスペース情報

## このフォルダについて

作成日: 2025-12-06  
元フォルダ: `/Users/tsuki3/shift_auth_system_prototype/`

このフォルダは開発用フォルダから最新のコードをコピーして作成されました。

## チャット履歴

詳細なチャット履歴は `CHAT_HISTORY_2025-12-06.md` を参照してください。

## 重要なドキュメント

1. **CHAT_HISTORY_2025-12-06.md** - 今日の会話の全記録
2. **ARCHITECTURE_DECISIONS.md** - アーキテクチャ決定記録
3. **MIGRATION_TO_SQL.md** - SQL移行計画
4. **SUPABASE_SETUP.md** - Supabaseセットアップガイド
5. **FEATURE_ANALYSIS.md** - 機能分析と需要判断

## 次のステップ

### SQL化を進める場合

1. Supabaseアカウント作成
2. `SUPABASE_SETUP.md` に従ってセットアップ
3. データマイグレーション実行
4. コード修正

### そのまま使う場合

```bash
# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# アプリ起動
python main.py

# ブラウザで開く
# http://localhost:8080
```

## 重要な意思決定まとめ

### プラットフォーム
- ✅ GCP App Engine（現状維持）
- ✅ Supabase無料プラン（SQL化する場合）
- ❌ AWS Lightsail（2度手間）

### コスト
- 現状: ¥3,000/月
- SQL化後: ¥3,000/月（Supabase無料）
- または: ¥4,780/月（Cloud SQL使用）

### 機能方針
- ✅ シフト管理に集中
- ⚠️ 在庫管理は分離検討
- ⚠️ マニュアルはオプション化

## 現在の状態

✅ アプリは完全に動作
✅ 9月まで実績データあり
✅ 全機能が利用可能
✅ ローカルで即起動可能

---

作成: 2025-12-06  
目的: 作業環境の記録

