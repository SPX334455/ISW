# FILE: app.py
# Free backend - FastAPI version (Render + Env Vars)
from fastapi import FastAPI
import httpx, datetime, os

app = FastAPI()

# Environment variable'dan oku (Render > Environment Variables > Key: target_username, Value: "kullaniciadi")
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
    r = httpx.get(url, headers=headers)
    data = r.json()
    user = data.get("graphql", {}).get("user", {})
    story_timestamp = user.get("highlight_reel_count")  # dummy alan (örnek)
    now = datetime.datetime.utcnow().isoformat()

    if story_timestamp != LAST_ID:
        LAST_ID = story_timestamp
        return {"new_story": True, "time": now, "username": USERNAME}

    return {"new_story": False, "time": now, "username": USERNAME}
