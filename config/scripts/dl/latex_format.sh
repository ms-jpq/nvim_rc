#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


if [[ -d "$LIB" ]]
then
  cd "$LIB" || exit 1
  OPTS=(--recurse-submodules --no-tags)
  git pull "${OPTS[@]}" origin "refs/tags/${TAG}:refs/tags/${TAG}"
else
  OPTS=(--depth=1 --recurse-submodules --shallow-submodules)
  git clone "${OPTS[@]}" --branch "$TAG" "$URI" "$LIB"
fi

PERL_LIB_DIR="$(dirname -- "$LIB")/perllibs"
PERL_LIBS=(
  YAML::Tiny
  File::HomeDir
  Unicode::GCString
)

cpanm --local-lib "$PERL_LIB_DIR" -- "${PERL_LIBS[@]}"
cp -- "$(dirname -- "$0")/../exec/latexindent.sh" "$BIN"
