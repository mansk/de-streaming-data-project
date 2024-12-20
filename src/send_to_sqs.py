import boto3
import json
import logging


def send_to_sqs(messages: list[dict], queue: str):
    """Sends messages to named SQS queue."""
    sqs = boto3.client("sqs")

    entries = [
        {"Id": str(i), "MessageBody": json.dumps(message)}
        for i, message in enumerate(messages)
    ]

    # Get URL for queue
    queue_url = sqs.get_queue_url(QueueName=queue)
    queue_url = queue_url["QueueUrl"]

    # Send to queue
    logging.info(f"Sending {len(messages)} messages to queue {queue}")
    response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)

    return response
