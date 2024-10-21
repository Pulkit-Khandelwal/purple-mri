
src_dir=/data/pulkit/docker_stuff/docker_nighres/check/data_for_topology_correction
tgt_dir=/data/pulkit/docker_stuff/docker_nighres/check/data_for_topology_correction/output_corrected_topology
output_dir=/data/pulkit/docker_stuff/docker_nighres/check/data_for_topology_correction/output_corrected_topology_final_use

mkdir -p ${output_dir}

for filename in $(ls ${src_dir})
do
  filename_subj="${filename%???????}"
  echo $filename $filename_subj

  c3d ${tgt_dir}/${filename_subj}_gm_cortex_cruise_retained_overlap.nii.gz -ceil -o ${output_dir}/${filename_subj}_gm_cortex_cruise_retained_overlap_rounded.nii.gz

  c3d ${tgt_dir}/${filename_subj}_all_other_labels.nii.gz ${output_dir}/${filename_subj}_gm_cortex_cruise_retained_overlap_rounded.nii.gz -add -o ${output_dir}/${filename_subj}_aseg_ready_with_overlap_corrected.nii.gz

  c3d ${output_dir}/${filename_subj}_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 1 2 3 4 5 6 7 8 9 10 -o ${output_dir}/${filename_subj}.nii.gz

done;
