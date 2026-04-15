from app.fetchers.base import BASE_URL, headers
import requests

LIVERPOOL_ID = 64

def get_liverpool_fixtures():
    fixture_url = f"{BASE_URL}/teams/{LIVERPOOL_ID}/matches?status=SCHEDULED"
    try:
        response = requests.get(fixture_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "matches" not in data:
            raise ValueError(f"Unexpected response format: {data.keys()}")
        
        return data
    except requests.RequestException as e:
        print(f"Error fetching Liverpool fixtures: {e}")
        return {"matches": []}

def get_liverpool_last_results():
    results_url = f"{BASE_URL}/teams/{LIVERPOOL_ID}/matches?status=FINISHED"
    try:
        response = requests.get(results_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "matches" not in data:
            raise ValueError(f"Unexpected response format: {data.keys()}")
        
        return data
    except requests.RequestException as e:
        print(f"Error fetching Liverpool results: {e}")
        return {"matches": []}