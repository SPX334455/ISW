# FILE: app.py
# Instagram Story Watcher (using instagram-scraper21 API with user ID)
from fastapi import FastAPI
import httpx, os, datetime

app = FastAPI()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
TARGET_USER_ID = os.getenv("TARGET_USER_ID")  # numeric Instagram ID
HOST = "instagram-scraper21.p.rapidapi.com"
ENDPOINT = f"https://{HOST}/api/v1/user-stories?id={TARGET_USER_ID}"

LAST_IDS = set()  # memory cache to detect new stories


@app.get("/")
def home():
    return {
        "status": "ok",
        "watching_user_id": TARGET_USER_ID,
        "message": "Instagram Story Watcher running"
    }


@app.get("/stories")
def check_stories():
    """
    Check for new Instagram stories by user ID.
    Uses instagram-scraper21 RapidAPI endpoint.
    """
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": HOST
    }

    try:
        r = httpx.get(ENDPOINT, headers=headers, timeout=10)
        if r.status_code != 200:
            return {"error": f"API error {r.status_code}", "new_story": False}

        data = r.json()
        stories = data.get("data", {}).get("reel_feed", [])

        if not stories:
            return {"new_story": False, "message": "No active stories"}

        current_ids = {s.get("id") for s in stories if "id" in s}
        new_stories = current_ids - LAST_IDS

        if new_stories:
            LAST_IDS.update(new_stories)
            urls = [
                s.get("video_versions", [{}])[0].get("url")
                or s.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                for s in stories if s.get("id") in new_stories
            ]
            urls = [u for u in urls if u]
            return {
                "new_story": True,
                "time": datetime.datetime.utcnow().isoformat(),
                "user_id": TARGET_USER_ID,
                "media_urls": urls
            }

        return {"new_story": False, "user_id": TARGET_USER_ID}

    except Exception as e:
        return {"error": str(e), "new_story": False}
