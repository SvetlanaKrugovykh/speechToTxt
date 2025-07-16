#!/usr/bin/env python3
"""
Simple Audio Processor - SIMPLIFIED VERSION
Just works on any Linux/Windows without complexity
"""

import os
import sys
import glob
import time

# Try to import faster-whisper
try:
    from faster_whisper import WhisperModel
    print("✅ faster-whisper available")
except ImportError:
    print("❌ Install faster-whisper: pip install faster-whisper")
    sys.exit(1)

# Try to import torch for GPU detection
try:
    import torch
    if torch.cuda.is_available():
        print(f"🚀 GPU available: {torch.cuda.get_device_name(0)}")
        device = "cuda"
        compute_type = "float16"
    else:
        print("💻 Using CPU")
        device = "cpu"
        compute_type = "int8"
except ImportError:
    print("💻 Using CPU (torch not available)")
    device = "cpu"
    compute_type = "int8"

def simple_transcribe(file_path, model_size="small"):
    """Simple transcription function"""
    try:
        print(f"Loading {model_size} model...")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        print(f"🎵 Processing: {os.path.basename(file_path)}")
        segments, _ = model.transcribe(file_path, language=None, beam_size=1, best_of=1, temperature=0)
        
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
        
        return transcription.strip()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def process_folder(source_dir, output_dir=None):
    """Process all audio files in folder"""
    if output_dir is None:
        output_dir = "./output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find audio files
    audio_files = []
    for ext in ['*.m4a', '*.mp3', '*.wav', '*.ogg', '*.flac']:
        audio_files.extend(glob.glob(os.path.join(source_dir, '**', ext), recursive=True))
    
    if not audio_files:
        print(f"❌ No audio files found in {source_dir}")
        return
    
    print(f"📊 Found {len(audio_files)} files")
    print(f"📁 Output: {output_dir}")
    print("=" * 50)
    
    success = 0
    start_time = time.time()
    
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] ", end="")
        
        file_start = time.time()
        transcription = simple_transcribe(file_path)
        
        if transcription:
            # Save result
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}_transcription.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Source: {file_path}\n")
                f.write(f"Device: {device}\n")
                f.write("=" * 50 + "\n\n")
                f.write(transcription)
            
            print(f"✅ Saved: {os.path.basename(output_file)}")
            print(f"📝 Text: {transcription[:80]}...")
            success += 1
        
        file_end = time.time()
        print(f"⏱️ Time: {file_end - file_start:.1f}s")
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 50)
    print("🏁 COMPLETED")
    print(f"✅ Success: {success}")
    print(f"📊 Total: {len(audio_files)}")
    print(f"⏱️ Total time: {total_time:.1f}s")
    print(f"⚡ Avg per file: {total_time/len(audio_files):.1f}s")

if __name__ == "__main__":
    print("🎤 SIMPLE AUDIO PROCESSOR")
    print("=" * 50)
    
    # Get directories
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./output"
    else:
        source_dir = input("📁 Enter audio folder path: ").strip()
        if not source_dir:
            print("❌ Source directory required")
            sys.exit(1)
        output_dir = input("📁 Enter output folder [./output]: ").strip()
        if not output_dir:
            output_dir = "./output"
    
    # Process
    process_folder(source_dir, output_dir)
