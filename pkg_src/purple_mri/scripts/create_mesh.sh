working_dir=$1
tgt_dir_FS_mesh=$2
tgt_dir_FS_mesh_decimated=$3
str_split=$4
for i in $str_split; do subjects+=($i) ; done

hemis=rh
for subj in "${subjects[@]}"
do
  echo ${subj}
  SUBJECTS_DIR=${working_dir}/${subj}
  
  mri_pretess ${SUBJECTS_DIR}/mri/filled.mgz 1 ${SUBJECTS_DIR}/mri/mri.mgz ${tgt_dir_FS_mesh}/${subj}_pretess.mgz
  mri_tessellate ${tgt_dir_FS_mesh}/${subj}_pretess.mgz 1 ${tgt_dir_FS_mesh}/${subj}.orig.nofix
  mris_convert ${tgt_dir_FS_mesh}/${subj}.orig.nofix ${tgt_dir_FS_mesh}/${subj}.orig.nofix.vtk

  # decimate the vtk file
  python3 -m purple_mri.scripts.decimate_mesh ${tgt_dir_FS_mesh} ${tgt_dir_FS_mesh_decimated} ${subj}.orig.nofix.vtk ${subj}.decimated.orig.nofix.vtk

  # convert back to FreeSurfer format and this will act as the input to the topology correction step
  mris_convert ${tgt_dir_FS_mesh_decimated}/${subj}.decimated.orig.nofix.vtk ${tgt_dir_FS_mesh_decimated}/${subj}.decimated.orig.nofix

  cp ${tgt_dir_FS_mesh_decimated}/${subj}.decimated.orig.nofix ${working_dir}/${subj}/surf/${hemis}.orig.nofix

done;
