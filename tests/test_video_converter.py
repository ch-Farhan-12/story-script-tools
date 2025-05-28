"""
Unit tests for the video converter module.
"""

import pytest
import os
import shutil
from pathlib import Path
import subprocess
from python_scripts.video_converter import VideoConverter

@pytest.fixture(scope="function")
def video_converter(tmp_path):
    """Create a VideoConverter instance for testing."""
    output_dir = tmp_path / "test_converted"
    return VideoConverter(output_dir=str(output_dir))

@pytest.fixture
def test_video(tmp_path):
    """Create a test video file."""
    video_path = tmp_path / "test_video.mp4"
    
    # Create a 3-second test video using FFmpeg
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=3:size=320x240:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=3",
        "-c:v", "libx264", "-c:a", "aac", str(video_path)
    ], check=True)
    
    return str(video_path)

def test_initialization(video_converter):
    """Test VideoConverter initialization."""
    assert isinstance(video_converter.output_dir, Path)
    assert video_converter.output_dir.exists()

def test_convert_to_avi(video_converter, test_video):
    """Test converting video to AVI format."""
    output_path = video_converter.convert(test_video, "avi")
    assert os.path.exists(output_path)
    assert output_path.endswith(".avi")

def test_convert_to_webm(video_converter, test_video):
    """Test converting video to WebM format."""
    output_path = video_converter.convert(test_video, "webm")
    assert os.path.exists(output_path)
    assert output_path.endswith(".webm")

def test_convert_multiple(video_converter, test_video):
    """Test converting video to multiple formats."""
    formats = ["avi", "webm"]
    output_paths = video_converter.convert_multiple(test_video, formats)
    
    assert len(output_paths) == len(formats)
    for path, fmt in zip(output_paths, formats):
        assert os.path.exists(path)
        assert path.endswith(f".{fmt}")

def test_custom_output_filename(video_converter, test_video):
    """Test custom output filename functionality."""
    custom_name = "custom_output.avi"
    output_path = video_converter.convert(
        test_video,
        "avi",
        output_filename=custom_name
    )
    assert os.path.basename(output_path) == custom_name

def test_quality_settings(video_converter, test_video):
    """Test different quality settings."""
    for quality in ["low", "medium", "high"]:
        output_path = video_converter.convert(
            test_video,
            "mp4",
            quality=quality,
            output_filename=f"quality_{quality}.mp4"
        )
        assert os.path.exists(output_path)

def test_invalid_format(video_converter, test_video):
    """Test handling of invalid format."""
    with pytest.raises(ValueError):
        video_converter.convert(test_video, "invalid_format")

def test_nonexistent_file(video_converter):
    """Test handling of nonexistent input file."""
    with pytest.raises(FileNotFoundError):
        video_converter.convert("nonexistent.mp4", "avi")

def test_file_exists_no_overwrite(video_converter, test_video):
    """Test handling of existing output file without overwrite."""
    # First conversion
    output_filename = "test_no_overwrite.avi"
    output_path = video_converter.convert(
        test_video,
        "avi",
        output_filename=output_filename
    )
    
    # Second conversion should fail
    with pytest.raises(FileExistsError):
        video_converter.convert(
            test_video,
            "avi",
            output_filename=output_filename
        )

def test_file_exists_with_overwrite(video_converter, test_video):
    """Test handling of existing output file with overwrite."""
    # First conversion
    output_filename = "test_overwrite.avi"
    output_path = video_converter.convert(
        test_video,
        "avi",
        output_filename=output_filename
    )
    
    # Second conversion should succeed
    output_path = video_converter.convert(
        test_video,
        "avi",
        output_filename=output_filename,
        overwrite=True
    )
    assert os.path.exists(output_path)
