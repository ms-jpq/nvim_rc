#!/usr/bin/env -S -- bash

set -Eeu
set -o pipefail
shopt -s nullglob

cd -- "$(dirname -- "$0")" || exit 1

exec -- python3 -m go deps "$@"
