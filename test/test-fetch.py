from src.fetch import fetch
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse, parse_qs
import pytest
from test.fixtures import response_fixture


@pytest.fixture
def response():
    return response_fixture


@patch("src.fetch.requests.get")
def test_fetch_returns_list(mock_get, response):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    result = fetch()

    assert isinstance(result, list)


@patch("src.fetch.requests.get")
def test_fetch_returns_list_of_dicts(mock_get, response):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    result = fetch()

    assert all(isinstance(item, dict) for item in result)


@patch("src.fetch.requests.get")
def test_fetch_returns_list_of_length_10(mock_get, response):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response
    result = fetch()

    assert len(result) == 10


@patch("src.fetch.requests.get")
def test_fetch_correctly_constructs_querystring(mock_get):
    url = None

    def side_effect(arg):
        nonlocal url
        url = arg

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"response": {"results": []}}

        return response

    mock_get.side_effect = side_effect

    fetch('"machine learning"', "2023-01-01")

    parsed_qs = parse_qs(urlparse(url).query)

    assert parsed_qs["q"][0] == '"machine learning"'
    assert parsed_qs["from-date"][0] == "2023-01-01"
