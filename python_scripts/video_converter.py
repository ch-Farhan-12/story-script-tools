#!/usr/bin/env python3
"""
video_converter.py

A module for converting video files to different formats using FFmpeg.
Supports common video formats like MP4, AVI, MOV, MKV, and WebM.
"""

import os
import subprocess
import uuid
from typing import List, Optional, Dict, Literal
from pathlib import Path
from dataclasses import dataclass

# Supported video formats and their FFmpeg settings
FormatType = Literal["mp4", "avi", "mov", "mkv", "webm"]

@dataclass
class FormatSettings:
    """Settings for each video format."""
    container: str
    video_codec: str
    audio_codec: str
    extra_args: List[str] = None

    def __post_init__(self):
        if self.extra_args is None:
            self.extra_args = []

FORMAT_SETTINGS: Dict[str, FormatSettings] = {
    "mp4": FormatSettings(
        container="mp4",
        video_codec="libx264",
        audio_codec="aac",
        extra_args=["-preset", "medium", "-crf", "23"]
    ),
    "avi": FormatSettings(
        container="avi",
        video_codec="mpeg4",
        audio_codec="mp3",
        extra_args=["-q:v", "6"]
    ),
    "mov": FormatSettings(
        container="mov",
        video_codec="libx264",
        audio_codec="aac",
        extra_args=["-preset", "medium", "-crf", "23"]
    ),
    "mkv": FormatSettings(
        container="matroska",
        video_codec="libx264",
        audio_codec="aac",
        extra_args=["-preset", "medium", "-crf", "23"]
    ),
    "webm": FormatSettings(
        container="webm",
        video_codec="libvpx-vp9",
        audio_codec="libopus",
        extra_args=["-b:v", "0", "-crf", "30", "-row-mt", "1"]
    )
}

class VideoConverter:
    """
    A class for converting videos to different formats using FFmpeg.
    """
    
    def __init__(self, output_dir: str = "converted_videos"):
        """
        Initialize the VideoConverter.
        
        Args:
            output_dir: Directory to save converted videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify FFmpeg installation
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg is not installed or not found in system PATH. "
                "Please install FFmpeg to use this converter."
            )
    
    def convert(self,
               input_path: str,
               output_format: FormatType,
               output_filename: Optional[str] = None,
               quality: Optional[str] = "medium",
               overwrite: bool = False) -> str:
        """
        Convert a video file to the specified format.
        
        Args:
            input_path: Path to input video file
            output_format: Desired output format (mp4, avi, mov, mkv, webm)
            output_filename: Optional custom filename for output
            quality: Quality setting (low, medium, high)
            overwrite: Whether to overwrite existing files
            
        Returns:
            Path to the converted video file
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if output_format not in FORMAT_SETTINGS:
            raise ValueError(
                f"Unsupported format: {output_format}. "
                f"Supported formats: {', '.join(FORMAT_SETTINGS.keys())}"
            )
        
        # Set output filename
        if output_filename is None:
            # Add unique identifier to prevent conflicts
            unique_id = str(uuid.uuid4())[:8]
            output_filename = f"{input_path.stem}_{unique_id}.{output_format}"
        elif not output_filename.endswith(f".{output_format}"):
            output_filename = f"{output_filename}.{output_format}"
        
        output_path = self.output_dir / output_filename
        
        # Check if output file exists
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_path}. "
                "Use overwrite=True to force conversion."
            )
        
        # Get format settings
        settings = FORMAT_SETTINGS[output_format]
        
        # Adjust quality settings
        quality_settings = self._get_quality_settings(quality, output_format)
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-c:v", settings.video_codec,
            "-c:a", settings.audio_codec
        ]
        
        # Add format-specific arguments
        if settings.extra_args:
            cmd.extend(settings.extra_args)
        
        # Add quality settings
        if quality_settings:
            cmd.extend(quality_settings)
        
        # Add output path
        cmd.extend(["-y" if overwrite else "-n", str(output_path)])
        
        try:
            # Run FFmpeg command
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg conversion failed: {error_msg}")
        
        return str(output_path)
    
    def convert_multiple(self,
                        input_path: str,
                        formats: List[FormatType],
                        quality: Optional[str] = "medium",
                        overwrite: bool = False) -> List[str]:
        """
        Convert a video file to multiple formats.
        
        Args:
            input_path: Path to input video file
            formats: List of desired output formats
            quality: Quality setting (low, medium, high)
            overwrite: Whether to overwrite existing files
            
        Returns:
            List of paths to the converted video files
        """
        output_paths = []
        for fmt in formats:
            output_path = self.convert(
                input_path,
                fmt,
                quality=quality,
                overwrite=overwrite
            )
            output_paths.append(output_path)
        return output_paths
    
    def _get_quality_settings(self,
                            quality: str,
                            output_format: str) -> List[str]:
        """
        Get FFmpeg quality settings based on format and quality level.
        
        Args:
            quality: Quality setting (low, medium, high)
            output_format: Output format
            
        Returns:
            List of FFmpeg arguments for quality settings
        """
        if quality not in ["low", "medium", "high"]:
            return []
        
        # Quality settings for different formats
        quality_settings = {
            "mp4": {
                "low": ["-preset", "ultrafast", "-crf", "28"],
                "medium": ["-preset", "medium", "-crf", "23"],
                "high": ["-preset", "slow", "-crf", "18"]
            },
            "webm": {
                "low": ["-crf", "35"],
                "medium": ["-crf", "30"],
                "high": ["-crf", "25"]
            }
        }
        
        # Use MP4 settings for MOV and MKV
        if output_format in ["mov", "mkv"]:
            return quality_settings["mp4"][quality]
        
        return quality_settings.get(output_format, {}).get(quality, [])

def main():
    """Example usage of the VideoConverter class."""
    try:
        # Create converter
        converter = VideoConverter(output_dir="converted_output")
        
        # Example video conversion
        video_path = "example.mp4"
        if Path(video_path).exists():
            print("\nConverting video to multiple formats:")
            output_paths = converter.convert_multiple(
                video_path,
                formats=["avi", "webm"],
                quality="medium"
            )
            for path in output_paths:
                print(f"Converted: {path}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
