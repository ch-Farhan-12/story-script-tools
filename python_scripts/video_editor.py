#!/usr/bin/env python3
"""
video_editor.py

A module providing basic video editing functionalities using MoviePy.
Features include:
- Trimming videos
- Adding transitions (fade, slide)
- Adding text overlays
- Combining multiple clips
"""

from typing import List, Tuple, Optional, Union, Literal
from pathlib import Path
import numpy as np
from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx,
    transfx
)

TransitionType = Literal["fade", "slide_left", "slide_right", "slide_up", "slide_down"]

class VideoEditor:
    """
    A class providing video editing functionality.
    """
    
    def __init__(self, output_dir: str = "edited_videos"):
        """
        Initialize the VideoEditor.
        
        Args:
            output_dir: Directory to save edited videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def trim_video(self,
                  video_path: str,
                  start_time: float,
                  end_time: float,
                  output_filename: Optional[str] = None) -> str:
        """
        Trim a video to specified start and end times.
        
        Args:
            video_path: Path to input video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_filename: Optional custom filename for output
            
        Returns:
            Path to the trimmed video
        """
        # Load video
        video = VideoFileClip(video_path)
        
        # Validate times
        if start_time < 0:
            start_time = 0
        if end_time > video.duration:
            end_time = video.duration
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")
        
        # Trim video
        trimmed = video.subclip(start_time, end_time)
        
        # Set output filename
        if output_filename is None:
            base_name = Path(video_path).stem
            output_filename = f"{base_name}_trimmed.mp4"
        
        output_path = self.output_dir / output_filename
        
        # Write video
        trimmed.write_videofile(str(output_path))
        
        # Clean up
        video.close()
        trimmed.close()
        
        return str(output_path)
    
    def add_text(self,
                video_path: str,
                text: str,
                position: Tuple[str, str] = ('center', 'center'),
                start_time: Optional[float] = None,
                end_time: Optional[float] = None,
                fontsize: int = 50,
                color: str = 'white',
                font: str = 'DejaVu-Sans',
                output_filename: Optional[str] = None) -> str:
        """
        Add text overlay to a video.
        
        Args:
            video_path: Path to input video
            text: Text to overlay
            position: Tuple of (x, y) position ('left', 'center', 'right' for x; 'top', 'center', 'bottom' for y)
            start_time: When to start showing text (None for start of video)
            end_time: When to stop showing text (None for end of video)
            fontsize: Font size
            color: Text color
            font: Font name
            output_filename: Optional custom filename for output
            
        Returns:
            Path to the video with text overlay
        """
        # Load video
        video = VideoFileClip(video_path)
        
        # Create text clip
        txt_clip = TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font=font,
            size=video.size  # Set size to match video
        )
        
        # Set position
        txt_clip = txt_clip.set_position(position)
        
        # Set duration
        if start_time is None:
            start_time = 0
        if end_time is None:
            end_time = video.duration
            
        txt_clip = txt_clip.set_start(start_time).set_end(end_time)
        
        # Composite video
        final = CompositeVideoClip([video, txt_clip])
        
        # Set output filename
        if output_filename is None:
            base_name = Path(video_path).stem
            output_filename = f"{base_name}_with_text.mp4"
        
        output_path = self.output_dir / output_filename
        
        # Write video
        final.write_videofile(str(output_path))
        
        # Clean up
        video.close()
        txt_clip.close()
        final.close()
        
        return str(output_path)
    
    def add_transition(self,
                      video_paths: List[str],
                      transition_type: TransitionType = "fade",
                      transition_duration: float = 1.0,
                      output_filename: Optional[str] = None) -> str:
        """
        Combine multiple videos with transitions.
        
        Args:
            video_paths: List of paths to input videos
            transition_type: Type of transition
            transition_duration: Duration of transition in seconds
            output_filename: Optional custom filename for output
            
        Returns:
            Path to the combined video with transitions
        """
        if len(video_paths) < 2:
            raise ValueError("Need at least 2 videos to add transitions")
        
        # Load videos
        clips = [VideoFileClip(path) for path in video_paths]
        final_clips = []
        
        # Apply transitions
        for i, clip in enumerate(clips):
            if i == len(clips) - 1:  # Last clip
                final_clips.append(clip)
                continue
                
            if transition_type == "fade":
                # Adjust clip durations for proper transition timing
                clip = clip.set_duration(clip.duration - transition_duration/2)
                next_clip = clips[i + 1].set_duration(clips[i + 1].duration - transition_duration/2)
                
                clip = clip.crossfadeout(transition_duration/2)
                next_clip = next_clip.crossfadein(transition_duration/2)
            elif transition_type == "slide_left":
                clip = clip.fx(transfx.slide_out, duration=transition_duration, side="left")
                next_clip = clips[i + 1].fx(transfx.slide_in, duration=transition_duration, side="right")
            elif transition_type == "slide_right":
                clip = clip.fx(transfx.slide_out, duration=transition_duration, side="right")
                next_clip = clips[i + 1].fx(transfx.slide_in, duration=transition_duration, side="left")
            elif transition_type == "slide_up":
                clip = clip.fx(transfx.slide_out, duration=transition_duration, side="top")
                next_clip = clips[i + 1].fx(transfx.slide_in, duration=transition_duration, side="bottom")
            elif transition_type == "slide_down":
                clip = clip.fx(transfx.slide_out, duration=transition_duration, side="bottom")
                next_clip = clips[i + 1].fx(transfx.slide_in, duration=transition_duration, side="top")
            
            final_clips.append(clip)
            clips[i + 1] = next_clip
        
        # Concatenate clips
        final = concatenate_videoclips(final_clips)
        
        # Set output filename
        if output_filename is None:
            output_filename = "combined_with_transitions.mp4"
        
        output_path = self.output_dir / output_filename
        
        # Write video
        final.write_videofile(str(output_path))
        
        # Clean up
        for clip in clips:
            clip.close()
        final.close()
        
        return str(output_path)

def main():
    """Example usage of the VideoEditor class."""
    try:
        # Create editor
        editor = VideoEditor(output_dir="edited_output")
        
        # Example video trimming
        video_path = "example.mp4"
        if Path(video_path).exists():
            print("\nTrimming video:")
            output_path = editor.trim_video(
                video_path,
                start_time=5,
                end_time=10
            )
            print(f"Output: {output_path}")
        
        # Example text overlay
        if Path(video_path).exists():
            print("\nAdding text overlay:")
            output_path = editor.add_text(
                video_path,
                text="Hello World!",
                position=('center', 'bottom'),
                fontsize=70,
                color='white'
            )
            print(f"Output: {output_path}")
        
        # Example transitions
        video_paths = ["video1.mp4", "video2.mp4"]
        if all(Path(p).exists() for p in video_paths):
            print("\nCombining videos with transition:")
            output_path = editor.add_transition(
                video_paths,
                transition_type="fade",
                transition_duration=1.0
            )
            print(f"Output: {output_path}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
