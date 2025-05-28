"""
Unit tests for the character module.
"""

import pytest
from python_scripts.character import Character, CharacterAppearance, CharacterClothing

def test_character_creation():
    """Test basic character creation and attributes."""
    char = Character("John Doe")
    assert char.name == "John Doe"
    assert isinstance(char.appearance, CharacterAppearance)
    assert isinstance(char.clothing, CharacterClothing)
    assert char.personality == []
    assert char.background == ""
    assert char.relationships == {}
    assert char.scene_specific_states == {}

def test_update_appearance():
    """Test updating character appearance attributes."""
    char = Character("Jane Doe")
    
    # Test valid attributes
    char.update_appearance(
        height="tall",
        hair_color="blonde",
        eye_color="blue"
    )
    assert char.appearance.height == "tall"
    assert char.appearance.hair_color == "blonde"
    assert char.appearance.eye_color == "blue"
    
    # Test invalid attribute
    with pytest.raises(ValueError):
        char.update_appearance(invalid_attr="value")

def test_update_clothing():
    """Test updating character clothing attributes."""
    char = Character("Bob Smith")
    
    # Test valid attributes
    char.update_clothing(
        top="blue shirt",
        bottom="black pants",
        accessories=["watch", "glasses"]
    )
    assert char.clothing.top == "blue shirt"
    assert char.clothing.bottom == "black pants"
    assert char.clothing.accessories == ["watch", "glasses"]
    
    # Test invalid attribute
    with pytest.raises(ValueError):
        char.update_clothing(invalid_attr="value")

def test_personality_traits():
    """Test adding personality traits."""
    char = Character("Alice Johnson")
    
    char.add_personality_trait("confident")
    char.add_personality_trait("intelligent")
    assert "confident" in char.personality
    assert "intelligent" in char.personality
    
    # Test duplicate trait
    char.add_personality_trait("confident")
    assert char.personality.count("confident") == 1

def test_relationships():
    """Test managing character relationships."""
    char = Character("Main Character")
    
    char.add_relationship("Sidekick", "best friend")
    char.add_relationship("Antagonist", "arch-nemesis")
    
    assert char.relationships["Sidekick"] == "best friend"
    assert char.relationships["Antagonist"] == "arch-nemesis"
    
    # Test updating relationship
    char.add_relationship("Sidekick", "former friend")
    assert char.relationships["Sidekick"] == "former friend"

def test_scene_states():
    """Test managing scene-specific states."""
    char = Character("Scene Character")
    
    # Set scene state
    char.set_scene_state("scene_1", 
                        mood="happy",
                        location="garden",
                        action="reading")
    
    # Get scene state
    state = char.get_scene_state("scene_1")
    assert state["mood"] == "happy"
    assert state["location"] == "garden"
    assert state["action"] == "reading"
    
    # Test non-existent scene
    assert char.get_scene_state("non_existent_scene") is None

def test_serialization():
    """Test character serialization to and from dict/JSON."""
    # Create character with data
    char = Character("Test Character")
    char.update_appearance(height="medium", hair_color="brown")
    char.update_clothing(top="t-shirt", bottom="jeans")
    char.add_personality_trait("friendly")
    char.set_background("Test background")
    char.add_relationship("Friend", "close friend")
    char.set_scene_state("scene_1", mood="happy")
    
    # Convert to dict
    char_dict = char.to_dict()
    
    # Create new character from dict
    new_char = Character.from_dict(char_dict)
    
    # Verify data
    assert new_char.name == char.name
    assert new_char.appearance.height == char.appearance.height
    assert new_char.appearance.hair_color == char.appearance.hair_color
    assert new_char.clothing.top == char.clothing.top
    assert new_char.clothing.bottom == char.clothing.bottom
    assert new_char.personality == char.personality
    assert new_char.background == char.background
    assert new_char.relationships == char.relationships
    assert new_char.scene_specific_states == char.scene_specific_states

def test_character_description():
    """Test character description generation."""
    char = Character("Description Test")
    
    # Set up character attributes
    char.update_appearance(
        height="tall",
        hair_color="black",
        hair_style="short",
        eye_color="brown",
        distinguishing_features=["scar on left cheek"]
    )
    
    char.update_clothing(
        top="red sweater",
        bottom="blue jeans",
        accessories=["silver necklace"]
    )
    
    # Get description without scene state
    desc = char.describe()
    assert "Description Test" in desc
    assert "tall" in desc
    assert "black" in desc
    assert "short" in desc
    assert "brown" in desc
    assert "scar on left cheek" in desc
    assert "red sweater" in desc
    assert "blue jeans" in desc
    assert "silver necklace" in desc
    
    # Add scene state and get description
    char.set_scene_state("test_scene", mood="angry", action="pacing")
    desc_with_scene = char.describe("test_scene")
    assert "mood: angry" in desc_with_scene.lower()
    assert "action: pacing" in desc_with_scene.lower()

def test_json_serialization():
    """Test character serialization to and from JSON."""
    # Create character with data
    char = Character("JSON Test")
    char.update_appearance(height="short", hair_color="red")
    char.update_clothing(top="hoodie", bottom="shorts")
    
    # Convert to JSON and back
    json_str = char.to_json()
    new_char = Character.from_json(json_str)
    
    # Verify data
    assert new_char.name == char.name
    assert new_char.appearance.height == char.appearance.height
    assert new_char.appearance.hair_color == char.appearance.hair_color
    assert new_char.clothing.top == char.clothing.top
    assert new_char.clothing.bottom == char.clothing.bottom
