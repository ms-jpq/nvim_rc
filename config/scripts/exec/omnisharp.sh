#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


LIB="$(dirname -- "$0")/../lib"
BIN="$LIB/omnisharp/OmniSharp"


if hash asdf 2> /dev/null
then
  export DOTNET_ROOT=
  DOTNET_ROOT="$(dirname -- "$(asdf which dotnet)")"
fi


exec -- "$BIN" "$@"
