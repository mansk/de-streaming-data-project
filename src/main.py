import argparse
from src.fetch import fetch
from src.send_to_sqs import send_to_sqs


def main(search_term, date_from=None, sqs_queue_name="guardian_content"):
    messages = fetch(search_term, date_from)

    if len(messages):
        send_to_sqs(messages, sqs_queue_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch up to 10 search results from Guardian API and send to SQS."
    )
    parser.add_argument(
        "search_term",
        help=(
            "Request content containing this free text. "
            "Supports AND, OR and NOT operators, "
            "and exact phrase queries using double quotes. "
            "Note entire search term must be enclosed in single quotes "
            "if it contains phrases in double quotes."
        ),
    )
    parser.add_argument(
        "--date_from", help="Return only content published on or after this date."
    )
    parser.add_argument(
        "--sqs_queue_name",
        default="guardian_content",
        help="Name of destination SQS queue.",
    )
    args = parser.parse_args()

    main(args.search_term, args.date_from, args.sqs_queue_name)
