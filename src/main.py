from src.fetch import fetch
from src.send_to_sqs import send_to_sqs


def main(search_term, date_from=None, sqs_queue_name="guardian_content"):
    messages = fetch(search_term, date_from)

    if len(messages):
        send_to_sqs(messages, sqs_queue_name)
