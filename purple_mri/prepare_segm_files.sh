working_dir=$1
str_split=$2
generated_files_folder=$3
segm_path=$4
hemis=$5
for i in $str_split; do subjects+=($i) ; done

for subj in "${subjects[@]}"
do
    echo ${subj}
    cp ${segm_path}/${subj}.nii.gz ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_orig.nii.gz
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_orig.nii.gz -replace 6 7 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_orig.nii.gz

    ##### Let's get the CC for each label and then merge it
    base_file=${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_orig.nii.gz
    numlabel_array=(1 2 3 4 5 7 8 9 10)
    for numlabel in "${numlabel_array[@]}"
    do
    echo "CC for label " ${numlabel}
        c3d ${base_file} -retain-labels ${numlabel} -replace ${numlabel} 1 -comp -threshold 1 1 1 0 -replace 1 ${numlabel} -o ${generated_files_folder}/${subj}_label_${numlabel}_cc.nii.gz
    done

    c3d ${generated_files_folder}/${subj}_label_1_cc.nii.gz ${generated_files_folder}/${subj}_label_2_cc.nii.gz ${generated_files_folder}/${subj}_label_3_cc.nii.gz \
    ${generated_files_folder}/${subj}_label_4_cc.nii.gz ${generated_files_folder}/${subj}_label_5_cc.nii.gz ${generated_files_folder}/${subj}_label_7_cc.nii.gz \
    ${generated_files_folder}/${subj}_label_8_cc.nii.gz ${generated_files_folder}/${subj}_label_9_cc.nii.gz ${generated_files_folder}/${subj}_label_10_cc.nii.gz \
    -add -add -add -add -add -add -add -add -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz

    echo "CC obtained for each label and merged to get a nicer segmentation with no erroneous segmentation labels hanging around"
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -dup -lstat

    # REPLACED: BEFORE 9 0; NOW 9 192 (freeSurfer label for CC)
    # REPLACED: Correct labels for subcortical regions: 2 51 3 50 these are correct.
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -replace 1 42 2 51 3 50 4 52 5 49 7 41 8 43 9 192 10 53 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_${hemis}_FS_labels.nii.gz

    mri_convert ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_${hemis}_FS_labels.nii.gz ${generated_files_folder}/${subj}_aseg.mgz
    cp ${generated_files_folder}/${subj}_aseg.mgz ${generated_files_folder}/${subj}_aseg.presurf.mgz

    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_${hemis}_FS_labels.nii.gz -replace 0 100 42 142 50 150 51 151 52 152 49 149 41 241 43 143 53 153 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_${hemis}_FS_labels_presurf_100.nii.gz
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_${hemis}_FS_labels_presurf_100.nii.gz -dup -lstat
    mri_convert ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_${hemis}_FS_labels_presurf_100.nii.gz ${generated_files_folder}/${subj}_aseg.presurf_100.mgz

    # REPLACED: BEFORE: I did NOT include the ventricle in the WM label, but now I've added that (label 8)
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 2 3 4 5 7 8 9 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz -replace 2 1 3 1 4 1 5 1 7 1 8 1 9 1 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz
          
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only.nii.gz -comp -threshold 1 1 1 0 -o ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc.nii.gz

    mri_convert ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected_WM_only_cc.nii.gz ${generated_files_folder}/${subj}_wm.mgz
    cp ${generated_files_folder}/${subj}_wm.mgz ${generated_files_folder}/${subj}_filled.mgz

    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -replace 1 42 2 41 3 41 4 41 5 41 7 41 8 41 9 41 10 0 -o ${generated_files_folder}/${subj}_ribbon.nii.gz
    c3d ${generated_files_folder}/${subj}_reslice_aseg_ready_with_overlap_corrected.nii.gz -retain-labels 1 -o ${generated_files_folder}/${subj}_${hemis}.ribbon.nii.gz

    mri_convert ${generated_files_folder}/${subj}_${hemis}.ribbon.nii.gz ${generated_files_folder}/${subj}_${hemis}.ribbon.mgz
    mri_convert ${generated_files_folder}/${subj}_ribbon.nii.gz ${generated_files_folder}/${subj}.ribbon.mgz
done;
