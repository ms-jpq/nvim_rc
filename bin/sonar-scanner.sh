#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REAL="$(realpath -- "$0")"
BIN="$(dirname -- "$REAL")/../var/lib/sonar-scanner/bin/sonar-scanner"
NAME="$(basename -- "$PWD")"
KEY="$(jq --raw-input --raw-output '@uri' <<< "$NAME")"

export -- SONAR_USER_HOME="${XDG_CACHE_HOME:-"$HOME/.cache"}/sonar"
VARS="$SONAR_USER_HOME/vars"

if ! [[ -f $VARS ]]; then
  # shellcheck disable=SC2154
  "$EDITOR" "$VARS"
fi

# shellcheck disable=1090
source -- "$VARS"

EXEC=(
  "$BIN"
  --define sonar.projectKey="$KEY"
  --define sonar.projectName="$NAME"
  --define sonar.login="${SONAR_LOGIN:-"admin"}"
  --define sonar.host.url="$SONAR_HOST_URL"
  --define sonar.password="$SONAR_PASSWORD"
)

exec -- "${EXEC[@]}" "$@"
