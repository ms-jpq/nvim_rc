#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

DST="$1"
SRC="${2:-"$(</dev/fd/0)"}"
FMT="${FMT:-"$SRC"}"

case "$OSTYPE" in
linux*)
  T='tar'
  ;;
darwin*)
  T='/usr/bin/tar'
  ;;
msys)
  # shellcheck disable=SC2154
  T="$(cygpath -- "$SYSTEMROOT/system32/tar.exe")"
  ;;
*)
  set -x
  exit 1
  ;;
esac

TAR=("$T" --extract --file "$SRC" --directory "$DST")
if [[ "$OSTYPE" == linux* ]]; then
  TAR+=(--no-same-owner)
fi

case "$FMT" in
*.tar.bz | *.tar.bz2 | *.tbz | *.tbz2 | *.tar.gz | *.tgz | *.tar.xz | *.txz | *.tar.zst)
  "${TAR[@]}"
  ;;
*.zip | *.vsix)
  if [[ "$OSTYPE" == linux* ]]; then
    unzip -o -d "$DST" -- "$SRC"
  else
    "${TAR[@]}"
  fi
  ;;
*.gz | *.xz)
  gzip --decompress --keep --force --stdout -- "$SRC" >"$DST"
  ;;
*)
  set -x
  exit 1
  ;;
esac

tee >&2 <<-EOF
$SRC
-> -> ->
$DST
EOF
