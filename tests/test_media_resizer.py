"""
Unit tests for the media resizer module.
"""

import pytest
import os
import numpy as np
from pathlib import Path
from PIL import Image
from moviepy.editor import VideoFileClip, ColorClip
from python_scripts.media_resizer import MediaResizer

@pytest.fixture
def media_resizer():
    """Create a MediaResizer instance for testing."""
    return MediaResizer(output_dir="test_resized")

@pytest.fixture
def test_image(tmp_path):
    """Create a test image file."""
    image_path = tmp_path / "test_image.jpg"
    # Create a 400x300 test image (4:3 aspect ratio)
    img = Image.new('RGB', (400, 300), color='red')
    img.save(image_path)
    return str(image_path)

@pytest.fixture
def test_video(tmp_path):
    """Create a test video file."""
    video_path = tmp_path / "test_video.mp4"
    # Create a 400x300 test video (4:3 aspect ratio)
    clip = ColorClip(size=(400, 300), color=(255, 0, 0), duration=1)
    clip.write_videofile(str(video_path), fps=24)
    return str(video_path)

def test_initialization(media_resizer):
    """Test MediaResizer initialization."""
    assert isinstance(media_resizer.output_dir, Path)
    assert media_resizer.output_dir.exists()
    assert media_resizer.COMMON_RATIOS["16:9"] == (16, 9)
    assert media_resizer.COMMON_RATIOS["9:16"] == (9, 16)
    assert media_resizer.COMMON_RATIOS["1:1"] == (1, 1)

def test_nonexistent_files(media_resizer):
    """Test handling of nonexistent files."""
    with pytest.raises(FileNotFoundError):
        media_resizer.resize_image("nonexistent.jpg")
    
    with pytest.raises(FileNotFoundError):
        media_resizer.resize_video("nonexistent.mp4")

def test_invalid_aspect_ratio(media_resizer, test_image, test_video):
    """Test handling of invalid aspect ratios."""
    with pytest.raises(ValueError):
        media_resizer.resize_image(test_image, aspect_ratio="invalid")
    
    with pytest.raises(ValueError):
        media_resizer.resize_video(test_video, aspect_ratio="invalid")

def test_image_resizing(media_resizer, test_image):
    """Test image resizing functionality."""
    # Test different aspect ratios
    for ratio in ["16:9", "9:16", "1:1"]:
        output_path = media_resizer.resize_image(
            test_image,
            aspect_ratio=ratio,
            max_dimension=1920
        )
        
        # Check that output file exists
        assert os.path.exists(output_path)
        
        # Verify dimensions
        with Image.open(output_path) as img:
            width, height = img.size
            if ratio == "16:9":
                assert width / height == pytest.approx(16/9, rel=0.1)
            elif ratio == "9:16":
                assert width / height == pytest.approx(9/16, rel=0.1)
            elif ratio == "1:1":
                assert width == height

def test_video_resizing(media_resizer, test_video):
    """Test video resizing functionality."""
    # Test 16:9 aspect ratio
    output_path = media_resizer.resize_video(
        test_video,
        aspect_ratio="16:9",
        max_dimension=1920
    )
    
    # Check that output file exists
    assert os.path.exists(output_path)
    
    # Verify dimensions
    with VideoFileClip(output_path) as clip:
        width, height = clip.size
        assert width / height == pytest.approx(16/9, rel=0.1)

def test_max_dimension_constraint(media_resizer, test_image):
    """Test max dimension constraint."""
    max_dim = 800
    output_path = media_resizer.resize_image(
        test_image,
        aspect_ratio="16:9",
        max_dimension=max_dim
    )
    
    with Image.open(output_path) as img:
        width, height = img.size
        assert max(width, height) <= max_dim

def test_custom_output_filename(media_resizer, test_image, test_video):
    """Test custom output filename functionality."""
    # Test image
    custom_image_name = "custom_image.jpg"
    output_path = media_resizer.resize_image(
        test_image,
        aspect_ratio="16:9",
        output_filename=custom_image_name
    )
    assert os.path.basename(output_path) == custom_image_name
    
    # Test video
    custom_video_name = "custom_video.mp4"
    output_path = media_resizer.resize_video(
        test_video,
        aspect_ratio="16:9",
        output_filename=custom_video_name
    )
    assert os.path.basename(output_path) == custom_video_name

def test_fill_color(media_resizer, test_image):
    """Test fill color functionality."""
    fill_color = (0, 255, 0)  # Green
    output_path = media_resizer.resize_image(
        test_image,
        aspect_ratio="16:9",
        fill_color=fill_color
    )
    
    # Check fill color in corners (where padding should be)
    with Image.open(output_path) as img:
        # Convert to RGB if not already
        img = img.convert('RGB')
        # Check top-left corner pixel
        assert img.getpixel((0, 0)) == fill_color

def test_cleanup():
    """Clean up test files after running tests."""
    test_dir = Path("test_resized")
    if test_dir.exists():
        for file in test_dir.glob("*.*"):
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
