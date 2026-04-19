from app.fetchers.base import BASE_URL, get_headers, get_pl_matches
import requests
from datetime import datetime, timezone, timedelta

vietnam_tz = timezone(timedelta(hours=7))

def get_today_fixtures():
    fixtures_url = f"{BASE_URL}/matches"
    try:
        response = requests.get(fixtures_url, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        pl_matches = get_pl_matches(data)
        
        today_matches = []
        for match in pl_matches:
            utc_time = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(vietnam_tz)
            if local_time.date() == datetime.now(vietnam_tz).date():
                match["time"] = local_time.strftime("%H:%M")
                today_matches.append(match)
        return today_matches
    except requests.RequestException as e:
        print(f"Error fetching today's fixtures: {e}")
        return []
    