SUBJECTS_DIR=/path/to/freesurfer/processed/files/per_subject
# Place the fsaverage folder in the fsaverage_files folder (to avoid any errors)
fsaverage_files=${SUBJECTS_DIR}/fsaverage
working_dir=/path/to/working_dir
dot_dir=/path/to/cortexdots_final_dir
processed_files=/path/to/processed_files_dir
hemis=rh
hemis_other=lh
surface=pial # or can be inflated
subjects=()
fsaverage_pial_surface=/data/pulkit/exvivo_reg_reconstruct/surface_stuff_freesurfer/october_2024/purple_work/scripts_native_res_april2025/dots_to_template/fsaverage_pial.vtk

for subj in "${subjects[@]}"
do
echo "Processing: " ${subj}
# make a folder for each subject
mkdir -p ${working_dir}/${subj}

# copy the ${subj}_cortexdots_final.nii.gz to the working directory
cp ${dot_dir}/${subj}.nii.gz ${working_dir}/${subj}/${subj}_cortexdots_final.nii.gz

# split all the dot labels into different files in their corresponding subject folder
# c3d ${working_dir}/${subj}/${subj}_cortexdots_final.nii.gz -split -oo ${working_dir}/${subj}/${subj}_cortexdots_final_label%02d.nii.gz

# use the Python version
python3 split_labels.py ${working_dir}/${subj}/ ${subj}
raw_list=$(cat ${working_dir}/${subj}/"unique_labels_${subj}.txt")
clean_list=$(echo "$raw_list" | tr -d '[],')
read -a valid_labels <<< "$clean_list"
cp ${working_dir}/${subj}/unique_labels_${subj}.txt ${processed_files}

# inflate each individual dot
bash dilation_split_dots.sh ${working_dir} ${subj}

subj_dots_file=${subj}_cortexdots_final
for num in "${valid_labels[@]}"
do
echo ${subj} "label:" ${num}

# convert to mgz file
mri_convert ${working_dir}/${subj}/${subj_dots_file}_label${num}_dilated.nii.gz ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgz

# project the inflated dots to the native space surface
mri_vol2surf --src ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgz --out ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh --regheader ${subj} --hemi ${hemis}

# project the native mgh file to the fsaverage space
mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --is ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh --out ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.mgh

# convert mgh to vtk (on inflated and pial) in native space
mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated ${working_dir}/${subj}/${subj_dots_file}_label${num}.inflated.vtk

mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.pial ${working_dir}/${subj}/${subj_dots_file}_label${num}.pial.vtk

# convert mgh to vtk (on inflated and pial) in fsaverage space
mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.mgh ${fsaverage_files}/surf/${hemis}.inflated ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.inflated.vtk

mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.mgh ${fsaverage_files}/surf/${hemis}.pial ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.pial.vtk
done

python3 prepare_vtk_file_for_merge.py ${working_dir} ${subj}

####### merge arrays
c3d ${working_dir}/${subj}/${subj}_cortexdots_final.nii.gz -dup -lstat >> ${processed_files}/${subj}_dots_info.txt

# We will add a dummy first vtk mesh as just the pial surface
# so that we can load the mesh onto Paraview and start looking at 1 to 19 dots
# and ignore the index 0

cp ${fsaverage_pial_surface} ${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label0.fsaverage.pial_use.vtk
for num in $(seq 0 19)
do
  if [ -f "${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label${num}.fsaverage.pial_use.vtk" ]; then
    echo "Dot ${num} was placed!"
   else
    echo "Dot ${num} was NOT placed!"
    cp ${fsaverage_pial_surface} ${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label${num}.fsaverage.pial_use.vtk
  fi
    echo ${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label${num}.fsaverage.pial_use.vtk \ >> ${working_dir}/${subj}/"merge_arrays_string_${subj}.txt"
done

./mesh_merge_arrays -B -c \
${working_dir}/${subj}/${subj}_all_dots_fsaverage.${surface}.vtk dots $(cat ${working_dir}/${subj}/"merge_arrays_string_${subj}.txt")

cp ${working_dir}/${subj}/${subj}_all_dots_fsaverage.${surface}.vtk ${processed_files}

done;
