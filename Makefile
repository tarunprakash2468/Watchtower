# Makefile for common development tasks

.PHONY: install cli lint test run venv format clean build check

install:
	pip install -r requirements.txt
	
cli:
	pip install -e .

venv:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip

requirements:
	pipreqs ./src --force --savepath requirements.in
	pip-compile requirements.in -o requirements.txt

test:
	pytest

run:
	python src/watchtower/core/import_udl_to_nominal.py

format:
	ruff check . --fix
	black src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache build dist *.egg-info

build:
	python -m build

check: lint test
