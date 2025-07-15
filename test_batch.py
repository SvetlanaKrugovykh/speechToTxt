#!/usr/bin/env python3
"""
Test script for checking batch_processor on test data
"""
import os
import sys
import asyncio
import shutil
from pathlib import Path

# Add path to src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_environment():
    """Create test environment"""
    test_dir = os.path.join(os.path.dirname(__file__), 'test_audio')
    
    # Create test directory structure
    os.makedirs(os.path.join(test_dir, 'folder1'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'folder2', 'subfolder'), exist_ok=True)
    
    # Check if there are already test files in uploads
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    if os.path.exists(uploads_dir):
        audio_files = [f for f in os.listdir(uploads_dir) if f.endswith(('.wav', '.ogg', '.m4a', '.mp3'))]
        
        if audio_files:
            # Copy existing audio files for testing
            for i, audio_file in enumerate(audio_files[:3]):  # Limit to 3 files for test
                src_path = os.path.join(uploads_dir, audio_file)
                
                if i == 0:
                    dst_path = os.path.join(test_dir, 'test_audio_1.wav')
                elif i == 1:
                    dst_path = os.path.join(test_dir, 'folder1', 'test_audio_2.wav')
                else:
                    dst_path = os.path.join(test_dir, 'folder2', 'subfolder', 'test_audio_3.wav')
                
                shutil.copy2(src_path, dst_path)
                print(f"📁 Copied test file: {dst_path}")
    
    return test_dir

async def test_batch_processing():
    """Test batch processing"""
    # Create test environment
    test_dir = create_test_environment()
    
    # Set environment variable for test directory
    os.environ['AUDIO_SOURCE_DIR'] = test_dir
    
    # Import and run processor
    from src.batch_processor import BatchAudioProcessor
    
    processor = BatchAudioProcessor()
    
    print("=" * 80)
    print("TEST BATCH AUDIO PROCESSING")
    print("=" * 80)
    print(f"Test directory: {processor.source_dir}")
    print(f"Output directory: {processor.output_dir}")
    print("=" * 80)
    
    try:
        # Run processing in test mode
        await processor.process_batch(save_mode='combined')
        print("\n✅ Test processing completed successfully!")
        
        # Show results
        output_files = [f for f in os.listdir(processor.output_dir) if f.startswith('batch_transcription_')]
        print(f"\n📄 Created transcription files: {len(output_files)}")
        for file in output_files:
            print(f"   - {file}")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test environment
        if os.path.exists(test_dir):
            try:
                shutil.rmtree(test_dir)
                print(f"\n🧹 Test directory cleaned: {test_dir}")
            except Exception:
                print(f"\n⚠️ Could not clean test directory: {test_dir}")

if __name__ == "__main__":
    # Check that we are running from the correct directory
    if not os.path.exists('src'):
        print("❌ ERROR: Run the script from the project root directory")
        sys.exit(1)
    
    # Run testing
    asyncio.run(test_batch_processing())
