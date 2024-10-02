#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

DIR="$(dirname -- "$0")"

ln -v -snf -- '../var/modules/node_modules/.bin/diff2html' "$DIR/../../bin/diff2html"
