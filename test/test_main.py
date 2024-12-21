from unittest.mock import patch
from src.main import main


@patch("src.main.send_to_sqs")
@patch("src.main.fetch")
def test_main_calls_fetch_with_correct_arguments_without_date_from(
    mock_fetch, mock_send_to_sqs
):
    main("machine learning")

    mock_fetch.assert_called_once_with("machine learning", None)


@patch("src.main.send_to_sqs")
@patch("src.main.fetch")
def test_main_calls_fetch_with_correct_arguments_with_date_from(
    mock_fetch, mock_send_to_sqs
):
    main("machine learning", "2023-01-01")

    mock_fetch.assert_called_once_with("machine learning", "2023-01-01")


@patch("src.main.send_to_sqs")
@patch("src.main.fetch")
def test_main_does_not_call_send_to_sqs_when_no_results_from_fetch(
    mock_fetch, mock_send_to_sqs
):
    mock_fetch.return_value = []

    main("test")

    mock_send_to_sqs.assert_not_called()
