import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def get_headers():
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("No API found")    
    return {"X-Auth-Token": api_key}

def get_pl_matches(data: dict):
    if "matches" not in data:
        raise ValueError(f"Unexpected response format: {data.keys()}")
    
    matches = data["matches"]
    pl_matches = [match for match in matches if match["competition"]["code"] == "PL"]
    return pl_matches