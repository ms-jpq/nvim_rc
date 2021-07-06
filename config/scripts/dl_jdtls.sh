#!/usr/bin/env bash

set -eu
set -o pipefail


LATEST="$(< "$(get --cd "$TMP_DIR" -- "$URI")")"
get -- "$PREFIX/$LATEST" | unpack -

