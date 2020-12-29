#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1


PIP_HOME='vars/requirements'
pip3 install --upgrade --target "$PIP_HOME" --requirement requirements.txt < /dev/null