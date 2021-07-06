#!/usr/bin/env bash

set -eu
set -o pipefail


if [[ -d "$LIB_PATH" ]]
then
  cd "$LIB_PATH" || exit 1
  OPTS=(--recurse-submodules)
  git pull "${OPTS[@]}" origin "refs/tags/${TAG}:refs/tags/${TAG}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" --branch "$TAG" "$URI" "$LIB_PATH"
fi

(
  cd "$LIB_PATH/3rd/luamake" || exit 1
  ./compile/install.sh
  cd ../.. || exit 1
  ./3rd/luamake/luamake rebuild
)

ln --symbolic --force -- "$LIB_PATH/"*'/lua-language-server' "$BIN_PATH"

