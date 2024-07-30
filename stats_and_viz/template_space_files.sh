freesurfer_surface_processed=
mri_dir_mgz=
mri_dir_nifti=
redo_subjects_folder=
tgt_dir_FS_mesh_decimated=
vtk_files_for_glm_dir=
fsaverage_files=

subjects=()
echo ${#subjects[@]}

###### subjects=(102374L 125814L 127761R)
hemis=rh
hemis_other=lh

SUBJECTS_DIR=${freesurfer_surface_processed}
for subj in "${subjects[@]}"
do
  echo ${subj}

  # mris_resample to resample pial and white onto the fsaverage space
  # warp the labels and other measurements to the fsaverage
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --label aparc.annot --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --label aparc.a2009s.annot --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.a2009s.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --label aparc.DKTatlas.annot --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.DKTatlas.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --label aparc.HCP-MMP1.glasser.annot --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.HCP-MMP1.glasser.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --label aparc.Schaefer2018_400Parcels_17Networks.annot --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.Schaefer2018_400Parcels_17Networks.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --label aparc.Schaefer2018_400Parcels_7Networks.annot --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.Schaefer2018_400Parcels_7Networks.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --label economo.annot --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.economo.mgh

  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --meas thickness --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.thickness.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --meas thickness --fwhm 5 --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.thickness_5mm.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --meas curv --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.curvature.mgh
  mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --meas area --out ${vtk_files_for_glm_dir}/${subj}/${hemis}.area.mgh

  # convert to vtk pial
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.a2009s.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.a2009s.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.DKTatlas.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.DKTatlas.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.HCP-MMP1.glasser.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.HCP-MMP1.glasser.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.Schaefer2018_400Parcels_17Networks.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.Schaefer2018_400Parcels_17Networks.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.Schaefer2018_400Parcels_7Networks.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.Schaefer2018_400Parcels_7Networks.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.economo.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.economo.pial.vtk

  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.thickness.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.thickness.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.thickness_5mm.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.thickness_5mm.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.curvature.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.curvature.pial.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.area.mgh ${fsaverage_files}/surf/${hemis}.pial ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.area.pial.vtk

done;