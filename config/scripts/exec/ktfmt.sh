#!/usr/bin/env -S -- bash

set -Eeu
set -o pipefail
shopt -s globstar failglob

LIB="$(dirname -- "$0")/../lib"

exec -- java -jar "$LIB/ktfmt"/*.jar "$@"
