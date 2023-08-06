MAKEFLAGS += --check-symlink-times
MAKEFLAGS += --jobs
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables
MAKEFLAGS += --shuffle
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := --norc --noprofile -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar -c

.DEFAULT_GOAL := help

.PHONY: clean clobber lint build fmt runtime mvp patch install

clean:
	rm -v -rf -- .clj-kondo/ .lsp/ .mypy_cache/ .venv/ var/tmp/*.cache

clobber: clean
	sudo -- rm -v -rf -- pack/ var/

ifeq ($(origin USERPROFILE), command line)
HOME := $(USERPROFILE)
$(warning <<<<<<<<<<<<< $(USERPROFILE))
export -- HOME
endif

$(warning ->>>>>>> $(USERPROFILE))
$(warning ->>>>>>> $(HOME))

runtime: var/runtime/requirements.lock
var/runtime/requirements.lock:
	python3 -m go deps runtime

pack/modules/start/chadtree:
	env
	python3 -m go deps runtime packages mvp

mvp: pack/modules/start/chadtree

patch: var/runtime/requirements.lock
	python3 -m go deps packages

install:
	python3 -m go deps

.venv/bin/python3:
	python3 -m venv -- .venv

define PYDEPS
from itertools import chain
from os import execl
from sys import executable

from tomli import load

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
endef

.venv/bin/mypy: .venv/bin/python3
	'$<' -m pip install --requirement requirements.txt -- tomli
	'$<' <<< '$(PYDEPS)'

lint: .venv/bin/mypy
	'$<' -- .

build:
	docker build --progress plain --file docker/Dockerfile --tag nvim -- .

fmt: .venv/bin/mypy
	.venv/bin/isort --profile=black --gitignore -- .
	.venv/bin/black --extend-exclude pack -- .

