from dotenv import load_dotenv
import logging
import os
import requests

load_dotenv()
logging.basicConfig(level=logging.INFO)

ENDPOINT = "https://content.guardianapis.com/search"
API_KEY = os.getenv("GUARDIAN_API_KEY", default="test")


def fetch(search_term=None, date_from=None):
    querystring = f"api-key={API_KEY}"
    logstring = f"Fetching results with no search term"
    if search_term:
        querystring += f"&q={search_term}"
        logstring = f"Fetching results with search term '{search_term}'"
    if date_from:
        querystring += f"&from-date={date_from}"
        logstring += f", dated '{date_from}' or later"

    logging.info(logstring)
    response = requests.get(f"{ENDPOINT}?{querystring}")

    if response.status_code == 200:
        return response.json()["response"]["results"]
