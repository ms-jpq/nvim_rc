#!/usr/bin/env bash

set -eu
set -o pipefail


LATEST="$(< "$(get --cd "$TMP_DIR" -- "$URI")")"

get --cd "$TMP_DIR" -- "$PREFIX/$LATEST" | unpack - -- "$TMP_DIR"

