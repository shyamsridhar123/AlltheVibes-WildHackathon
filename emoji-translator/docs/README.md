# 🎉 Emoji Translator Agent

A fun and creative agent that converts text statements into emoji sequences. Perfect for adding visual flair to your messages!

## Features ✨

- **Dual Mode Operation**: Works with OpenAI API for creative translations or uses intelligent fallback pattern matching
- **Easy to Use**: Simple command-line interface with both batch and interactive modes
- **Smart Emoji Selection**: Uses semantic understanding to map words to the most appropriate emojis
- **No Dependencies Required**: Fallback mode works with just Python (no API key needed)
- **Fast and Reliable**: Cached emoji mappings for instant results in fallback mode

## Installation 🚀

### Prerequisites

- Python 3.6+

### Setup

1. Navigate to the project directory:
```bash
cd emoji-translator
```

2. (Optional) For API mode, set your OpenAI API key:
```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-key-here"

# macOS/Linux
export OPENAI_API_KEY=sk-your-key-here
```

3. (Optional) Install requests library for API mode:
```bash
pip install requests
```

## Usage 🎮

### Batch Mode (Single Translation)

Translate a single statement directly:

```bash
python src/emoji_translator.py "I love pizza and programming"
```

Output:
```
Input:  I love pizza and programming
Output: ❤️🍕💻
```

### Interactive Mode

Run without arguments to enter interactive mode:

```bash
python src/emoji_translator.py
```

Then type statements and see them translated in real-time:
```
📝 > The sun is shining brightly
😊 ☀️✨

📝 > I am sad and tired
😊 😢😴

📝 > Let's party and celebrate
😊 💃🎉🎊

📝 > quit
👋 Goodbye!
```

## Examples 📚

### Simple Statements
- **Input**: "Hello"  
  **Output**: 👋

- **Input**: "I love you"  
  **Output**: ❤️

- **Input**: "Happy dance"  
  **Output**: 😊💃

- **Input**: "Moon and stars"  
  **Output**: 🌙⭐

### Complex Statements
- **Input**: "I went to the beach and saw the ocean"  
  **Output**: 🏖️🌊👀

- **Input**: "Let's have pizza and beer at the party"  
  **Output**: 🍕🍺🎉

- **Input**: "The cat is sleeping by the fire"  
  **Output**: 🐱😴🔥

- **Input**: "Thunder and lightning during the storm"  
  **Output**: ⛈️⚡🌧️

- **Input**: "I got a trophy for winning the race"  
  **Output**: 🏆🎯

## How It Works 🔧

### API Mode
When an OpenAI API key is available:
- Uses GPT-3.5-turbo to creatively interpret your statement
- Generates context-aware emoji sequences
- More flexible and understands complex meanings
- May take a second or two due to API latency

### Fallback Mode (Pattern Matching)
When no API key is available:
- Uses a built-in dictionary of 100+ emoji mappings
- Intelligently matches words to relevant emojis
- Fast and offline-capable
- Works out of the box without any dependencies

The agent automatically chooses the best available mode based on your configuration.

## Supported Emojis 📖

The fallback mode includes mappings for:
- **Emotions**: happy, sad, angry, tired, love, laugh, cry
- **Actions**: dance, sleep, awake, laugh, cry, kiss
- **Objects**: pizza, cake, coffee, car, phone, computer, guitar, book
- **Nature**: sun, moon, star, rain, snow, fire, water, ocean, tree, flower
- **Animals**: dog, cat, bird, fish, cow, pig, lion, tiger
- **Travel**: car, bike, train, plane, rocket, ship, boat
- **Places**: house, building, beach, mountain, forest
- **And many more!**

## Troubleshooting 🐛

### "API Error" or timeout messages
- Check your OpenAI API key is valid
- Verify internet connection
- The agent will automatically fall back to pattern matching

### Limited emoji output in fallback mode
- The pattern matching mode performs best with common words
- Try using simpler, more direct language
- More specific words tend to have better matches

### Getting "🤔❓" as output
- This happens when no matching emojis are found
- Try rephrasing with more common words
- The API mode (with key) handles obscure words better

## API Mode Advantages 🌟

If you set up OpenAI API:
- Better understanding of abstract concepts
- More creative combinations
- Handles complex and multi-part sentences better
- Works with uncommon or technical terminology

## Tips & Tricks 💡

1. **Be Specific**: Use clear, specific words for better results
2. **Use Simpler Language**: Common words have better emoji mappings
3. **Mix Modes**: Start with API mode for testing, switch to fallback for offline use
4. **Chain Emoji**: The agent naturally creates emoji chains that flow together
5. **Combine Statements**: Try translating multiple concepts in one statement

## Supported Platforms 🖥️

- Windows (Command Prompt, PowerShell)
- macOS (Terminal)
- Linux (Any shell)
- WSL (Windows Subsystem for Linux)

## License 📄

This project is open source and free to use!

---

**Have fun translating your messages into emoji! 🚀😊🎉**
