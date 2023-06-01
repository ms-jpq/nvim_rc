#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O failglob -O globstar

if [[ ! "$OSTYPE" =~ "linux" ]]; then
  exit
fi

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

  PREFIX="$(dirname -- "$BIN")"
  for file in "$REPO/bin/"*; do
    ln --symbolic --force -- "$file" "$PREFIX/$(basename -- "$file")"
  done
fi
