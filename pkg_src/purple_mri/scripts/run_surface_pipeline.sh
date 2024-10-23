# read the mri files and create a list of the subjects
freesurfer_path=$1
working_dir=$2
mri_path=$3
segm_path=$4
external_atlases_path=$5
num_threads=$6
autodet_stats_dat=$7

subjects=()
for file in ${mri_path}/*.nii.gz
do
   fname=$(basename "$file" .nii.gz)
   subjects+=(${fname})
done

echo "Here are the list of subjects to be processed: " ${subjects[@]}

##### STEP 1: Prepare files from the initial 10-label deep learning based-segmentation
generated_files_folder=${working_dir}/files_prepared_for_pipeline
mkdir -p ${generated_files_folder}
prepare_segm_files.sh ${working_dir} "${subjects[*]}" ${generated_files_folder} ${segm_path}

##### STEP 2: Create FreeSurfer-like files
make_fs_directories.sh ${working_dir} ${generated_files_folder} ${mri_path} "${subjects[*]}"

##### STEP 3: Create mesh and downsample the same
tgt_dir_FS_mesh=${working_dir}/freesurfer_high_res_mesh
tgt_dir_FS_mesh_decimated=${working_dir}/decimated_mesh
mkdir -p ${tgt_dir_FS_mesh}
mkdir -p ${tgt_dir_FS_mesh_decimated}

# this file calls the Python script: decimate_mesh.py
create_mesh.sh ${working_dir} ${tgt_dir_FS_mesh} ${tgt_dir_FS_mesh_decimated} "${subjects[*]}"

##### STEP 4: Perform some intial regsitration to get all the required orientations
do_mni_txs.sh ${freesurfer_path} ${working_dir} "${subjects[*]}"

##### STEP 5: Perform surface-based topology correction
topology_correction.sh ${working_dir} "${subjects[*]}"

##### STEP 6: Perform surface-based parcellation
parcellation.sh ${working_dir} "${subjects[*]}" ${freesurfer_path} ${num_threads} ${external_atlases_path} ${autodet_stats_dat}