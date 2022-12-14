#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


FILE="$(get -- "$URI")"
mkdir --parents -- "$LIB"
cp -- "$FILE" "$LIB/"
cp -- "$(dirname -- "$0")/../exec/phan.sh" "$BIN"
