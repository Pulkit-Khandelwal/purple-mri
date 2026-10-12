#!/usr/bin/env bash
set -euo pipefail
root="${1:-/opt/purple_pial}"
mkdir -p "$root/reports"
LD_LIBRARY_PATH="$root/lib" ldd "$root/bin/mris_place_surface" > "$root/reports/ldd.txt" 2>&1
if grep -q 'not found' "$root/reports/ldd.txt"; then
  cat "$root/reports/ldd.txt"
  exit 1
fi
# Reject a binary or collected library that requires a newer glibc than Focal.
: > "$root/reports/glibc-requirements.txt"
for elf in "$root/bin/mris_place_surface" "$root"/lib/*; do
  readelf --version-info "$elf" >> "$root/reports/glibc-requirements.txt"
done
required=$(grep -oE 'GLIBC_[0-9]+\.[0-9]+(\.[0-9]+)?' "$root/reports/glibc-requirements.txt" | sed 's/GLIBC_//' | sort -Vu | tail -1)
if [ -n "$required" ] && [ "$(printf '%s\n' "$required" 2.31 | sort -V | tail -1)" != 2.31 ]; then
  echo "ERROR: runtime requires GLIBC_$required (maximum allowed: 2.31)" >&2
  exit 1
fi
status=0
"$root/run-pial.sh" --help > "$root/reports/help.txt" 2>&1 || status=$?
# This FreeSurfer program normally returns 1 when printing help.
if [ "$status" -gt 1 ] || ! grep -q 'compialtion test by Pulkit Khandelwal' "$root/reports/help.txt"; then
  cat "$root/reports/help.txt"
  echo "ERROR: custom binary startup check failed (status $status)" >&2
  exit 1
fi
printf 'PASS: libraries resolved; GLIBC <= 2.31; custom help printed (exit %s).\n' "$status" | tee "$root/reports/smoke-test.txt"
printf '%s\n' 'Surface-placement equivalence has NOT been tested.' >> "$root/reports/smoke-test.txt"
