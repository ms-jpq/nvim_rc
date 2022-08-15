#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


get -- "$URI"
cp -- "$(dirname "$0")/../exec/phan.sh" "$BIN"
