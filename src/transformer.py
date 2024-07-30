# transformer.py
import os
import subprocess
import sys

try:
    import whisper
except ImportError:
    print("Whisper is not available. Installing whisper...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "whisper"])
    import whisper

try:
    from pydub import AudioSegment
except ImportError:
    print("pydub is not available. Installing pydub...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pydub"])
    from pydub import AudioSegment

from converters.audio_converter import convert_to_wav

def handle_file_upload(clientId, file, segment_number):
    if file.filename == '':
        return {"error": "No selected file"}, 400

    filename = generate_filename(segment_number, clientId)
    filepath = os.path.join('uploads', filename)
    
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())
    
    return filepath, filename

def generate_filename(segment_number, clientId):
    segment_name = os.getenv('SEGMENT_NAME', 'segment')
    return f"{clientId}_{segment_name}_{segment_number}.wav"
    
def transcribe_audio(file_path):
    try:
        model = whisper.load_model("small")
        wav_file_path = convert_to_wav(file_path)
        result = model.transcribe(wav_file_path)
        return result["text"], None 
        return "This is a test transcription", None
    except Exception as e:
        print(f"Error in audio transcription: {e}")
        return None, str(e)
    