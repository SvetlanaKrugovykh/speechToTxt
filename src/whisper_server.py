import numpy
import os
from pydub import AudioSegment

try:
    import whisper
except ImportError:
    print("Whisper is not available. Installing whisper...")

# from src.converters.audio_converter import convert_to_wav

# Load the Whisper model
try:
    model = whisper.load_model("small") 
except Exception as e:
    print(f"Error loading Whisper model: {e}")



def convert_to_wav(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    output_file_path = os.path.splitext(file_path)[0] + ".wav"
    if file_ext == ".wav":
        print("File is already in WAV format.")
        return file_path
    try:
        if file_ext == ".mp3":
            audio = AudioSegment.from_mp3(file_path)
        elif file_ext == ".ogg":
            audio = AudioSegment.from_ogg(file_path)
        elif file_ext == ".flac":
            audio = AudioSegment.from_file(file_path, "flac")
        else:
            print(f"Unsupported file format: {file_ext}")
            return None
        audio.export(output_file_path, format="wav")
        print(f"File converted to WAV: {output_file_path}")
        return output_file_path
    except Exception as e:
        print(f"Error converting file to WAV: {e}")
        return None


file_path = '/app/assets/audio/greeting.mp3'
wav_file_path = convert_to_wav(file_path)


# Transcribe the audio file
try:
    result = model.transcribe(wav_file_path)  
    print(result["text"])
except Exception as e:
    print(f"Error transcribing audio file: {e}")
