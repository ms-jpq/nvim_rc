#!/usr/bin/env bash

set -eu
set -o pipefail


T_BIN="$(dirname "$BIN")/tectonic"


if [[ "$OS" == 'Darwin' ]]
then
  URI="$MAC_URI"
  T_URI="$T_MAC_URI"
else
  URI="$LINUX_URI"
  T_URI="$T_LINUX_URI"
fi


TMP="$(mktemp --directory)"
get -- "$URI" | unpack --dest "$TMP"
get -- "$T_URI" | unpack --dest "$TMP"
mv -- "$TMP/texlab" "$BIN"
mv -- "$TMP/tectonic" "$T_BIN"
chmod +x -- "$BIN" "$T_BIN"
