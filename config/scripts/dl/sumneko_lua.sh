#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


if [[ "$OS" != "Linux" ]]
then
  exit
fi


LOCATION="$PWD/lua-lsp"
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
  OPTS=(--recurse-submodules --no-tags)
  git pull "${OPTS[@]}" origin "refs/tags/${TAG}:refs/tags/${TAG}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" --branch "$TAG" "$URI" "$REPO"
fi


if [[ ! -x "$BIN" ]]
then
  (
    export PATH="$VENV_BIN:$PATH"
    cd "$REPO/3rd/luamake" || exit 1

    if [[ "$OS" == 'Darwin' ]]
    then
      NAME=macos
    else
      NAME=linux
    fi

    ninja -f "$PWD/compile/ninja/$NAME.ninja"
    cd "$REPO" || exit 1
    "$REPO/3rd/luamake/luamake" rebuild
  )

  PREFIX="$(dirname -- "$BIN")"
  for file in "$REPO/bin/"*
  do
    ln --symbolic --force -- "$file" "$PREFIX/$(basename "$file")"
  done
fi
