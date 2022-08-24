#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


get -- "$URI" | unpack --dest "$LIB"
ln --symbolic --force -- "$LIB/fsautocomplete" "$BIN"
chmod +x -- "$BIN"
