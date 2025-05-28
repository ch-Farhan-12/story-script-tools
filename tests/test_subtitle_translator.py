"""
Unit tests for the subtitle translator module.
"""

import pytest
import os
from pathlib import Path
import responses
from python_scripts.subtitle_translator import SubtitleTranslator, SubtitleEntry

@pytest.fixture
def subtitle_translator(tmp_path):
    """Create a SubtitleTranslator instance for testing."""
    return SubtitleTranslator(output_dir=str(tmp_path))

@pytest.fixture
def sample_srt():
    """Create a sample SRT content."""
    return """1
00:00:01,000 --> 00:00:04,000
Hello, welcome to our video.

2
00:00:04,500 --> 00:00:08,000
Today we'll learn something interesting.
"""

@pytest.fixture
def sample_entries():
    """Create sample subtitle entries."""
    return [
        SubtitleEntry(
            index=1,
            start_time="00:00:01,000",
            end_time="00:00:04,000",
            text="Hello, welcome to our video."
        ),
        SubtitleEntry(
            index=2,
            start_time="00:00:04,500",
            end_time="00:00:08,000",
            text="Today we'll learn something interesting."
        )
    ]

def test_initialization(subtitle_translator):
    """Test SubtitleTranslator initialization."""
    assert subtitle_translator.output_dir.exists()
    assert subtitle_translator.tts_generator is None

def test_parse_srt(subtitle_translator, sample_srt, sample_entries):
    """Test SRT parsing."""
    entries = subtitle_translator.parse_srt(sample_srt)
    assert len(entries) == len(sample_entries)
    
    for parsed, expected in zip(entries, sample_entries):
        assert parsed.index == expected.index
        assert parsed.start_time == expected.start_time
        assert parsed.end_time == expected.end_time
        assert parsed.text == expected.text

def test_parse_invalid_srt(subtitle_translator):
    """Test handling of invalid SRT content."""
    invalid_srt = "This is not a valid SRT file"
    with pytest.raises(ValueError, match="Invalid SRT format: missing subtitle numbers"):
        subtitle_translator.parse_srt(invalid_srt)

def test_save_srt(subtitle_translator, sample_entries):
    """Test saving SRT file."""
    output_path = subtitle_translator.save_srt(sample_entries, "test.srt")
    assert os.path.exists(output_path)
    
    # Verify content
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "00:00:01,000 --> 00:00:04,000" in content
        assert "Hello, welcome to our video." in content

def test_language_mapping(subtitle_translator):
    """Test language code mapping."""
    assert "en" in subtitle_translator.LANGUAGE_MAPPING
    assert "voice_id" in subtitle_translator.LANGUAGE_MAPPING["en"]
    assert "code" in subtitle_translator.LANGUAGE_MAPPING["en"]

@responses.activate
def test_translation_error_handling(subtitle_translator):
    """Test handling of translation errors."""
    # Mock error response
    responses.add(
        responses.POST,
        subtitle_translator.translate_url,
        json={"error": "Invalid language"},
        status=400
    )
    
    with pytest.raises(RuntimeError, match="Translation request failed"):
        subtitle_translator.translate_text(
            "Test text",
            source_lang="invalid",
            target_lang="invalid"
        )

def test_voiceover_without_api_key(subtitle_translator, sample_entries):
    """Test voiceover generation without API key."""
    with pytest.raises(RuntimeError, match="TTS Generator not initialized"):
        subtitle_translator.generate_voiceover(
            sample_entries,
            target_lang="es"
        )

@responses.activate
def test_process_subtitles(subtitle_translator, sample_srt, tmp_path):
    """Test complete subtitle processing."""
    # Mock successful translation responses for both subtitles
    responses.add(
        responses.POST,
        subtitle_translator.translate_url,
        json={"translatedText": "Hola, bienvenidos a nuestro video."},
        status=200
    )
    
    responses.add(
        responses.POST,
        subtitle_translator.translate_url,
        json={"translatedText": "Hoy aprenderemos algo interesante."},
        status=200
    )
    
    # Create temporary input file
    input_path = tmp_path / "input.srt"
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(sample_srt)
    
    result = subtitle_translator.process_subtitles(
        str(input_path),
        source_lang="en",
        target_lang="es",
        generate_audio=False
    )
    
    assert "subtitles" in result
    assert os.path.exists(result["subtitles"])
    assert "audio" not in result  # Since generate_audio=False
    
    # Verify translated content
    with open(result["subtitles"], 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Hola, bienvenidos a nuestro video." in content
        assert "Hoy aprenderemos algo interesante." in content

def test_invalid_target_language(subtitle_translator, sample_entries):
    """Test handling of invalid target language for voiceover."""
    translator = SubtitleTranslator(tts_api_key="dummy_key")
    with pytest.raises(ValueError, match="Unsupported target language"):
        translator.generate_voiceover(
            sample_entries,
            target_lang="invalid"
        )

@responses.activate
def test_mock_translation(subtitle_translator):
    """Test translation with mocked API response."""
    # Mock successful translation response
    responses.add(
        responses.POST,
        subtitle_translator.translate_url,
        json={"translatedText": "Hola, bienvenidos a nuestro video."},
        status=200
    )
    
    translated = subtitle_translator.translate_text(
        "Hello, welcome to our video.",
        source_lang="en",
        target_lang="es"
    )
    
    assert translated == "Hola, bienvenidos a nuestro video."

def test_empty_text_translation(subtitle_translator):
    """Test handling of empty text translation."""
    result = subtitle_translator.translate_text(
        "",
        source_lang="en",
        target_lang="es"
    )
    assert result == ""

def test_parse_empty_srt(subtitle_translator):
    """Test handling of empty SRT content."""
    with pytest.raises(ValueError, match="Invalid SRT content"):
        subtitle_translator.parse_srt("")
