#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

ln -v -snf -- '../var/modules/node_modules/.bin/diff2html' "${0%/*}/../../bin/diff2html"
