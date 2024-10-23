working_dir=$1
generated_files_folder=$2
mri_dir=$3
str_split=$4
for i in $str_split; do subjects+=($i) ; done

hemis=rh
for subj in "${subjects[@]}"
do
  echo ${subj}

  SUBJECTS_DIR=${working_dir}/${subj}
  mkdir -p ${SUBJECTS_DIR}

  mkdir -p ${SUBJECTS_DIR}/mri \
  ${SUBJECTS_DIR}/surf \
  ${SUBJECTS_DIR}/scripts \
  ${SUBJECTS_DIR}/label \
  ${SUBJECTS_DIR}/stats \
  ${SUBJECTS_DIR}/mri/transforms

  mri_convert ${mri_dir}/${subj}.nii.gz ${SUBJECTS_DIR}/mri/${subj}.mgz

  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/mri.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/brain.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/brainmask.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/brain.finalsurfs.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/rawavg.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/norm.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/nu.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/orig.mgz
  cp ${SUBJECTS_DIR}/mri/${subj}.mgz ${SUBJECTS_DIR}/mri/T1.mgz

  cp ${generated_files_folder}/${subj}_filled.mgz ${SUBJECTS_DIR}/mri/filled.mgz
  cp ${generated_files_folder}/${subj}_wm.mgz ${SUBJECTS_DIR}/mri/wm.mgz
  
  cp ${generated_files_folder}/${subj}_aseg.presurf.mgz ${SUBJECTS_DIR}/mri/aseg.presurf.mgz
  cp ${generated_files_folder}/${subj}_aseg.presurf_100.mgz ${SUBJECTS_DIR}/mri/aseg.presurf_100.mgz
  cp ${generated_files_folder}/${subj}_aseg.mgz ${SUBJECTS_DIR}/mri/aseg.mgz
  cp ${generated_files_folder}/${subj}_rh.ribbon.mgz ${SUBJECTS_DIR}/mri/${hemis}.ribbon.mgz
  cp ${generated_files_folder}/${subj}.ribbon.mgz ${SUBJECTS_DIR}/mri/ribbon.mgz

done;
