#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REPO="$1"
CACHE="$PWD/${REPO/\//.}.cache"

if ! [[ -v LOCKED ]] && command -v -- flock >/dev/null; then
  LOCKED=1 exec -- flock "$0" "$0" "$@"
fi

if ! [[ -f "$CACHE" ]]; then
  CURL=(
    curl
    --fail-with-body
    --location
    --no-progress-meter
    --max-time 60
  )
  if [[ -v GH_TOKEN ]]; then
    CURL+=(
      --header "Authorization: Bearer $GH_TOKEN"
    )
  fi
  CURL+=(
    -- "https://api.github.com/repos/$REPO/releases/latest"
  )

  JQ=(
    jq --exit-status
    --raw-output '.tag_name'
  )

  LINES="$("${CURL[@]}" | "${JQ[@]}")"
  readarray -t -d $'\n' -- TAGS <<<"$LINES"
  printf -- '%s' "${TAGS[0]}" >"$CACHE"
fi

exec -- cat -- "$CACHE"
