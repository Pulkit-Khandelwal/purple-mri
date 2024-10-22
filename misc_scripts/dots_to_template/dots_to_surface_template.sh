
fsaverage_files=/path/to/freesurfer_installation/subjects/fsaverage
# Also place the fsaverage folder in the fsaverage_files folder (to avoid any errors)
SUBJECTS_DIR=/path/to/freesurfer/processed/files/per_subject
working_dir=/path/to/working_dir
dot_dir=/path/to/cortexdots_final_dir

subjects=()
hemis=rh
hemis_other=lh

for subj in "${subjects[@]}"
do
echo "Processing: " ${subj}

# make a folder for each subject
mkdir -p ${working_dir}/${subj}

# copy the ${subj}_cortexdots_final.nii.gz to the working directory
cp ${dot_dir}/${subj}_cortexdots_final.nii.gz ${working_dir}/${subj}/${subj}_cortexdots_final.nii.gz

# split all the dot labels into different files in their corresponding subject folder
c3d ${working_dir}/${subj}/${subj}_cortexdots_final.nii.gz -split -oo ${working_dir}/${subj}/${subj}_cortexdots_final_label%02d.nii.gz

# inflate each individual dot
bash dilation_split_dots.sh ${working_dir} ${subj}

subj_dots_file=${subj}_cortexdots_final
for num in {1..19}
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
done;
