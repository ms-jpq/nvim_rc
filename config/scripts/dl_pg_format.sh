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

ln --symbolic --force -- "$LIB_PATH/$BIN_NAME" "$BIN_PATH"

