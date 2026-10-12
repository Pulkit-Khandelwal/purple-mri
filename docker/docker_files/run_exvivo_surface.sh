#!/usr/bin/env bash
set -eo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="${EXVIVO_INPUT_DIR:-/data/exvivo/data_for_inference}"
DL_DIR="${EXVIVO_DL_OUTPUT_DIR:-${EXVIVO_ALL_OUTPUT_DIR:-$INPUT_DIR/output_from_nnunet_inference/exvivo_dl}}"
SEGM_DIR="${EXVIVO_SEGM_DIR:-$DL_DIR/05_purple_corrected}"
WORK_DIR="${EXVIVO_SURFACE_OUTPUT_DIR:-$INPUT_DIR/output_from_nnunet_inference/exvivo_surface}"
HEMI="${EXVIVO_HEMI:-}"
THREADS="${EXVIVO_THREADS:-8}"
export FREESURFER_HOME="${FREESURFER_HOME:-/opt/freesurfer}"
export FS_LICENSE="${FS_LICENSE:-/opt/freesurfer/license.txt}"
fail() { echo "Surface setup: $*" >&2; exit 2; }
[[ "$HEMI" == rh || "$HEMI" == lh ]] || fail 'set EXVIVO_HEMI=rh or EXVIVO_HEMI=lh (one hemisphere per batch).'
[[ "$THREADS" =~ ^[1-9][0-9]*$ ]] || fail 'EXVIVO_THREADS must be a positive integer.'
[[ -s "$FS_LICENSE" ]] || fail "mount your FreeSurfer license at $FS_LICENSE, or set FS_LICENSE."
[[ -d "$INPUT_DIR" ]] || fail "MRI input directory does not exist: $INPUT_DIR"
# Legacy surface commands split subject lists on spaces; reject ambiguous paths early.
for path in "$INPUT_DIR" "$SEGM_DIR" "$WORK_DIR" "$FREESURFER_HOME"; do
  [[ "$path" == /* && "$path" != *[[:space:]]* ]] || fail "use absolute paths without whitespace: $path"
done
[[ -f "$FREESURFER_HOME/SetUpFreeSurfer.sh" ]] || fail 'FreeSurfer installation missing.'
export NO_FSFAST=1
source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
export PATH="/opt/c3d/bin:$PATH"
export SUBJECTS_DIR="$WORK_DIR" EXVIVO_THREADS="$THREADS" OMP_NUM_THREADS="$THREADS" ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS="$THREADS"
for tool in c3d mri_convert mri_tessellate mris_fix_topology mris_place_surface mri_surf2volseg; do
  command -v "$tool" >/dev/null || fail "missing program: $tool"
done
[[ -x /opt/purple_pial/run-pial.sh ]] || fail 'custom pial bundle missing.'
[[ -f /opt/purple-mri/purple_mri/autodet.gw.stats.binary.dat ]] || fail 'statistics file missing.'
[[ -f "$FREESURFER_HOME/subjects/fsaverage/surf/$HEMI.sphere.reg" ]] || fail 'fsaverage missing.'
if [[ -e "$WORK_DIR" ]]; then
  [[ -d "$WORK_DIR" && -z "$(ls -A "$WORK_DIR")" ]] || fail "output is not empty: $WORK_DIR; choose a new EXVIVO_SURFACE_OUTPUT_DIR."
fi
[[ "${1:-}" != --preflight ]] || exit 0
export EXVIVO_TIMING_DIR="${EXVIVO_TIMING_DIR:-${WORK_DIR}_timings}"
source "$SCRIPT_DIR/exvivo_timing.sh"
surface_started=$(date +%s)
surface_started_utc=$(timing_utc)
surface_finish() {
  local rc=$?
  trap - EXIT
  timing_total surface "$surface_started" "$surface_started_utc" "$rc"
}
trap surface_finish EXIT
timed_step surface setup01 "Validate and copy input volumes" /surface_env/bin/python "$SCRIPT_DIR/surface_inputs.py" "$INPUT_DIR" "$SEGM_DIR" "$WORK_DIR" "$HEMI"
# Real copies in the mounted output: no container-only links.
timed_step surface setup02 "Copy FreeSurfer fsaverage" cp -a "$FREESURFER_HOME/subjects/fsaverage" "$WORK_DIR/fsaverage"
timed_step surface setup03 "Copy repository fsaverage surfaces" cp -a /opt/purple-mri/fsaverage/. "$WORK_DIR/fsaverage/"
cp /opt/purple-mri/purple_mri/autodet.gw.stats.binary.dat "$WORK_DIR/autodet.gw.stats.binary.dat"
printf '%s\n' "$HEMI" > "$WORK_DIR/hemisphere.txt"
cp /opt/purple-mri/SOURCE_REVISION "$WORK_DIR/source_revision.txt"
start=$(date +%s)
{
  date -Is
  echo "Hemisphere: $HEMI; threads: $THREADS"
  echo "Corrected segmentation: $SEGM_DIR"
  bash /opt/purple-mri/purple_mri/run_surface_pipeline.sh \
    "$FREESURFER_HOME" "$WORK_DIR" "$WORK_DIR/inputs/mri" "$WORK_DIR/inputs/segmentation" \
    /opt/purple-mri/freesurfer_atlases "$THREADS" "$HEMI"
  echo "Elapsed seconds: $(( $(date +%s) - start ))"
  date -Is
} 2>&1 | tee "$WORK_DIR/surface_pipeline.log"
printf 'Complete\n' > "$WORK_DIR/COMPLETE"
echo "Surface outputs: $WORK_DIR"
