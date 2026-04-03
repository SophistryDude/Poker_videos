"""Step 4: Upload video to YouTube using the YouTube Data API v3."""

from pathlib import Path
import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config.settings import (
    YOUTUBE_CATEGORY_ID,
    YOUTUBE_PRIVACY,
    YOUTUBE_CLIENT_SECRETS,
    YOUTUBE_TOKEN_FILE,
)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_service():
    """Authenticate and return a YouTube API service object."""
    creds = None

    if YOUTUBE_TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            if not YOUTUBE_CLIENT_SECRETS.exists():
                raise FileNotFoundError(
                    f"Missing {YOUTUBE_CLIENT_SECRETS}\n"
                    "Download your OAuth 2.0 client credentials from:\n"
                    "https://console.cloud.google.com/apis/credentials\n"
                    "Save the JSON as config/client_secrets.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(YOUTUBE_CLIENT_SECRETS), SCOPES
            )
            creds = flow.run_local_server(port=0)

        YOUTUBE_TOKEN_FILE.write_text(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(
    video_path: str | Path,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
) -> str:
    """Upload a video to YouTube.

    Returns the YouTube video ID.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    print(f"[YouTube] Authenticating...")
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": YOUTUBE_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY,
        },
    }

    print(f"[YouTube] Uploading {video_path.name}...")
    media = MediaFileUpload(str(video_path), resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = request.execute()
    video_id = response["id"]
    print(f"[YouTube] Upload complete! Video ID: {video_id}")
    print(f"[YouTube] URL: https://youtube.com/watch?v={video_id}")
    print(f"[YouTube] Status: {YOUTUBE_PRIVACY} (change in YouTube Studio)")
    return video_id


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python -m steps.youtube_upload <video_file> <title>")
        sys.exit(1)
    video_id = upload_to_youtube(sys.argv[1], sys.argv[2])
    print(f"Uploaded: https://youtube.com/watch?v={video_id}")
