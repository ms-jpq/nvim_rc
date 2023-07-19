#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

mkdir -p -- "$LIB"
export -- GO111MODULE=on GOPATH GOPATH="$LIB"
go install -- github.com/wader/jq-lsp@master
install -b -- "$LIB/bin/${BIN##*/}" "$BIN"
