SUBJECTS_DIR=
vtk_files_for_glm_dir=
fsaverage_files=

subjects=()
hemis=rh
hemis_other=lh
surface_type=pial # or inflated

for subj in "${subjects[@]}"
do
  echo ${subj}

  # resample native subject-space surfaces onto the fsaverage space
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

  # convert to vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.a2009s.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.a2009s.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.DKTatlas.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.DKTatlas.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.HCP-MMP1.glasser.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.HCP-MMP1.glasser.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.Schaefer2018_400Parcels_17Networks.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.Schaefer2018_400Parcels_17Networks.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.aparc.Schaefer2018_400Parcels_7Networks.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.aparc.Schaefer2018_400Parcels_7Networks.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.economo.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.economo.${surface_type}.vtk

  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.thickness.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.thickness.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.thickness_5mm.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.thickness_5mm.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.curvature.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.curvature.${surface_type}.vtk
  mris_convert -c ${vtk_files_for_glm_dir}/${subj}/${hemis}.area.mgh ${fsaverage_files}/surf/${hemis}.${surface_type} ${vtk_files_for_glm_dir}/vtk_files/${subj}.${hemis}.area.${surface_type}.vtk

done;
