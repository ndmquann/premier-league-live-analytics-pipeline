from app.fetchers.base import BASE_URL, headers
import requests

def get_standings():
    standings_url = f"{BASE_URL}/competitions/PL/standings"
    try:
        response = requests.get(standings_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "standings" not in data:
            raise ValueError(f"Unexpected response format: {data.keys()}")
        
        return data["standings"][0]["table"]
    except requests.RequestException as e:
        print(f"Error fetching standings: {e}")
        return []