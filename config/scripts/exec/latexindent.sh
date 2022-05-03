#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


LIB="$(dirname "$(dirname "$(realpath "$0")")")/lib"


export PERL5LIB="$LIB/perllibs/lib/perl5"
exec "$LIB/latexindent/latexindent.pl" "$@"
