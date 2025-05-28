#!/usr/bin/env python3
"""
video_creator.py

This module provides functionality to create videos from images and audio files,
with optional background music.
"""

import os
from typing import List, Optional, Tuple
from pathlib import Path
import numpy as np
from moviepy.editor import (
    ImageClip, 
    AudioFileClip, 
    CompositeVideoClip, 
    concatenate_videoclips,
    VideoFileClip
)

class VideoCreator:
    """
    A class to create videos from images and audio files with background music.
    
    Attributes:
        output_dir (Path): Directory to save generated videos
        default_duration (float): Default duration for images without audio
        fade_duration (float): Duration of fade effects between clips
    """
    
    def __init__(self, 
                 output_dir: str = "generated_videos",
                 default_duration: float = 5.0,
                 fade_duration: float = 1.0):
        """
        Initialize the VideoCreator.
        
        Args:
            output_dir: Directory to save generated videos
            default_duration: Default duration for images without audio (seconds)
            fade_duration: Duration of fade effects between clips (seconds)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.default_duration = default_duration
        self.fade_duration = fade_duration
    
    def create_video(self,
                    image_paths: List[str],
                    audio_paths: Optional[List[str]] = None,
                    background_music_path: Optional[str] = None,
                    output_filename: str = "output.mp4",
                    bg_music_volume: float = 0.3,
                    fps: int = 24) -> str:
        """
        Create a video from images and audio files.
        
        Args:
            image_paths: List of paths to image files
            audio_paths: Optional list of paths to audio files (must match images)
            background_music_path: Optional path to background music file
            output_filename: Name of the output video file
            bg_music_volume: Volume level for background music (0.0 to 1.0)
            fps: Frames per second for the output video
            
        Returns:
            Path to the generated video file
            
        Raises:
            ValueError: If inputs are invalid
            FileNotFoundError: If any input files are missing
        """
        # Validate inputs
        if not image_paths:
            raise ValueError("At least one image path must be provided")
        
        if audio_paths and len(audio_paths) != len(image_paths):
            raise ValueError("Number of audio files must match number of images")
        
        # Verify all files exist
        for path in image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
        
        if audio_paths:
            for path in audio_paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Audio file not found: {path}")
        
        if background_music_path and not os.path.exists(background_music_path):
            raise FileNotFoundError(f"Background music file not found: {background_music_path}")
        
        # Create video clips
        video_clips = []
        for i, image_path in enumerate(image_paths):
            # Create image clip
            image_clip = ImageClip(image_path)
            
            # Get duration from audio if available, otherwise use default
            duration = self.default_duration
            if audio_paths and audio_paths[i]:
                audio_clip = AudioFileClip(audio_paths[i])
                duration = audio_clip.duration
                image_clip = image_clip.set_audio(audio_clip)
            
            # Set duration and add fade effects
            image_clip = image_clip.set_duration(duration)
            
            # Add fade in/out
            if i == 0:  # First clip
                image_clip = image_clip.fadein(self.fade_duration)
            if i == len(image_paths) - 1:  # Last clip
                image_clip = image_clip.fadeout(self.fade_duration)
            
            video_clips.append(image_clip)
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(video_clips, 
                                          method="compose",
                                          padding=-self.fade_duration)
        
        # Add background music if provided
        if background_music_path:
            bg_music = AudioFileClip(background_music_path)
            
            # Loop music if it's shorter than the video
            if bg_music.duration < final_clip.duration:
                num_loops = int(np.ceil(final_clip.duration / bg_music.duration))
                bg_music = concatenate_videoclips([bg_music] * num_loops).subclip(0, final_clip.duration)
            else:
                # Trim music if it's longer than the video
                bg_music = bg_music.subclip(0, final_clip.duration)
            
            # Set volume and add to video
            bg_music = bg_music.volumex(bg_music_volume)
            final_clip = final_clip.set_audio(CompositeVideoClip([final_clip]).audio.set_duration(final_clip.duration))
            final_clip = final_clip.set_audio(CompositeVideoClip([
                final_clip,
                ImageClip(np.zeros((1, 1, 3)), duration=final_clip.duration).set_audio(bg_music)
            ]).audio)
        
        # Ensure output filename has .mp4 extension
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        output_path = self.output_dir / output_filename
        
        # Write the final video
        final_clip.write_videofile(
            str(output_path),
            fps=fps,
            codec='libx264',
            audio_codec='aac'
        )
        
        # Close clips to free up resources
        final_clip.close()
        for clip in video_clips:
            clip.close()
        
        return str(output_path)
    
    @staticmethod
    def get_video_info(video_path: str) -> Tuple[float, Tuple[int, int], float]:
        """
        Get information about a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Tuple containing:
            - Duration in seconds
            - Tuple of (width, height)
            - FPS (frames per second)
            
        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        video = VideoFileClip(video_path)
        duration = video.duration
        size = (video.w, video.h)
        fps = video.fps
        video.close()
        
        return duration, size, fps

def main():
    """Example usage of the VideoCreator class."""
    # Example image and audio paths
    image_paths = [
        "example_images/image1.jpg",
        "example_images/image2.jpg",
        "example_images/image3.jpg"
    ]
    
    audio_paths = [
        "example_audio/audio1.mp3",
        "example_audio/audio2.mp3",
        "example_audio/audio3.mp3"
    ]
    
    try:
        # Create video creator
        creator = VideoCreator(
            output_dir="output_videos",
            default_duration=5.0,
            fade_duration=1.0
        )
        
        # Create video with background music
        output_path = creator.create_video(
            image_paths=image_paths,
            audio_paths=audio_paths,
            background_music_path="example_audio/background.mp3",
            output_filename="my_video.mp4",
            bg_music_volume=0.3
        )
        
        print(f"\nVideo created successfully!")
        print(f"Output path: {output_path}")
        
        # Get video information
        duration, (width, height), fps = creator.get_video_info(output_path)
        print(f"\nVideo Information:")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Resolution: {width}x{height}")
        print(f"FPS: {fps}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
