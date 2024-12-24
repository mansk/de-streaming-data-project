# Guardian API to SQS streamer

## Overview
This a Python application designed to retrieve information about articles from the Guardian API based on a specified search term (and optionally a date). The application then publishes the retrieved data in JSON form to an AWS Simple Queue Service (SQS) queue where it can then be consumed by a pipeline component or user.

The application ensures that each message has at least "webPublicationDate", "webTitle" and "webUrl" fields.


## Prerequisites
- **Python**
- **AWS account**: Required to use AWS SQS and Secrets Manager.
- **Guardian API key**: Obtain a free API key from the Guardian at https://open-platform.theguardian.com


## Setup
1. **Clone the repository**:
   Then `cd` into the cloned directory.
2. **Install dependencies, run tests and checks**:
   ```sh
   make all
   ```
3. **Store the Guardian API key in AWS Secrets Manager**:
   The name of the secret should be `GUARDIAN_API_KEY`.
4. **Create a target queue in Amazon SQS.**


## Usage
### Command line
To run the application from the command line, make sure the virtual environment is activated:
```sh
source venv/bin/activate
```

Set the `PYTHONPATH` environment variable to the current directory:
```sh
export PYTHONPATH=$(pwd)
```

Then use the following command:
```sh
python src/main.py "search_term" --date_from "YYYY-MM-DD" --sqs_queue_name "queue_name"
```

#### Command-Line Arguments
- `search_term` (required): The term to search for in articles. Supports logical operators and exact phrase queries.
- `--date_from` (optional): Return only content published on or after this date.
- `--sqs_queue_name` (optional): The name of the destination SQS queue. Default is `guardian_content`.

#### Example
```sh
python src/main.py "machine learning" --date_from "2023-01-01" --sqs_queue_name "guardian_content"
```


### Deployment as a component in a data platform
#### AWS Lambda Layer
The Makefile includes a target that will package the code into a zip file for an AWS Lambda Layer:
  ```sh
   make lambda_layer
   ```


## Future tasks
1. Use Terraform to provision all necessary AWS infrastructure.
2. CI/CD with GitHub Actions.
3. Include a preview of the content of each article in the message sent to the queue.