from src.fetch import fetch
import boto3
import logging
from moto import mock_aws
import os
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse, parse_qs, unquote
import pytest
from test.fixtures import response_fixture


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def mock_sm_client(aws_credentials):
    """Return a mocked Secrets Manager client with a stored secret."""
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(Name="GUARDIAN_API_KEY", SecretString="test")
        yield client


@pytest.fixture(scope="function")
def mock_sm_client_no_api_key(aws_credentials):
    """Return a mocked Secrets Manager client without a stored secret."""
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        yield client


@pytest.fixture
def response():
    return response_fixture


@patch("src.fetch.requests.get")
def test_fetch_returns_list(mock_get, mock_sm_client, response):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    result = fetch()

    assert isinstance(result, list)


@patch("src.fetch.requests.get")
def test_fetch_returns_list_of_dicts(mock_get, mock_sm_client, response):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    result = fetch()

    assert all(isinstance(item, dict) for item in result)


@patch("src.fetch.requests.get")
def test_fetch_returns_list_of_length_10(mock_get, mock_sm_client, response):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    result = fetch()

    assert len(result) == 10


@patch("src.fetch.requests.get")
def test_fetch_correctly_constructs_querystring(mock_get, mock_sm_client):
    url = None

    def side_effect(arg_url, *args, **kwargs):
        nonlocal url
        url = arg_url

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"response": {"results": []}}

        return response

    mock_get.side_effect = side_effect

    fetch('"machine learning"', "2023-01-01")

    parsed_qs = parse_qs(urlparse(url).query)

    assert "q" in parsed_qs
    assert parsed_qs["q"][0] == '"machine learning"'
    assert "from-date" in parsed_qs
    assert parsed_qs["from-date"][0] == "2023-01-01"


@patch("src.fetch.requests.get")
def test_fetch_logs_call_with_no_search_term_and_no_date_from(
    mock_get, mock_sm_client, response, caplog
):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response

    with caplog.at_level(logging.INFO):
        fetch()

    assert "Fetching results with no search term" in caplog.text
    assert "dated" not in caplog.text


@patch("src.fetch.requests.get")
def test_fetch_logs_call_with_search_term_and_no_date_from(
    mock_get, mock_sm_client, response, caplog
):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    search_term = "machine learning"

    with caplog.at_level(logging.INFO):
        fetch(search_term)

    assert f"Fetching results with search term '{search_term}'" in caplog.text
    assert "dated" not in caplog.text


@patch("src.fetch.requests.get")
def test_fetch_logs_call_with_no_search_term_and_date_from(
    mock_get, mock_sm_client, response, caplog
):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    date_from = "2023-01-01"

    with caplog.at_level(logging.INFO):
        fetch(None, date_from)

    assert "Fetching results with no search term" in caplog.text
    assert f" dated '{date_from}" in caplog.text


@patch("src.fetch.requests.get")
def test_fetch_logs_call_with_search_term_and_date_from(
    mock_get, mock_sm_client, response, caplog
):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    search_term = "machine learning"
    date_from = "2023-01-01"

    with caplog.at_level(logging.INFO):
        fetch(search_term, date_from)

    assert f"Fetching results with search term '{search_term}" in caplog.text
    assert f" dated '{date_from}" in caplog.text


@patch("src.fetch.requests.get")
def test_fetch_logs_failed_api_requests_with_status_code_401(
    mock_get, mock_sm_client, caplog
):
    mock_get.return_value.status_code = 401

    with caplog.at_level(logging.ERROR):
        fetch()

    assert "Failed to fetch results" in caplog.text


@patch("src.fetch.requests.get")
def test_fetch_logs_failed_api_requests_with_non_401_status_code(
    mock_get, mock_sm_client, caplog
):
    status_code = 400
    error_message = "Test error message"
    mock_get.return_value.status_code = status_code
    mock_get.return_value.json.return_value = {
        "response": {"message": error_message}
    }

    with caplog.at_level(logging.ERROR):
        fetch()

    assert "Failed to fetch results" in caplog.text
    assert f"status code {status_code}" in caplog.text
    assert f"Server returned error message: {error_message}" in caplog.text


@patch("src.fetch.requests.get")
def test_fetch_applies_url_encoding_to_query_parameters(
    mock_get, mock_sm_client
):
    url = None

    def side_effect(arg_url, *args, **kwargs):
        nonlocal url
        url = arg_url

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"response": {"results": []}}

        return response

    mock_get.side_effect = side_effect

    search_term = "@+/^"
    date_from = "2010-07-20T10:00:00+05:00"

    fetch(search_term, date_from)

    parsed_qs = parse_qs(urlparse(url).query)

    assert unquote(parsed_qs["q"][0]) == search_term
    assert unquote(parsed_qs["from-date"][0]) == date_from


@patch("src.fetch.requests.get")
def test_fetch_logs_failure_to_retrieve_api_key_from_aws_sm(
    mock_get, mock_sm_client_no_api_key, caplog
):
    search_term = "machine learning"

    with caplog.at_level(logging.ERROR):
        fetch(search_term)

    assert "Failed to retrieve Guardian API key" in caplog.text
