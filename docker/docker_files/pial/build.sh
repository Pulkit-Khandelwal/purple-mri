#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v docker >/dev/null || { echo 'Docker is required.' >&2; exit 1; }
image="${PIAL_IMAGE:-purple-pial:ubuntu20-test}"
export DOCKER_BUILDKIT=1
docker build --platform linux/amd64 --progress=plain \
  --build-arg "BUILD_JOBS=${BUILD_JOBS:-4}" -t "$image" .
printf '\nBuilt %s; startup checks passed during the image build.\n' "$image"
