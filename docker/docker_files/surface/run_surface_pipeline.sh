#!/usr/bin/env bash
set -eo pipefail
source /src/exvivo_timing.sh
freesurfer_path=$1
working_dir=$2
mri_path=$3
segm_path=$4
external_atlases_path=$5
num_threads=$6
hemis=$7
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export SUBJECTS_DIR="$working_dir" EXVIVO_THREADS="$num_threads"
shopt -s nullglob
subjects=()
for file in "$mri_path"/*.nii.gz; do subjects+=("$(basename "$file" .nii.gz)"); done
((${#subjects[@]})) || { echo "No MRI files" >&2; exit 1; }
generated_files_folder="$working_dir/files_prepared_for_pipeline"
tgt_dir_FS_mesh="$working_dir/freesurfer_high_res_mesh"
tgt_dir_FS_mesh_decimated="$working_dir/decimated_mesh"
mkdir -p "$generated_files_folder" "$tgt_dir_FS_mesh" "$tgt_dir_FS_mesh_decimated"
echo "[surface 1/6] Prepare segmentation volumes"
timed_step surface 01 "Prepare segmentation volumes" bash "$SCRIPT_DIR/prepare_segm_files.sh" "$working_dir" "${subjects[*]}" "$generated_files_folder" "$segm_path" "$hemis"
echo "[surface 2/6] Prepare FreeSurfer subjects"
timed_step surface 02 "Prepare FreeSurfer subjects" bash "$SCRIPT_DIR/make_fs_directories.sh" "$working_dir" "$generated_files_folder" "$mri_path" "$hemis" "${subjects[*]}"
echo "[surface 3/6] Tessellate and decimate"
timed_step surface 03 "Tessellate and decimate" bash "$SCRIPT_DIR/create_mesh.sh" "$working_dir" "$tgt_dir_FS_mesh" "$tgt_dir_FS_mesh_decimated" "$hemis" "${subjects[*]}"
echo "[surface 4/6] Estimate transforms"
timed_step surface 04 "Estimate transforms" bash "$SCRIPT_DIR/do_mni_txs.sh" "$freesurfer_path" "$working_dir" "${subjects[*]}"
echo "[surface 5/6] Correct surface topology"
timed_step surface 05 "Correct surface topology" bash "$SCRIPT_DIR/topology_correction.sh" "$working_dir" "$hemis" "${subjects[*]}"
echo "[surface 6/6] Place surfaces, parcellate, and compute metrics"
timed_step surface 06 "Place surfaces, parcellate and compute metrics" bash "$SCRIPT_DIR/parcellation.sh" "$working_dir" "${subjects[*]}" "$freesurfer_path" "$num_threads" "$external_atlases_path" "$hemis"
