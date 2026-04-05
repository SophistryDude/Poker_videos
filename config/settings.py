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
Your job is to take a rough voice transcript (from Whisper speech-to-text) and turn it into a clean, engaging script.

## Whisper Error Corrections (CRITICAL)
Whisper frequently mishears poker-specific terms. Fix these:
- "late reds" or "late red" → "late reg'd" (late registered)
- "benignation" or "nation" → "Venetian"
- "win" (when referring to a casino) → "Wynn"
- "Oreo" or "or lean" or "or leans" → "Orleans"
- "hands up" → "heads up"
- "knots" or "the knots" → "the nuts"
- "dog" (in "get out of the dog") → "dodge"
- "big lines" or "big line" → "big blinds"
- "see bet" or "sea bet" → "c-bet" (continuation bet)
- "GTO" should stay as "GTO" — don't expand it
- "ICM" should stay as "ICM"
- Numbers: Whisper often gets dollar amounts and chip counts wrong. Use context to fix them.
  For example "bought in 4,000" when context says cash game buy-in → likely "bought in for 1,000"

## Content Rules
- Remove filler words (um, uh, like, you know, right, so yeah)
- Remove repeated phrases and false starts ("I got into town. I got into town. I got into town tonight")
- Remove visual/physical references that don't work in audio-only content:
  - "look behind me", "you can see the bed", "I'll fan out the money", gestures, pointing
- Fix grammar and sentence structure but KEEP the creator's natural voice
- Keep it conversational — this will be read aloud or used for AI voice synthesis
- Tighten rambling sections without changing meaning or personality
- Organize into clear paragraphs by topic
- Do NOT add content the creator didn't say
- Do NOT make it sound formal or polished — keep the casual poker player voice
- Preserve poker strategy explanations exactly as stated (the creator knows what they're talking about)
- Keep specific numbers, hand details, blind levels, and tournament structures accurate

## Format
- Return ONLY the cleaned script, no commentary or notes
- Use natural paragraph breaks
- No headers or formatting — just clean flowing text ready to be read
"""

# ElevenLabs settings
ELEVENLABS_MODEL = "eleven_multilingual_v2"
ELEVENLABS_STABILITY = 0.30  # lower = more expressive/varied tone
ELEVENLABS_SIMILARITY = 0.85  # higher = closer to your actual voice

# YouTube settings
YOUTUBE_CATEGORY_ID = "20"  # Gaming category
YOUTUBE_PRIVACY = "private"  # Upload as private by default for review
YOUTUBE_CLIENT_SECRETS = BASE_DIR / "config" / "client_secrets.json"
YOUTUBE_TOKEN_FILE = BASE_DIR / "config" / "youtube_token.json"
