#!/usr/bin/env python3
"""
Direct file processing script - uses the same logic as app.py but without web server
"""
import os
import sys
import glob
from pathlib import Path

# Add path to src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.transformer import transcribe_audio

def process_single_audio_file(file_path, output_dir):
    """Process single audio file using the same logic as app.py"""
    print(f"Processing: {file_path}")
    
    try:
        # Use the same transcribe_audio function as in app.py
        result = transcribe_audio(file_path)
        
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
            output_file = os.path.join(output_dir, f"{base_name}_transcription.txt")
            
            # Save transcription
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Source file: {file_path}\n")
                f.write("=" * 60 + "\n\n")
                f.write(transcription)
            
            print(f"✅ Saved: {output_file}")
            print(f"📝 Text: {transcription[:100]}...")
            return True
        else:
            print(f"❌ Empty transcription")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    # Get source directory from environment or use default
    source_dir = os.getenv('AUDIO_SOURCE_DIR', r'D:\02_Проекты\LK-TRANS\2025\AI\AUDIO')
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("DIRECT AUDIO FILE PROCESSING")
    print("=" * 80)
    print(f"Source directory: {source_dir}")
    print(f"Output directory: {output_dir}")
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
    
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] ", end="")
        
        if process_single_audio_file(file_path, output_dir):
            success_count += 1
        else:
            error_count += 1
    
    # Final statistics
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETED")
    print("=" * 80)
    print(f"✅ Successfully processed: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Total files: {len(audio_files)}")
    print(f"📂 Output directory: {output_dir}")

if __name__ == "__main__":
    # Check that we are running from the correct directory
    if not os.path.exists('src'):
        print("❌ ERROR: Run the script from the project root directory")
        sys.exit(1)
    
    main()
