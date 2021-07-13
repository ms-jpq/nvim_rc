#!/usr/bin/env bash

set -eu
set -o pipefail


TMP="$(mktemp --directory)"
get --type '.zip' "$URI" | unpack --dest "$TMP" -
printf '%s\n\n' '#!/usr/bin/env node' > "$BIN"
cat -- "$TMP/extension/dist/server/tailwindServer.js" >> "$BIN"
chmod +x -- "$BIN"

