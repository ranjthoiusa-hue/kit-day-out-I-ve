import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = Path("token.json")
CLIENT_SECRET_FILE = Path("client_secret.json")

def youtube_client():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        if not CLIENT_SECRET_FILE.exists():
            raise FileNotFoundError(
                "client_secret.json is missing. Download OAuth Desktop credentials "
                "from Google Cloud Console and place the file in the project root."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)

def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "22",
) -> dict:
    if not Path(video_path).is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    auto_publish = os.getenv("AUTO_PUBLISH", "false").lower() == "true"
    privacy = "public" if auto_publish else "private"
    made_for_kids = os.getenv("YOUTUBE_MADE_FOR_KIDS", "false").lower() == "true"

    youtube = youtube_client()
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    return {
        "video_id": response.get("id"),
        "privacy_status_requested": privacy,
        "made_for_kids_declared": made_for_kids,
        "url": f"https://www.youtube.com/watch?v={response.get('id')}",
    }
