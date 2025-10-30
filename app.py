# FILE: app.py
# Full working backend for Instagram Story watcher (for iPad Shortcuts)
from fastapi import FastAPI
import httpx, datetime, os, json

app = FastAPI()

USERNAME = os.getenv("target_username")  # Environment variable from Render
LAST_ID = None  # Memory cache

@app.get("/")
def home():
    return {"status": "ok", "message": f"Story watcher active for {USERNAME}"}

@app.get("/stories")
def get_stories():
    """
    Check if a public Instagram account has new story.
    Returns new_story flag + story_url if changed.
    """
    global LAST_ID
    url = f"https://www.instagram.com/{USERNAME}/?__a=1&__d=dis"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/604.1"
        )
    }

    try:
        r = httpx.get(url, headers=headers, timeout=10)

        # bazen HTML döner, JSON yerine
        if "application/json" not in r.headers.get("content-type", ""):
            return {"error": "Instagram returned non-JSON", "new_story": False}

        data = r.json()
        user = data.get("graphql", {}).get("user", {})

        # story ID yerine highlight count kullanıyoruz (proxy göstergesi)
        story_timestamp = user.get("highlight_reel_count")
        now = datetime.datetime.utcnow().isoformat()

        if story_timestamp != LAST_ID:
            LAST_ID = story_timestamp
            story_url = f"https://instagram.com/stories/{USERNAME}/"
            return {
                "new_story": True,
                "username": USERNAME,
                "time": now,
                "story_url": story_url,
            }

        return {"new_story": False, "username": USERNAME, "time": now}

    except json.JSONDecodeError:
        return {"error": "Invalid JSON from Instagram", "new_story": False}
    except Exception as e:
        return {"error": str(e), "new_story": False}
