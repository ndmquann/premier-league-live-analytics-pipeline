from app.fetchers.base import BASE_URL, headers
import requests
from datetime import datetime, timezone, timedelta

vietnam_tz = timezone(timedelta(hours=7))

def get_today_fixtures():
    fixtures_url = f"{BASE_URL}/competitions/PL/matches?status=SCHEDULED"
    try:
        response = requests.get(fixtures_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "matches" not in data:
            raise ValueError(f"Unexpected response format: {data.keys()}")
        
        today_matches = []
        for match in data["matches"]:
            utc_time = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(vietnam_tz)
            if local_time.date() == datetime.now(vietnam_tz).date():
                today_matches.append(match)
        return today_matches
    except requests.RequestException as e:
        print(f"Error fetching today's fixtures: {e}")
        return []
    