#!/usr/bin/env -S -- bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


LOCATION="$PWD/glsl-ls"
REPO="$LOCATION/repo"

VENV="$LOCATION/venv"
VENV_BIN="$VENV/bin"
NINJA="$VENV_BIN/ninja"

PATH="$VENV_BIN:$PATH"


if [[ ! -x "$NINJA" ]]
then
  python3 -m venv -- "$VENV"
  "$VENV_BIN/pip" install -- ninja
fi


if [[ -d "$REPO" ]]
then
  cd -- "$REPO" || exit 1
  OPTS=(--recurse-submodules --no-tags)
  git pull "${OPTS[@]}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" "$URI" "$REPO"
fi


if [[ ! "$OSTYPE" =~ "linux" ]]
then
  exit
fi

if [[ ! -x "$BIN" ]]
then
  cd -- "$REPO" || exit 1
  make build
  ln --symbolic --force -- "$PWD/build/glslls" "$BIN"
fi
