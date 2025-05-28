#!/usr/bin/env python3
"""
text_to_speech.py

This module provides functionality to convert text to speech using the TTSMaker API
and save the result as an MP3 file.
"""

import os
import requests
import json
from typing import Optional, Dict, Any
from pathlib import Path
import time

class TTSGenerator:
    """
    A class to handle text-to-speech conversion using the TTSMaker API.
    
    Attributes:
        api_key (str): TTSMaker API key
        base_url (str): Base URL for the TTSMaker API
        output_dir (Path): Directory to save generated audio files
    """
    
    def __init__(self, api_key: str, output_dir: str = "generated_audio"):
        """
        Initialize the TTS Generator.
        
        Args:
            api_key: TTSMaker API key
            output_dir: Directory to save generated audio files (default: "generated_audio")
        """
        self.api_key = api_key
        self.base_url = "https://api.ttsmaker.com/v1"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_speech(self, 
                       text: str, 
                       voice_id: str = "en-US-1", 
                       filename: Optional[str] = None,
                       speed: float = 1.0,
                       volume: float = 1.0) -> str:
        """
        Generate speech from text and save as MP3.
        
        Args:
            text: The text to convert to speech
            voice_id: The ID of the voice to use (default: "en-US-1")
            filename: Optional filename for the output MP3 (default: auto-generated)
            speed: Speech speed multiplier (0.5 to 2.0)
            volume: Volume level (0.1 to 5.0)
            
        Returns:
            Path to the generated MP3 file
            
        Raises:
            ValueError: If the input parameters are invalid
            RuntimeError: If the API request fails
        """
        # Validate input
        if not text.strip():
            raise ValueError("Text input cannot be empty")
        
        if not (0.5 <= speed <= 2.0):
            raise ValueError("Speed must be between 0.5 and 2.0")
        
        if not (0.1 <= volume <= 5.0):
            raise ValueError("Volume must be between 0.1 and 5.0")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"tts_{timestamp}.mp3"
        elif not filename.endswith('.mp3'):
            filename = f"{filename}.mp3"
        
        output_path = self.output_dir / filename
        
        # Prepare API request
        url = f"{self.base_url}/create"
        
        payload = {
            "api_key": self.api_key,
            "text": text,
            "voice_id": voice_id,
            "speed": speed,
            "volume": volume,
            "format": "mp3"
        }
        
        try:
            # Make API request
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            if result.get("status") != "success":
                raise RuntimeError(f"API Error: {result.get('message', 'Unknown error')}")
            
            # Download the audio file
            audio_url = result["audio_url"]
            audio_response = requests.get(audio_url)
            audio_response.raise_for_status()
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(audio_response.content)
            
            return str(output_path)
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API Request failed: {str(e)}")
    
    def list_available_voices(self) -> Dict[str, Any]:
        """
        Get a list of available voices from the API.
        
        Returns:
            Dictionary containing available voices and their details
            
        Raises:
            RuntimeError: If the API request fails
        """
        url = f"{self.base_url}/voices"
        
        try:
            response = requests.get(url, params={"api_key": self.api_key})
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch voices: {str(e)}")

def main():
    """Example usage of the TTSGenerator class."""
    # Get API key from environment variable
    api_key = os.getenv("TTSMAKER_API_KEY")
    
    if not api_key:
        print("Error: TTSMAKER_API_KEY environment variable not set")
        print("\nTo use this script:")
        print("1. Sign up for a TTSMaker API key at https://ttsmaker.com")
        print("2. Set the environment variable:")
        print("   export TTSMAKER_API_KEY='your-api-key-here'")
        return
    
    try:
        # Create TTS generator
        tts = TTSGenerator(api_key)
        
        # Example text
        text = """
        Welcome to the text-to-speech generator. 
        This is a sample conversion to demonstrate the functionality.
        """
        
        print("Generating speech from text...")
        output_file = tts.generate_speech(
            text=text,
            voice_id="en-US-1",
            speed=1.0,
            volume=1.0
        )
        
        print(f"\nSuccess! Audio saved to: {output_file}")
        
        # List available voices
        print("\nFetching available voices...")
        voices = tts.list_available_voices()
        print("\nAvailable voices:")
        for voice in voices.get("voices", []):
            print(f"- {voice['voice_id']}: {voice.get('name')} ({voice.get('language')})")
        
    except (ValueError, RuntimeError) as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
