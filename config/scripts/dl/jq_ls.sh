#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O failglob -O globstar

mkdir --parents -- "$LIB"
export -- GO111MODULE=on GOPATH GOPATH="$LIB"
go install -- github.com/wader/jq-lsp@master
ln --symbolic --force -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
