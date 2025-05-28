#!/usr/bin/env python3
"""
character.py

This module provides a Character class to manage character attributes consistently
across multiple scenes in a story.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import json

@dataclass
class CharacterAppearance:
    """Class to store character's physical appearance attributes."""
    height: str = ""
    build: str = ""
    hair_color: str = ""
    hair_style: str = ""
    eye_color: str = ""
    skin_tone: str = ""
    distinguishing_features: List[str] = field(default_factory=list)
    age: str = ""

@dataclass
class CharacterClothing:
    """Class to store character's clothing attributes."""
    top: str = ""
    bottom: str = ""
    footwear: str = ""
    accessories: List[str] = field(default_factory=list)
    style: str = ""
    color_scheme: List[str] = field(default_factory=list)

class Character:
    """
    A class to manage character attributes and ensure consistency across scenes.
    
    Attributes:
        name (str): The character's name
        appearance (CharacterAppearance): The character's physical appearance
        clothing (CharacterClothing): The character's clothing
        personality (List[str]): List of personality traits
        background (str): Character's background story
        relationships (Dict[str, str]): Character's relationships with others
        scene_specific_states (Dict[str, Any]): States that may change between scenes
    """
    
    def __init__(self, name: str):
        """
        Initialize a new character.
        
        Args:
            name: The character's name
        """
        self.name = name
        self.appearance = CharacterAppearance()
        self.clothing = CharacterClothing()
        self.personality: List[str] = []
        self.background: str = ""
        self.relationships: Dict[str, str] = {}
        self.scene_specific_states: Dict[str, Any] = {}
    
    def update_appearance(self, **kwargs) -> None:
        """
        Update character's appearance attributes.
        
        Args:
            **kwargs: Appearance attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self.appearance, key):
                setattr(self.appearance, key, value)
            else:
                raise ValueError(f"Invalid appearance attribute: {key}")
    
    def update_clothing(self, **kwargs) -> None:
        """
        Update character's clothing attributes.
        
        Args:
            **kwargs: Clothing attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self.clothing, key):
                setattr(self.clothing, key, value)
            else:
                raise ValueError(f"Invalid clothing attribute: {key}")
    
    def add_personality_trait(self, trait: str) -> None:
        """
        Add a personality trait to the character.
        
        Args:
            trait: The personality trait to add
        """
        if trait not in self.personality:
            self.personality.append(trait)
    
    def set_background(self, background: str) -> None:
        """
        Set the character's background story.
        
        Args:
            background: The character's background story
        """
        self.background = background
    
    def add_relationship(self, character_name: str, relationship: str) -> None:
        """
        Add or update a relationship with another character.
        
        Args:
            character_name: Name of the related character
            relationship: Description of the relationship
        """
        self.relationships[character_name] = relationship
    
    def set_scene_state(self, scene_id: str, **state) -> None:
        """
        Set character's state for a specific scene.
        
        Args:
            scene_id: Identifier for the scene
            **state: State attributes for the scene
        """
        self.scene_specific_states[scene_id] = state
    
    def get_scene_state(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """
        Get character's state for a specific scene.
        
        Args:
            scene_id: Identifier for the scene
            
        Returns:
            Dictionary containing the character's state for the scene,
            or None if no state exists for the scene
        """
        return self.scene_specific_states.get(scene_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert character data to a dictionary.
        
        Returns:
            Dictionary containing all character attributes
        """
        return {
            "name": self.name,
            "appearance": asdict(self.appearance),
            "clothing": asdict(self.clothing),
            "personality": self.personality,
            "background": self.background,
            "relationships": self.relationships,
            "scene_specific_states": self.scene_specific_states
        }
    
    def to_json(self) -> str:
        """
        Convert character data to JSON string.
        
        Returns:
            JSON string containing all character attributes
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """
        Create a Character instance from a dictionary.
        
        Args:
            data: Dictionary containing character attributes
            
        Returns:
            New Character instance
        """
        character = cls(data["name"])
        
        # Set appearance
        appearance_data = data.get("appearance", {})
        character.appearance = CharacterAppearance(**appearance_data)
        
        # Set clothing
        clothing_data = data.get("clothing", {})
        character.clothing = CharacterClothing(**clothing_data)
        
        # Set other attributes
        character.personality = data.get("personality", [])
        character.background = data.get("background", "")
        character.relationships = data.get("relationships", {})
        character.scene_specific_states = data.get("scene_specific_states", {})
        
        return character
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Character':
        """
        Create a Character instance from a JSON string.
        
        Args:
            json_str: JSON string containing character attributes
            
        Returns:
            New Character instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def describe(self, scene_id: Optional[str] = None) -> str:
        """
        Generate a description of the character, optionally including scene-specific state.
        
        Args:
            scene_id: Optional scene identifier to include scene-specific state
            
        Returns:
            String description of the character
        """
        description_parts = []
        
        # Basic description
        description_parts.append(f"{self.name} is a {self.appearance.height} person with "
                               f"{self.appearance.hair_color} {self.appearance.hair_style} hair "
                               f"and {self.appearance.eye_color} eyes.")
        
        # Distinguishing features
        if self.appearance.distinguishing_features:
            features = ", ".join(self.appearance.distinguishing_features)
            description_parts.append(f"They have {features}.")
        
        # Clothing
        clothing_desc = []
        if self.clothing.top:
            clothing_desc.append(f"wearing a {self.clothing.top}")
        if self.clothing.bottom:
            clothing_desc.append(f"{self.clothing.bottom}")
        if self.clothing.footwear:
            clothing_desc.append(f"{self.clothing.footwear}")
        if clothing_desc:
            description_parts.append("They are " + " and ".join(clothing_desc) + ".")
        
        # Accessories
        if self.clothing.accessories:
            accessories = ", ".join(self.clothing.accessories)
            description_parts.append(f"Their accessories include {accessories}.")
        
        # Scene-specific state
        if scene_id and scene_id in self.scene_specific_states:
            state = self.scene_specific_states[scene_id]
            state_desc = ", ".join(f"{k}: {v}" for k, v in state.items())
            description_parts.append(f"In this scene: {state_desc}")
        
        return " ".join(description_parts)

def main():
    """Example usage of the Character class."""
    # Create a new character
    john = Character("John Smith")
    
    # Set appearance
    john.update_appearance(
        height="tall",
        build="athletic",
        hair_color="brown",
        hair_style="short and neat",
        eye_color="blue",
        skin_tone="fair",
        distinguishing_features=["small scar above right eyebrow"]
    )
    
    # Set clothing
    john.update_clothing(
        top="navy blue blazer over white shirt",
        bottom="dark jeans",
        footwear="brown leather boots",
        accessories=["silver watch", "wedding ring"],
        style="smart casual"
    )
    
    # Add personality traits
    john.add_personality_trait("determined")
    john.add_personality_trait("analytical")
    
    # Set background
    john.set_background("Former detective turned private investigator")
    
    # Add relationships
    john.add_relationship("Sarah Smith", "wife")
    john.add_relationship("Detective Johnson", "former partner")
    
    # Set scene-specific state
    john.set_scene_state("crime_scene_1", 
                        mood="tense",
                        action="examining evidence",
                        holding="magnifying glass")
    
    # Print character description
    print("\nCharacter Description:")
    print("-" * 40)
    print(john.describe("crime_scene_1"))
    print("\nFull Character Data (JSON):")
    print("-" * 40)
    print(john.to_json())

if __name__ == "__main__":
    main()
