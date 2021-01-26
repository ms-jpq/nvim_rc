#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname $0)" || exit 1


_RUN_TIME="$PWD/.vars/runtime"
_ACTIVATE="$_RUN_TIME/bin/activate"

if [[ -f "$_ACTIVATE" ]]
then
  source "$_ACTIVATE"
else
  python3 -m venv -- "$_RUN_TIME"
  exec "$0" "$@"
fi


exec python3 -m python "$@"