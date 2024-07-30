
freesurfer_surface_processed=
tgt_dir_FS_mesh=
tgt_dir_FS_mesh_decimated=

for subj in "${subjects_miccai[@]}"
do
  echo ${subj}
  SUBJECTS_DIR=${freesurfer_surface_processed}/${subj}

  mri_pretess ${SUBJECTS_DIR}/mri/filled.mgz 1 ${SUBJECTS_DIR}/mri/mri.mgz ${tgt_dir_FS_mesh}/${subj}_pretess.mgz
  mri_tessellate ${tgt_dir_FS_mesh}/${subj}_pretess.mgz 1 ${tgt_dir_FS_mesh}/${subj}.orig.nofix
  mris_convert ${tgt_dir_FS_mesh}/${subj}.orig.nofix ${tgt_dir_FS_mesh}/${subj}.orig.nofix.vtk

  # decimate the vtk file
  python3 decimate_mesh.py ${subj}.orig.nofix.vtk ${subj}.decimated.orig.nofix.vtk

  #convert back to FreeSurfer format and this will act as the input to the topology correction step
  mris_convert ${tgt_dir_FS_mesh_decimated}/${subj}.decimated.orig.nofix.vtk ${tgt_dir_FS_mesh_decimated}/${subj}.decimated.orig.nofix

done;
