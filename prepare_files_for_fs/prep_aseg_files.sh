wm_orig_save_path=/wm_orig
gm_cruise_retained_overlap=/gm_cruise_retained_overlap
redo_subjects_folder=

subjects=()
for subj in "${subjects[@]}"
do
  echo ${subj}
  hemis_check=${subj: -1}
  echo $hemis_check

  var=R
  if [ "$hemis_check" == "$var" ]; then
        echo "Right hemis"
        hemis=rh
        cp ${wm_orig_save_path}/${subj}_reslice_wm_orig.nii.gz ${redo_subjects_folder}/${subj}_reslice_wm_orig.nii.gz
        cp ${gm_cruise_retained_overlap}/${subj}_reslice_gm_cortex_cruise_retained_overlap.nii.gz ${redo_subjects_folder}/${subj}_reslice_gm_cortex_cruise_retained_overlap.nii.gz      
    else
        echo "Left hemis"
        hemis=lh
        c3d ${wm_orig_save_path}/${subj}_reslice_wm_orig.nii.gz -flip y ${redo_subjects_folder}/${subj}_reslice_wm_orig.nii.gz
        c3d ${gm_cruise_retained_overlap}/${subj}_reslice_gm_cortex_cruise_retained_overlap.nii.gz -flip y ${redo_subjects_folder}/${subj}_reslice_gm_cortex_cruise_retained_overlap.nii.gz
  fi  

        c3d ${redo_subjects_folder}/${subj}_reslice_wm_orig.nii.gz ${redo_subjects_folder}/${subj}_reslice_gm_cortex_cruise_retained_overlap.nii.gz -add -o ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz
        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -dup -lstat

        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 1 2 3 4 5 7 8 -o ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz
        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -dup -lstat

        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -replace 1 42 2 50 3 51 4 52 5 49 7 41 8 43 -o ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels.nii.gz

        mri_convert ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels.nii.gz ${redo_subjects_folder}/${subj}_aseg.mgz
        cp ${redo_subjects_folder}/${subj}_aseg.mgz ${redo_subjects_folder}/${subj}_aseg.presurf.mgz

        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels.nii.gz -replace 0 100 42 142 50 150 51 151 52 152 49 149 41 241 43 143 -o ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels_presurf_100.nii.gz
        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels_presurf_100.nii.gz -dup -lstat
        mri_convert ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_RH_FS_labels_presurf_100.nii.gz ${redo_subjects_folder}/${subj}_aseg.presurf_100.mgz

        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 2 3 4 5 7 8 -o ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz
        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz -replace 2 1 3 1 4 1 5 1 7 1 8 1 -o ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz
        mri_convert ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz ${redo_subjects_folder}/${subj}_wm.mgz
        cp ${redo_subjects_folder}/${subj}_wm.mgz ${redo_subjects_folder}/${subj}_filled.mgz

        c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -replace 1 42 2 41 3 41 4 41 5 41 7 41 8 41 -o ${redo_subjects_folder}/${subj}_ribbon.nii.gz
        c3d ${redo_subjects_folder}/${subj}_ribbon.nii.gz -replace 42 1 41 0 -o ${redo_subjects_folder}/${subj}_rh.ribbon.nii.gz

        mri_convert ${redo_subjects_folder}/${subj}_rh.ribbon.nii.gz ${redo_subjects_folder}/${subj}_rh.ribbon.mgz
        mri_convert ${redo_subjects_folder}/${subj}_ribbon.nii.gz ${redo_subjects_folder}/${subj}.ribbon.mgz
done;