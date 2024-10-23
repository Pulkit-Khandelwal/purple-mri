working_dir=$1
str_split=$2
generated_files_folder=$3
segm_path=$4
for i in $str_split; do subjects+=($i) ; done

for subj in "${subjects[@]}"
do
    echo ${subj}

    cp ${segm_path}/${subj}.nii.gz ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz

    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -replace 6 7 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz

    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -replace 1 42 2 50 3 51 4 52 5 49 7 41 8 43 9 0 10 53 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels.nii.gz

    mri_convert ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels.nii.gz ${generated_files_folder}/${subj}_aseg.mgz
    cp ${generated_files_folder}/${subj}_aseg.mgz ${generated_files_folder}/${subj}_aseg.presurf.mgz

    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels.nii.gz -replace 0 100 42 142 50 150 51 151 52 152 49 149 41 241 43 143 53 153 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels_presurf_100.nii.gz
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels_presurf_100.nii.gz -dup -lstat
    mri_convert ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels_presurf_100.nii.gz ${generated_files_folder}/${subj}_aseg.presurf_100.mgz

    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 2 3 4 5 7 9 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz -replace 2 1 3 1 4 1 5 1 7 1 9 1 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz
        
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz -comp -threshold 1 1 1 0 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc.nii.gz

    mri_convert ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc.nii.gz ${generated_files_folder}/${subj}_wm.mgz
    cp ${generated_files_folder}/${subj}_wm.mgz ${generated_files_folder}/${subj}_filled.mgz

    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -replace 1 42 2 41 3 41 4 41 5 41 7 41 8 41 9 41 10 0 -o ${generated_files_folder}/${subj}_ribbon.nii.gz
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 1 -o ${generated_files_folder}/${subj}_rh.ribbon.nii.gz

    mri_convert ${generated_files_folder}/${subj}_rh.ribbon.nii.gz ${generated_files_folder}/${subj}_rh.ribbon.mgz
    mri_convert ${generated_files_folder}/${subj}_ribbon.nii.gz ${generated_files_folder}/${subj}.ribbon.mgz
done;