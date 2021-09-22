#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


LOCATION="$PWD/lua-ls"
REPO="$LOCATION/repo"

VENV="$LOCATION/venv"
VENV_BIN="$VENV/bin"
NINJA="$VENV_BIN/ninja"

if [[ ! -x "$NINJA" ]]
then
  python3 -m venv "$VENV"
  "$VENV_BIN/pip" install -- ninja
fi


if [[ -d "$REPO" ]]
then
  cd "$REPO" || exit 1
  OPTS=(--recurse-submodules)
  git pull "${OPTS[@]}" origin "refs/tags/${TAG}:refs/tags/${TAG}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" --branch "$TAG" "$URI" "$REPO"
fi


if [[ "$OS" = "Linux" ]]
then
  exit
fi


if [[ ! -x "$BIN" ]]
then
  (
    export PATH="$VENV_BIN:$PATH"
    cd "$REPO/3rd/luamake" || exit 1
    ./compile/install.sh
    cd ../.. || exit 1
    ./3rd/luamake/luamake rebuild
  )
  cp -- "../exec/luals" "$BIN"
fi
