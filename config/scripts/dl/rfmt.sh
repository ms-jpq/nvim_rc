#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


cp -- "$(dirname -- "$0")/../exec/styler.r" "$BIN"
