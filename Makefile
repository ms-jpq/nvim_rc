MAKEFLAGS += --jobs
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -Eeuo pipefail -O dotglob -O failglob -O globstar -c

.DEFAULT_GOAL := help

.PHONY: clean clobber

clean:
	rm -rf -- .clj-kondo/ .lsp/ .mypy_cache/ .venv/

clobber: clean
	sudo -- rm -rf -- pack/ var/

patch:
	python3 -m go deps packages

install:
	python3 -m go deps

.venv/bin/pip:
	python3 -m venv -- .venv

.venv/bin/mypy: .venv/bin/pip
	'$<' install --upgrade --requirement requirements.txt -- mypy types-PyYAML isort black

.PHONY: lint

lint: .venv/bin/mypy
	'$<' -- .

.PHONY: build

build:
	docker build --file docker/Dockerfile --tag nvim -- .

fmt: .venv/bin/mypy
	.venv/bin/isort --profile=black --gitignore -- .
	.venv/bin/black --extend-exclude pack -- .
