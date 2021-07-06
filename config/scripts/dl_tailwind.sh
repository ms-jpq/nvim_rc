#!/usr/bin/env bash

set -eu
set -o pipefail


get --type '.zip' "$URI" | unpack - -- "$TMP_DIR"
printf '%s\n' '#!/usr/bin/env node' > "$BIN_PATH"
cat -- "$TMP_DIR/extension/dist/extension/index.js" >> "$BIN_PATH"
chmod +x -- "$BIN_PATH"

