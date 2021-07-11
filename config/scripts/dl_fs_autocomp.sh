#!/usr/bin/env bash

set -eu
set -o pipefail


mkdir --parents -- "$LIB"
cd "$LIB" || exit 1
dotnet new tool-manifest --force
dotnet tool install fsautocomplete
dotnet tool update fsautocomplete
