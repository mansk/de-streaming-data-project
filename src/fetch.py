from dotenv import load_dotenv
import os
import requests

load_dotenv()

ENDPOINT = "https://content.guardianapis.com"
API_KEY = os.getenv("GUARDIAN_API_KEY", default="test")


def fetch():
    response = requests.get(
        f"https://content.guardianapis.com/search?api-key={API_KEY}"
    )

    if response.status_code == 200:
        return response.json()["response"]["results"]
