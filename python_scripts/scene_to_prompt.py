#!/usr/bin/env python3
"""
scene_to_prompt.py

This module provides functionality to convert scene descriptions into detailed
image prompts suitable for AI image generation models like Stable Diffusion.
"""

import sys
from typing import List, Optional

class PromptGenerator:
    """A class to generate image prompts from scene descriptions."""
    
    # Style modifiers to enhance the image quality
    STYLE_MODIFIERS = [
        "highly detailed",
        "ultra realistic",
        "8k resolution",
        "cinematic lighting",
        "professional photography",
    ]
    
    # Artistic style options
    ARTISTIC_STYLES = [
        "dramatic composition",
        "vibrant colors",
        "dynamic lighting",
        "photorealistic",
        "masterful technique",
    ]
    
    # Atmosphere and mood enhancers
    ATMOSPHERE_ENHANCERS = [
        "atmospheric",
        "immersive",
        "stunning",
        "epic",
        "beautiful",
    ]

    @staticmethod
    def validate_input(scene_description: str) -> None:
        """
        Validate the input scene description.
        
        Args:
            scene_description: The scene description to validate.
            
        Raises:
            ValueError: If the input is empty or not a string.
        """
        if not isinstance(scene_description, str):
            raise ValueError("Scene description must be a string")
        if not scene_description.strip():
            raise ValueError("Scene description cannot be empty")

    @classmethod
    def select_modifiers(cls, num_modifiers: int = 2) -> List[str]:
        """
        Select a subset of style modifiers to use in the prompt.
        
        Args:
            num_modifiers: Number of modifiers to select from each category.
            
        Returns:
            List of selected modifiers.
        """
        import random
        modifiers = []
        
        # Select from each category
        modifiers.extend(random.sample(cls.STYLE_MODIFIERS, num_modifiers))
        modifiers.extend(random.sample(cls.ARTISTIC_STYLES, num_modifiers))
        modifiers.extend(random.sample(cls.ATMOSPHERE_ENHANCERS, num_modifiers))
        
        return modifiers

    @classmethod
    def generate_image_prompt(cls, scene_description: str, 
                            num_modifiers: int = 2,
                            additional_context: Optional[str] = None) -> str:
        """
        Generate an AI image generation prompt from a scene description.
        
        Args:
            scene_description: The scene to generate a prompt for.
            num_modifiers: Number of modifiers to select from each category.
            additional_context: Optional additional context to add to the prompt.
            
        Returns:
            A detailed prompt string suitable for AI image generation.
            
        Raises:
            ValueError: If the input is invalid.
            
        Example:
            >>> generator = PromptGenerator()
            >>> scene = "a medieval marketplace at sunset"
            >>> print(generator.generate_image_prompt(scene))
            "A highly detailed, ultra realistic scene of a medieval marketplace 
            at sunset, with dramatic composition and vibrant colors, 
            atmospheric and stunning, 8k resolution, professional photography"
        """
        # Validate input
        cls.validate_input(scene_description)
        
        # Clean up the scene description - replace newlines with spaces and remove extra whitespace
        scene_description = ' '.join(scene_description.split())
        
        # Select modifiers
        modifiers = cls.select_modifiers(num_modifiers)
        
        # Build the prompt
        prompt_parts = [
            f"A {', '.join(modifiers[:2])} scene of",  # Initial style modifiers
            scene_description,  # The main scene description
            f"with {' and '.join(modifiers[2:4])}",  # Artistic style
            f"{', '.join(modifiers[4:])}",  # Atmosphere
        ]
        
        # Add additional context if provided
        if additional_context:
            prompt_parts.append(additional_context)
        
        # Combine all parts
        prompt = ", ".join(prompt_parts)
        
        return prompt

def main():
    """Main function to handle command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python scene_to_prompt.py \"<scene description>\"")
        print("\nExample:")
        print("python scene_to_prompt.py \"a bustling medieval marketplace at sunset\"")
        sys.exit(1)
    
    try:
        # Get the scene description from command line
        scene_description = sys.argv[1]
        
        # Generate the prompt
        prompt = PromptGenerator.generate_image_prompt(scene_description)
        
        # Print the result
        print("\nGenerated Image Prompt:")
        print("-" * 80)
        print(prompt)
        print("-" * 80)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
