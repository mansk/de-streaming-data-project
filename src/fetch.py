from dotenv import load_dotenv
import os
import requests

load_dotenv()

ENDPOINT = "https://content.guardianapis.com/search"
API_KEY = os.getenv("GUARDIAN_API_KEY", default="test")


def fetch(search_term=None, date_from=None):
    querystring = f"api-key={API_KEY}"
    if search_term:
        querystring += f"&q={search_term}"
    if date_from:
        querystring += f"&from-date={date_from}"

    response = requests.get(f"{ENDPOINT}?{querystring}")

    if response.status_code == 200:
        return response.json()["response"]["results"]

