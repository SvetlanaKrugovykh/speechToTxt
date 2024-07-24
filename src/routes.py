from flask import Blueprint, request, jsonify
import os
import sys

main = Blueprint('main', __name__)

try:
    import whisper
except ImportError:
    print("Whisper is not available. Installing whisper...")

from .converters.audio_converter import convert_to_wav

def generate_filename(segment_number):
    segment_name = os.getenv('SEGMENT_NAME', 'segment')
    return f"{segment_name}_{segment_number}.wav"
    
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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        segment_number = request.form.get('segment', 'unknown')
        filename = generate_filename(segment_number)        
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        transcription, error = transcribe_audio(filepath)  
        sys.stdout.reconfigure(encoding='utf-8')
        print(f'File {filename}, Transcription: {transcription}')
        os.remove(filepath)
        if transcription:
            return jsonify({'message': f'File {filename} uploaded and transcribed successfully', 'transcription': transcription}), 200
        else:
            return jsonify({'error': 'Failed to transcribe audio', 'reason': error}), 500
