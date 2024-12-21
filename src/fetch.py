from dotenv import load_dotenv
import logging
import os
import requests

load_dotenv()
logging.basicConfig(level=logging.INFO)

ENDPOINT = "https://content.guardianapis.com/search"
API_KEY = os.getenv("GUARDIAN_API_KEY", default="test")


def fetch(search_term: None | str = None, date_from: None | str = None):
    querystring = f"api-key={API_KEY}"
    logstring = f"Fetching results with no search term"
    if search_term:
        querystring += f"&q={search_term}"
        logstring = f"Fetching results with search term '{search_term}'"
    if date_from:
        querystring += f"&from-date={date_from}"
        logstring += f", dated '{date_from}' or later"

    logging.info(logstring)
    response = requests.get(f"{ENDPOINT}?{querystring}", timeout=5)

    if response.status_code == 200:
        return response.json()["response"]["results"]
    elif response.status_code == 401:
        logging.error(
            f"Failed to fetch results: status code 401. API key {API_KEY} may be invalid"
        )
    else:
        logging.error(f"Failed to fetch results: status code {response.status_code}")
        if error_message:=response.json()["response"]["message"]:
            logging.error(f"Server returned error message: {error_message}")
