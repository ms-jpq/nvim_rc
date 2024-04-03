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

tee >&2 <<-EOF
$SRC
>>>
$DST
EOF

{
  printf -- '%q ' "${CURL[@]}"
  printf -- '\n'
} >&2

if ! [[ -f "$DST" ]]; then
  rm -fr -- "$ETAG" "$TTAG" >&2
fi

if "${CURL[@]}" >&2; then
  {
    mv -f -- "$TMP" "$DST"
    mv -f -- "$TTAG" "$ETAG"
  } >&2
  printf -- '%s' "$DST"
else
  rm -fr -- "$TTAG" "$TMP" >&2
fi
