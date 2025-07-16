#!/usr/bin/env python3
"""
Universal Batch Processor - works on Linux, Windows, Colab
Automatically detects environment and uses optimal settings
"""

import os
import sys
import platform
import subprocess
import glob
import time
from pathlib import Path

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not installed (optional)")
    # Continue without .env support

# Try to import required libraries
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

class UniversalProcessor:
    def __init__(self):
        self.model = None
        self.device = None
        self.compute_type = None
        self.environment = self._detect_environment()
        self._setup_optimal_config()
    
    def _detect_environment(self):
        """Detect current environment"""
        # Check if running in Google Colab
        try:
            import google.colab
            return "colab"
        except ImportError:
            pass
        
        # Check if running in Jupyter
        try:
            get_ipython().__class__.__name__
            return "jupyter"
        except NameError:
            pass
        
        # Check OS
        os_name = platform.system().lower()
        if os_name == "linux":
            return "linux"
        elif os_name == "windows":
            return "windows"
        else:
            return "other"
    
    def _setup_optimal_config(self):
        """Setup optimal configuration for current environment"""
        print(f"🖥️  Detected environment: {self.environment}")
        
        # Check GPU availability
        gpu_available = False
        if TORCH_AVAILABLE:
            gpu_available = torch.cuda.is_available()
            if gpu_available:
                gpu_name = torch.cuda.get_device_name(0)
                print(f"🚀 GPU available: {gpu_name}")
        
        # Configure device and compute type
        if gpu_available:
            self.device = "cuda"
            if self.environment == "colab":
                self.compute_type = "float16"  # Colab GPU optimized
            else:
                self.compute_type = "float16"  # Linux GPU optimized
        else:
            self.device = "cpu"
            self.compute_type = "int8"  # CPU optimized
        
        print(f"⚙️  Device: {self.device}")
        print(f"⚡ Compute type: {self.compute_type}")
    
    def _get_model(self, model_size="small"):
        """Get or create model (singleton pattern)"""
        if self.model is None:
            if not FASTER_WHISPER_AVAILABLE:
                print("❌ faster-whisper not available. Install with: pip install faster-whisper")
                return None
            
            print(f"🔄 Loading {model_size} model...")
            self.model = WhisperModel(
                model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            print("✅ Model loaded successfully!")
        
        return self.model
    
    def transcribe_audio(self, file_path, model_size="small"):
        """Transcribe audio file"""
        try:
            model = self._get_model(model_size)
            if model is None:
                return None, "Model not available"
            
            print(f"🎵 Processing: {os.path.basename(file_path)}")
            
            # Transcribe
            segments, _ = model.transcribe(
                file_path,
                language=None,  # Auto detection
                beam_size=1,
                best_of=1,
                temperature=0
            )
            
            # Collect transcription
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "
            
            return transcription.strip(), None
            
        except Exception as e:
            return None, str(e)
    
    def process_batch(self, source_dir, output_dir=None, model_size="small"):
        """Process batch of audio files"""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print("=" * 80)
        print("🌍 UNIVERSAL BATCH PROCESSOR")
        print("=" * 80)
        print(f"🖥️  Environment: {self.environment}")
        print(f"📁 Source: {source_dir}")
        print(f"📁 Output: {output_dir}")
        print(f"🧠 Model: {model_size}")
        print(f"⚙️  Device: {self.device}")
        print("=" * 80)
        
        # Find audio files
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
            transcription, error = self.transcribe_audio(file_path, model_size)
            
            if error:
                print(f"❌ Error: {error}")
                error_count += 1
                continue
            
            if transcription:
                # Save result
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_file = os.path.join(output_dir, f"{base_name}_UNIVERSAL_transcription.txt")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Source: {file_path}\n")
                    f.write(f"Environment: {self.environment}\n")
                    f.write(f"Device: {self.device}\n")
                    f.write(f"Model: {model_size}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(transcription)
                
                print(f"✅ Saved: {os.path.basename(output_file)}")
                print(f"📝 Text: {transcription[:100]}...")
                success_count += 1
            else:
                print("❌ Empty transcription")
                error_count += 1
            
            file_end = time.time()
            print(f"⏱️ Time: {file_end - file_start:.1f}s")
        
        # Final stats
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 80)
        print("🏁 PROCESSING COMPLETED")
        print("=" * 80)
        print(f"✅ Success: {success_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📊 Total: {len(audio_files)}")
        print(f"⏱️ Total time: {total_time:.1f}s")
        if success_count > 0:
            print(f"⚡ Avg per file: {total_time/len(audio_files):.1f}s")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal Audio Processor')
    parser.add_argument('--source', '-s', required=True, help='Source directory with audio files')
    parser.add_argument('--output', '-o', help='Output directory (default: ./output)')
    parser.add_argument('--model', '-m', default='small', choices=['tiny', 'base', 'small', 'medium', 'large'], 
                        help='Model size (default: small)')
    
    args = parser.parse_args()
    
    # Create processor and run
    processor = UniversalProcessor()
    processor.process_batch(args.source, args.output, args.model)

if __name__ == "__main__":
    # Check if running with command line arguments
    if len(sys.argv) > 1:
        main()
    else:
        # Interactive mode
        print("🌍 UNIVERSAL PROCESSOR - Interactive Mode")
        print("=" * 50)
        
        processor = UniversalProcessor()
        
        # Get source directory from .env or user input
        source_dir = os.getenv('AUDIO_SOURCE_DIR')
        if source_dir:
            print(f"📁 Using source from .env: {source_dir}")
        else:
            source_dir = input("📁 Enter source directory: ").strip()
            if not source_dir:
                source_dir = r'D:\02_Проекты\LK-TRANS\2025\AI\AUDIO'  # Default
        
        # Get output directory from .env or user input
        output_dir = os.getenv('OUTPUT_DIR')
        if not output_dir:
            output_dir = input("📁 Enter output directory [./output]: ").strip()
            if not output_dir:
                output_dir = "./output"
        else:
            print(f"📁 Using output from .env: {output_dir}")
        
        # Get model size
        model_size = os.getenv('MODEL_SIZE')
        if not model_size:
            model_size = input("🧠 Model size (tiny/base/small/medium/large) [small]: ").strip()
            if not model_size:
                model_size = "small"
        else:
            print(f"🧠 Using model from .env: {model_size}")
        
        # Run processing
        processor.process_batch(source_dir, output_dir, model_size)
