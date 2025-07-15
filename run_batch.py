#!/usr/bin/env python3
"""
Script for running batch audio file processing
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add path to src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.batch_processor import BatchAudioProcessor

async def main():
    """Main function for running batch processing"""
    processor = BatchAudioProcessor()
    
    print("=" * 80)
    print("BATCH AUDIO FILE PROCESSING")
    print("=" * 80)
    print(f"Source directory: {processor.source_dir}")
    print(f"Output directory: {processor.output_dir}")
    print("=" * 80)
    
    # Check if source directory exists
    if not os.path.exists(processor.source_dir):
        print(f"❌ ERROR: Source directory not found: {processor.source_dir}")
        print("Create directory or change path in AUDIO_SOURCE_DIR variable")
        return
    
    try:
        # Get save mode from environment variable
        save_mode = os.getenv('SAVE_MODE', 'both')  # both = combined + individual files
        print(f"Save mode: {save_mode}")
        
        # Run processing
        await processor.process_batch(save_mode=save_mode)
        print("\n✅ Batch processing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check that we are running from the correct directory
    if not os.path.exists('src'):
        print("❌ ERROR: Run the script from the project root directory")
        sys.exit(1)
    
    # Run asynchronous processing
    asyncio.run(main())
