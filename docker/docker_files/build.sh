#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v docker >/dev/null || { echo 'Docker is required.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'Python 3 is required for input checks.' >&2; exit 1; }
python3 check_build_inputs.py
export DOCKER_BUILDKIT=1
export PIAL_IMAGE="${PIAL_IMAGE:-purple-pial:ubuntu20-test}"
bash pial/build.sh
docker build --platform linux/amd64 --progress=plain \
  --build-arg "PIAL_BASE_IMAGE=$PIAL_IMAGE" \
  -t "${IMAGE_TAG:-pulks/docker_purple_mri:v1.1.0}" .
