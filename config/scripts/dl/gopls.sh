#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

mkdir -p -- "$LIB"
export -- GO111MODULE=on GOPATH GOPATH="$LIB"
go install -- golang.org/x/tools/gopls@latest
install -b -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
