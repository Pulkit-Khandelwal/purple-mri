#!/usr/bin/env bash
set -eo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="${EXVIVO_INPUT_DIR:-/data/exvivo/data_for_inference}"
DL_OUTPUT_WAS_SET="${EXVIVO_DL_OUTPUT_DIR+x}"
OUT_DIR="${EXVIVO_DL_OUTPUT_DIR:-${EXVIVO_ALL_OUTPUT_DIR:-${INPUT_DIR}/output_from_nnunet_inference/exvivo_dl}}"
export EXVIVO_INPUT_DIR="$INPUT_DIR" EXVIVO_DL_OUTPUT_DIR="$OUT_DIR"
usage() {
  cat <<'HELP'
Usage: bash /src/commands_nnunet_inference.sh STAGE [STAGE]
  exvivo_dl                         All adult DL models and merge
  exvivo_surface                    Adult surface reconstruction and atlases
  exvivo_dl exvivo_surface           DL, then surfaces from 05_purple_corrected
  exvivo_dl_infant                   Placeholder (not implemented)
  exvivo_surface_infant              Placeholder (not implemented)
  exvivo_all                         Backward-compatible alias for exvivo_dl
All existing individual model options remain available.
For surface stages set EXVIVO_HEMI=rh or lh, EXVIVO_THREADS=8, and mount FS_LICENSE.
HELP
}
(($#)) || { usage; exit 2; }
[[ "$1" != --help && "$1" != -h ]] || { usage; exit 0; }
stages=("$@")
# Validate the entire request before starting costly work.
for stage in "${stages[@]}"; do
  case "$stage" in
    exvivo_dl_infant|exvivo_surface_infant)
      echo "Infant pipeline not implemented yet: $stage" >&2; exit 2 ;;
    exvivo_dl|exvivo_all|exvivo_surface|exvivo_t2w|invivo_flair_wmh|exvivo_flash_thalamus|exvivo_posthoc_topology|exvivo_umc_strip_cerebellum|exvivo_multi_sequence_mtl_amygdala_subfields|exvivo_multi_sequence_subcortical|exvivo_flash_more_subcort) ;;
    *) echo "Unknown option: $stage" >&2; usage; exit 2 ;;
  esac
done
if ((${#stages[@]} > 1)); then
  [[ ${#stages[@]} == 2 && ( "${stages[0]}" == exvivo_dl || "${stages[0]}" == exvivo_all ) && "${stages[1]}" == exvivo_surface ]] || {
    echo "Supported sequence: exvivo_dl exvivo_surface" >&2; exit 2;
  }
fi
# Preserve the old output default for callers still using exvivo_all.
if [[ "${stages[0]}" == exvivo_all && -z "$DL_OUTPUT_WAS_SET" && -z "${EXVIVO_ALL_OUTPUT_DIR:-}" && "$OUT_DIR" == "$INPUT_DIR/output_from_nnunet_inference/exvivo_dl" ]]; then
  OUT_DIR="$INPUT_DIR/output_from_nnunet_inference/exvivo_all"
  export EXVIVO_DL_OUTPUT_DIR="$OUT_DIR"
fi
for stage in "${stages[@]}"; do
  if [[ "$stage" == exvivo_surface ]]; then
    bash "$SCRIPT_DIR/run_exvivo_surface.sh" --preflight
  fi
done
export EXVIVO_TIMING_DIR="${EXVIVO_TIMING_DIR:-$INPUT_DIR/output_from_nnunet_inference/timings_$(date -u +%Y%m%dT%H%M%SZ)_$$}"
source "$SCRIPT_DIR/exvivo_timing.sh"
overall_started=$(date +%s)
overall_started_utc=$(timing_utc)
dl_active=0
launcher_finish() {
  local rc=$?
  trap - EXIT
  if [[ "$dl_active" == 1 ]]; then
    timing_total dl "$dl_started" "$dl_started_utc" "$rc"
  fi
  timing_total overall "$overall_started" "$overall_started_utc" "$rc"
}
trap launcher_finish EXIT
activate_dl() {
  source /ml/bin/activate
  export nnUNet_preprocessed="/src/nnunet_paths_that_it_requires"
  export RESULTS_FOLDER="/src/nnunet_paths_that_it_requires"
  export nnUNet_raw_data_base="/src/nnunet_paths_that_it_requires"
  command -v nnUNet_predict >/dev/null
}
predict() {
  nnUNet_predict -i "$2" -o "$3" -t "$1" -tr "${4:-nnUNetTrainerV2}" \
    -m 3d_fullres --disable_mixed_precision -f all
}
helper() {
  python "$SCRIPT_DIR/merge_exvivo.py" "$1" --input-dir "$INPUT_DIR" --output-dir "$OUT_DIR"
}
for stage in "${stages[@]}"; do
  if [[ "$stage" == exvivo_surface ]]; then
    bash "$SCRIPT_DIR/run_exvivo_surface.sh"
    continue
  fi
  activate_dl
  if [[ "$stage" == exvivo_dl || "$stage" == exvivo_all ]]; then
    dl_started=$(date +%s)
    dl_started_utc=$(timing_utc)
    dl_active=1
    timed_step dl setup "Initialize DL output" helper init
    echo "[1/8] Original Purple 10-label segmentation"
    timed_step dl 01 "Original Purple 10-label segmentation" predict 283 "$INPUT_DIR" "$OUT_DIR/01_purple_original"
    echo "[2/8] Component cleanup"
    timed_step dl 02 "Component cleanup" helper clean-components
    echo "[3/8] Prepare topology input"
    timed_step dl 03 "Prepare topology input" helper prepare-topology
    echo "[4/8] Post-hoc topology prediction"
    timed_step dl 04 "Topology prediction" predict 279 "$OUT_DIR/02_topology_input" "$OUT_DIR/03_topology_prediction"
    echo "[5/8] Save buried sulcus mask and corrected Purple segmentation"
    timed_step dl 05 "Apply buried-sulcus removal" helper apply-topology
    echo "[6/8] MTL and amygdala subfields"
    timed_step dl 06 "MTL and amygdala subfields" predict 269 "$INPUT_DIR" "$OUT_DIR/06_mtl"
    echo "[7/8] Subcortical structures"
    timed_step dl 07 "Subcortical structures" predict 2732 "$INPUT_DIR" "$OUT_DIR/07_subcortical"
    echo "[8/8] Merge and clean residual labels"
    timed_step dl 08 "Merge and clean residual labels" helper merge
    timing_total dl "$dl_started" "$dl_started_utc" 0
    dl_active=0
    echo "All intermediate NIfTI files: $OUT_DIR"
    echo "Corrected Purple: $OUT_DIR/05_purple_corrected"
    echo "Final merged segmentation: $OUT_DIR/11_final_merged"
  else
    trainer=nnUNetTrainerV2
    case "$stage" in
      exvivo_t2w) task=283 ;;
      invivo_flair_wmh) task=451; trainer=nnUNetTrainerWMHV2 ;;
      exvivo_flash_thalamus) task=276 ;;
      exvivo_posthoc_topology) task=279 ;;
      exvivo_umc_strip_cerebellum) task=101 ;;
      exvivo_multi_sequence_mtl_amygdala_subfields) task=269 ;;
      exvivo_multi_sequence_subcortical) task=2732 ;;
      exvivo_flash_more_subcort) task=289 ;;
    esac
    predict "$task" "$INPUT_DIR" "${EXVIVO_MODEL_OUTPUT_DIR:-$INPUT_DIR/output_from_nnunet_inference}" "$trainer"
  fi
done
