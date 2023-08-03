#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

# shellcheck disable=2154
mkdir -v -p -- "$LIB"
export -- GO111MODULE=on GOPATH GOPATH="$LIB"
go install -- github.com/wader/jq-lsp@master
# shellcheck disable=2154
install -v -b -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
