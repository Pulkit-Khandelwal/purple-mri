freesurfer_surface_processed=
mri_dir_mgz=
mri_dir_nifti=
redo_subjects_folder=
tgt_dir_FS_mesh_decimated=

subjects=()
for subj in "${subjects[@]}"
do

  echo ${subj}
  SUBJECTS_DIR=${freesurfer_surface_processed}/${subj}
  
  mri_convert ${SUBJECTS_DIR}/mri/rawavg.mgz ${SUBJECTS_DIR}/mri/orig_conform.mgz --conform
  
  tkregister2 --mov ${SUBJECTS_DIR}/mri/rawavg.mgz --targ ${SUBJECTS_DIR}/mri/orig_conform.mgz \
  --reg ${SUBJECTS_DIR}/mri/transforms/register.native.dat --regheader-center \
  --noedit --ltaout ${SUBJECTS_DIR}/mri/transforms/init_for_mris_register.lta
  
  mri_add_xform_to_header -c ${SUBJECTS_DIR}/mri/transforms/talairach.xfm ${SUBJECTS_DIR}/mri/orig_conform.mgz ${SUBJECTS_DIR}/mri/orig_conform.mgz
  
  mri_info ${SUBJECTS_DIR}/mri/orig_conform.mgz
  
  /path/to/fs_installation/freesurfer/bin/talairach_avi --i ${SUBJECTS_DIR}/mri/orig_conform.mgz --xfm ${SUBJECTS_DIR}/mri/transforms/talairach.auto.xfm
  
  cp ${SUBJECTS_DIR}/mri/transforms/talairach.auto.xfm ${SUBJECTS_DIR}/mri/transforms/talairach.xfm
  
  lta_convert --src ${SUBJECTS_DIR}/mri/orig_conform.mgz --trg /data/pulkit/exvivo_reg_reconstruct/freesurfer_installation/freesurfer/average/mni305.cor.mgz \
  --inxfm ${SUBJECTS_DIR}/mri/transforms/talairach.xfm --outlta ${SUBJECTS_DIR}/mri/transforms/talairach.xfm.lta --subject fsaverage --ltavox2vox
  
  mri_add_xform_to_header -c ${SUBJECTS_DIR}/mri/transforms/talairach.xfm ${SUBJECTS_DIR}/mri/orig_conform.mgz ${SUBJECTS_DIR}/mri/orig_conform.mgz

done;
