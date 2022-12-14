#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


cp -- "$(dirname -- "$0")/../exec/lintr.r" "$BIN"
