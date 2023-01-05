#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


LIB="$(dirname -- "$0")/../lib"


export PERL5LIB="$LIB/_perl_/lib/perl5"
exec -- "$LIB/latexindent/latexindent.pl" "$@"
