#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

case "$OSTYPE" in
darwin*)
  BASENAME="$DARWIN"
  ;;
linux*)
  BASENAME="$LINUX"
  ;;
*)
  BASENAME="$NT"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp --directory)"
VERSION="$(curl --no-progress-meter --location "$BASE_URI" | htmlq --attribute href -- 'body > table > tbody > tr:nth-last-child(2) > td > a')"
URI="$BASE_URI/$VERSION/$BASENAME"
get -- "$URI" | unpack --dest "$TMP"
mv -- "$TMP/lemminx"* "$BIN"
chmod +x -- "$BIN"
