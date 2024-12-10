from src.fetch import fetch
from unittest.mock import patch
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
