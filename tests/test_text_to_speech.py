"""
Unit tests for the text-to-speech module.
"""

import pytest
from unittest.mock import Mock, patch
import os
from pathlib import Path
from python_scripts.text_to_speech import TTSGenerator

# Mock API responses
MOCK_SUCCESS_RESPONSE = {
    "status": "success",
    "audio_url": "https://example.com/audio.mp3",
    "message": "Audio generated successfully"
}

MOCK_VOICES_RESPONSE = {
    "status": "success",
    "voices": [
        {
            "voice_id": "en-US-1",
            "name": "Emma",
            "language": "English (US)",
            "gender": "Female"
        },
        {
            "voice_id": "en-GB-1",
            "name": "James",
            "language": "English (UK)",
            "gender": "Male"
        }
    ]
}

@pytest.fixture
def tts_generator():
    """Create a TTSGenerator instance with test API key."""
    return TTSGenerator("test_api_key", output_dir="test_output")

def test_initialization(tts_generator):
    """Test TTSGenerator initialization."""
    assert tts_generator.api_key == "test_api_key"
    assert tts_generator.output_dir == Path("test_output")
    assert tts_generator.output_dir.exists()

def test_empty_text(tts_generator):
    """Test that empty text raises ValueError."""
    with pytest.raises(ValueError):
        tts_generator.generate_speech("")
    
    with pytest.raises(ValueError):
        tts_generator.generate_speech("   ")

def test_invalid_speed(tts_generator):
    """Test that invalid speed values raise ValueError."""
    with pytest.raises(ValueError):
        tts_generator.generate_speech("Test text", speed=0.4)
    
    with pytest.raises(ValueError):
        tts_generator.generate_speech("Test text", speed=2.1)

def test_invalid_volume(tts_generator):
    """Test that invalid volume values raise ValueError."""
    with pytest.raises(ValueError):
        tts_generator.generate_speech("Test text", volume=0.05)
    
    with pytest.raises(ValueError):
        tts_generator.generate_speech("Test text", volume=5.1)

@patch('requests.post')
@patch('requests.get')
def test_successful_generation(mock_get, mock_post, tts_generator):
    """Test successful speech generation."""
    # Mock the API response
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: MOCK_SUCCESS_RESPONSE
    )
    
    # Mock the audio download
    mock_get.return_value = Mock(
        status_code=200,
        content=b"mock audio content"
    )
    
    # Test with default parameters
    output_path = tts_generator.generate_speech("Test text")
    
    # Verify API call
    mock_post.assert_called_once()
    assert mock_post.call_args[1]['json']['text'] == "Test text"
    assert mock_post.call_args[1]['json']['voice_id'] == "en-US-1"
    
    # Verify file creation
    assert Path(output_path).exists()
    assert Path(output_path).suffix == '.mp3'

@patch('requests.post')
def test_api_error(mock_post, tts_generator):
    """Test handling of API errors."""
    # Mock an API error response
    mock_post.return_value = Mock(
        status_code=400,
        json=lambda: {
            "status": "error",
            "message": "Invalid API key"
        }
    )
    
    with pytest.raises(RuntimeError):
        tts_generator.generate_speech("Test text")

@patch('requests.get')
def test_list_voices(mock_get, tts_generator):
    """Test fetching available voices."""
    # Mock the API response
    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: MOCK_VOICES_RESPONSE
    )
    
    voices = tts_generator.list_available_voices()
    
    # Verify API call
    mock_get.assert_called_once()
    
    # Verify response parsing
    assert voices == MOCK_VOICES_RESPONSE
    assert len(voices["voices"]) == 2
    assert voices["voices"][0]["voice_id"] == "en-US-1"
    assert voices["voices"][1]["voice_id"] == "en-GB-1"

@patch('requests.post')
@patch('requests.get')
def test_custom_filename(mock_get, mock_post, tts_generator):
    """Test generation with custom filename."""
    # Mock the API response
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: MOCK_SUCCESS_RESPONSE
    )
    
    # Mock the audio download
    mock_get.return_value = Mock(
        status_code=200,
        content=b"mock audio content"
    )
    
    # Test with custom filename
    output_path = tts_generator.generate_speech("Test text", filename="custom_output")
    
    # Verify file creation with correct extension
    assert Path(output_path).name == "custom_output.mp3"

def test_cleanup():
    """Clean up test files after running tests."""
    test_dir = Path("test_output")
    if test_dir.exists():
        for file in test_dir.glob("*.mp3"):
            file.unlink()
        test_dir.rmdir()

# Run cleanup after all tests
def teardown_module(module):
    """Clean up after all tests have run."""
    test_cleanup()
