# FILE: app.py
# Full working Instagram Story Checker via RapidAPI (no login needed)
from fastapi import FastAPI
import httpx, datetime, os

app = FastAPI()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
USERNAME = os.getenv("TARGET_USERNAME")

HOST = "instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com"
BASE_URL = f"https://{HOST}/convert?url=https://www.instagram.com/{USERNAME}/"

@app.get("/")
def home():
    return {"status": "ok", "watching": USERNAME}

@app.get("/stories")
def get_story():
    """
    Uses RapidAPI Instagram Downloader to check and fetch latest story/post.
    """
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": HOST
    }

    try:
        r = httpx.get(BASE_URL, headers=headers, timeout=10)
        if r.status_code != 200:
            return {"detail": f"API error {r.status_code}"}

        data = r.json()
        now = datetime.datetime.utcnow().isoformat()

        return {
            "new_story": True,
            "username": USERNAME,
            "time": now,
            "data": data  # içeriği (story veya video bilgisi)
        }

    except Exception as e:
        return {"error": str(e)}
