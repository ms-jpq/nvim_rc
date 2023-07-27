#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO="$1"

CURL=(
  curl --fail
  --location
  --no-progress-meter
  --max-time 60
  -- "https://api.github.com/repos/$REPO/tags"
)
JQ=(
  jq --exit-status
  --raw-output '.[].name'
)

LINES="$("${CURL[@]}" | "${JQ[@]}")"
readarray -t -d $'\n' -- TAGS <<<"$LINES"
printf -- '%s' "${TAGS[0]}"
