"""
Unit tests for the scene to prompt generator module.
"""

import pytest
from python_scripts.scene_to_prompt import PromptGenerator

def test_valid_scene_description():
    """Test generating a prompt from a valid scene description."""
    scene = "a medieval marketplace at sunset"
    prompt = PromptGenerator.generate_image_prompt(scene)
    
    # Check that the prompt contains the scene description
    assert scene in prompt
    
    # Check that the prompt contains elements from each modifier category
    style_found = any(style in prompt.lower() for style in PromptGenerator.STYLE_MODIFIERS)
    artistic_found = any(art in prompt.lower() for art in PromptGenerator.ARTISTIC_STYLES)
    atmosphere_found = any(atm in prompt.lower() for atm in PromptGenerator.ATMOSPHERE_ENHANCERS)
    
    assert style_found, "Prompt should contain style modifiers"
    assert artistic_found, "Prompt should contain artistic styles"
    assert atmosphere_found, "Prompt should contain atmosphere enhancers"

def test_empty_input():
    """Test that empty input raises ValueError."""
    with pytest.raises(ValueError, match="Scene description cannot be empty"):
        PromptGenerator.generate_image_prompt("")
    
    with pytest.raises(ValueError, match="Scene description cannot be empty"):
        PromptGenerator.generate_image_prompt("   ")

def test_invalid_input_type():
    """Test that non-string input raises ValueError."""
    with pytest.raises(ValueError, match="Scene description must be a string"):
        PromptGenerator.generate_image_prompt(None)
    
    with pytest.raises(ValueError, match="Scene description must be a string"):
        PromptGenerator.generate_image_prompt(123)

def test_prompt_structure():
    """Test that the generated prompt follows the expected structure."""
    scene = "a futuristic city"
    prompt = PromptGenerator.generate_image_prompt(scene)
    
    # Check basic prompt structure
    assert prompt.startswith("A "), "Prompt should start with 'A '"
    assert "scene of" in prompt, "Prompt should contain 'scene of'"
    assert "with" in prompt, "Prompt should contain 'with' for style modifiers"

def test_custom_modifier_count():
    """Test generating a prompt with a custom number of modifiers."""
    scene = "a peaceful garden"
    prompt = PromptGenerator.generate_image_prompt(scene, num_modifiers=1)
    
    # Count the number of modifiers used
    modifier_count = sum(1 for mod in PromptGenerator.STYLE_MODIFIERS if mod in prompt.lower())
    artistic_count = sum(1 for art in PromptGenerator.ARTISTIC_STYLES if art in prompt.lower())
    atmosphere_count = sum(1 for atm in PromptGenerator.ATMOSPHERE_ENHANCERS if atm in prompt.lower())
    
    # With num_modifiers=1, we should have at most 1 modifier from each category
    assert modifier_count <= 1, "Should have at most 1 style modifier"
    assert artistic_count <= 1, "Should have at most 1 artistic style"
    assert atmosphere_count <= 1, "Should have at most 1 atmosphere enhancer"

def test_additional_context():
    """Test generating a prompt with additional context."""
    scene = "a mountain landscape"
    context = "trending on artstation"
    prompt = PromptGenerator.generate_image_prompt(scene, additional_context=context)
    
    # Check that both scene and context are in the prompt
    assert scene in prompt, "Prompt should contain the scene description"
    assert context in prompt, "Prompt should contain the additional context"

def test_whitespace_handling():
    """Test that the generator properly handles whitespace in input."""
    scene = "  a desert oasis   \n  with palm trees  "
    prompt = PromptGenerator.generate_image_prompt(scene)
    
    # Check that excessive whitespace is cleaned up
    assert "  a desert" not in prompt, "Leading whitespace should be removed"
    assert "trees  " not in prompt, "Trailing whitespace should be removed"
    assert "\n" not in prompt, "Newlines should be removed"
