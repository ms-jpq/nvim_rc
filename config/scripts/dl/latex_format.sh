#!/usr/bin/env -S bash

set -Eeu
set -o pipefail
shopt -s globstar failglob


if [[ ! -d "$LIB" ]]
then
  TMP="$(mktemp --directory)"
  get -- "$URI" | unpack --dest "$TMP"
  TMP_LIB="$(mktemp --tmpdir "$TMP" --directory)"
  mv -- "$TMP"/* "$TMP_LIB"

  PERL_LIB_DIR="$TMP_LIB/_perl_"
  PERL_LIBS=(
    YAML::Tiny
    File::HomeDir
    Unicode::GCString
  )

  cpanm --local-lib "$PERL_LIB_DIR" -- "${PERL_LIBS[@]}"

  rm --recursive --force -- "$LIB"
  mv -- "$TMP_LIB" "$LIB"
fi

cp -- "$(dirname -- "$0")/../exec/latexindent.sh" "$BIN"
