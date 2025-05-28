#!/usr/bin/env python3
"""
media_resizer.py

This module provides functionality to resize images and videos to specific aspect ratios
while maintaining quality and handling different input formats.
"""

import os
from typing import Tuple, Union, Literal
from pathlib import Path
import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip, ImageClip, ColorClip, CompositeVideoClip

AspectRatioType = Literal["16:9", "9:16", "1:1", "4:3", "3:4"]

class MediaResizer:
    """
    A class to handle resizing of images and videos to specific aspect ratios.
    
    Attributes:
        COMMON_RATIOS (dict): Dictionary of common aspect ratios and their dimensions
        output_dir (Path): Directory to save resized media
    """
    
    COMMON_RATIOS = {
        "16:9": (16, 9),
        "9:16": (9, 16),
        "1:1": (1, 1),
        "4:3": (4, 3),
        "3:4": (3, 4)
    }
    
    def __init__(self, output_dir: str = "resized_media"):
        """
        Initialize the MediaResizer.
        
        Args:
            output_dir: Directory to save resized media files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _calculate_dimensions(self, 
                            current_width: int, 
                            current_height: int, 
                            target_ratio: Tuple[int, int],
                            max_dimension: int = 1920) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Calculate new dimensions to match target aspect ratio.
        
        Args:
            current_width: Current width of the media
            current_height: Current height of the media
            target_ratio: Tuple of (width, height) ratio
            max_dimension: Maximum allowed dimension
            
        Returns:
            Tuple of ((new_width, new_height), (target_width, target_height))
        """
        target_w, target_h = target_ratio
        target_aspect = target_w / target_h
        current_aspect = current_width / current_height
        
        # Calculate new dimensions maintaining aspect ratio
        if current_aspect > target_aspect:
            # Media is wider than target ratio
            new_height = current_height
            new_width = int(new_height * target_aspect)
        else:
            # Media is taller than target ratio
            new_width = current_width
            new_height = int(new_width / target_aspect)
        
        # Scale down if exceeds max dimension
        if new_width > max_dimension or new_height > max_dimension:
            if new_width > new_height:
                scale = max_dimension / new_width
            else:
                scale = max_dimension / new_height
            new_width = int(new_width * scale)
            new_height = int(new_height * scale)
        
        # Calculate target dimensions for padding
        if new_width / new_height > target_aspect:
            target_height = new_height
            target_width = int(target_height * target_aspect)
        else:
            target_width = new_width
            target_height = int(target_width / target_aspect)
        
        return (new_width, new_height), (target_width, target_height)
    
    def resize_image(self,
                    image_path: str,
                    aspect_ratio: AspectRatioType = "16:9",
                    max_dimension: int = 1920,
                    output_filename: str = None,
                    fill_color: Tuple[int, int, int] = (0, 0, 0)) -> str:
        """
        Resize an image to match the target aspect ratio.
        
        Args:
            image_path: Path to the input image
            aspect_ratio: Target aspect ratio (e.g., "16:9", "9:16", "1:1")
            max_dimension: Maximum allowed dimension
            output_filename: Optional custom filename for output
            fill_color: RGB color tuple for padding
            
        Returns:
            Path to the resized image
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If aspect ratio is invalid
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if aspect_ratio not in self.COMMON_RATIOS:
            raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")
        
        # Open and get image dimensions
        img = Image.open(image_path)
        current_width, current_height = img.size
        
        # Calculate new dimensions
        (new_width, new_height), (target_width, target_height) = self._calculate_dimensions(
            current_width, current_height, 
            self.COMMON_RATIOS[aspect_ratio],
            max_dimension
        )
        
        # Create new image with padding
        new_img = Image.new('RGB', (target_width, target_height), fill_color)
        
        # Resize original image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate paste position to center the image
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        
        # Paste resized image onto padded background
        new_img.paste(resized_img, (paste_x, paste_y))
        
        # Set output filename
        if output_filename is None:
            base_name = Path(image_path).stem
            output_filename = f"{base_name}_{aspect_ratio.replace(':', 'x')}.jpg"
        
        output_path = self.output_dir / output_filename
        new_img.save(output_path, quality=95, optimize=True)
        
        return str(output_path)
    
    def resize_video(self,
                    video_path: str,
                    aspect_ratio: AspectRatioType = "16:9",
                    max_dimension: int = 1920,
                    output_filename: str = None,
                    fill_color: Tuple[int, int, int] = (0, 0, 0)) -> str:
        """
        Resize a video to match the target aspect ratio.
        
        Args:
            video_path: Path to the input video
            aspect_ratio: Target aspect ratio (e.g., "16:9", "9:16", "1:1")
            max_dimension: Maximum allowed dimension
            output_filename: Optional custom filename for output
            fill_color: RGB color tuple for padding
            
        Returns:
            Path to the resized video
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If aspect ratio is invalid
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if aspect_ratio not in self.COMMON_RATIOS:
            raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")
        
        # Load video
        video = VideoFileClip(video_path)
        current_width, current_height = video.size
        
        # Calculate new dimensions
        (new_width, new_height), (target_width, target_height) = self._calculate_dimensions(
            current_width, current_height,
            self.COMMON_RATIOS[aspect_ratio],
            max_dimension
        )
        
        # Create background clip with fill color
        bg_clip = ColorClip(
            size=(target_width, target_height),
            color=fill_color,
            duration=video.duration
        )
        
        # Resize video
        resized_video = video.resize((new_width, new_height))
        
        # Calculate position to center the video
        x_center = (target_width - new_width) // 2
        y_center = (target_height - new_height) // 2
        
        # Composite video onto background
        final_clip = CompositeVideoClip(
            [bg_clip, resized_video.set_position((x_center, y_center))],
            size=(target_width, target_height)
        )
        
        # Set output filename
        if output_filename is None:
            base_name = Path(video_path).stem
            output_filename = f"{base_name}_{aspect_ratio.replace(':', 'x')}.mp4"
        
        output_path = self.output_dir / output_filename
        
        # Write final video
        final_clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=video.fps
        )
        
        # Clean up
        video.close()
        final_clip.close()
        
        return str(output_path)

def main():
    """Example usage of the MediaResizer class."""
    try:
        # Create resizer
        resizer = MediaResizer(output_dir="resized_output")
        
        # Example image resizing
        image_path = "example.jpg"
        if os.path.exists(image_path):
            print(f"\nResizing image to different aspect ratios:")
            for ratio in ["16:9", "9:16", "1:1"]:
                output_path = resizer.resize_image(
                    image_path,
                    aspect_ratio=ratio,
                    max_dimension=1920
                )
                print(f"- {ratio}: {output_path}")
        
        # Example video resizing
        video_path = "example.mp4"
        if os.path.exists(video_path):
            print(f"\nResizing video to 16:9:")
            output_path = resizer.resize_video(
                video_path,
                aspect_ratio="16:9",
                max_dimension=1920
            )
            print(f"Output: {output_path}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
