
freesurfer_surface_processed=
mri_dir_mgz=
mri_dir_nifti=
redo_subjects_folder=
tgt_dir_FS_mesh_decimated=

subjects=()
for filename in "${subjects[@]}"
do
  echo ${filename}
  hemis_check=${filename: -1}
  echo $hemis_check

  SUBJECTS_DIR=${freesurfer_surface_processed}/${filename}
: << C2
  mkdir -p ${SUBJECTS_DIR}

  mkdir -p ${SUBJECTS_DIR}/mri \
  ${SUBJECTS_DIR}/surf \
  ${SUBJECTS_DIR}/scripts \
  ${SUBJECTS_DIR}/label \
  ${SUBJECTS_DIR}/stats \
  ${SUBJECTS_DIR}/mri/transforms

  var=R
  if [ "$hemis_check" == "$var" ]; then
        echo "Right hemis"
        mri_convert ${mri_dir_nifti}/${filename}_reslice_0000.nii.gz ${mri_dir_mgz}/${filename}.mgz
    else
        echo "Left hemis"
        /data/pulkit/exvivo_reg_reconstruct/c3d-1.4.0-Linux-gcc64/bin/c3d ${mri_dir_nifti}/${filename}_reslice_0000.nii.gz -flip y ${mri_dir_nifti}/${filename}_reslice_0000_flipped.nii.gz
        mri_convert ${mri_dir_nifti}/${filename}_reslice_0000_flipped.nii.gz ${mri_dir_mgz}/${filename}.mgz
  fi
  
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/mri.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/brain.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/brainmask.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/brain.finalsurfs.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/rawavg.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/norm.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/nu.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/orig.mgz
  cp ${mri_dir_mgz}/${filename}.mgz ${SUBJECTS_DIR}/mri/T1.mgz
C2

  mri_convert ${redo_subjects_folder}/${filename}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc_holes.nii.gz ${SUBJECTS_DIR}/mri/filled.mgz
  mri_convert ${redo_subjects_folder}/${filename}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc_holes.nii.gz ${SUBJECTS_DIR}/mri/wm.mgz

  hemis=rh
  cp ${tgt_dir_FS_mesh_decimated}/${filename}.decimated.orig.nofix ${SUBJECTS_DIR}/surf/${hemis}.orig.nofix

  cp ${redo_subjects_folder}/${filename}_aseg.presurf.mgz ${SUBJECTS_DIR}/mri/aseg.presurf.mgz
  cp ${redo_subjects_folder}/${filename}_aseg.presurf_100.mgz ${SUBJECTS_DIR}/mri/aseg.presurf_100.mgz
  cp ${redo_subjects_folder}/${filename}_aseg.mgz ${SUBJECTS_DIR}/mri/aseg.mgz
  cp ${redo_subjects_folder}/${filename}_rh.ribbon.mgz ${SUBJECTS_DIR}/mri/${hemis}.ribbon.mgz
  cp ${redo_subjects_folder}/${filename}.ribbon.mgz ${SUBJECTS_DIR}/mri/ribbon.mgz

done;
