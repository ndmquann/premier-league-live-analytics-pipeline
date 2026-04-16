from app.fetchers.base import BASE_URL, get_headers
import requests

LIVERPOOL_ID = 64

def get_liverpool_fixtures():
    fixture_url = f"{BASE_URL}/teams/{LIVERPOOL_ID}/matches"
    try:
        response = requests.get(fixture_url, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        if "matches" not in data:
            raise ValueError(f"Unexpected response format: {data.keys()}")
        
        matches = []
        for match in data["matches"]:
            if match["status"] == "SCHEDULED":
                matches.append(match)

        return matches
    except requests.RequestException as e:
        print(f"Error fetching Liverpool fixtures: {e}")
        return []

def get_liverpool_last_results():
    results_url = f"{BASE_URL}/teams/{LIVERPOOL_ID}/matches"
    try:
        response = requests.get(results_url, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        if "matches" not in data:
            raise ValueError(f"Unexpected response format: {data.keys()}")
        
        matches = []
        for match in data["matches"]:
            if match["status"] == "FINISHED":
                matches.append(match)

        return matches
    except requests.RequestException as e:
        print(f"Error fetching Liverpool results: {e}")
        return []