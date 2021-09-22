#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob

cd "$(dirname "$0")" || exit 1


cp -- "../exec/rfmt.r" "$BIN"
