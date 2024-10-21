src_dir=/data/cruise_files/data_for_topology_correction
tgt_dir=/data/cruise_files/data_for_topology_correction/output_corrected_topology

mkdir -p ${tgt_dir}

# create files for toplogy correction
# the input is ther 10-label deep learning output
for filename in $(ls ${src_dir})
do
  filename_subj="${filename%???????}"
  echo $filename $filename_subj

  ./data/c3d ${src_dir}/${filename} -replace 2 7 3 7 4 7 5 7 6 7 8 7 9 7 10 7 -o ${tgt_dir}/${filename_subj}_gm_wm.nii.gz
  ./data/c3d ${tgt_dir}/${filename_subj}_gm_wm.nii.gz -replace 7 0 -o ${tgt_dir}/${filename_subj}_gm.nii.gz
  ./data/c3d ${tgt_dir}/${filename_subj}_gm_wm.nii.gz -replace 1 0 7 1 -o ${tgt_dir}/${filename_subj}_wm.nii.gz
  ./data/c3d ${tgt_dir}/${filename_subj}_gm_wm.nii.gz -replace 1 0 7 0 0 1 -o ${tgt_dir}/${filename_subj}_csf.nii.gz

  ./data/c3d ${src_dir}/${filename} -replace 1 0 2 7 3 7 4 7 5 7 6 7 8 7 9 7 10 7 -o ${tgt_dir}/${filename_subj}_wm_plus_binarized.nii.gz
  ./data/c3d ${src_dir}/${filename} -replace 1 0 -o ${tgt_dir}/${filename_subj}_all_other_labels.nii.gz

done;

# run topology correction to get cruise-corrected GM
python3 /data/nighres_topology_corection.py

: << SKIP
# merge the topology corrected GM with the rest of the labels
for filename in $(ls ${src_dir})
do
  filename_subj="${filename%???????}"
  echo $filename $filename_subj

  #./data/c3d ${tgt_dir}/${filename_subj}_all_other_labels.nii.gz ${tgt_dir}/${filename_subj}_gm_cortex_cruise_retained_overlap.nii.gz -add -o ${tgt_dir}/${filename_subj}_aseg_ready_with_overlap_corrected.nii.gz
  #./data/c3d ${tgt_dir}/${filename_subj}_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 1 2 3 4 5 6 7 8 9 10 -o ${tgt_dir}/${filename_subj}_topology_corrected_all_labels.nii.gz

done;
SKIP
