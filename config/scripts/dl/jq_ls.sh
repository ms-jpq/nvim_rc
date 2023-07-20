#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

# shellcheck disable=2154
mkdir -p -- "$LIB"
export -- GO111MODULE=on GOPATH GOPATH="$LIB"
go install -- github.com/wader/jq-lsp@master
# shellcheck disable=2154
install -b -- "$LIB/bin/${BIN##*/}" "$BIN"
