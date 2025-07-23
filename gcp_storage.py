import os
from google.cloud import storage
import tempfile
import shutil

class GCPStorageManager:
    def __init__(self, bucket_name="shift-auth-system-data"):
        self.bucket_name = bucket_name
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(bucket_name)
            self.available = True
        except Exception as e:
            print(f"GCP Storage not available: {e}")
            self.available = False
        
    def upload_file(self, local_path, gcp_path):
        """ローカルファイルをGCPにアップロード"""
        if not self.available:
            print("GCP Storage not available")
            return
        blob = self.bucket.blob(gcp_path)
        blob.upload_from_filename(local_path)
        
    def download_file(self, gcp_path, local_path):
        """GCPからローカルにダウンロード"""
        if not self.available:
            print("GCP Storage not available")
            return
        blob = self.bucket.blob(gcp_path)
        blob.download_to_filename(local_path)
        
    def list_files(self, prefix=""):
        """指定されたプレフィックスのファイル一覧を取得"""
        if not self.available:
            print("GCP Storage not available")
            return []
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]
        
    def file_exists(self, gcp_path):
        """ファイルの存在確認"""
        if not self.available:
            print("GCP Storage not available")
            return False
        blob = self.bucket.blob(gcp_path)
        return blob.exists()
        
    def delete_file(self, gcp_path):
        """ファイルを削除"""
        if not self.available:
            print("GCP Storage not available")
            return
        blob = self.bucket.blob(gcp_path)
        blob.delete()

# データフォルダの同期
def sync_data_folder():
    """ローカルのdataフォルダとGCPを同期"""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    storage_manager = GCPStorageManager()
    if not storage_manager.available:
        print("GCP Storage not available, skipping sync")
        return
    
    # GCPからローカルにダウンロード
    for blob_name in storage_manager.list_files("data/"):
        local_path = blob_name
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        storage_manager.download_file(blob_name, local_path)
        
def backup_data_folder():
    """ローカルのdataフォルダをGCPにバックアップ"""
    storage_manager = GCPStorageManager()
    if not storage_manager.available:
        print("GCP Storage not available, skipping backup")
        return
    
    for root, dirs, files in os.walk("data"):
        for file in files:
            local_path = os.path.join(root, file)
            gcp_path = local_path
            storage_manager.upload_file(local_path, gcp_path) 