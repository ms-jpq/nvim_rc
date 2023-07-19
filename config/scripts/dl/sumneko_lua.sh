#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

if [[ ! "$OSTYPE" =~ "<>" ]]; then
  exit
fi

URI='https://github.com/LuaLS/lua-language-server'
TAG='3.6.11'

LOCATION="$PWD/lua-lsp"
REPO="$LOCATION/repo"

VENV="$LOCATION/venv"
VENV_BIN="$VENV/bin"
NINJA="$VENV_BIN/ninja"

if [[ ! -x "$NINJA" ]]; then
  python3 -m venv -- "$VENV"
  "$VENV_BIN/pip" install -- ninja
fi

if [[ -d "$REPO" ]]; then
  cd -- "$REPO"
  OPTS=(--recurse-submodules --no-tags)
  git pull "${OPTS[@]}" origin "refs/tags/$TAG:refs/tags/$TAG"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" --branch "$TAG" "$URI" "$REPO"
fi

if [[ ! -x "$BIN" ]]; then
  (
    PATH="$VENV_BIN:$PATH"
    cd -- "$REPO/3rd/luamake"

    case "$OSTYPE" in
    darwin*)
      NAME=macos
      ;;
    linux*)
      NAME=linux
      ;;
    *)
      NAME=msvc
      ;;
    esac

    ninja -f "$PWD/compile/ninja/$NAME.ninja"
    cd -- "$REPO"
    "$REPO/3rd/luamake/luamake" rebuild
  )

  PREFIX="${BIN%/*}"
  for file in "$REPO/bin/"*; do
    ln -sf -- "$file" "$PREFIX/$(basename -- "$file")"
  done
fi
