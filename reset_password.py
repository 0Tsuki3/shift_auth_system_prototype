#!/usr/bin/env python3
"""
パスワードリセットスクリプト

管理者とテストスタッフのパスワードをリセットします。
"""

from werkzeug.security import generate_password_hash
import csv

def reset_passwords():
    """パスワードをリセットしてauth.csvを更新"""
    
    # 新しいパスワード設定
    passwords = {
        'admin': 'admin123',        # 管理者：admin123
        'test_staff': 'staff123'    # テストスタッフ：staff123
    }
    
    print("=" * 50)
    print("パスワードリセットツール")
    print("=" * 50)
    print()
    print("新しいパスワードを生成中...")
    print()
    
    # パスワードハッシュ生成
    auth_data = [
        {
            'id': '1',
            'account': 'admin',
            'password': generate_password_hash('admin123'),
            'role': 'admin'
        },
        {
            'id': '2',
            'account': 'test_staff',
            'password': generate_password_hash('staff123'),
            'role': 'staff'
        }
    ]
    
    # auth.csvに書き込み
    with open('data/auth.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'account', 'password', 'role']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(auth_data)
    
    print("✅ パスワードをリセットしました！")
    print()
    print("=" * 50)
    print("ログイン情報")
    print("=" * 50)
    print()
    print("【管理者アカウント】")
    print(f"  アカウント: admin")
    print(f"  パスワード: admin123")
    print()
    print("【テストスタッフアカウント】")
    print(f"  アカウント: test_staff")
    print(f"  パスワード: staff123")
    print()
    print("=" * 50)
    print("http://localhost:5050/login でログインしてください")
    print("=" * 50)

if __name__ == '__main__':
    reset_passwords()
