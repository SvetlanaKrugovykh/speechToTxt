#!/usr/bin/env python3
"""
Colab Result Fetcher
- Downloads all files from the specified Google Drive output folder (by ID)
- Saves them to the local output directory
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
GOOGLE_DRIVE_OUTPUT_FOLDER_ID = os.getenv('GOOGLE_DRIVE_OUTPUT_FOLDER_ID')  # Output folder ID for results
GOOGLE_DRIVE_AUDIO_FOLDER_ID = os.getenv('GOOGLE_DRIVE_AUDIO_FOLDER_ID')    # (Optional) Input audio folder ID
LOCAL_OUTPUT_PATH = os.getenv('OUTPUT_DIR', './output')  # Local output folder
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT', 'service_account.json')  # Service account JSON key
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    # Also get mimeType to skip Google Docs files
    results = service.files().list(q=query, fields='files(id, name, modifiedTime, mimeType)').execute()
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

    if not GOOGLE_DRIVE_OUTPUT_FOLDER_ID:
        print("❌ GOOGLE_DRIVE_OUTPUT_FOLDER_ID is not set in the environment!")
        return

    service = get_drive_service()
    folder_id = GOOGLE_DRIVE_OUTPUT_FOLDER_ID

    Path(LOCAL_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    already_downloaded = set()
    print(f"📁 Monitoring Google Drive output folder ID: {folder_id}")
    print(f"📂 Local output: {LOCAL_OUTPUT_PATH}")

    # Wait for all 24 files to appear in the output folder
    print("🔎 Waiting for all expected files to appear in Google Drive output folder...")
    while True:
        files = list_files_in_folder(service, folder_id)
        ready_files = [f for f in files if not f['mimeType'].startswith('application/vnd.google-apps.')]
        if len(ready_files) >= 24:
            colab_finish_time = datetime.now()
            print(f"✅ All expected files found in Google Drive output folder at: {colab_finish_time}")
            print(f"⏳ Time from start to all files ready: {colab_finish_time - start_time}")
            break
        else:
            print(f"⏳ Waiting... {len(ready_files)}/24 files present.")
        time.sleep(30)

    # Now download all files
    while True:
        files = list_files_in_folder(service, folder_id)
        new_files = [f for f in files if f['name'] not in already_downloaded and not f['mimeType'].startswith('application/vnd.google-apps.')]
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
