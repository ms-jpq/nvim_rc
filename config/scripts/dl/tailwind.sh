#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob

cd "$(dirname "$0")" || exit 1


TMP="$(mktemp --directory)"
get "$URI" | unpack --format 'zip' --dest "$TMP"
printf '%s\n\n' '#!/usr/bin/env node' > "$BIN"
cat -- "$TMP/extension/dist/server/tailwindServer.js" >> "$BIN"
chmod +x -- "$BIN"

