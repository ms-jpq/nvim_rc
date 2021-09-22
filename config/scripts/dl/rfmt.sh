#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


cp -- "../exec/rfmt.r" "$BIN"
