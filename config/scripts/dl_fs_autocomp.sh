#!/usr/bin/env bash

set -eu
set -o pipefail


get -- "$URI" | unpack - --dest "$LIB"
