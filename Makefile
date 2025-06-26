# Makefile for TTS CLI Tool Development

.PHONY: help install install-dev test test-cov lint format type-check clean build run-example security-check docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  type-check   - Run type checking"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  run-example  - Run example with sample text"
	@echo "  run-web      - Run unified web server (CLI + Web)"
	@echo "  run-web-prod - Run web server in production mode"
	@echo "  test-file-management - Test unified file management system"
	@echo "  security     - Run security checks"
	@echo "  docs         - Generate documentation"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[test,dev]"

# Testing
test:
	PYTHONPATH=. pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-integration:
	pytest tests/test_integration.py -v -m integration

test-unit:
	pytest tests/test_basic_functionality.py -v -m unit

test-file-management:
	PYTHONPATH=. python tests/test_unified_file_management.py

# Code quality
lint:
	flake8 src/ tests/ --max-line-length=127 --extend-ignore=E203,W503
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	black src/ tests/ --line-length=127
	black --check src/ tests/ --line-length=127

format-fix:
	black src/ tests/ --line-length=127

type-check:
	mypy src/ --ignore-missing-imports --no-strict-optional

# Build and packaging
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

build-check: build
	twine check dist/*

# Security
security:
	bandit -r src/ -f txt
	safety check

security-json:
	bandit -r src/ -f json -o security-report.json
	safety check --json --output safety-deps.json

# Development utilities
run-example:
	python -m src.main -t "Hello world! This is a test of the text-to-speech system."

run-example-file:
	python -m src.main -f examples/data/input.txt

run-example-translate:
	python -m src.main -t "Bonjour le monde" --language en

run-example-verbose:
	python -m src.main -t "Hello world!" --verbose

run-web:
	python -m src.web_server --reload

run-web-prod:
	python -m src.web_server --host 0.0.0.0 --port 8000

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "README.md contains the main documentation"
	@echo "Use 'make docs-serve' to serve docs locally if needed"

# Cleanup output files
clean-output:
	rm -rf temp/session_*
	rm -rf temp/*.wav
	rm -rf temp/*.txt
	rm -rf temp/*.mp3

# Install pre-commit hooks
install-hooks:
	pre-commit install

# Run all quality checks
check-all: lint type-check test security

# Development workflow
dev-setup: install-dev install-hooks
	@echo "Development environment setup complete!"

# Release workflow
release-check: clean build build-check test-cov security
	@echo "Release checks complete!"

# Docker targets (if Docker is used)
docker-build:
	docker build -t tts-cli .

docker-run:
	docker run --rm -it tts-cli

# Performance profiling (if needed)
profile:
	python -m cProfile -o profile.stats -m src.main -t "Performance test text"
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Generate requirements.txt from pyproject.toml (if needed for Docker/CI)
requirements:
	uv pip compile pyproject.toml -o requirements.txt

requirements-dev:
	uv pip compile pyproject.toml --extra test --extra dev -o requirements-dev.txt
