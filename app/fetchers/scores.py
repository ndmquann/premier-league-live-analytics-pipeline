from app.fetchers.base import BASE_URL, get_headers, get_pl_matches
import requests

LIVE_STATUSES = ["IN_PLAY", "PAUSED", "EXTRA_TIME", "PENALTY_SHOOTOUT"]

def get_live_scores():
    scores_url = f"{BASE_URL}/matches"
    try:
        response = requests.get(scores_url, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        pl_matches = get_pl_matches(data)
        
        matches = []
        for match in pl_matches:
            if match["status"] in LIVE_STATUSES:
                matches.append(match)

        return matches
    except requests.RequestException as e:
        print(f"Error fetching live scores: {e}")
        return []

def is_match_live(matches: list) -> bool:
    return any(m["status"] in LIVE_STATUSES for m in matches)