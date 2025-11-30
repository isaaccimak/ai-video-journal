import os
import uuid
import shutil
import subprocess
from datetime import datetime
from typing import BinaryIO


class VideoService:
    """Service for handling video file operations and conversions."""
    
    def __init__(self, base_dir: str = "videos"):
        """
        Initialize the video service.
        
        Args:
            base_dir: Base directory for storing videos (default: "videos")
        """
        self.base_dir = base_dir
    
    def save_and_convert_video(self, video_file: BinaryIO, filename: str) -> str:
        """
        Save and convert a video file to MP4 format.
        
        Args:
            video_file: Binary file object containing the video data
            filename: Desired filename for the saved video
            
        Returns:
            str: Full path to the saved video file
            
        Raises:
            Exception: If video conversion fails
        """
        # Generate timestamp for directory name (ddmmyyyy_hhmmss)
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        
        # Create directory structure: videos/ddmmyyyy_hhmmss/
        video_dir = os.path.join(self.base_dir, timestamp)
        os.makedirs(video_dir, exist_ok=True)
        
        # Ensure filename has .mp4 extension
        if not filename.endswith('.mp4'):
            final_filename = f"{filename}.mp4"
        else:
            final_filename = filename
        
        # Create temp file for input WebM
        temp_input_path = f"temp_input_{uuid.uuid4()}.webm"
        final_output_path = os.path.join(video_dir, final_filename)
        
        try:
            # Save uploaded WebM to temp file
            with open(temp_input_path, "wb") as buffer:
                shutil.copyfileobj(video_file, buffer)
            
            # Convert to MP4 using ffmpeg
            self._convert_to_mp4(temp_input_path, final_output_path)
            
            print(f"Video saved and converted to: {final_output_path}")
            return final_output_path
            
        finally:
            # Cleanup temp file
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
    
    def _convert_to_mp4(self, input_path: str, output_path: str) -> None:
        """
        Convert a video file to MP4 format using ffmpeg.
        
        Args:
            input_path: Path to input video file
            output_path: Path where MP4 should be saved
            
        Raises:
            Exception: If ffmpeg conversion fails
        """
        # Command: ffmpeg -i input.webm -c:v libx264 -preset fast -c:a aac output.mp4
        # -y: Overwrite output files without asking
        # -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2": Ensure dimensions are even for libx264
        command = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-y",
            output_path
        ]
        
        print(f"Converting video: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            raise Exception(f"FFmpeg conversion failed: {result.stderr}")


# Singleton instance
video_service = VideoService()
