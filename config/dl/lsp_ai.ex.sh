#!/usr/bin/env -S -- bash -Eeu -o pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar

set -o pipefail

set -a
# shellcheck disable=SC1091
source -- "$HOME/.local/opt/ai/.env"
set +a

exec -- "$(dirname -- "$0")/../lib/lsp-ai/lsp-ai" "$@"
