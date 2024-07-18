#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

SRC="$1"
DST="${2:-"$(basename -- "$SRC")"}"

TTAG="$DST.ttag"
ETAG="$DST.etag"

CURL=(
  curl
  --fail-with-body
  --location
  --remove-on-error
  --create-dirs
  --remote-time
  --no-progress-meter
  --max-time 600
  --etag-compare "$ETAG"
  --etag-save "$TTAG"
  --output "$DST"
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
  if [[ -f $TTAG ]]; then
    mv -f -- "$TTAG" "$ETAG"
  fi >&2
  printf -- '%s' "$DST"
else
  rm -fr -- "$TTAG" >&2
  set -x
  exit 1
fi
