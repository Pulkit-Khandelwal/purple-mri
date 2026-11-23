#!/usr/bin/env bash
# Entry point for pancake preparation and local thickness measurements.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
case "${1:---help}" in
  prepare)
    shift
    exec "${PYTHON:-python3}" "${script_dir}/prepare_pancakes.py" "$@"
    ;;
  -h|--help)
    cat <<'HELP'
Usage: bash runme.sh COMMAND [arguments]

  prepare       Create local pancakes from an automated segmentation
  dot           Measure one labeled location
  subj          Measure selected or all locations in one specimen
  batch         Measure specimens listed in a TSV
  stats_table   Export existing measurements as CSV
  check         Check executable paths and permissions

For command options: bash runme.sh COMMAND --help
HELP
    ;;
  *) exec "${PYTHON:-python3}" "${script_dir}/thickness.py" "$@" ;;
esac
