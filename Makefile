# Makefile for common development tasks

.PHONY: install lint test run

install:
	pip install -r requirements/requirements.txt
	pip install -r requirements/dev.txt

lint:
	ruff check .

test:
	pytest

run:
	python core/import_udl_to_nominal.py

