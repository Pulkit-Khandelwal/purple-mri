#!/usr/bin/env bash
set -euo pipefail
pial_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Scope custom libraries to this process; do not change the standard FS environment.
export LD_LIBRARY_PATH="$pial_root/lib"
exec "$pial_root/bin/mris_place_surface" "$@"
