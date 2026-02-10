# Quick Start Guide - Emoji Translator Agent

## Simple Usage

### Run Batch Translations
```bash
python ../src/emoji_translator.py "Your text here"
```

### Run Interactive Mode
```bash
python ../src/emoji_translator.py
```

---

## Example Commands to Try

### Simple Translations
```bash
python ../src/emoji_translator.py "Hello"
python ../src/emoji_translator.py "I love you"
python ../src/emoji_translator.py "Happy birthday"
```

### Food & Drink
```bash
python ../src/emoji_translator.py "Let's have pizza and beer"
python ../src/emoji_translator.py "Coffee time"
python ../src/emoji_translator.py "Eating cake at the party"
```

### Emotions
```bash
python ../src/emoji_translator.py "I am so happy"
python ../src/emoji_translator.py "Feeling sad and tired"
python ../src/emoji_translator.py "Angry and frustrated"
```

### Nature & Weather
```bash
python ../src/emoji_translator.py "The sun is shining brightly"
python ../src/emoji_translator.py "Rain and thunder storm"
python ../src/emoji_translator.py "Snow falling on the mountain"
```

### Animals
```bash
python ../src/emoji_translator.py "A cat and a dog playing"
python ../src/emoji_translator.py "Lion roaring in the forest"
python ../src/emoji_translator.py "Bird flying in the sky"
```

### Travel & Adventure
```bash
python ../src/emoji_translator.py "Road trip by car"
python ../src/emoji_translator.py "Flying on a plane across the ocean"
python ../src/emoji_translator.py "Rocket to the moon"
```

### Celebration
```bash
python ../src/emoji_translator.py "Let's party and celebrate"
python ../src/emoji_translator.py "Fireworks and dancing"
python ../src/emoji_translator.py "Trophy win and celebration"
```

---

## Expected Outputs

| Input | Expected Output |
|-------|-----------------|
| "Hello" | 👋 |
| "I love you" | ❤️ |
| "Happy birthday" | 🎂 |
| "Pizza and beer" | 🍕🍺 |
| "I am happy" | 😊 |
| "Sad and tired" | 😢😴 |
| "Sun shining" | ☀️ |
| "Rain storm" | 🌧️⛈️ |
| "Cat playing" | 🐱 |
| "Party and celebrate" | 🎉🎊 |

---

## Interactive Mode Example

```bash
$ python ../src/emoji_translator.py

📱 Emoji Translator Agent (Fallback Mode)
----------------------------------------
Note: No OpenAI API key found, using fallback pattern matching

Enter text to translate (or 'quit' to exit):

📝 > I love pizza and programming
😊 👋❤️🍕

📝 > The cat is sleeping
😊 🐱😴

📝 > Let's celebrate
😊 🎉

📝 > quit
👋 Goodbye!
```

---

## Tips

- **Use simple, clear words** for best results in fallback mode
- **Combine multiple concepts** in one statement
- **Try different phrasings** if you don't like the emoji output
- **Set OPENAI_API_KEY** for more creative translations with API mode

---

For complete documentation, see [README.md](README.md)
