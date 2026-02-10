#!/usr/bin/env python3
"""
Emoji Translator Agent - Converts text statements into emoji sequences
"""

import json
import os
import sys
from typing import Optional

# Try to import requests for API calls, but make it optional
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Emoji mapping dictionary for fallback mode
EMOJI_MAPPINGS = {
    "hello": "👋",
    "hi": "👋",
    "goodbye": "👋",
    "bye": "👋",
    "love": "❤️",
    "happy": "😊",
    "sad": "😢",
    "angry": "😠",
    "tired": "😴",
    "sleep": "😴",
    "awake": "👀",
    "laugh": "😂",
    "cry": "😭",
    "dance": "💃",
    "party": "🎉",
    "celebration": "🎊",
    "sun": "☀️",
    "sunny": "☀️",
    "moon": "🌙",
    "night": "🌙",
    "star": "⭐",
    "rain": "🌧️",
    "snow": "❄️",
    "cold": "❄️",
    "fire": "🔥",
    "hot": "🔥",
    "water": "💧",
    "ocean": "🌊",
    "beach": "🏖️",
    "mountain": "⛰️",
    "tree": "🌳",
    "forest": "🌲",
    "flower": "🌸",
    "rose": "🌹",
    "apple": "🍎",
    "banana": "🍌",
    "pizza": "🍕",
    "cake": "🎂",
    "coffee": "☕",
    "beer": "🍺",
    "wine": "🍷",
    "car": "🚗",
    "bike": "🚴",
    "train": "🚂",
    "plane": "✈️",
    "rocket": "🚀",
    "ship": "🚢",
    "boat": "⛵",
    "house": "🏠",
    "building": "🏢",
    "computer": "💻",
    "phone": "📱",
    "camera": "📷",
    "music": "🎵",
    "guitar": "🎸",
    "drum": "🥁",
    "book": "📚",
    "pencil": "✏️",
    "pen": "🖊️",
    "art": "🎨",
    "trophy": "🏆",
    "medal": "🥇",
    "goal": "🎯",
    "heart": "❤️",
    "star": "⭐",
    "sparkle": "✨",
    "magic": "✨",
    "skull": "💀",
    "danger": "⚠️",
    "warning": "⚠️",
    "check": "✅",
    "cross": "❌",
    "eyes": "👀",
    "look": "👀",
    "hand": "👋",
    "thumbs": "👍",
    "fist": "✊",
    "person": "👤",
    "man": "👨",
    "woman": "👩",
    "baby": "👶",
    "king": "👑",
    "queen": "👑",
    "prince": "👑",
    "doctor": "👨‍⚕️",
    "teacher": "👨‍🏫",
    "dog": "🐕",
    "cat": "🐱",
    "bird": "🐦",
    "fish": "🐠",
    "cow": "🐄",
    "pig": "🐷",
    "lion": "🦁",
    "tiger": "🐯",
    "money": "💰",
    "coin": "🪙",
    "gift": "🎁",
    "diamond": "💎",
    "crown": "👑",
    "key": "🔑",
    "lock": "🔒",
    "unlock": "🔓",
    "bomb": "💣",
    "rainbow": "🌈",
    "cloud": "☁️",
    "lightning": "⚡",
    "thunder": "⛈️",
    "wind": "💨",
}


class EmojiTranslator:
    """Agent for translating text to emoji sequences"""

    def __init__(self, use_api: bool = True, api_key: Optional[str] = None):
        """
        Initialize the emoji translator.
        
        Args:
            use_api: Whether to attempt to use API (requires OPENAI_API_KEY)
            api_key: Optional API key (uses OPENAI_API_KEY env var if not provided)
        """
        self.use_api = use_api
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_available = self.use_api and self.api_key and REQUESTS_AVAILABLE
        
    def translate_with_api(self, text: str) -> str:
        """
        Translate text to emoji using OpenAI API.
        
        Args:
            text: The input text to translate
            
        Returns:
            Emoji string
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an emoji translator. Your job is to convert any text input into a creative sequence of emojis that represents the meaning and essence of the text. 
                        
Rules:
- Only output emojis, no text or punctuation
- Use multiple emojis to convey the meaning
- Be creative and use emojis that best represent the concepts
- The output should be a sequence of 3-8 relevant emojis
- Make sure the emoji combination effectively communicates the input text""",
                    },
                    {
                        "role": "user",
                        "content": f"Translate this to emojis: {text}"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 100,
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                emoji_output = result["choices"][0]["message"]["content"].strip()
                return emoji_output
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return self.translate_with_fallback(text)
                
        except Exception as e:
            print(f"API call failed: {e}")
            return self.translate_with_fallback(text)

    def translate_with_fallback(self, text: str) -> str:
        """
        Fallback method using pattern matching and emoji mappings.
        
        Args:
            text: The input text to translate
            
        Returns:
            Emoji string
        """
        text_lower = text.lower()
        emojis = []
        
        # Split text into words and find matching emojis
        words = text_lower.split()
        for word in words:
            # Remove common punctuation
            clean_word = word.strip(".,!?;:-'\"")
            
            # Direct match
            if clean_word in EMOJI_MAPPINGS:
                emojis.append(EMOJI_MAPPINGS[clean_word])
            # Partial match
            else:
                for key, emoji in EMOJI_MAPPINGS.items():
                    if key in clean_word or clean_word in key:
                        emojis.append(emoji)
                        break
        
        # If no emojis found, return a generic response
        if not emojis:
            return "🤔❓"
        
        return "".join(emojis[:8])  # Limit to 8 emojis

    def translate(self, text: str) -> str:
        """
        Translate text to emoji using the best available method.
        
        Args:
            text: The input text to translate
            
        Returns:
            Emoji string
        """
        if self.api_available:
            return self.translate_with_api(text)
        else:
            return self.translate_with_fallback(text)


def main():
    """Main entry point for the emoji translator"""
    
    # Check if API key is available and notify user
    api_key = os.getenv("OPENAI_API_KEY")
    
    translator = EmojiTranslator(use_api=True)
    
    if translator.api_available:
        print("🚀 Emoji Translator Agent (API Mode)")
        print("-" * 40)
        print("Mode: Using OpenAI API")
    else:
        print("📱 Emoji Translator Agent (Fallback Mode)")
        print("-" * 40)
        if not REQUESTS_AVAILABLE:
            print("Note: requests library not available, using pattern matching mode")
        else:
            print("Note: No OpenAI API key found, using fallback pattern matching")
    
    print()
    
    # Interactive mode or batch mode
    if len(sys.argv) > 1:
        # Batch mode - translate the provided argument
        text = " ".join(sys.argv[1:])
        result = translator.translate(text)
        print(f"Input:  {text}")
        print(f"Output: {result}")
    else:
        # Interactive mode
        print("Enter text to translate (or 'quit' to exit):")
        print()
        
        while True:
            try:
                user_input = input("📝 > ").strip()
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                result = translator.translate(user_input)
                print(f"😊 {result}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
