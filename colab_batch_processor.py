#!/usr/bin/env python3
"""
Google Colab Batch Processor for Faster-Whisper
This script is designed to run in Google Colab with GPU acceleration
SEPARATE module - does not interfere with existing project!
"""

import os
import sys
import glob
import time
from pathlib import Path

# Try to import faster-whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    print("faster-whisper not installed. Install with: !pip install faster-whisper")
    FASTER_WHISPER_AVAILABLE = False

# Try to load .env file for GOOGLE_DRIVE_PATH
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not installed (optional)")
    # Continue without .env support

# Global model instance for Colab (load once, use many times)
_colab_model = None

def setup_colab_environment():
    """Setup Google Colab environment"""
    print("🚀 Setting up Google Colab environment...")
    
    # Check if running in Colab
    try:
        import google.colab
        IN_COLAB = True
        print("✅ Running in Google Colab")
    except ImportError:
        IN_COLAB = False
        print("⚠️  Not running in Google Colab - will use CPU")
    
    # Check GPU availability
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
        device = "cuda"
        compute_type = "float16"  # GPU optimized
    else:
        print("⚠️  No GPU available - using CPU")
        device = "cpu"
        compute_type = "int8"  # CPU optimized
    
    return IN_COLAB, device, compute_type

def get_colab_faster_whisper_model(device="cuda", compute_type="float16"):
    """Get or create faster-whisper model optimized for Colab"""
    global _colab_model
    
    if _colab_model is None:
        print("🔄 Loading Faster-Whisper model for Colab (GPU accelerated)...")
        _colab_model = WhisperModel(
            "small",  # You can change to "medium" for better quality
            device=device,
            compute_type=compute_type
        )
        print("✅ Model loaded successfully!")
    
    return _colab_model

def transcribe_audio_colab(file_path, device="cuda", compute_type="float16"):
    """Transcribe audio using faster-whisper in Colab"""
    try:
        print(f"🎵 Processing: {os.path.basename(file_path)}")
        
        # Get model
        model = get_colab_faster_whisper_model(device, compute_type)
        
        # Transcribe directly (no WAV conversion needed in Colab)
        segments, info = model.transcribe(
            file_path, 
            language=None,  # Auto language detection
            beam_size=1,    # Faster
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

def process_batch_colab(source_dir=None, output_dir=None):
    """Process batch of audio files in Google Colab"""
    if not FASTER_WHISPER_AVAILABLE:
        print("❌ Install faster-whisper first: !pip install faster-whisper")
        return

    # Use GOOGLE_DRIVE_PATH from .env if source_dir not provided
    if source_dir is None:
        source_dir = os.getenv('GOOGLE_DRIVE_PATH', '/content/drive/MyDrive/audio_files')
        print(f"📁 Using GOOGLE_DRIVE_PATH: {source_dir}")

    # Setup Colab environment
    IN_COLAB, device, compute_type = setup_colab_environment()

    if output_dir is None:
        output_dir = "/content/output"  # Default Colab output
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("🚀 GOOGLE COLAB FASTER-WHISPER BATCH PROCESSING")
    print("=" * 80)
    print(f"📁 Source directory: {source_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🖥️  Device: {device}")
    print(f"⚡ Compute type: {compute_type}")
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
    
    print(f"📊 Found {len(audio_files)} audio files")
    
    # Process files
    success_count = 0
    error_count = 0
    
    start_time = time.time()
    
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] ", end="")
        
        file_start = time.time()
        
        # Transcribe
        transcription, error = transcribe_audio_colab(file_path, device, compute_type)
        
        if error:
            print(f"❌ Error: {error}")
            error_count += 1
            continue
        
        if transcription and transcription.strip():
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}_COLAB_transcription.txt")
            
            # Save transcription
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Source file: {file_path}\n")
                f.write("Method: Faster-Whisper (Google Colab)\n")
                f.write(f"Device: {device}\n")
                f.write(f"Compute type: {compute_type}\n")
                f.write("=" * 60 + "\n\n")
                f.write(transcription)
            
            print(f"✅ Saved: {output_file}")
            print(f"📝 Text: {transcription[:100]}...")
            success_count += 1
        else:
            print("❌ Empty transcription")
            error_count += 1
        
        file_end = time.time()
        print(f"⏱️ Time: {file_end - file_start:.1f}s")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Final statistics
    print("\n" + "=" * 80)
    print("🏁 GOOGLE COLAB PROCESSING COMPLETED")
    print("=" * 80)
    print(f"✅ Successfully processed: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total files processed: {len(audio_files)}")
    print(f"⏱️ Total time: {total_time:.1f}s")
    if success_count > 0:
        print(f"⚡ Average time per file: {total_time/len(audio_files):.1f}s")
    print(f"📂 Output directory: {output_dir}")
    print("Files saved with '_COLAB_' prefix")

# Example usage function for Colab
def colab_example():
    """Example usage in Google Colab"""
    print("""
    🚀 GOOGLE COLAB USAGE EXAMPLE:
    
    1. Upload this script to Colab
    2. Install faster-whisper: !pip install faster-whisper
    3. Mount Google Drive: 
       from google.colab import drive
       drive.mount('/content/drive')
    4. Run batch processing:
       process_batch_colab('/content/drive/MyDrive/audio_files')
    
    That's it! GPU acceleration included! 🚀
    """)

if __name__ == "__main__":
    colab_example()
