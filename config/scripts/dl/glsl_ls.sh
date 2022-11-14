#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


if [[ ! "$OSTYPE" =~ "linux" ]]
then
  exit
fi


LOCATION="$PWD/glsl-ls"
REPO="$LOCATION/repo"

VENV="$LOCATION/venv"
VENV_BIN="$VENV/bin"
NINJA="$VENV_BIN/ninja"

if [[ ! -x "$NINJA" ]]
then
  python3 -m venv -- "$VENV"
  "$VENV_BIN/pip" install -- ninja
else
  export PATH="$VENV_BIN:$PATH"
fi


if [[ -d "$REPO" ]]
then
  cd "$REPO" || exit 1
  OPTS=(--recurse-submodules --no-tags)
  git pull "${OPTS[@]}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" "$URI" "$REPO"
fi


if [[ ! -x "$BIN" ]]
then
  cd "$REPO" || exit 1
  make build
  ln --symbolic --force -- "$PWD/build/glslls" "$BIN"
fi
