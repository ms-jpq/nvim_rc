#!/usr/bin/env -S -- bash -Eeuo pipefail -O failglob -O globstar

T_BIN="$(dirname -- "$BIN")/tectonic"

case "$OSTYPE" in
darwin*)
  URI="$DARWIN_URI"
  T_URI="$T_DARWIN_URI"
  ;;
linux*)
  URI="$LINUX_URI"
  T_URI="$T_LINUX_URI"
  ;;
*)
  # shellcheck disable=SC2153
  URI="$NT_URI"
  T_URI="$T_NT_URI"
  BIN="$BIN.exe"
  T_BIN="$T_BIN.exe"
  ;;
esac

TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
get -- "$T_URI" | unpack --dest "$TMP"
mv -- "$TMP/texlab"* "$BIN"
mv -- "$TMP/tectonic"* "$T_BIN"
chmod +x -- "$BIN" "$T_BIN"
