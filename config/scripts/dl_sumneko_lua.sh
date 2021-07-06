#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ -d "$LIB" ]]
then
  cd "$LIB" || exit 1
  OPTS=(--recurse-submodules)
  git pull "${OPTS[@]}" origin "refs/tags/${TAG}:refs/tags/${TAG}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" --branch "$TAG" "$URI" "$LIB"
fi

(
  cd "$LIB/3rd/luamake" || exit 1
  ./compile/install.sh
  cd ../.. || exit 1
  ./3rd/luamake/luamake rebuild
)

ln --symbolic --force -- "$LIB/"*'/lua-language-server' "$BIN"

