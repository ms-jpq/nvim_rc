#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar nullglob


cd -- "$(dirname -- "$0")" || exit 1


exec -- python -m go deps "$@"
