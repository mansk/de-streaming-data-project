import boto3
from botocore.exceptions import ClientError
import logging
import requests
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)

ENDPOINT = "https://content.guardianapis.com/search"
API_KEY = "test"


def fetch(search_term: None | str = None, date_from: None | str = None):
    """
    Fetch information about articles from the Guardian API based on a search
    term and an optional `date_from` parameter.
    """

    logging.info("Retrieving API key from AWS Secrets Manager")
    sm_client = boto3.client("secretsmanager")
    try:
        response = sm_client.get_secret_value(SecretId="GUARDIAN_API_KEY")

        API_KEY = response["SecretString"]
    except ClientError as e:
        logging.error(
            "Failed to retrieve Guardian API key from Secrets Manager: ",
            f"{e.response['Error']['Message']}",
        )

    params = {"api-key": API_KEY}
    logstring = "Fetching results with no search term"
    if search_term:
        params["q"] = search_term
        logstring = f"Fetching results with search term '{search_term}'"
    if date_from:
        params["from-date"] = date_from
        logstring += f", dated '{date_from}' or later"

    logging.info(logstring)
    querystring = urlencode(params)
    response = requests.get(f"{ENDPOINT}?{querystring}", timeout=5)

    if response.status_code == 200:
        return response.json()["response"]["results"]
    elif response.status_code == 401:
        logging.error(
            (
                "Failed to fetch results: status code 401. "
                f"API key {API_KEY} may be invalid"
            )
        )
    else:
        logging.error(
            (f"Failed to fetch results: status code {response.status_code}")
        )
        if error_message := response.json()["response"]["message"]:
            logging.error(f"Server returned error message: {error_message}")
