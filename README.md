# YouTube Kids AI Agent

A starter Python service for **English-language YouTube Kids publishing workflows**.

## Current scope
- Generate SEO-friendly titles, descriptions, and tags from a video topic.
- Create a simple 1280x720 thumbnail image from a title.
- Upload a video to YouTube using your own Google OAuth consent.
- Set YouTube's **Made for Kids** declaration on uploaded videos.
- Publish as **Public** when `AUTO_PUBLISH=true`; otherwise upload as Private.

**Video editing is intentionally not included.** This project does not create or edit the video itself.

## Important
YouTube's Made for Kids declaration must be accurate for the actual content. Do not mark every video as made for kids automatically unless it genuinely is directed to children. Review titles, descriptions, thumbnails, audience settings, and the final video before publishing. You are responsible for compliance with YouTube policies and applicable law.

## 1. Requirements
- Python 3.10+
- A YouTube channel
- A Google Cloud project with YouTube Data API v3 enabled
- OAuth 2.0 Desktop application credentials downloaded as `client_secret.json`

## 2. Install
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Put your downloaded Google OAuth file at `client_secret.json`. Never commit it.

## 3. Configure
Edit `.env`:
- `AUTO_PUBLISH=false` initially. Change to `true` only after testing.
- `YOUTUBE_MADE_FOR_KIDS=true` only for content genuinely directed to children.
- Optionally add `OPENAI_API_KEY` for AI-assisted metadata generation.

## 4. Run
```bash
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for the interactive API.

## 5. Generate metadata
POST `/generate-seo` with JSON:
```json
{"topic":"A gentle bedtime story about a little rabbit","keywords":["bedtime story","kids story"]}
```

## 6. Create a thumbnail
POST `/thumbnail` with JSON:
```json
{"title":"The Little Rabbit's Bedtime Adventure"}
```
The response returns the saved thumbnail path.

## 7. Upload
POST `/upload` as multipart form data:
- `video`: MP4 video file
- `title`: video title
- `description`: description
- `tags`: comma-separated tags

The first upload opens Google's OAuth browser consent flow. Approve access for the YouTube channel you intend to use. The app stores a local token in `token.json`; keep it private.

## Security
Never upload `.env`, `client_secret.json`, `token.json`, API keys, or other credentials to GitHub. Use local environment variables or a secret manager for deployment. This starter app has no public authentication layer; run it locally and do not expose it to the internet without adding authentication, upload limits, and HTTPS.

## Current status
This is a starter scaffold, not a hosted always-on agent. Automatic publishing works only after you configure Google OAuth and run the service in a suitable environment.
