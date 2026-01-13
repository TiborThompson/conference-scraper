"""Quick test to verify API keys are loaded correctly."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

print("\n Checking API Keys from .env file...\n")

keys = {
 "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
 "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
 "GENAI_API_KEY": os.getenv("GENAI_API_KEY"),
 "GENAI_API_KEY_ALT": os.getenv("GENAI_API_KEY_ALT"),
 "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
}

for key_name, key_value in keys.items():
 if key_value:
 masked = key_value[:10] + "..." + key_value[-4:] if len(key_value) > 14 else key_value[:6] + "..."
 print(f" {key_name}: {masked}")
 else:
 print(f" {key_name}: Not found")

print("\n" + "=" * 60)
print("API Keys Status:")
print("=" * 60)

if keys["OPENAI_API_KEY"]:
 print(" OpenAI: Ready to use")
else:
 print(" OpenAI: Not configured")

if keys["ANTHROPIC_API_KEY"]:
 print(" Anthropic: Ready to use")
else:
 print(" Anthropic: Not configured")

if keys["GENAI_API_KEY"]:
 print(" Google Gemini: Ready to use")
else:
 print(" Google Gemini: Not configured")

print("\n You can now run:")
print(" python demo.py https://example.com")
print("")
