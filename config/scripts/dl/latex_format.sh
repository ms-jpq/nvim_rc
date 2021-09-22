#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


cd "$(dirname "$0")" || exit 1


if [[ -d "$LIB" ]]
then
  cd "$LIB" || exit 1
  OPTS=(--recurse-submodules)
  git pull "${OPTS[@]}" origin "refs/tags/${TAG}:refs/tags/${TAG}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" --branch "$TAG" "$URI" "$LIB"
fi

ln --symbolic --force -- "$LIB/latexindent.pl" "$BIN"

