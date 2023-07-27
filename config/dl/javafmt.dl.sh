#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

VERSION='1.17.0'
URI="https://github.com/google/google-java-format/releases/latest/download/google-java-format-$VERSION-all-deps.jar"

# shellcheck disable=SC2154
FMT="$LIB/google-java-format.jar"
JAR="$(get.py -- "$URI")"

mkdir -p -- "$LIB"
cp -f -- "$JAR" "$FMT"
# shellcheck disable=SC2154
install -b -- "${0%/*}/javafmt.ex.sh" "$BIN"
