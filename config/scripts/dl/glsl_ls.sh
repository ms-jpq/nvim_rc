#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar

LOCATION="$PWD/glsl-ls"
REPO="$LOCATION/repo"

VENV="$LOCATION/venv"
VENV_BIN="$VENV/bin"
NINJA="$VENV_BIN/ninja"

PATH="$VENV_BIN:$PATH"

if [[ ! -x "$NINJA" ]]; then
  python3 -m venv -- "$VENV"
  "$VENV_BIN/pip" install -- ninja
fi

if [[ -d "$REPO" ]]; then
  cd -- "$REPO"
  OPTS=(--recurse-submodules --no-tags --force)
  git pull "${OPTS[@]}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" "$URI" "$REPO"
fi

if [[ ! "$OSTYPE" =~ "linux" ]]; then
  exit
fi

if [[ ! -x "$BIN" ]]; then
  cd -- "$REPO"
  make build
  ln --symbolic --force -- "$PWD/build/glslls" "$BIN"
fi
