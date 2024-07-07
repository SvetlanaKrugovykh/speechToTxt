import numpy

try:
    import whisper
except ImportError:
    print("Whisper is not available. Installing whisper...")

from src.converters.audio_converter import convert_to_wav

try:
    model = whisper.load_model("small") 
except Exception as e:
    print(f"Error loading Whisper model: {e}")

file_path = '/app/assets/audio/greeting.mp3'
wav_file_path = convert_to_wav(file_path)


# Transcribe the audio file
try:
    result = model.transcribe(wav_file_path)  
    print(result["text"])
except Exception as e:
    print(f"Error transcribing audio file: {e}")
