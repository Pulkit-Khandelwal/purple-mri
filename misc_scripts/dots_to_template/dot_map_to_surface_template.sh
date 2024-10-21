#### inflate the dots and project to fsaverage surface
fsaverage_files=/path/to/freesurfer_installation/subjects/fsaverage
freesurfer_surface_processed=/path/to/fs_outputs_per_subject
SUBJECTS_DIR=${freesurfer_surface_processed}
working_dir=/path/to/dir
dot_dir=/path/to/dir

subjects=(ABC XYZ)
hemis=rh
hemis_other=lh

for subj in "${subjects[@]}"
do
echo "Processing: " ${subj}
subj_dots_file=${subj}_cortexdots_final

hemis_check=${subj: -1}
  var=R
  if [ "$hemis_check" == "$var" ]; then
        echo "Right hemis"
    else
        echo "Left hemis and so flipping it"
        # flip the left to the right ones
        c3d ${dot_dir}/${subj}/${subj}_cortexdots_final.nii.gz -flip y -o ${dot_dir}/${subj}/${subj}_cortexdots_final_flip.nii.gz
  done

        # split all the dot labels into their respective folders
        c3d ${dot_dir}/${subj}/${subj}_cortexdots_final_flip.nii.gz -split -oo ${dot_dir}/${subj}/${subj}_cortexdots_final_label%02d.nii.gz

        # inflate the dots
        bash dilation_splitted_dots.sh ${subj}

        # make each subject's directory for the processed files
        mkdir -p ${working_dir}/${subj}

        for num in {1..19}
        do
        echo ${subj} "label:" ${num}

        # convert to mgz file
        mri_convert ${dot_dir}/${subj}/${subj_dots_file}_label${num}_dilated.nii.gz ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgz

        # project the inflated dots to the surface
        mri_vol2surf --src ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgz --out ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh --regheader ${subj} --hemi ${hemis}

        # project the native mgh file to the fsaverage space
        mris_preproc --s ${subj} --target fsaverage --hemi ${hemis} --is ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh --out ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.mgh

        # convert mgh to vtk (on inflated and pial) in native space
        mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated ${working_dir}/${subj}/${subj_dots_file}_label${num}.inflated.vtk

        mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.mgh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.pial ${working_dir}/${subj}/${subj_dots_file}_label${num}.pial.vtk

        # convert mgh to vtk (on inflated and pial) in fsaverage space
        mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.mgh ${fsaverage_files}/surf/${hemis}.inflated ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.inflated.vtk

        mris_convert -c ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.mgh ${fsaverage_files}/surf/${hemis}.pial ${working_dir}/${subj}/${subj_dots_file}_label${num}.fsaverage.pial.vtk
        
done;
