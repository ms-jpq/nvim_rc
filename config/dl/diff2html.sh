#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

DIR="$(dirname -- "$0")"
case "$OSTYPE" in
msys)
  SUFFIX='.js'
  exit
  ;;
*)
  SUFFIX=''
  ;;
esac

ln -v -snf -- "../var/modules/node_modules/.bin/diff2html$SUFFIX" "$DIR/../../bin/diff2html$SUFFIX"
