#!/usr/bin/env -S -- bash -Eeuo pipefail -O dotglob -O failglob -O globstar

cd -- "$(dirname -- "$0")/.." 

IMAGE='nvim'
docker build -f 'docker/Dockerfile' -t "$IMAGE" .
