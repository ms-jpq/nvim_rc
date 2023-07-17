#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE_URI='https://releases.hashicorp.com/terraform-ls'

HREF="$(curl --fail --location --no-progress-meter --max-time 60 -- "$BASE_URI" | htmlq --attribute href -- 'body > ul > li:nth-child(2) > a')"
VERSION="${HREF%%/}"
VERSION="${VERSION##*/}"

case "$OSTYPE" in
darwin*)
  NAME=darwin_arm64
  ;;
linux*)
  NAME=linux_amd64
  ;;
*)
  NAME=windows_amd64
  ;;
esac

URI="$BASE_URI/$VERSION/terraform-ls_${VERSION}_$NAME.zip"
TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
mv --force -- "$TMP/terraform"* "$BIN"
chmod +x -- "$BIN"
