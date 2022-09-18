#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


FILE="$(get -- "$URI")"
mkdir --parents -- "$LIB"
cp -- "$FILE" "$LIB/"
cp -- "$(dirname -- "$0")/../exec/phan.sh" "$BIN"
