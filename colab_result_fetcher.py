#!/usr/bin/env python3
"""
Colab Result Fetcher
- Monitors new files in the output folder on Google Drive
- Downloads them to the local output directory
- Logs the start and end time of the transfer
- Preserves file names as in Colab
"""

import os
import time
from datetime import datetime
from pathlib import Path

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# Settings
GOOGLE_DRIVE_OUTPUT_PATH = os.getenv('GOOGLE_DRIVE_OUTPUT_PATH', 'output')  # Output folder on Google Drive
LOCAL_OUTPUT_PATH = os.getenv('OUTPUT_DIR', './output')  # Local output folder
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT', 'service_account.json')  # Service account JSON key
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def get_folder_id(service, folder_name):
    results = service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                                   spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if not items:
        print(f"❌ Folder '{folder_name}' not found on Google Drive!")
        return None
    return items[0]['id']

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields='files(id, name, modifiedTime)').execute()
    return results.get('files', [])

def download_file(service, file_id, file_name, local_path):
    request = service.files().get_media(fileId=file_id)
    local_file = os.path.join(local_path, file_name)
    fh = open(local_file, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()
    print(f"✅ Downloaded: {file_name}")

def fetch_colab_results():
    print("🚀 Starting Colab Result Fetcher...")
    start_time = datetime.now()
    print(f"⏱️ Start: {start_time}")

    service = get_drive_service()
    folder_id = get_folder_id(service, GOOGLE_DRIVE_OUTPUT_PATH)
    if not folder_id:
        return

    Path(LOCAL_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    already_downloaded = set()
    print(f"📁 Monitoring Google Drive folder: {GOOGLE_DRIVE_OUTPUT_PATH}")
    print(f"📂 Local output: {LOCAL_OUTPUT_PATH}")

    while True:
        files = list_files_in_folder(service, folder_id)
        new_files = [f for f in files if f['name'] not in already_downloaded]
        if new_files:
            for f in new_files:
                download_file(service, f['id'], f['name'], LOCAL_OUTPUT_PATH)
                already_downloaded.add(f['name'])
        else:
            print("⏳ Waiting for new files...")
        # Stop if all 24 files are downloaded
        if len(already_downloaded) >= 24:
            break
        time.sleep(30)  # Check every 30 seconds

    end_time = datetime.now()
    print(f"⏱️ End: {end_time}")
    print(f"⏳ Total time: {end_time - start_time}")
    print(f"📊 Files downloaded: {len(already_downloaded)}")
    print("🏁 All results fetched!")

if __name__ == "__main__":
    fetch_colab_results()
