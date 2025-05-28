"""
Unit tests for the video creator module.
"""

import pytest
import os
import numpy as np
from pathlib import Path
from PIL import Image
from moviepy.editor import AudioClip, ColorClip, ImageClip
from python_scripts.video_creator import VideoCreator

@pytest.fixture
def video_creator():
    """Create a VideoCreator instance for testing."""
    return VideoCreator(output_dir="test_output")

@pytest.fixture
def test_files(tmp_path):
    """Create test image and audio files."""
    # Create test images
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    image_paths = []
    
    for i in range(3):
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color=(i*50, i*50, i*50))
        img_path = image_dir / f"test_image_{i}.jpg"
        img.save(img_path)
        image_paths.append(str(img_path))
    
    # Create test audio files (1 second of silence)
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    audio_paths = []
    
    def make_frame(t):
        """Create a silent audio frame."""
        return np.zeros((2,))  # Stereo silence
    
    for i in range(3):
        audio_path = audio_dir / f"test_audio_{i}.mp3"
        # Create a silent audio clip
        silent_clip = AudioClip(make_frame, duration=1.0)
        silent_clip.write_audiofile(str(audio_path), fps=44100, nbytes=2)
        audio_paths.append(str(audio_path))
    
    # Create background music
    bg_music_path = audio_dir / "background.mp3"
    bg_clip = AudioClip(make_frame, duration=3.0)
    bg_clip.write_audiofile(str(bg_music_path), fps=44100, nbytes=2)
    
    return {
        "image_paths": image_paths,
        "audio_paths": audio_paths,
        "bg_music_path": str(bg_music_path)
    }

def test_initialization(video_creator):
    """Test VideoCreator initialization."""
    assert isinstance(video_creator.output_dir, Path)
    assert video_creator.output_dir.exists()
    assert video_creator.default_duration == 5.0
    assert video_creator.fade_duration == 1.0

def test_empty_image_paths(video_creator):
    """Test that empty image paths raises ValueError."""
    with pytest.raises(ValueError):
        video_creator.create_video([])

def test_mismatched_audio_paths(video_creator, test_files):
    """Test that mismatched number of audio files raises ValueError."""
    with pytest.raises(ValueError):
        video_creator.create_video(
            test_files["image_paths"],
            audio_paths=test_files["audio_paths"][:1]  # Fewer audio files than images
        )

def test_nonexistent_files(video_creator):
    """Test that nonexistent files raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        video_creator.create_video(["nonexistent.jpg"])
    
    # Create a temporary image for testing
    img = Image.new('RGB', (100, 100), color=(0, 0, 0))
    img_path = "temp_test.jpg"
    img.save(img_path)
    
    try:
        with pytest.raises(FileNotFoundError):
            video_creator.create_video(
                [img_path],
                audio_paths=["nonexistent.mp3"]
            )
    finally:
        # Clean up
        os.remove(img_path)

def test_successful_video_creation(video_creator):
    """Test successful video creation with basic options."""
    # Create a simple test video
    img = Image.new('RGB', (100, 100), color=(0, 0, 0))
    img_path = "test_image.jpg"
    img.save(img_path)
    
    try:
        output_path = video_creator.create_video(
            image_paths=[img_path],
            output_filename="test_video.mp4"
        )
        
        # Check that output file exists
        assert os.path.exists(output_path)
        assert output_path.endswith(".mp4")
        
        # Check video properties
        duration, size, fps = video_creator.get_video_info(output_path)
        assert duration > 0
        assert size == (100, 100)
        assert fps == 24
    finally:
        # Clean up
        os.remove(img_path)

def test_video_info(video_creator):
    """Test getting video information."""
    # Create a simple video clip for testing
    clip = ColorClip((100, 100), color=(0, 0, 0), duration=1)
    output_path = str(video_creator.output_dir / "info_test.mp4")
    clip.write_videofile(output_path, fps=24)
    
    duration, size, fps = video_creator.get_video_info(output_path)
    assert isinstance(duration, float)
    assert isinstance(size, tuple)
    assert isinstance(fps, (int, float))
    assert len(size) == 2
    assert all(isinstance(x, int) for x in size)

def test_cleanup():
    """Clean up test files after running tests."""
    test_dir = Path("test_output")
    if test_dir.exists():
        for file in test_dir.glob("*.mp4"):
            try:
                file.unlink()
            except OSError:
                pass
        try:
            test_dir.rmdir()
        except OSError:
            pass

# Run cleanup after all tests
def teardown_module(module):
    """Clean up after all tests have run."""
    test_cleanup()
