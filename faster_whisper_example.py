# faster_whisper_example.py
from faster_whisper import WhisperModel

def transcribe_audio_fast(file_path):
    try:
        # Load model once (can be moved to __init__)
        model_size = os.getenv('MODEL_SIZE')
        compute_type = os.getenv('COMPUTE_TYPE', 'int8')  # Default to int8 for speed
        print(f"Loading {model_size} model with compute type {compute_type}...")
        model = WhisperModel(model_size, device="cpu", compute_type=compute_type)  #for speed, use "float32" for quality

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
