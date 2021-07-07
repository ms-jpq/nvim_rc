#!/usr/bin/env bash

set -eu
set -o pipefail


get "$URI" | unpack -
mv -- './server' "$LIB"
ln --symbolic --force -- "$LIB/bin/kotlin-language-server" "$BIN"
