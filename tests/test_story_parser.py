"""
Unit tests for the story parser module.
"""

import pytest
from python_scripts.story_parser import parse_story_script

def test_valid_script():
    """Test parsing a valid script with multiple scenes."""
    script = """
    Scene 1: The Beginning
    This is the first scene.
    
    Scene 2: The Middle
    This is the second scene.
    
    Scene 3: The End
    This is the final scene.
    """
    
    result = parse_story_script(script)
    
    assert len(result) == 3
    assert result[0]["scene_number"] == 1
    assert "first scene" in result[0]["description"]
    assert result[1]["scene_number"] == 2
    assert "second scene" in result[1]["description"]
    assert result[2]["scene_number"] == 3
    assert "final scene" in result[2]["description"]

def test_empty_input():
    """Test that empty input raises ValueError."""
    with pytest.raises(ValueError):
        parse_story_script("")
    
    with pytest.raises(ValueError):
        parse_story_script("   ")

def test_invalid_input_type():
    """Test that non-string input raises ValueError."""
    with pytest.raises(ValueError):
        parse_story_script(None)
    
    with pytest.raises(ValueError):
        parse_story_script(123)

def test_no_scenes():
    """Test that script without scene markers raises ValueError."""
    script = "This is just some text without any scene markers."
    with pytest.raises(ValueError):
        parse_story_script(script)

def test_single_scene():
    """Test parsing a script with only one scene."""
    script = "Scene 1: The Only Scene\nThis is the only scene in the script."
    
    result = parse_story_script(script)
    
    assert len(result) == 1
    assert result[0]["scene_number"] == 1
    assert "only scene" in result[0]["description"]

def test_scene_with_multiple_paragraphs():
    """Test parsing a scene that contains multiple paragraphs."""
    script = """Scene 1: Complex Scene
    First paragraph of the scene.
    
    Second paragraph of the scene.
    
    Third paragraph with multiple lines
    and more content here.
    Scene 2: Next Scene
    The second scene starts here.
    """
    
    result = parse_story_script(script)
    
    assert len(result) == 2
    assert "First paragraph" in result[0]["description"]
    assert "Second paragraph" in result[0]["description"]
    assert "Third paragraph" in result[0]["description"]
    assert "second scene" in result[1]["description"].lower()
