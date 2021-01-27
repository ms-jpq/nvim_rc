#!/usr/bin/env bash

set -eu
set -o pipefail

cd "$(dirname "$0")" || exit 1


export PATH="$PWD/.vars/runtime/bin:$PATH"
exec "$@"