from flask import Blueprint, request, jsonify
import os
import re
import sys
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

main = Blueprint('main', __name__)

try:
    import whisper
except ImportError:
    print("Whisper is not available. Installing whisper...")

from .converters.audio_converter import convert_to_wav

def check_authorization():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, jsonify({'error': 'Authorization header missing'}), 401

    auth_url = os.getenv('AUTH_URL')
    auth_response = requests.post(
        auth_url,
        headers={'Authorization': auth_header, 'Content-Type': 'application/json'},
        json={'token': auth_header},
        verify=False
    )

    if auth_response.status_code != 200:
        return None, jsonify({'error': 'Authorization failed'}), 401

    try:
        auth_data = auth_response.json()
    except ValueError:
        return None, jsonify({'error': 'Invalid JSON response from authorization server'}), 500

    if not isinstance(auth_data, dict) or not auth_data.get('decodedToken'):
        print('Authorization failed')
        return None, jsonify({'error': 'Authorization failed'}), 401

    decoded_token = auth_data['decodedToken']
    user_id = decoded_token['clientId']
    user_id = re.sub(r'[<>:"/\\|?*]', '_', user_id)
    return user_id, None, None

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