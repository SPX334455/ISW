# FILE: app.py
from fastapi import FastAPI
import httpx, datetime, os

app = FastAPI()

USERNAME = os.getenv("target_username")
LAST_ID = None

@app.get("/")
def home():
    return {"status": "ok", "message": f"Story watcher active for {USERNAME}"}

@app.get("/stories")
def get_stories():
    global LAST_ID
    url = f"https://www.instagram.com/{USERNAME}/?__a=1&__d=dis"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = httpx.get(url, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        return {"error": f"Request failed: {e}"}

    # 🔍 Güvenli JSON parse — hata durumunda log döndür
    try:
        data = r.json()
    except Exception:
        # Burada Instagram HTML döndürüyorsa, ilk 200 karakteri gör
        text_preview = r.text[:200]
        return {
            "error": "Invalid JSON from Instagram",
            "preview": text_preview
        }

    user = data.get("graphql", {}).get("user", {})
    story_timestamp = user.get("highlight_reel_count")
    now = datetime.datetime.utcnow().isoformat()

    if story_timestamp != LAST_ID:
        LAST_ID = story_timestamp
        return {"new_story": True, "time": now, "username": USERNAME}

    return {"new_story": False, "time": now, "username": USERNAME}
