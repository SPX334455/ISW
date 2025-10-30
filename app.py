# FILE: app.py
# free backend - FastAPI version (no APNs)
from fastapi import FastAPI
import httpx, datetime

app = FastAPI()

USERNAME = "hedef_username", "target_usarname"  # <-- buraya takip etmek istediğin hesap adını yaz
LAST_ID = None  # memory cache

@app.get("/")
def home():
    return {"status": "ok", "message": "Story watcher active."}

@app.get("/stories")
def get_stories():
    """
    Fetch public stories metadata.
    Simple scraping with external API wrapper (no login).
    """
    global LAST_ID
    url = f"https://www.instagram.com/{USERNAME}/?__a=1&__d=dis"
    r = httpx.get(url, headers={"User-Agent":"Mozilla/5.0"})
    data = r.json()
    user = data.get("graphql", {}).get("user", {})
    story_timestamp = user.get("highlight_reel_count")  # dummy field for demo
    now = datetime.datetime.utcnow().isoformat()
    if story_timestamp != LAST_ID:
        LAST_ID = story_timestamp
        return {"new_story": True, "time": now, "username": USERNAME}
    return {"new_story": False, "time": now}
