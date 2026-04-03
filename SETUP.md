# Poker Video Pipeline — Setup Guide

## 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Whisper also needs `ffmpeg` installed:
- **Windows**: `winget install ffmpeg` or download from https://ffmpeg.org/download.html
- Add ffmpeg to your PATH

## 2. Get Your API Keys

### Anthropic (Claude) — Script Cleanup
1. Go to https://console.anthropic.com/settings/keys
2. Create a new API key
3. Copy it

### ElevenLabs — Voice Cloning
1. Sign up at https://elevenlabs.io (Starter plan ~$5/mo for voice cloning)
2. Go to https://elevenlabs.io/settings/api-keys
3. Copy your API key
4. **Create your voice clone:**
   - Go to https://elevenlabs.io/voice-lab
   - Click "Add Generative or Cloned Voice" → "Instant Voice Cloning"
   - Upload 1-5 minutes of clean audio of your voice (more = better quality)
   - Name it and create
   - Copy the Voice ID from the voice settings

### YouTube — Video Upload
1. Go to https://console.cloud.google.com
2. Create a new project (or use existing)
3. Enable the **YouTube Data API v3**
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Application type: **Desktop app**
6. Download the JSON file
7. Save it as `config/client_secrets.json`
8. First upload will open a browser for Google sign-in

## 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your actual keys:
```
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=xi-...
ELEVENLABS_VOICE_ID=abc123...
```

## 4. Usage

### Run the full pipeline on a single file:
```bash
python pipeline.py input_audio/my_recording.mp3 --skip-upload
```

### Run each step individually:
```bash
# Transcribe only
python -m steps.transcribe input_audio/my_recording.mp3

# Clean up a transcript
python -m steps.cleanup transcripts/my_recording_transcript.txt

# Generate voice audio
python -m steps.voice_synth cleaned_scripts/my_recording_script.txt

# Upload a video
python -m steps.youtube_upload video_output/my_video.mp4 "My Video Title"
```

### Auto-watch mode (process files as you drop them in):
```bash
python watch.py
```
Then just drag audio files into the `input_audio/` folder.

## 5. Video Creation (Manual Step for Now)

After steps 1-3, you'll have:
- A cleaned script in `cleaned_scripts/`
- AI voice audio in `voice_output/`

Use one of these tools to create the video:
- **HeyGen** (heygen.com) — AI avatar + your voice clone
- **Pictory** (pictory.ai) — Paste script, auto-generates video
- **InVideo AI** (invideo.io) — Script-to-video with AI
- **CapCut** (capcut.com) — Free, manual editing with AI features

Save the final video to `video_output/` then upload:
```bash
python -m steps.youtube_upload video_output/my_video.mp4 "Video Title"
```

## Pipeline Flow

```
input_audio/my_talk.mp3
    → [Whisper] → transcripts/my_talk_transcript.txt
    → [Claude]  → cleaned_scripts/my_talk_script.txt
    → [ElevenLabs] → voice_output/my_talk_voice.mp3
    → [You: create video with HeyGen/Pictory/etc]
    → video_output/my_talk_final.mp4
    → [YouTube API] → uploaded (private by default)
```
