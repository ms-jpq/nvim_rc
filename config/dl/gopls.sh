#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

case "$OSTYPE" in
msys)
  BIN="$BIN.exe"
  ;;
*) ;;
esac

# shellcheck disable=2154
mkdir -v -p -- "$LIB"
export -- GO111MODULE=on GOPATH="$LIB"
go install -- golang.org/x/tools/gopls@latest
# shellcheck disable=2154
install -v -b -- "$LIB/bin/$(basename -- "$BIN")" "$BIN"
