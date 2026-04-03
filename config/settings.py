"""Pipeline configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_AUDIO_DIR = BASE_DIR / "input_audio"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
CLEANED_SCRIPTS_DIR = BASE_DIR / "cleaned_scripts"
VOICE_OUTPUT_DIR = BASE_DIR / "voice_output"
VIDEO_OUTPUT_DIR = BASE_DIR / "video_output"

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# Whisper settings
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large

# Claude settings for script cleanup
CLEANUP_SYSTEM_PROMPT = """You are a script editor for a poker content creator's YouTube channel.
Your job is to take a rough voice transcript and turn it into a clean, engaging script.

Rules:
- Remove filler words (um, uh, like, you know)
- Fix grammar and sentence structure
- Keep the creator's natural voice and personality
- Organize into clear sections/paragraphs
- Keep it conversational — this will be read aloud
- Add [PAUSE] markers where natural pauses should go
- Do NOT add any content the creator didn't say
- Return ONLY the cleaned script, no commentary
"""

# ElevenLabs settings
ELEVENLABS_MODEL = "eleven_multilingual_v2"
ELEVENLABS_STABILITY = 0.5
ELEVENLABS_SIMILARITY = 0.75

# YouTube settings
YOUTUBE_CATEGORY_ID = "20"  # Gaming category
YOUTUBE_PRIVACY = "private"  # Upload as private by default for review
YOUTUBE_CLIENT_SECRETS = BASE_DIR / "config" / "client_secrets.json"
YOUTUBE_TOKEN_FILE = BASE_DIR / "config" / "youtube_token.json"
