"""
Unit tests for the story enhancer module.
"""

import pytest
from python_scripts.story_enhancer import StoryEnhancer, EmotionalElement, PlotTwist

@pytest.fixture
def story_enhancer():
    """Create a StoryEnhancer instance for testing."""
    return StoryEnhancer()

@pytest.fixture
def sample_scene():
    """Create a sample scene for testing."""
    return {
        "scene_number": 1,
        "description": "John sits alone in his room, struggling with a difficult decision."
    }

@pytest.fixture
def sample_script():
    """Create a sample script for testing."""
    return """
    Scene 1: The Beginning
    Sarah sits alone in her apartment, struggling with her thoughts.
    
    Scene 2: The Discovery
    A mysterious package arrives at her doorstep.
    
    Scene 3: The Decision
    Sarah must choose between two difficult paths.
    """

def test_initialization(story_enhancer):
    """Test StoryEnhancer initialization."""
    assert len(story_enhancer.emotional_elements) > 0
    assert len(story_enhancer.plot_twists) > 0

def test_analyze_emotional_potential(story_enhancer, sample_scene):
    """Test emotional potential analysis."""
    elements = story_enhancer.analyze_emotional_potential(sample_scene)
    assert len(elements) > 0
    assert all(isinstance(element, EmotionalElement) for element in elements)

def test_identify_plot_twist_opportunities(story_enhancer):
    """Test plot twist opportunity identification."""
    scenes = [
        {"scene_number": 1, "description": "A mysterious past haunts the character"},
        {"scene_number": 2, "description": "Strange coincidences begin to occur"}
    ]
    twists = story_enhancer.identify_plot_twist_opportunities(scenes)
    assert len(twists) > 0
    assert all(isinstance(twist, PlotTwist) for twist in twists)

def test_enhance_scene(story_enhancer, sample_scene):
    """Test scene enhancement."""
    enhanced_scene = story_enhancer.enhance_scene(sample_scene)
    assert enhanced_scene["scene_number"] == sample_scene["scene_number"]
    assert len(enhanced_scene["description"]) > len(sample_scene["description"])
    assert "[Emotional Enhancement" in enhanced_scene["description"]

def test_add_plot_twist(story_enhancer):
    """Test adding plot twist."""
    scenes = [
        {"scene_number": 1, "description": "Scene one"},
        {"scene_number": 2, "description": "Scene two"},
        {"scene_number": 3, "description": "Scene three"},
        {"scene_number": 4, "description": "Scene four"}
    ]
    enhanced_scenes = story_enhancer.add_plot_twist(scenes)
    assert len(enhanced_scenes) == len(scenes)
    assert any("[Plot Twist" in scene["description"] for scene in enhanced_scenes)

def test_enhance_story(story_enhancer, sample_script):
    """Test complete story enhancement."""
    enhanced_script = story_enhancer.enhance_story(sample_script)
    assert len(enhanced_script) > len(sample_script)
    assert "[Emotional Enhancement" in enhanced_script
    assert "[Plot Twist" in enhanced_script

def test_enhance_empty_script(story_enhancer):
    """Test handling of empty script."""
    with pytest.raises(ValueError):
        story_enhancer.enhance_story("")

def test_enhance_invalid_script(story_enhancer):
    """Test handling of invalid script."""
    with pytest.raises(ValueError):
        story_enhancer.enhance_story("Invalid script without proper scene markers")

def test_emotional_element_intensity(story_enhancer):
    """Test emotional element intensity ranges."""
    for element in story_enhancer.emotional_elements:
        assert 1 <= element.intensity <= 10

def test_plot_twist_impact(story_enhancer):
    """Test plot twist impact ranges."""
    for twist in story_enhancer.plot_twists:
        assert 1 <= twist.impact <= 10
