#!/usr/bin/env bash
set -eo pipefail
[[ $# == 7 ]] || { echo "Usage: $0 FS_HOME OUTPUT MRI SEGMENTATIONS ATLASES THREADS STATS_FILE (legacy RH-only)" >&2; exit 2; }
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Legacy helpers split subject lists and use unquoted path expansions.
for value in "$@"; do
  [[ "$value" != *[^a-zA-Z0-9_./-]* ]] || { echo "Legacy arguments must not contain whitespace or shell metacharacters" >&2; exit 2; }
done
[[ "$6" =~ ^[1-9][0-9]*$ ]] || { echo "THREADS must be positive" >&2; exit 2; }
echo "WARNING: running legacy RH-only native surface workflow" >&2
# read the mri files and create a list of the subjects
freesurfer_path=$1
working_dir=$2
mri_path=$3
segm_path=$4
external_atlases_path=$5
num_threads=$6
autodet_stats_dat=$7

subjects=()
shopt -s nullglob
for file in "${mri_path}"/*.nii.gz
do
   fname=$(basename "$file" .nii.gz)
   [[ "$fname" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]] || { echo "Unsafe subject filename" >&2; exit 2; }
   [[ -s "${segm_path}/${fname}.nii.gz" ]] || { echo "Missing segmentation for $fname" >&2; exit 2; }
   subjects+=("${fname}")
done
((${#subjects[@]})) || { echo "No MRI files" >&2; exit 2; }
[[ -s "$autodet_stats_dat" ]] || { echo "Missing statistics file" >&2; exit 2; }

echo "Here are the list of subjects to be processed: " ${subjects[@]}

##### STEP 1: Prepare files from the initial 10-label deep learning based-segmentation
generated_files_folder=${working_dir}/files_prepared_for_pipeline
mkdir -p ${generated_files_folder}
bash "$SCRIPT_DIR/prepare_segm_files.sh" "${working_dir}" "${subjects[*]}" "${generated_files_folder}" "${segm_path}"

##### STEP 2: Create FreeSurfer-like files
bash "$SCRIPT_DIR/make_fs_directories.sh" "${working_dir}" "${generated_files_folder}" "${mri_path}" "${subjects[*]}"

##### STEP 3: Create mesh and downsample the same
tgt_dir_FS_mesh=${working_dir}/freesurfer_high_res_mesh
tgt_dir_FS_mesh_decimated=${working_dir}/decimated_mesh
mkdir -p ${tgt_dir_FS_mesh}
mkdir -p ${tgt_dir_FS_mesh_decimated}

# this file calls the Python script: decimate_mesh.py
bash "$SCRIPT_DIR/create_mesh.sh" "${working_dir}" "${tgt_dir_FS_mesh}" "${tgt_dir_FS_mesh_decimated}" "${subjects[*]}"

##### STEP 4: Perform some intial regsitration to get all the required orientations
bash "$SCRIPT_DIR/do_mni_txs.sh" "${freesurfer_path}" "${working_dir}" "${subjects[*]}"

##### STEP 5: Perform surface-based topology correction
bash "$SCRIPT_DIR/topology_correction.sh" "${working_dir}" "${subjects[*]}"

##### STEP 6: Perform surface-based parcellation
bash "$SCRIPT_DIR/parcellation.sh" "${working_dir}" "${subjects[*]}" "${freesurfer_path}" "${num_threads}" "${external_atlases_path}" "${autodet_stats_dat}"
