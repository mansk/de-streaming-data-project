import boto3
from moto import mock_aws
import json
import os
import pytest
from src.send_to_sqs import send_to_sqs
from test.fixtures import results_fixture


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def mock_sqs_client(aws_credentials):
    """Return a mocked SQS client."""
    with mock_aws():
        yield boto3.client("sqs", region_name="eu-west-2")


@pytest.fixture
def messages():
    return [
        {key: message[key] for key in ("webPublicationDate", "webTitle", "webUrl")}
        for message in results_fixture
    ]


def test__send_to_sqs__correctly_sends_json_to_sqs(mock_sqs_client, messages):
    test_queue_name = "SENTINEL"
    response = mock_sqs_client.create_queue(QueueName=test_queue_name)
    mock_queue_url = response["QueueUrl"]

    send_to_sqs(messages, test_queue_name)

    retrieved_messages = mock_sqs_client.receive_message(
        QueueUrl=mock_queue_url, MaxNumberOfMessages=10
    )["Messages"]

    retrieved_messages = [json.loads(message["Body"]) for message in retrieved_messages]

    assert all(
        [
            any(
                [
                    sent_message == retrieved_message
                    for retrieved_message in retrieved_messages
                ]
            )
            for sent_message in messages
        ]
    )
