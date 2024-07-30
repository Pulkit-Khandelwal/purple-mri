wm_orig_save_path=
gm_cruise_retained_overlap=
redo_subjects_folder=

for subj in "${subjectsubjectss[@]}"
do
  echo ${subj}
  hemis_check=${subj: -1}
  echo $hemis_check
  
  c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz -comp -threshold 1 1 1 0 -o ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc.nii.gz

  c3d ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc.nii.gz -holefill 10 1 ${redo_subjects_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc_holes.nii.gz
done;