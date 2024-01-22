#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='google/google-java-format'
VERSION="$(gh-latest.sh . "$REPO")"
VERSION="${VERSION#v}"
URI="https://github.com/$REPO/releases/latest/download/google-java-format-$VERSION-all-deps.jar"

# shellcheck disable=SC2154
FMT="$LIB/google-java-format.jar"
JAR="$(get.py -- "$URI")"

mkdir -v -p -- "$LIB"
cp -v -f -- "$JAR" "$FMT"
# shellcheck disable=SC2154
install -v -b -- "$(dirname -- "$0")/javafmt.ex.sh" "$BIN"
