freesurfer_surface_processed=
roi_analysis_files=

subjects=()
echo ${subjects[@]}

hemis=rh
SUBJECTS_DIR=${freesurfer_surface_processed}
for subj in "${subjects[@]}"
do
  echo ${subj}

  asegstats2table --subjects ${subj} --common-segs --meas volume --stats=aseg.stats --table=${roi_analysis_files}/${subj}_segstats.txt
  aparcstats2table --subjects ${subj} --hemi ${hemis} --meas thickness --parc=aparc --tablefile=${roi_analysis_files}/${subj}_${hemis}_thickness_aparc.txt 
  aparcstats2table --subjects ${subj} --hemi ${hemis} --meas thicknessstd --parc=aparc --tablefile=${roi_analysis_files}/${subj}_${hemis}_thicknessstd_aparc.txt 
  aparcstats2table --subjects ${subj} --hemi ${hemis} --meas volume --parc=aparc --tablefile=${roi_analysis_files}/${subj}_${hemis}_volume_aparc.txt 
  aparcstats2table --subjects ${subj} --hemi ${hemis} --meas meancurv --parc=aparc --tablefile=${roi_analysis_files}/${subj}_${hemis}_meancurv_aparc.txt 
  aparcstats2table --subjects ${subj} --hemi ${hemis} --meas gauscurv --parc=aparc --tablefile=${roi_analysis_files}/${subj}_${hemis}_gauscurv_aparc.txt 
  aparcstats2table --subjects ${subj} --hemi ${hemis} --meas foldind --parc=aparc --tablefile=${roi_analysis_files}/${subj}_${hemis}_foldind_aparc.txt 
  aparcstats2table --subjects ${subj} --hemi ${hemis} --meas curvind --parc=aparc --tablefile=${roi_analysis_files}/${subj}_${hemis}_curvind_aparc.txt 

done;