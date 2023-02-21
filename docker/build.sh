#!/usr/bin/env -S -- bash -Eeuo pipefail -O failglob -O globstar

cd -- "$(dirname -- "$0")/.." || exit 1

IMAGE='nvim'
docker build -f 'docker/Dockerfile' -t "$IMAGE" .
