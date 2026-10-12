#!/usr/bin/env bash
set -eo pipefail
working_dir=$1
str_split=$2
generated_files_folder=$3
segm_path=$4
hemis=$5
read -r -a subjects <<< "$str_split"
for subj in "${subjects[@]}"; do
    base="${generated_files_folder}/${subj}_purple_corrected"
    # Keep the authoritative 10-label result intact. No repeated per-label CC cleanup.
    cp "${segm_path}/${subj}.nii.gz" "${base}.nii.gz"
    # Surface-only working copy: upstream convention treats WMH as WM.
    c3d "${base}.nii.gz" -replace 6 7 -o "${base}_surface_working.nii.gz"
    work="${base}_surface_working.nii.gz"
    # Retain the upstream RH-coded segmentation convention for excised hemispheres.
    c3d "$work" -replace 1 42 2 51 3 50 4 52 5 49 7 41 8 43 9 192 10 53 \
        -o "${base}_FS_labels.nii.gz"
    mri_convert "${base}_FS_labels.nii.gz" "${generated_files_folder}/${subj}_aseg.mgz"
    cp "${generated_files_folder}/${subj}_aseg.mgz" "${generated_files_folder}/${subj}_aseg.presurf.mgz"
    c3d "${base}_FS_labels.nii.gz" \
        -replace 0 100 42 142 50 150 51 151 52 152 49 149 41 241 43 143 53 153 \
        -o "${base}_FS_labels_presurf_100.nii.gz"
    mri_convert "${base}_FS_labels_presurf_100.nii.gz" "${generated_files_folder}/${subj}_aseg.presurf_100.mgz"
    # Only the derived tessellation mask keeps its largest combined component.
    c3d "$work" -replace 1 0 10 0 -binarize \
        -o "${base}_WM_mask.nii.gz"
    c3d "${base}_WM_mask.nii.gz" -comp -threshold 1 1 1 0 \
        -o "${base}_WM_mask_cc.nii.gz"
    mri_convert "${base}_WM_mask_cc.nii.gz" "${generated_files_folder}/${subj}_wm.mgz"
    cp "${generated_files_folder}/${subj}_wm.mgz" "${generated_files_folder}/${subj}_filled.mgz"
    c3d "$work" -replace 1 42 2 41 3 41 4 41 5 41 7 41 8 41 9 41 10 0 \
        -o "${base}_ribbon.nii.gz"
    c3d "$work" -threshold 1 1 1 0 -o "${base}_${hemis}.ribbon.nii.gz"
    mri_convert "${base}_${hemis}.ribbon.nii.gz" "${generated_files_folder}/${subj}_${hemis}.ribbon.mgz"
    mri_convert "${base}_ribbon.nii.gz" "${generated_files_folder}/${subj}.ribbon.mgz"
done
