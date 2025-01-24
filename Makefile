# Makefile for running tests, security checks, code quality checks, and installation

PROJECT_NAME := Guardian-API-to-SQS
SHELL := /bin/bash
PYTHON := python
PIP := pip

## Create python interpreter environment.
create-environment:
	@echo ">>> Creating virtual environment for $(PROJECT_NAME)"; \
	$(PYTHON) -m venv venv;

# Define utility variable to help calling executables from the virtual environment
ACTIVATE_ENV := source venv/bin/activate

define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

## Build the environment requirements
requirements: create-environment
	$(call execute_in_env,$(PIP) install --upgrade pip pip-tools setuptools)
	$(call execute_in_env,pip-compile --output-file requirements.txt pyproject.toml)
	$(call execute_in_env,$(PIP) install -r ./requirements.txt)
	@rm -rf src/*egg-info

## Build the environment requirements, including dependencies for tests and checks
dev-requirements: create-environment
	$(call execute_in_env,$(PIP) install --upgrade pip pip-tools setuptools)
	$(call execute_in_env,pip-compile --extra dev --output-file dev-requirements.txt pyproject.toml)
	$(call execute_in_env,$(PIP) install -r ./dev-requirements.txt)
	@rm -rf src/*egg-info

# Run all checks then let user know that the CLI is ready to use
all: run-checks
	@echo
	@echo ">>> Installation completed and all checks run successfully"
	@echo "To activate virtual environment:"
	@echo "    source venv/bin/activate"
	@echo "Then run the script:"
	@echo "python src/main.py search_term [--date_from DATE_FROM] [--sqs_queue_name SQS_QUEUE_NAME]"

# Run all checks
run-checks: dev-requirements test bandit pip-audit lint format

# Run unit tests
test: dev-requirements
	$(call execute_in_env,pytest test/)

# Run Bandit for security analysis
bandit: dev-requirements
	$(call execute_in_env,bandit -r src/)

# Run pip-audit for dependency vulnerability checks
pip-audit: dev-requirements
	$(call execute_in_env,pip-audit)

# Lint code for PEP 8 compliance
lint: dev-requirements
	$(call execute_in_env,flake8 --per-file-ignores="test/fixtures.py:E501" src/ test/)

# Format code using Black
format: dev-requirements
	$(call execute_in_env,black --line-length=79 src/ test/)

# Create deployment package for Lambda layer
lambda_layer: requirements clean
	rm -rf lambda_layer
	mkdir -p lambda_layer/python
	$(PYTHON) -m venv lambda_venv;
	source lambda_venv/bin/activate && \
	$(PIP) install -r requirements.txt -t lambda_layer/python/lib/python3.13/site-packages
	cp -r src/* lambda_layer/python/
	cd lambda_layer && zip -r ../lambda_layer.zip . && cd ..
	rm -rf lambda_layer
	@echo "Lambda layer package created: lambda_layer.zip"

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm -f {} +
