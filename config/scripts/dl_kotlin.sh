#!/usr/bin/env bash

set -eu
set -o pipefail


get -- "$URI" | unpack -
rm --recursive --force -- "$LIB"
mv -- './server' "$LIB"
LL="$LIB/bin/kotlin-language-server"
ln --symbolic --force -- "$LL" "$BIN"
chmod +x -- "$LL"
