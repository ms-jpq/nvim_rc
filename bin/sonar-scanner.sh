#!/usr/bin/env -S -- bash -Eeu -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

REAL="$(realpath -- "$0")"
BIN="$(dirname "$REAL")/../var/lib/sonar-scanner/bin/sonar-scanner"
NAME="$(basename -- "$PWD")"
KEY="$(jq --raw-input --raw-output '@uri' <<<"$NAME")"

EXEC=(
  "$BIN"
  --define sonar.projectKey="$KEY"
  --define sonar.projectName="$NAME"
  --define sonar.login=admin
  --define sonar.host.url="$1"
  --define sonar.password="$2"
)

shift -- 2

exec -- "${EXEC[@]}" "$@"
