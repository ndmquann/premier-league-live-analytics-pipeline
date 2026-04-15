from app.fetchers.base import BASE_URL, headers
import requests

LIVE_STATUSES = ["IN_PLAY", "PAUSED", "EXTRA_TIME", "PENALTY_SHOOTOUT"]

def get_live_scores():
    live = ",".join(LIVE_STATUSES)
    scores_url = f"{BASE_URL}/competitions/PL/matches?status={live}"
    try:
        response = requests.get(scores_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "matches" not in data:
            raise ValueError(f"Unexpected response format: {response.json().keys()}")
        
        return data["matches"]
    except requests.RequestException as e:
        print(f"Error fetching live scores: {e}")
        return []
    
def extract_match_info(match):
    home_team = match["homeTeam"]["name"]
    away_team = match["awayTeam"]["name"]
    score = f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}"
    goals = []
    for goal in match["goals"]:
        goals.append({
            "scorer": goal["scorer"]["name"],
            "team": goal["team"]["name"],
            "assist": goal["assist"]["name"] if goal["assist"] else "N/A",
            "minute": goal["minute"]
        })
    return {
        "home_team": home_team,
        "away_team": away_team,
        "score": score,
        "goals": goals
    }

def is_match_live(matches: list) -> bool:
    return any(m["status"] in LIVE_STATUSES for m in matches)