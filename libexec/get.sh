#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

SRC="$1"
BASE="$(basename -- "$SRC")"
DST="${2:-"$BASE"}"

ETAG="$DST.etag"
TTAG="$DST.ttag"
TMP="$DST.tmp"

CURL=(
  curl
  --fail-with-body
  --location
  --create-dirs
  --remote-time
  --no-progress-meter
  --max-time 600
  --etag-compare "$ETAG"
  --etag-save "$TTAG"
  --output "$TMP"
  -- "$SRC"
)

tee >&2 <<- EOF
$SRC
>>>
$DST
EOF

if ! [[ -f $DST ]]; then
  rm -fr -- "$ETAG" "$TTAG"
fi >&2

if "${CURL[@]}" >&2; then
  {
    if [[ -f $TMP ]]; then
      mv -f -- "$TMP" "$DST"
    fi
    if [[ -f $TTAG ]]; then
      mv -f -- "$TTAG" "$ETAG"
    fi
  } >&2
  printf -- '%s' "$DST"
else
  rm -fr -- "$TTAG" "$TMP" >&2
  set -x
  exit 1
fi
