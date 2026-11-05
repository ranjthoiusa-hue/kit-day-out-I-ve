import os
import uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

from app.seo import generate_seo
from app.youtube import upload_video

load_dotenv()
app = FastAPI(title="YouTube Kids AI Agent", version="0.1.0")
OUTPUT_DIR = Path("output")
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

class SeoRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    keywords: list[str] = []

class ThumbnailRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)

@app.get("/")
def root():
    return {
        "name": "YouTube Kids AI Agent",
        "status": "starter-ready",
        "features": ["English SEO metadata", "thumbnail generation", "YouTube upload"],
        "video_editing": False,
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/generate-seo")
def seo_endpoint(request: SeoRequest):
    return generate_seo(request.topic, request.keywords)

@app.post("/thumbnail")
def thumbnail_endpoint(request: ThumbnailRequest):
    image = Image.new("RGB", (1280, 720), (255, 231, 170))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 76)
    except OSError:
        font = ImageFont.load_default()

    words = request.title.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > 22 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    lines = lines[:4]

    y = 250 - (len(lines) * 45)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = max(40, (1280 - (bbox[2] - bbox[0])) // 2)
        draw.text((x + 4, y + 4), line, font=font, fill=(60, 50, 50))
        draw.text((x, y), line, font=font, fill=(25, 70, 130))
        y += 100

    filename = OUTPUT_DIR / f"thumbnail-{uuid.uuid4().hex[:8]}.jpg"
    image.save(filename, quality=92)
    return {"thumbnail_path": str(filename), "width": 1280, "height": 720}

@app.post("/upload")
async def upload_endpoint(
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
):
    if not video.filename or not video.filename.lower().endswith((".mp4", ".mov", ".m4v")):
        raise HTTPException(status_code=400, detail="Upload an MP4, MOV, or M4V video.")
    safe_name = f"{uuid.uuid4().hex}_{Path(video.filename).name}"
    video_path = UPLOAD_DIR / safe_name
    try:
        with video_path.open("wb") as output:
            while chunk := await video.read(1024 * 1024):
                output.write(chunk)
        result = upload_video(
            str(video_path),
            title.strip(),
            description.strip(),
            [tag.strip() for tag in tags.split(",") if tag.strip()],
            os.getenv("YOUTUBE_CATEGORY_ID", "22"),
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        await video.close()
