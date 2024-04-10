#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE_URI='https://download.jboss.org/jbosstools/vscode/stable/lemminx-binary'

case "$OSTYPE" in
darwin*)
  BASENAME='lemminx-osx-x86_64.zip'
  ;;
linux*)
  BASENAME='lemminx-linux.zip'
  ;;
*)
  BASENAME='lemminx-win32.zip'
  BIN="$BIN.exe"
  ;;
esac

VERSION="$(curl --fail-with-body --location --no-progress-meter --max-time 600 -- "$BASE_URI" | htmlq --attribute href -- 'body > table > tbody > tr:nth-last-child(2) > td > a')"
URI="$BASE_URI/$VERSION/$BASENAME"
# shellcheck disable=SC2154
get.sh "$URI" | unpack.sh "$TMP"
install -v -b -- "$TMP/lemminx"* "$BIN"
