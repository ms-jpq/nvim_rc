#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

BASE_URI='https://releases.hashicorp.com/terraform-ls'

HREF="$(curl --fail-with-body --location --no-progress-meter --max-time 600 -- "$BASE_URI" | htmlq --attribute href -- 'body > ul > li:nth-child(2) > a')"
VERSION="${HREF%%/}"
VERSION="${VERSION##*/}"

case "$HOSTTYPE" in
aarch64)
  HT='arm64'
  ;;
*)
  HT='amd64'
  ;;
esac

case "$OSTYPE" in
darwin*)
  NAME="darwin_$HT"
  ;;
linux*)
  NAME="linux_$HT"
  ;;
*)
  NAME="windows_$HT"
  BIN="$BIN.exe"
  ;;
esac

URI="$BASE_URI/$VERSION/terraform-ls_${VERSION}_$NAME.zip"
TMP="$(mktemp -d)"
get.sh "$URI" | unpack.sh "$TMP"
# shellcheck disable=2154
install -v -b -- "$TMP/terraform"* "$BIN"
rm -v -fr -- "$TMP"
