#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s globstar failglob


LIB="$(dirname "$(dirname "$(realpath "$0")")")/lib/jdtls"
OS="$(uname | tr '[:upper:]' '[:lower:]')"

CANDIDATES=("$LIB/plugins/org.eclipse.equinox.launcher_"*'.jar')
export JAR="${CANDIDATES[0]}"
export WORKSPACE="${WORKSPACE:="$PWD"}"
# export GRADLE_HOME="$(which gradle | rg --color=never --passthru --replace '' -- '/bin/gradle$')"

ARGS=(
  -Declipse.application=org.eclipse.jdt.ls.core.id1
  -Dosgi.bundles.defaultStartLevel=4
  -Declipse.product=org.eclipse.jdt.ls.core.product
  -Dlog.protocol=true
  -Dlog.level=ALL
  -Xms1g
  -Xmx2G
  -jar
  "$JAR"
  -configuration
  "$LIB/config_$OS"
  -data
  "$WORKSPACE"
  --add-modules=ALL-SYSTEM
  --add-opens
  java.base/java.util=ALL-UNNAMED
  --add-opens
  java.base/java.lang=ALL-UNNAMED
  )


exec java "${ARGS[@]}"
