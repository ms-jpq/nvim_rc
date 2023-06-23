MAKEFLAGS += --jobs
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar -c

.DEFAULT_GOAL := help

.PHONY: clean clobber patch install lint build fmt

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
	'$<' install --upgrade --requirement requirements.txt

	.venv/bin/python3 <<EOF
	from itertools import chain
	from os import execl
	from sys import executable
	from tomllib import load

	toml = load(open("pyproject.toml", "rb"))
	project = toml["project"]
	execl(
			executable,
			executable,
			"-m",
			"pip",
			"install",
			"--upgrade",
			"--",
			*project.get("dependencies", ()),
			*chain.from_iterable(project["optional-dependencies"].values()),
	)
	EOF

lint: .venv/bin/mypy
	'$<' -- .

build:
	docker build --file docker/Dockerfile --tag nvim -- .

fmt: .venv/bin/mypy
	.venv/bin/isort --profile=black --gitignore -- .
	.venv/bin/black --extend-exclude pack -- .
