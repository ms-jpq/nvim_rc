#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO='SonarSource/sonar-scanner-cli'
BASE='https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli'
VERSION="$(gh-latest.sh . "$REPO")"

case "$OSTYPE" in
darwin*)
  URI="${BASE}-${VERSION}-macosx.zip"
  ;;
linux*)
  URI="${BASE}-${VERSION}-linux.zip"
  ;;
*)
  URI="${BASE}-${VERSION}-windows.zip"
  BIN="$BIN.exe"
  ;;
esac

TMP="$(mktemp -d)"
get.sh "$URI" | unpack.sh "$TMP"
# shellcheck disable=2154
rm -rf -- "$LIB"
chmod +x "$TMP"/*/{bin/*,jre/bin/*}
mv -f -- "$TMP"/* "$LIB"
rm -rf -- "$TMP"
