# batch_processor.py
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from .transformer import transcribe_audio
from .converters.audio_converter import convert_to_wav

# Load environment variables from .env file
load_dotenv()

class BatchAudioProcessor:
    def __init__(self):
        self.source_dir = os.getenv('AUDIO_SOURCE_DIR', r'D:\02_Проекты\LK-TRANS\2025\AI\AUDIO')
        self.output_dir = os.getenv('OUTPUT_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output'))
        self.supported_extensions = {'.ogg', '.m4a', '.wav', '.mp3', '.flac', '.aac'}
        self.setup_logging()
        self.ensure_output_dir()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        numeric_level = getattr(logging, log_level, logging.INFO)
        
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.output_dir, 'batch_processing.log'), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")
    
    def find_audio_files(self):
        """Find all audio files in directory and subdirectories"""
        audio_files = []
        
        if not os.path.exists(self.source_dir):
            self.logger.error(f"Source directory does not exist: {self.source_dir}")
            return audio_files
        
        self.logger.info(f"Scanning directory: {self.source_dir}")
        
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                
                if file_ext in self.supported_extensions:
                    audio_files.append(file_path)
                    self.logger.info(f"Found audio file: {file_path}")
                else:
                    self.logger.debug(f"Skipping non-audio file: {file_path}")
        
        self.logger.info(f"Total audio files found: {len(audio_files)}")
        return audio_files
    
    def generate_output_filename(self, audio_file_path, transcription_type='individual'):
        """Generate output filename"""
        if transcription_type == 'combined':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"combined_transcriptions_{timestamp}.txt"
        
        # For individual files
        relative_path = os.path.relpath(audio_file_path, self.source_dir)
        # Replace backslashes with underscores and remove extension
        safe_name = relative_path.replace('\\', '_').replace('/', '_')
        name_without_ext = os.path.splitext(safe_name)[0]
        return f"transcription_{name_without_ext}.txt"
    
    def save_transcription(self, audio_file_path, transcription, save_mode='individual'):
        """Save transcription to file"""
        try:
            if save_mode == 'individual':
                # Save to separate file for each audio
                output_filename = self.generate_output_filename(audio_file_path, 'individual')
                output_path = os.path.join(self.output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"File: {audio_file_path}\n")
                    f.write(f"Processing date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(transcription)
                
                self.logger.info(f"Transcription saved to: {output_path}")
                
            elif save_mode == 'combined':
                # Add to common file
                output_filename = self.generate_output_filename(None, 'combined')
                output_path = os.path.join(self.output_dir, output_filename)
                
                with open(output_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"FILE: {audio_file_path}\n")
                    f.write(f"PROCESSING DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(transcription)
                    f.write("\n\n")
                
                self.logger.info(f"Transcription appended to: {output_path}")
                
        except Exception as e:
            self.logger.error(f"Error saving transcription for {audio_file_path}: {e}")
    
    def process_single_file(self, audio_file_path, save_mode='individual'):
        """Process single audio file"""
        try:
            self.logger.info(f"Processing file: {audio_file_path}")
            
            # Audio transcription - returns (text, error)
            result = transcribe_audio(audio_file_path)
            
            # Handle the tuple return value
            if isinstance(result, tuple):
                transcription, error = result
                if error:
                    self.logger.error(f"Transcription error for {audio_file_path}: {error}")
                    return False
            else:
                # If it's not a tuple, assume it's the transcription text
                transcription = result
            
            if transcription and transcription.strip():
                self.save_transcription(audio_file_path, transcription, save_mode)
                return True
            else:
                self.logger.error(f"Empty transcription for: {audio_file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing {audio_file_path}: {e}")
            return False
            return False
    
    def process_all_files(self, save_mode='individual'):
        """Process all found audio files
        
        Args:
            save_mode (str): 'individual' - separate file for each audio,
                           'combined' - all transcriptions in one file
        """
        audio_files = self.find_audio_files()
        
        if not audio_files:
            self.logger.warning("No audio files found to process")
            return
        
        processed_count = 0
        failed_count = 0
        
        # Create header for combined file
        if save_mode == 'combined':
            output_filename = self.generate_output_filename(None, 'combined')
            output_path = os.path.join(self.output_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("BATCH AUDIO TRANSCRIPTION\n")
                f.write(f"Source directory: {self.source_dir}\n")
                f.write(f"Processing start date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total files to process: {len(audio_files)}\n")
                f.write("=" * 80 + "\n")
        
        for audio_file in audio_files:
            if self.process_single_file(audio_file, save_mode):
                processed_count += 1
            else:
                failed_count += 1
        
        # Final statistics
        self.logger.info(f"Processing completed:")
        self.logger.info(f"  Successfully processed: {processed_count}")
        self.logger.info(f"  Failed: {failed_count}")
        self.logger.info(f"  Total files: {len(audio_files)}")
        
        # Add statistics to combined file
        if save_mode == 'combined':
            output_filename = self.generate_output_filename(None, 'combined')
            output_path = os.path.join(self.output_dir, output_filename)
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write("PROCESSING STATISTICS\n")
                f.write(f"Completion date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Successfully processed: {processed_count}\n")
                f.write(f"Errors: {failed_count}\n")
                f.write(f"Total files: {len(audio_files)}\n")
    
    async def process_batch(self, save_mode='individual'):
        """Asynchronous batch processing of all found audio files
        
        Args:
            save_mode (str): 'individual' - separate file for each audio,
                           'combined' - all transcriptions in one file,
                           'both' - both modes
        """
        if save_mode == 'both':
            # Process both modes
            await self.process_batch('individual')
            await self.process_batch('combined')
            return
        
        audio_files = self.find_audio_files()
        
        if not audio_files:
            self.logger.warning("No audio files found to process")
            return
        
        processed_count = 0
        failed_count = 0
        
        # Create header for combined file
        if save_mode == 'combined':
            output_filename = self.generate_output_filename(None, 'combined')
            output_path = os.path.join(self.output_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("BATCH AUDIO TRANSCRIPTION\n")
                f.write(f"Source directory: {self.source_dir}\n")
                f.write(f"Processing start date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total files to process: {len(audio_files)}\n")
                f.write("=" * 80 + "\n")
        
        # Process files with progress indicator
        for i, audio_file in enumerate(audio_files, 1):
            print(f"Processing {i}/{len(audio_files)}: {os.path.basename(audio_file)}")
            
            if self.process_single_file(audio_file, save_mode):
                processed_count += 1
            else:
                failed_count += 1
            
            # Add small delay to prevent overwhelming the system
            await asyncio.sleep(0.1)
        
        # Final statistics
        self.logger.info("Async processing completed:")
        self.logger.info(f"  Successfully processed: {processed_count}")
        self.logger.info(f"  Failed: {failed_count}")
        self.logger.info(f"  Total files: {len(audio_files)}")
        
        # Add statistics to combined file
        if save_mode == 'combined':
            output_filename = self.generate_output_filename(None, 'combined')
            output_path = os.path.join(self.output_dir, output_filename)
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write("PROCESSING STATISTICS\n")
                f.write(f"Completion date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Successfully processed: {processed_count}\n")
                f.write(f"Errors: {failed_count}\n")
                f.write(f"Total files: {len(audio_files)}\n")

def main():
    """Main function for running batch processing"""
    # Load environment variables
    load_dotenv()
    
    processor = BatchAudioProcessor()
    
    # Get save mode from environment variable
    save_mode = os.getenv('SAVE_MODE', 'individual')  # or 'combined' or 'both'
    
    print("Starting batch audio file processing...")
    print(f"Source directory: {processor.source_dir}")
    print(f"Output directory: {processor.output_dir}")
    print(f"Save mode: {save_mode}")
    
    processor.process_all_files(save_mode)
    print("Batch processing completed!")

if __name__ == "__main__":
    main()
