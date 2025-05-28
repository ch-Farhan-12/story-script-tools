#!/usr/bin/env python3
"""
story_parser.py

This module provides functionality to parse a story script into scenes.
Each scene is represented as a dictionary containing scene number and description.
"""

import re
from typing import List, Dict, Any

def parse_story_script(story_script: str) -> List[Dict[str, Any]]:
    """
    Parse a story script and split it into scenes.

    Args:
        story_script (str): The input story script text.
            Expected format includes scene markers like 'Scene 1:', 'Scene 2:', etc.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains:
            - scene_number (int): The number of the scene
            - description (str): The description/content of the scene

    Raises:
        ValueError: If the input is empty, not a string, or contains no valid scenes.

    Example:
        >>> script = '''
        ... Scene 1: The beginning
        ... Character walks into room
        ... Scene 2: The conflict
        ... Argument breaks out
        ... '''
        >>> parse_story_script(script)
        [
            {'scene_number': 1, 'description': 'The beginning\nCharacter walks into room'},
            {'scene_number': 2, 'description': 'The conflict\nArgument breaks out'}
        ]
    """
    # Input validation
    if not isinstance(story_script, str):
        raise ValueError("Input must be a string")
    
    if not story_script.strip():
        raise ValueError("Input cannot be empty")

    # Regular expression to match scene markers and their content
    # Matches "Scene" followed by numbers, colon, and captures all text until the next scene or end
    scene_pattern = r"Scene\s+(\d+):(.+?)(?=Scene\s+\d+:|$)"
    
    # Find all scenes in the script
    scenes = re.finditer(scene_pattern, story_script, re.DOTALL)
    
    # Convert matches to list of dictionaries
    scene_list = []
    for match in scenes:
        scene_number = int(match.group(1))
        # Clean up the description: remove extra whitespace and strip
        description = match.group(2).strip()
        
        scene_list.append({
            "scene_number": scene_number,
            "description": description
        })
    
    # Check if any scenes were found
    if not scene_list:
        raise ValueError("No valid scenes found in the script. Scenes should be marked with 'Scene X:'")
    
    return scene_list


def main():
    """
    Main function to demonstrate the script's functionality with a sample story.
    """
    # Example usage with a sample script
    sample_script = """
    Scene 1: The Beginning
    A quiet morning in the city. The sun rises over the skyline.
    
    Scene 2: The Discovery
    John finds a mysterious package on his doorstep.
    
    Scene 3: The Decision
    After much deliberation, John decides to open the package.
    """
    
    try:
        scenes = parse_story_script(sample_script)
        print("Parsed Scenes:")
        print("-" * 40)
        for scene in scenes:
            print(f"Scene {scene['scene_number']}:")
            print(scene['description'])
            print("-" * 40)
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
