from flask import Blueprint, request, jsonify
import requests
import os
import re
import sys
import json
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

main = Blueprint('main', __name__)

try:
    import whisper
except ImportError:
    print("Whisper is not available. Installing whisper...")

from .converters.audio_converter import convert_to_wav

class SSLContextAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)

def check_authorization():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, jsonify({'error': 'Authorization header missing'}), 401

    auth_url = os.getenv('AUTH_URL')
    if not auth_url:
        return None, jsonify({'error': 'Authorization URL not set'}), 500

    ssl_context = create_urllib3_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    session = requests.Session()
    adapter = SSLContextAdapter(ssl_context)
    session.mount('https://', adapter)   

    try:
        auth_response = session.post(
            auth_url,
            headers={'Authorization': auth_header, 'Content-Type': 'application/json'},
            json={'token': auth_header},
            verify=False 
        )
        auth_response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None, json.dumps({'error': 'Authorization failed'}), 401
    except requests.exceptions.RequestException as req_err:
        print(f"Error during requests to {auth_url}: {req_err}")
        return None, json.dumps({'error': 'Authorization request failed'}), 500

    try:
        auth_data = auth_response.json()
    except ValueError:
        return None, json.dumps({'error': 'Invalid JSON response from authorization server'}), 500

    if not isinstance(auth_data, dict) or not auth_data.get('decodedToken'):
        print('Authorization failed')
        return None, json.dumps({'error': 'Authorization failed'}), 401

    decoded_token = auth_data['decodedToken']
    user_id = decoded_token['clientId']
    user_id = re.sub(r'[<>:"/\\|?*]', '_', user_id)
    print(f"User ID: {user_id}")
    return auth_data.get('user_id'), None, 200

def handle_file_upload(user_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    segment_number = request.form.get('segment', 'unknown')
    filename = generate_filename(segment_number, user_id)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    return filepath, filename

def generate_filename(segment_number, user_id=""):
    segment_name = os.getenv('SEGMENT_NAME', 'segment')
    return f"{user_id}_{segment_name}_{segment_number}.wav"
    
def transcribe_audio(file_path):
    try:
        model = whisper.load_model("small")
        wav_file_path = convert_to_wav(file_path)
        result = model.transcribe(wav_file_path)
        return result["text"], None 
    except Exception as e:
        print(f"Error in audio transcription: {e}")
        return None, str(e)  

@main.route('/upload', methods=['POST'])
def upload_audio():
    user_id = ""
    if int(os.getenv('CHECK_AUTHORIZATION', '0')) == 1:
        user_id, error_response, status_code = check_authorization()
        if error_response:
            return error_response, status_code

    filepath, filename = handle_file_upload(user_id)
    transcription, error = transcribe_audio(filepath)

    if int(os.getenv('TRANSCRIPTION_OUT_LOG', '0')) == 1:
        sys.stdout.reconfigure(encoding='utf-8')
        print(f"User ID: {user_id}")
        print(f'File {filename}, Transcription: {transcription}')

    os.remove(filepath)
    if transcription:
        return jsonify({'message': f'File {filename} uploaded and transcribed successfully', 'transcription': transcription}), 200
    else:
        return jsonify({'error': 'Failed to transcribe audio', 'reason': error}), 500