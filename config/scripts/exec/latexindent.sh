#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


LIB="$(dirname -- "$(dirname -- "$(realpath -- "$0")")")/lib"


export PERL5LIB="$LIB/_perl_/lib/perl5"
exec "$LIB/latexindent/latexindent.pl" "$@"
