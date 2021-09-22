#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


cp -- "$(dirname "$0")/rfmt.r" "$BIN"
