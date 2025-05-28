"""
Unit tests for the video editor module.
"""

import pytest
import os
from pathlib import Path
from moviepy.editor import VideoFileClip, ColorClip
from python_scripts.video_editor import VideoEditor

@pytest.fixture
def video_editor():
    """Create a VideoEditor instance for testing."""
    return VideoEditor(output_dir="test_edited")

@pytest.fixture
def test_video(tmp_path):
    """Create a test video file."""
    video_path = tmp_path / "test_video.mp4"
    # Create a 3-second test video
    clip = ColorClip(size=(480, 360), color=(255, 0, 0), duration=3)
    clip.write_videofile(str(video_path), fps=24)
    return str(video_path)

@pytest.fixture
def test_videos(tmp_path):
    """Create multiple test video files."""
    video_paths = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    
    for i, color in enumerate(colors):
        video_path = tmp_path / f"test_video_{i}.mp4"
        clip = ColorClip(size=(480, 360), color=color, duration=2)
        clip.write_videofile(str(video_path), fps=24)
        video_paths.append(str(video_path))
    
    return video_paths

def test_initialization(video_editor):
    """Test VideoEditor initialization."""
    assert isinstance(video_editor.output_dir, Path)
    assert video_editor.output_dir.exists()

def test_trim_video(video_editor, test_video):
    """Test video trimming functionality."""
    output_path = video_editor.trim_video(
        test_video,
        start_time=1,
        end_time=2
    )
    
    assert os.path.exists(output_path)
    with VideoFileClip(output_path) as clip:
        assert abs(clip.duration - 1.0) < 0.1

def test_invalid_trim_times(video_editor, test_video):
    """Test handling of invalid trim times."""
    with pytest.raises(ValueError):
        video_editor.trim_video(test_video, start_time=2, end_time=1)

def test_add_text(video_editor, test_video):
    """Test text overlay functionality."""
    output_path = video_editor.add_text(
        test_video,
        text="Test Text",
        position=('center', 'center'),
        fontsize=50,
        color='white'
    )
    
    assert os.path.exists(output_path)
    with VideoFileClip(output_path) as clip:
        assert abs(clip.duration - 3.0) < 0.1

def test_add_transition(video_editor, test_videos):
    """Test transition functionality."""
    # Test fade transition
    output_path = video_editor.add_transition(
        test_videos[:2],
        transition_type="fade",
        transition_duration=0.5
    )
    
    assert os.path.exists(output_path)
    with VideoFileClip(output_path) as clip:
        # Duration should be sum of clips minus transition overlap
        expected_duration = 2 * 2 - 0.5
        assert abs(clip.duration - expected_duration) < 0.1

def test_invalid_transition(video_editor, test_video):
    """Test handling of invalid transition inputs."""
    with pytest.raises(ValueError):
        video_editor.add_transition([test_video])  # Need at least 2 videos

def test_custom_output_filename(video_editor, test_video, test_videos):
    """Test custom output filename functionality."""
    # Test trimming
    custom_name = "custom_trimmed.mp4"
    output_path = video_editor.trim_video(
        test_video,
        start_time=1,
        end_time=2,
        output_filename=custom_name
    )
    assert os.path.basename(output_path) == custom_name
    
    # Test text overlay
    custom_name = "custom_text.mp4"
    output_path = video_editor.add_text(
        test_video,
        text="Test",
        output_filename=custom_name
    )
    assert os.path.basename(output_path) == custom_name
    
    # Test transition
    custom_name = "custom_transition.mp4"
    output_path = video_editor.add_transition(
        test_videos[:2],
        output_filename=custom_name
    )
    assert os.path.basename(output_path) == custom_name

def test_cleanup():
    """Clean up test files after running tests."""
    test_dir = Path("test_edited")
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
