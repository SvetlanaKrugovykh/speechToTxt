# faster_whisper_example.py
from faster_whisper import WhisperModel

def transcribe_audio_fast(file_path):
    try:
        # Load model once (can be moved to __init__)
        #model = WhisperModel("small", device="cpu", compute_type="int8")  #for speed, use "float32" for quality

        model = WhisperModel("small", device="cpu", compute_type="float32")  #for quality, use "int8" for speed
        
        # Transcription with settings optimized for mixed languages
        segments, info = model.transcribe(
            file_path, 
            language=None,  # Auto language detection
            beam_size=1,    # Faster but slightly lower quality
            best_of=1,      # Faster
            temperature=0   # More stable results
        )
        
        # Collect text from segments
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
            
        return transcription.strip(), None
        
    except Exception as e:
        return None, str(e)

# Installation:
# pip install faster-whisper
