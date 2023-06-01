#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O nullglob -O failglob -O globstar

mkdir --parents -- "$LIB"
export -- GO111MODULE=on GOPATH GOPATH="$LIB"
go install -- golang.org/x/tools/gopls@latest
ln --symbolic --force -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
