.PHONY: install test lint format check clean

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt

test:
	python -m pytest -v

lint:
	ruff check .
	black --check .
	isort --check-only .

format:
	ruff check --fix .
	isort .
	black .

check: lint test
	bandit -r app
	pip-audit -r requirements.txt

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ app/__pycache__ tests/__pycache__ *.egg-info
