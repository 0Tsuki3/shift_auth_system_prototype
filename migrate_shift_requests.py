#!/usr/bin/env python3
"""
シフト希望データのマイグレーションスクリプト

旧フォーマット（status: pending/approved/rejected）から
新フォーマット（request_type: fixed, read_status: unread/read）に変換

実行方法:
    python3 migrate_shift_requests.py
"""

import os
import csv
import glob
from datetime import datetime


def migrate_csv_file(file_path):
    """
    1つのCSVファイルをマイグレーション
    
    Args:
        file_path: CSVファイルのパス
    """
    print(f"処理中: {file_path}")
    
    # ファイルを読み込む
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 旧statusを新read_statusに変換
            old_status = row.get('status', 'pending')
            if old_status == 'pending':
                read_status = 'unread'
            else:  # approved or rejected
                read_status = 'read'
            
            # 新フォーマットのデータを作成
            new_row = {
                'id': row['id'],
                'account': row['account'],
                'date': row['date'],
                'start': row['start'],
                'end': row['end'],
                'request_type': 'fixed',  # デフォルト値
                'read_status': read_status,
                'note': row.get('note', ''),
                'created_at': row.get('created_at', '')
            }
            rows.append(new_row)
    
    # バックアップを作成
    backup_path = file_path + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    os.rename(file_path, backup_path)
    print(f"  バックアップ作成: {backup_path}")
    
    # 新フォーマットで保存
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'account', 'date', 'start', 'end', 'request_type', 'read_status', 'note', 'created_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    
    print(f"  変換完了: {len(rows)}件のデータを変換しました")


def main():
    """
    メイン処理：全てのシフト希望CSVファイルをマイグレーション
    """
    print("=" * 60)
    print("シフト希望データマイグレーション")
    print("=" * 60)
    print()
    
    # data/shift_request/ 配下の全CSVファイルを取得
    csv_files = glob.glob('data/shift_request/shift_request_*.csv')
    
    if not csv_files:
        print("マイグレーション対象のCSVファイルが見つかりません")
        return
    
    print(f"{len(csv_files)}個のファイルを処理します")
    print()
    
    # 各ファイルをマイグレーション
    for csv_file in sorted(csv_files):
        try:
            migrate_csv_file(csv_file)
            print()
        except Exception as e:
            print(f"  エラー: {e}")
            print()
    
    print("=" * 60)
    print("マイグレーション完了")
    print("=" * 60)
    print()
    print("次の手順:")
    print("1. アプリケーションを起動してテストしてください")
    print("2. 問題なければバックアップファイル（*.backup_*）を削除できます")
    print("3. git add . && git commit -m 'feat: シフト希望を既読/未読ベースに変更'")


if __name__ == '__main__':
    main()
