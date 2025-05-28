#!/usr/bin/env python3
"""
subtitle_translator.py

This module provides functionality to translate subtitles and generate
voiceovers in different languages using LibreTranslate API and TTSMaker.
"""

import os
import re
import requests
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
from python_scripts.text_to_speech import TTSGenerator

@dataclass
class SubtitleEntry:
    """Represents a single subtitle entry."""
    index: int
    start_time: str
    end_time: str
    text: str

class SubtitleTranslator:
    """
    A class to handle subtitle translation and voiceover generation.
    """
    
    # Language codes mapping (LibreTranslate to TTSMaker)
    LANGUAGE_MAPPING = {
        "en": {"code": "en-US", "voice_id": "en-US-1"},
        "es": {"code": "es-ES", "voice_id": "es-ES-1"},
        "fr": {"code": "fr-FR", "voice_id": "fr-FR-1"},
        "de": {"code": "de-DE", "voice_id": "de-DE-1"},
        "it": {"code": "it-IT", "voice_id": "it-IT-1"},
        "pt": {"code": "pt-BR", "voice_id": "pt-BR-1"},
        "nl": {"code": "nl-NL", "voice_id": "nl-NL-1"},
        "pl": {"code": "pl-PL", "voice_id": "pl-PL-1"},
        "ru": {"code": "ru-RU", "voice_id": "ru-RU-1"},
        "ja": {"code": "ja-JP", "voice_id": "ja-JP-1"},
        "ko": {"code": "ko-KR", "voice_id": "ko-KR-1"},
        "zh": {"code": "zh-CN", "voice_id": "zh-CN-1"}
    }
    
    def __init__(self, 
                 translate_url: str = "https://libretranslate.com/translate",
                 tts_api_key: Optional[str] = None,
                 output_dir: str = "translated_content"):
        """
        Initialize the SubtitleTranslator.
        
        Args:
            translate_url: URL for the LibreTranslate API
            tts_api_key: TTSMaker API key for voice generation
            output_dir: Directory to save translated files
        """
        self.translate_url = translate_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize TTS generator if API key is provided
        self.tts_generator = None
        if tts_api_key:
            self.tts_generator = TTSGenerator(tts_api_key, str(self.output_dir))
    
    def parse_srt(self, srt_content: str) -> List[SubtitleEntry]:
        """
        Parse SRT subtitle content into structured format.
        
        Args:
            srt_content: Content of the SRT file
            
        Returns:
            List of SubtitleEntry objects
            
        Raises:
            ValueError: If the SRT content is invalid
        """
        if not isinstance(srt_content, str) or not srt_content.strip():
            raise ValueError("Invalid SRT content: must be a non-empty string")
            
        entries = []
        blocks = re.split(r'\n\n+', srt_content.strip())
        
        # Check for valid SRT structure
        if not any(re.match(r'^\d+\s*$', block.split('\n')[0].strip()) for block in blocks):
            raise ValueError("Invalid SRT format: missing subtitle numbers")
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                index = int(lines[0])
                timing = lines[1]
                
                # Validate timing format
                if not re.match(r'^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}$', timing):
                    raise ValueError(f"Invalid timing format in block {index}")
                
                start_time, end_time = timing.split(' --> ')
                text = ' '.join(lines[2:])
                
                entries.append(SubtitleEntry(
                    index=index,
                    start_time=start_time.strip(),
                    end_time=end_time.strip(),
                    text=text.strip()
                ))
                
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid SRT format in block: {block}")
        
        return entries
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using LibreTranslate API.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
            
        Raises:
            RuntimeError: If translation fails
        """
        if not text.strip():
            return text
            
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
            "api_key": ""  # Add your API key here if required
        }
        
        try:
            response = requests.post(self.translate_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "translatedText" not in result:
                raise RuntimeError(f"Translation failed: {result.get('error', 'Unknown error')}")
            
            return result["translatedText"]
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Translation request failed: {str(e)}")
    
    def translate_subtitles(self, 
                          entries: List[SubtitleEntry],
                          source_lang: str,
                          target_lang: str) -> List[SubtitleEntry]:
        """
        Translate a list of subtitle entries.
        
        Args:
            entries: List of SubtitleEntry objects
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translated SubtitleEntry objects
        """
        translated_entries = []
        
        for entry in entries:
            translated_text = self.translate_text(
                entry.text,
                source_lang,
                target_lang
            )
            
            translated_entries.append(SubtitleEntry(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=translated_text
            ))
        
        return translated_entries
    
    def generate_voiceover(self,
                          entries: List[SubtitleEntry],
                          target_lang: str,
                          output_filename: Optional[str] = None) -> str:
        """
        Generate voiceover audio from translated subtitles.
        
        Args:
            entries: List of translated SubtitleEntry objects
            target_lang: Target language code
            output_filename: Optional filename for the output audio
            
        Returns:
            Path to the generated audio file
            
        Raises:
            RuntimeError: If TTS generation fails or is not configured
        """
        if not self.tts_generator:
            raise RuntimeError(
                "TTS Generator not initialized. "
                "Please provide a TTSMaker API key when creating SubtitleTranslator."
            )
        
        # Get voice ID for target language
        lang_info = self.LANGUAGE_MAPPING.get(target_lang)
        if not lang_info:
            raise ValueError(f"Unsupported target language: {target_lang}")
        
        # Combine all subtitle text with timing markers
        full_text = ""
        for entry in entries:
            # Add SSML pause markers based on timing
            full_text += f"{entry.text}\n<break time='500ms'/>\n"
        
        # Generate speech
        return self.tts_generator.generate_speech(
            text=full_text,
            voice_id=lang_info["voice_id"],
            filename=output_filename
        )
    
    def save_srt(self, entries: List[SubtitleEntry], output_filename: str) -> str:
        """
        Save subtitle entries as SRT file.
        
        Args:
            entries: List of SubtitleEntry objects
            output_filename: Name for the output SRT file
            
        Returns:
            Path to the saved SRT file
        """
        if not output_filename.endswith('.srt'):
            output_filename += '.srt'
        
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(f"{entry.index}\n")
                f.write(f"{entry.start_time} --> {entry.end_time}\n")
                f.write(f"{entry.text}\n\n")
        
        return str(output_path)
    
    def process_subtitles(self,
                         srt_path: str,
                         source_lang: str,
                         target_lang: str,
                         generate_audio: bool = True) -> Dict[str, str]:
        """
        Process subtitles: translate and optionally generate voiceover.
        
        Args:
            srt_path: Path to input SRT file
            source_lang: Source language code
            target_lang: Target language code
            generate_audio: Whether to generate voiceover audio
            
        Returns:
            Dictionary containing paths to generated files
        """
        # Read and parse input file
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        entries = self.parse_srt(srt_content)
        
        # Translate subtitles
        translated_entries = self.translate_subtitles(
            entries,
            source_lang,
            target_lang
        )
        
        # Generate output filenames
        base_name = Path(srt_path).stem
        srt_output = f"{base_name}_{target_lang}.srt"
        
        result = {
            "subtitles": self.save_srt(translated_entries, srt_output)
        }
        
        # Generate voiceover if requested
        if generate_audio:
            audio_output = f"{base_name}_{target_lang}.mp3"
            result["audio"] = self.generate_voiceover(
                translated_entries,
                target_lang,
                audio_output
            )
        
        return result

def main():
    """Example usage of the SubtitleTranslator class."""
    # Get API key from environment variable
    tts_api_key = os.getenv("TTSMAKER_API_KEY")
    
    if not tts_api_key:
        print("Warning: TTSMAKER_API_KEY not set. Audio generation will be disabled.")
    
    try:
        # Create translator
        translator = SubtitleTranslator(tts_api_key=tts_api_key)
        
        # Example subtitle content
        sample_srt = """1
00:00:01,000 --> 00:00:04,000
Hello, welcome to our video.

2
00:00:04,500 --> 00:00:08,000
Today we'll learn something interesting.
"""
        
        # Save sample content
        with open("sample.srt", "w") as f:
            f.write(sample_srt)
        
        # Process subtitles
        result = translator.process_subtitles(
            "sample.srt",
            source_lang="en",
            target_lang="es"
        )
        
        print("\nProcessing complete!")
        print(f"Translated subtitles: {result['subtitles']}")
        if 'audio' in result:
            print(f"Generated audio: {result['audio']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
