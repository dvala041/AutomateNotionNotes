import yt_dlp
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
import logging

# Set up logging
logger = logging.getLogger(__name__)

class AudioExtractor:
    """Service for extracting audio from video URLs using yt-dlp"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the AudioExtractor
        
        Args:
            output_dir: Directory to save extracted audio files. 
                       If None, uses system temp directory.
            instagram_username: Instagram username for authentication
            instagram_password: Instagram password for authentication
        """
        # Set default output directory to a more accessible location
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def extract_audio_from_url(
        self, 
        url: str, 
        audio_format: str = 'mp3',
        quality: str = 'best'
    ) -> Dict[str, Any]:
        """
        Extract audio from a video URL (Instagram Reel, YouTube, TikTok, etc.)
        
        Args:
            url: The video URL to extract audio from
            audio_format: Audio format (mp3, wav, m4a, etc.)
            quality: Audio quality ('best', 'worst', or specific bitrate)
        
        Returns:
            Dict containing:
                - success: bool
                - file_path: str (path to extracted audio file)
                - title: str (video title)
                - duration: float (duration in seconds)
                - error: str (if any error occurred)
        """
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': audio_format,
                'audioquality': quality,
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # Specify ffmpeg path
            }
            
            # Add post-processor for audio conversion
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': '192' if quality == 'best' else quality,
            }]
            
            result = {
                'success': False,
                'file_path': None,
                'title': None,
                'duration': None,
                'error': None
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info first
                logger.info(f"Extracting info for URL: {url}")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    result['error'] = "Could not extract video information"
                    return result
                
                # Get video details
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                logger.info(f"Video found: {title} ({duration}s)")
                
                # Download and extract audio
                logger.info("Downloading and extracting audio...")
                ydl.download([url])
                
                # Construct expected file path
                safe_title = self._sanitize_filename(title)
                audio_file = os.path.join(self.output_dir, f"{safe_title}.{audio_format}")
                
                # Check if file was created (try multiple possible filenames)
                possible_paths = [
                    audio_file,
                    os.path.join(self.output_dir, f"{title}.{audio_format}"),
                    os.path.join(self.output_dir, f"{title}.mp3"),
                ]
                
                found_file = None
                for path in possible_paths:
                    if os.path.exists(path):
                        found_file = path
                        break
                
                if found_file:
                    result.update({
                        'success': True,
                        'file_path': found_file,
                        'title': title,
                        'duration': duration
                    })
                    logger.info(f"Audio extracted successfully: {found_file}")
                else:
                    # # Try to find the file with glob pattern
                    # possible_files = list(Path(self.output_dir).glob(f"*{safe_title}*.{audio_format}"))
                    # if not possible_files:
                    #     # Try with original title
                    #     possible_files = list(Path(self.output_dir).glob(f"*{title}*.{audio_format}"))
                    # if not possible_files:
                    #     # Try any mp3 files
                    #     possible_files = list(Path(self.output_dir).glob(f"*.{audio_format}"))
                    
                    # if possible_files:
                    #     result.update({
                    #         'success': True,
                    #         'file_path': str(possible_files[0]),
                    #         'title': title,
                    #         'duration': duration
                    #     })
                    #     logger.info(f"Audio extracted successfully: {possible_files[0]}")
                    # else:
                    result['error'] = f"Audio file not found after extraction. Expected: {audio_file}, Searched in: {self.output_dir}"
                
                return result
                
        except yt_dlp.DownloadError as e:
            error_msg = f"Download error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'file_path': None,
                'title': None,
                'duration': None,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'file_path': None,
                'title': None,
                'duration': None,
                'error': error_msg
            }
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get video information without downloading
        
        Args:
            url: Video URL
        
        Returns:
            Dict with video metadata
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'success': True,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'description': info.get('description'),
                    'thumbnail': info.get('thumbnail'),
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_file(self, file_path: str) -> bool:
        """
        Remove extracted audio file
        
        Args:
            file_path: Path to the file to remove
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file system usage
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        import re
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\s+', '_', sanitized)  # Replace spaces with underscores
        return sanitized[:100]  # Limit length


