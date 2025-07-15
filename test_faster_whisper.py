#!/usr/bin/env python3
"""
EXPERIMENTAL: Direct file processing with Faster-Whisper
This is a SEPARATE script - does not modify the working project!
"""
import os
import sys
import glob
from pathlib import Path

# Add path to src for audio converter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    print("faster-whisper not installed. Install with: pip install faster-whisper")
    FASTER_WHISPER_AVAILABLE = False

from src.converters.audio_converter import convert_to_wav

# Global model instance to avoid reloading
_model = None

def get_faster_whisper_model():
    """Get or create faster-whisper model (load once, use many times)"""
    global _model
    if _model is None:
        print("Loading Faster-Whisper model (this happens only once)...")
        _model = WhisperModel(
            "small", 
            device="cpu", 
            compute_type="int8"  # Use int8 for speed, float16 for quality
        )
        print("Model loaded successfully!")
    return _model

def transcribe_audio_faster(file_path):
    """Transcribe audio using faster-whisper"""
    try:
        print("Converting to WAV...")
        wav_file_path = convert_to_wav(file_path)
        
        if wav_file_path is None:
            return None, "Failed to convert to WAV"
        
        if not os.path.exists(wav_file_path):
            return None, f"WAV file not created: {wav_file_path}"
        
        print("Transcribing with Faster-Whisper...")
        model = get_faster_whisper_model()
        
        # Transcribe with optimized settings
        segments, _ = model.transcribe(
            wav_file_path,
            language=None,      # Auto-detect language (good for mixed languages)
            beam_size=1,        # Faster but slightly lower quality
            best_of=1,          # Faster
            temperature=0.0,    # More stable results
            vad_filter=True,    # Voice activity detection - removes silence
            vad_parameters={"min_silence_duration_ms": 500}
        )
        
        # Collect text from segments
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
            
        return transcription.strip(), None
        
    except Exception as e:
        return None, str(e)

def process_single_audio_file_faster(file_path, output_dir):
    """Process single audio file using faster-whisper"""
    print(f"Processing: {file_path}")
    
    try:
        result = transcribe_audio_faster(file_path)
        
        # Handle tuple return (text, error)
        if isinstance(result, tuple):
            transcription, error = result
            if error:
                print(f"❌ Error: {error}")
                return False
        else:
            transcription = result
        
        if transcription and transcription.strip():
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}_FASTER_transcription.txt")
            
            # Save transcription
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Source file: {file_path}\n")
                f.write("Method: Faster-Whisper\n")
                f.write("=" * 60 + "\n\n")
                f.write(transcription)
            
            print(f"✅ Saved: {output_file}")
            print(f"📝 Text: {transcription[:100]}...")
            return True
        else:
            print("Empty transcription")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function for faster-whisper testing"""
    if not FASTER_WHISPER_AVAILABLE:
        print("Install faster-whisper first: pip install faster-whisper")
        return
    
    # Get source directory from environment or use default
    source_dir = os.getenv('AUDIO_SOURCE_DIR', r'D:\02_Проекты\LK-TRANS\2025\AI\AUDIO')
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("EXPERIMENTAL: FASTER-WHISPER AUDIO PROCESSING")
    print("=" * 80)
    print(f"Source directory: {source_dir}")
    print(f"Output directory: {output_dir}")
    print("Files will be saved with '_FASTER_' prefix to avoid conflicts")
    print("=" * 80)
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"❌ ERROR: Source directory not found: {source_dir}")
        return
    
    # Find all audio files
    audio_extensions = ['*.m4a', '*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']
    audio_files = []
    
    for ext in audio_extensions:
        pattern = os.path.join(source_dir, '**', ext)
        files = glob.glob(pattern, recursive=True)
        audio_files.extend(files)
    
    if not audio_files:
        print(f"❌ No audio files found in {source_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files")
    
    # Process files
    success_count = 0
    error_count = 0
    
    import time
    start_time = time.time()
    
    # Process ALL files (remove [:3] limitation)
    total_files = len(audio_files)
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{total_files}] ", end="")
        
        file_start = time.time()
        if process_single_audio_file_faster(file_path, output_dir):
            success_count += 1
        else:
            error_count += 1
        file_end = time.time()
        print(f"⏱️ Time: {file_end - file_start:.1f}s")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Final statistics
    print("\n" + "=" * 80)
    print("FASTER-WHISPER PROCESSING COMPLETED")
    print("=" * 80)
    print(f"✅ Successfully processed: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"Total files processed: {total_files}")
    print(f"⏱️ Total time: {total_time:.1f}s")
    if success_count > 0:
        print(f"⚡ Average time per file: {total_time/total_files:.1f}s")
    print(f"📂 Output directory: {output_dir}")
    print("Files saved with '_FASTER_' prefix")

if __name__ == "__main__":
    if not os.path.exists('src'):
        print("❌ ERROR: Run the script from the project root directory")
        sys.exit(1)
    
    main()
