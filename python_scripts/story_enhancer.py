#!/usr/bin/env python3
"""
story_enhancer.py

This module analyzes story scripts and enhances them by adding emotional depth
and trending plot elements based on common viral storytelling patterns.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random
from python_scripts.story_parser import parse_story_script

@dataclass
class EmotionalElement:
    """Represents an emotional story element."""
    name: str
    description: str
    intensity: int  # 1-10 scale
    trigger_words: List[str]

@dataclass
class PlotTwist:
    """Represents a plot twist pattern."""
    name: str
    description: str
    impact: int  # 1-10 scale
    setup_elements: List[str]
    payoff_elements: List[str]

# Common emotional elements in viral stories
EMOTIONAL_ELEMENTS = [
    EmotionalElement(
        name="unexpected_kindness",
        description="A sudden act of kindness from an unexpected source",
        intensity=8,
        trigger_words=["alone", "struggle", "difficult", "help"]
    ),
    EmotionalElement(
        name="redemption",
        description="A character overcomes their past mistakes",
        intensity=9,
        trigger_words=["mistake", "regret", "change", "better"]
    ),
    EmotionalElement(
        name="sacrifice",
        description="Someone gives up something important for others",
        intensity=10,
        trigger_words=["important", "give up", "others", "save"]
    ),
    EmotionalElement(
        name="revelation",
        description="A surprising truth is revealed that changes everything",
        intensity=9,
        trigger_words=["truth", "discover", "realize", "secret"]
    )
]

# Trending plot twist patterns
PLOT_TWISTS = [
    PlotTwist(
        name="hidden_connection",
        description="Characters discover they're connected in unexpected ways",
        impact=8,
        setup_elements=["mysterious past", "coincidence", "shared history"],
        payoff_elements=["revelation", "emotional reunion", "changed relationship"]
    ),
    PlotTwist(
        name="moral_gray_area",
        description="The clear distinction between right and wrong becomes blurred",
        impact=9,
        setup_elements=["ethical dilemma", "difficult choice", "conflicting loyalties"],
        payoff_elements=["complex decision", "unexpected consequences", "character growth"]
    ),
    PlotTwist(
        name="time_revelation",
        description="Events are not in the sequence they appear to be",
        impact=8,
        setup_elements=["mysterious timeline", "inconsistent memories", "déjà vu"],
        payoff_elements=["timeline twist", "memory revelation", "true sequence revealed"]
    ),
    PlotTwist(
        name="identity_subversion",
        description="A character is not who they appear to be",
        impact=9,
        setup_elements=["subtle hints", "inconsistent behavior", "hidden agenda"],
        payoff_elements=["true identity revealed", "motivation exposed", "relationships redefined"]
    )
]

class StoryEnhancer:
    """
    A class for analyzing and enhancing story scripts with emotional elements
    and trending plot twists.
    """
    
    def __init__(self):
        """Initialize the StoryEnhancer with default patterns."""
        self.emotional_elements = EMOTIONAL_ELEMENTS
        self.plot_twists = PLOT_TWISTS
    
    def analyze_emotional_potential(self, scene: Dict[str, Any]) -> List[EmotionalElement]:
        """
        Analyze a scene for potential emotional enhancement opportunities.
        
        Args:
            scene: Dictionary containing scene information
            
        Returns:
            List of relevant emotional elements that could enhance the scene
        """
        relevant_elements = []
        description = scene["description"].lower()
        
        for element in self.emotional_elements:
            # Check if any trigger words are present in the scene
            if any(word in description for word in element.trigger_words):
                relevant_elements.append(element)
        
        return relevant_elements
    
    def identify_plot_twist_opportunities(self, scenes: List[Dict[str, Any]]) -> List[PlotTwist]:
        """
        Identify opportunities for plot twists based on scene sequence.
        
        Args:
            scenes: List of scene dictionaries
            
        Returns:
            List of potential plot twists that could enhance the story
        """
        potential_twists = []
        
        # Analyze scene sequence for twist opportunities
        for twist in self.plot_twists:
            setup_count = 0
            for scene in scenes:
                description = scene["description"].lower()
                # Check if scene contains setup elements
                if any(element in description for element in twist.setup_elements):
                    setup_count += 1
            
            # If multiple setup elements are present, this twist might work well
            if setup_count >= 2:
                potential_twists.append(twist)
        
        return potential_twists
    
    def enhance_scene(self,
                     scene: Dict[str, Any],
                     emotional_elements: Optional[List[EmotionalElement]] = None) -> Dict[str, Any]:
        """
        Enhance a scene with emotional elements.
        
        Args:
            scene: Dictionary containing scene information
            emotional_elements: Optional list of specific emotional elements to use
            
        Returns:
            Enhanced scene dictionary
        """
        if emotional_elements is None:
            emotional_elements = self.analyze_emotional_potential(scene)
        
        if not emotional_elements:
            return scene
        
        # Choose a random emotional element to incorporate
        element = random.choice(emotional_elements)
        
        # Create enhanced description
        enhanced_description = (
            f"{scene['description']}\n\n"
            f"[Emotional Enhancement - {element.name}]:\n"
            f"{element.description}"
        )
        
        return {
            "scene_number": scene["scene_number"],
            "description": enhanced_description
        }
    
    def add_plot_twist(self,
                      scenes: List[Dict[str, Any]],
                      twist: Optional[PlotTwist] = None) -> List[Dict[str, Any]]:
        """
        Add a plot twist to the story.
        
        Args:
            scenes: List of scene dictionaries
            twist: Optional specific plot twist to use
            
        Returns:
            Enhanced list of scenes with plot twist
        """
        if not scenes:
            return scenes
        
        if twist is None:
            potential_twists = self.identify_plot_twist_opportunities(scenes)
            if potential_twists:
                twist = random.choice(potential_twists)
            else:
                twist = random.choice(self.plot_twists)
        
        # Choose a scene in the latter half of the story for the twist
        twist_index = len(scenes) // 2 + random.randint(0, len(scenes) // 2 - 1)
        
        # Add the twist
        scenes[twist_index]["description"] = (
            f"{scenes[twist_index]['description']}\n\n"
            f"[Plot Twist - {twist.name}]:\n"
            f"{twist.description}\n"
            f"This revelation changes everything that came before..."
        )
        
        return scenes
    
    def enhance_story(self, story_script: str) -> str:
        """
        Enhance a complete story script with emotional elements and plot twists.
        
        Args:
            story_script: Input story script text
            
        Returns:
            Enhanced story script text
        """
        # Parse the script into scenes
        scenes = parse_story_script(story_script)
        
        # Enhance each scene with emotional elements
        enhanced_scenes = []
        for scene in scenes:
            emotional_elements = self.analyze_emotional_potential(scene)
            enhanced_scene = self.enhance_scene(scene, emotional_elements)
            enhanced_scenes.append(enhanced_scene)
        
        # Add plot twists
        enhanced_scenes = self.add_plot_twist(enhanced_scenes)
        
        # Convert back to script format
        enhanced_script = ""
        for scene in enhanced_scenes:
            enhanced_script += f"\nScene {scene['scene_number']}:\n{scene['description']}\n"
        
        return enhanced_script.strip()

def main():
    """Example usage of the StoryEnhancer class."""
    # Sample story script
    sample_script = """
    Scene 1: The Beginning
    Sarah sits alone in her apartment, scrolling through old photos.
    The city lights flicker outside her window.
    
    Scene 2: The Letter
    A mysterious letter arrives, addressed in familiar handwriting.
    Sarah's hands shake as she opens it.
    
    Scene 3: The Decision
    After reading the letter, Sarah packs a small bag.
    She looks at her apartment one last time before leaving.
    """
    
    try:
        # Create enhancer and enhance the story
        enhancer = StoryEnhancer()
        enhanced_script = enhancer.enhance_story(sample_script)
        
        print("Original Script:")
        print("-" * 60)
        print(sample_script)
        print("\nEnhanced Script:")
        print("-" * 60)
        print(enhanced_script)
        
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
