"""
Transcript loader for handling different file types and converting them to text
Supports JSON, TXT, audio files (WAV, MP3), and video files (MP4, MKV)
"""
import os
import json
import tempfile
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import speech_recognition as sr
import whisper
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import streamlit as st

# Configure FFmpeg path for pydub
ffmpeg_path = r"C:\FFmpeg\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
if os.path.exists(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.ffprobe = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptLoader:
    """Handles loading and processing of different file types to extract text"""
    
    def __init__(self):
        """Initialize the transcript loader"""
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self.supported_audio_formats = ['.wav', '.mp3', '.m4a', '.flac', '.aac']
        self.supported_video_formats = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
        self.supported_text_formats = ['.txt', '.json']
    
    def load_whisper_model(self, model_size: str = "base"):
        """Load Whisper model for speech recognition"""
        try:
            self.whisper_model = whisper.load_model(model_size)
            logger.info(f"Loaded Whisper model: {model_size}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def process_file(self, file_path: str, file_type: str = None) -> Dict:
        """
        Process a file and extract text content
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('text', 'audio', 'video')
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        # Determine file type if not provided
        if file_type is None:
            if file_extension in self.supported_text_formats:
                file_type = 'text'
            elif file_extension in self.supported_audio_formats:
                file_type = 'audio'
            elif file_extension in self.supported_video_formats:
                file_type = 'video'
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        
        logger.info(f"Processing {file_type} file: {file_path}")
        
        if file_type == 'text':
            return self._process_text_file(file_path)
        elif file_type == 'audio':
            return self._process_audio_file(file_path)
        elif file_type == 'video':
            return self._process_video_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _process_text_file(self, file_path: Path) -> Dict:
        """Process text files (TXT or JSON)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                if file_path.suffix.lower() == '.json':
                    data = json.load(file)
                    # Handle different JSON structures
                    if isinstance(data, dict):
                        if 'transcript' in data:
                            text = data['transcript']
                        elif 'text' in data:
                            text = data['text']
                        elif 'content' in data:
                            text = data['content']
                        else:
                            # If it's a dict but no obvious text field, convert to string
                            text = json.dumps(data, indent=2)
                    elif isinstance(data, list):
                        # Handle list of messages/segments
                        text = ' '.join([str(item) for item in data])
                    else:
                        text = str(data)
                else:
                    text = file.read()
            
            return {
                'text': text,
                'file_type': 'text',
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'processing_method': 'direct_read'
            }
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            raise
    
    def _process_audio_file(self, file_path: Path) -> Dict:
        """Process audio files using Whisper or SpeechRecognition"""
        try:
            # Try Whisper first (more accurate)
            if self.whisper_model is not None:
                return self._process_audio_with_whisper(file_path)
            else:
                return self._process_audio_with_speech_recognition(file_path)
        except Exception as e:
            logger.error(f"Error processing audio file {file_path}: {e}")
            raise
    
    def _process_audio_with_whisper(self, file_path: Path) -> Dict:
        """Process audio using Whisper"""
        try:
            # Load Whisper model if not already loaded
            if self.whisper_model is None:
                self.load_whisper_model()
            
            # Convert to WAV if needed for better Whisper compatibility
            audio_file = self._convert_to_wav(file_path)
            
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_file)
            text = result["text"]
            
            # Clean up temporary file
            if audio_file != str(file_path):
                os.unlink(audio_file)
            
            return {
                'text': text,
                'file_type': 'audio',
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'processing_method': 'whisper',
                'language': result.get('language', 'unknown'),
                'segments': result.get('segments', [])
            }
        except Exception as e:
            logger.error(f"Whisper processing failed for {file_path}: {e}")
            # Don't fallback to speech recognition, just raise the error
            raise ValueError(f"Whisper processing failed: {e}")
    
    def _process_audio_with_speech_recognition(self, file_path: Path) -> Dict:
        """Process audio using SpeechRecognition library"""
        try:
            # Convert audio to WAV if needed
            audio_file = self._convert_to_wav(file_path)
            
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.record(source)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            # Clean up temporary file
            if audio_file != str(file_path):
                os.unlink(audio_file)
            
            return {
                'text': text,
                'file_type': 'audio',
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'processing_method': 'speech_recognition'
            }
        except sr.UnknownValueError:
            logger.error(f"Could not understand audio in {file_path}")
            raise ValueError("Could not understand audio. Please try a different file or check audio quality.")
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            raise ValueError("Speech recognition service unavailable. Please try again later.")
    
    def _process_video_file(self, file_path: Path) -> Dict:
        """Process video files by extracting audio first"""
        try:
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            # Extract audio from video
            video = VideoFileClip(str(file_path))
            audio = video.audio
            audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            audio.close()
            video.close()
            
            # Process the extracted audio
            audio_result = self._process_audio_file(Path(temp_audio_path))
            
            # Clean up temporary file
            os.unlink(temp_audio_path)
            
            # Update metadata for video
            audio_result.update({
                'file_type': 'video',
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'video_duration': video.duration if 'video' in locals() else None
            })
            
            return audio_result
        except Exception as e:
            logger.error(f"Error processing video file {file_path}: {e}")
            raise
    
    def _convert_to_wav(self, file_path: Path) -> str:
        """Convert audio file to WAV format for speech recognition"""
        if file_path.suffix.lower() == '.wav':
            return str(file_path)
        
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Convert to WAV
            audio = AudioSegment.from_file(str(file_path))
            audio.export(temp_path, format="wav")
            
            return temp_path
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {e}")
            raise
    
    def process_streamlit_upload(self, uploaded_file) -> Dict:
        """
        Process a file uploaded through Streamlit
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name
            
            # Process the file
            result = self.process_file(temp_file_path)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return result
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}")
            raise
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if file is supported
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file is supported
        """
        file_extension = Path(file_path).suffix.lower()
        all_supported_formats = (
            self.supported_text_formats + 
            self.supported_audio_formats + 
            self.supported_video_formats
        )
        return file_extension in all_supported_formats
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats"""
        return {
            'text': self.supported_text_formats,
            'audio': self.supported_audio_formats,
            'video': self.supported_video_formats
        }

# Global transcript loader instance
transcript_loader = TranscriptLoader()

def get_transcript_loader() -> TranscriptLoader:
    """Get the global transcript loader instance"""
    return transcript_loader
