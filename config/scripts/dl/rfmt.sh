#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


cp -- "$(dirname "$0")/../exec/rfmt.r" "$BIN"
