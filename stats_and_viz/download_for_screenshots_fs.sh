freesurfer_surface_processed=
mri_dir_mgz=
mri_dir_nifti=
redo_subjects_folder=
tgt_dir_FS_mesh_decimated=


to_save_dir=

subjects=()
echo ${subjects[@]}

hemis=rh
for subj in "${subjects[@]}"
do
echo ${subj}

mkdir -p ${to_save_dir}/${subj}
mkdir -p ${to_save_dir}/${subj}/surf
mkdir -p ${to_save_dir}/${subj}/label
mkdir -p ${to_save_dir}/${subj}/mri

cp -r ${freesurfer_surface_processed}/${subj}/surf/rh.pial ${to_save_dir}/${subj}/surf
cp -r ${freesurfer_surface_processed}/${subj}/surf/rh.curv ${to_save_dir}/${subj}/surf
cp -r ${freesurfer_surface_processed}/${subj}/surf/rh.sulc ${to_save_dir}/${subj}/surf
cp -r ${freesurfer_surface_processed}/${subj}/surf/rh.inflated ${to_save_dir}/${subj}/surf
cp -r ${freesurfer_surface_processed}/${subj}/surf/rh.smoothwm ${to_save_dir}/${subj}/surf
cp -r ${freesurfer_surface_processed}/${subj}/label/*.annot ${to_save_dir}/${subj}/label
cp -r ${freesurfer_surface_processed}/${subj}/mri/mri.mgz ${to_save_dir}/${subj}/mri
cp -r ${freesurfer_surface_processed}/${subj}/mri/aparc.DKTatlas+aseg.mgz ${to_save_dir}/${subj}/mri
cp -r ${freesurfer_surface_processed}/${subj}/mri/aseg.presurf.mgz ${to_save_dir}/${subj}/mri

done;