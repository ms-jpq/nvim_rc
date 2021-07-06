#!/usr/bin/env bash

set -eu
set -o pipefail


LATEST="$(< "$(get -- "$URI")")"
get -- "$PREFIX/$LATEST" | unpack -

