# FILE: app.py
# Real Instagram story watcher (login-free, via RapidAPI)
from fastapi import FastAPI, HTTPException
import httpx, os, datetime, uuid, aiofiles
from pathlib import Path

app = FastAPI()

USERNAME = os.getenv("TARGET_USERNAME")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
STORAGE_PATH = Path("data")
STORAGE_PATH.mkdir(exist_ok=True)

LAST_ID = None  # cache

def now():
    return datetime.datetime.utcnow().isoformat()

@app.get("/")
def home():
    return {"status": "ok", "watching": USERNAME}

@app.get("/stories")
async def stories():
    global LAST_ID
    if not USERNAME or not RAPIDAPI_KEY:
        raise HTTPException(status_code=400, detail="Missing env vars: TARGET_USERNAME or RAPIDAPI_KEY")

    url = f"https://instagram-story-downloader.p.rapidapi.com/index?url=https://www.instagram.com/{USERNAME}/"
    headers = {
        "x-rapidapi-host": "instagram-story-downloader.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY,
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=f"API error {r.status_code}")
    data = r.json()
    stories = data.get("result", [])
    if not stories:
        return {"new_story": False, "username": USERNAME, "time": now()}

    latest = stories[0]
    story_id = latest.get("id") or latest.get("url")
    if story_id != LAST_ID:
        LAST_ID = story_id
        media_url = latest.get("url")
        ext = "mp4" if "mp4" in media_url else "jpg"
        filename = f"{USERNAME}_{uuid.uuid4().hex}.{ext}"
        path = STORAGE_PATH / filename
        async with httpx.AsyncClient() as c:
            m = await c.get(media_url)
        if m.status_code == 200:
            async with aiofiles.open(path, "wb") as f:
                await f.write(m.content)
        return {
            "new_story": True,
            "username": USERNAME,
            "time": now(),
            "media_url": media_url,
            "file": f"/media/{filename}",
        }
    return {"new_story": False, "username": USERNAME, "time": now()}

@app.get("/media/{filename}")
async def serve_file(filename: str):
    path = STORAGE_PATH / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="file not found")
    from fastapi.responses import FileResponse
    return FileResponse(path)
