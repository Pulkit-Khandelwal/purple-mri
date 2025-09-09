# Register the postmortem t2w to the corresponding invivo t1w MRI hemisphere
# Note this code uses SythSeg to segment the invivo t1w images. SynthSeg runs on 1mm space which I got via c3d.
# The 10-label purple's output is used for exvivo t2w images.
# We resample the exvivo to 1mm space as well using c3d.
# Please familarize yourself with the code and see if you have to change the file names or folders as per your use case.

####### ex vivo
exvivo_mri_dir=/data/pulkit/for_zkm/postmortem_t2w_mri
exvivo_segm_dir=/data/pulkit/for_zkm/postmortem_t2w_segm_10_label
exvivo_segm_cleaned_dir=/data/pulkit/for_zkm/postmortem_t2w_segm_10_label_cleaned

####### in vivo
invivo_dir_mri=/data/pulkit/for_zkm/antemortem_t1w_qced_resampled_1mm
invivo_dir_segm=/data/pulkit/for_zkm/antemortem_t1w_qced_resampled_1mm_synthseg_segm

####### working directory
work_dir=/data/pulkit/for_zkm/work_dir_registration
mkdir -p ${work_dir}

subjects=()


:<<'SKIP'
for subj in ${invivo_dir_mri}/*
    subj_use="$(basename "$subj")"
    indd=${subj_use: 5:6}
    echo ${indd}
SKIP

for subj in "${subjects[@]}"
do
    indd=${subj: 5:6}
    echo ${indd}

    subj_exvivo=${indd}R
    exvivo_mri=${exvivo_mri_dir}/${subj_exvivo}_t2w_0000.nii.gz
    exvivo_segm_orig=${exvivo_segm_dir}/${subj_exvivo}_t2w.nii.gz

    if [ -f "$exvivo_mri" ]; then
    echo "this is right hemis"
    side=R

    else
    echo "this is left hemis"
    side=L
    subj_exvivo=${indd}L
    exvivo_mri=${exvivo_mri_dir}/${subj_exvivo}_t2w_0000.nii.gz
    exvivo_segm_orig=${exvivo_segm_dir}/${subj_exvivo}_t2w.nii.gz
    fi
        
    invivo_mri=${invivo_dir_mri}/${subj}.nii.gz
    invivo_segm=${invivo_dir_segm}/${subj}_synthseg.nii.gz

    mkdir -p ${work_dir}/${subj_exvivo}
    mkdir -p ${work_dir}/${subj_exvivo}/labels_split

    numlabel_array=(1 2 3 4 5 7 8 9 10)
    c3d ${exvivo_segm_orig} -replace 6 7 -o ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_v1.nii.gz
    base_file=${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_v1.nii.gz
    for numlabel in "${numlabel_array[@]}"
    do
    echo "CC for label " ${numlabel}
        c3d ${base_file} -retain-labels ${numlabel} -replace ${numlabel} 1 -comp -threshold 1 1 1 0 -replace 1 ${numlabel} -o ${work_dir}/${subj_exvivo}/labels_split//${subj_exvivo}_label_${numlabel}_cc.nii.gz
    done

    c3d ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_1_cc.nii.gz ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_2_cc.nii.gz ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_3_cc.nii.gz \
    ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_4_cc.nii.gz ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_5_cc.nii.gz ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_7_cc.nii.gz \
    ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_8_cc.nii.gz ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_9_cc.nii.gz ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_label_10_cc.nii.gz \
    -add -add -add -add -add -add -add -add -o ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_t2w_cleaned.nii.gz

    echo "CC obtained for each label and merged to get a nicer segmentation with no erroneous segmentation labels hanging around"
    c3d ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_t2w_cleaned.nii.gz -dup -lstat
    cp ${work_dir}/${subj_exvivo}/labels_split/${subj_exvivo}_t2w_cleaned.nii.gz ${exvivo_segm_cleaned_dir}

    exvivo_segm=${exvivo_segm_cleaned_dir}/${subj_exvivo}_t2w_cleaned.nii.gz

    ###### Postmortem 1mm space
    c3d ${exvivo_mri} -resample-mm 1.0x1.0x1.0mm -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_mri_resampled.nii.gz
    mri_label2vol --seg ${exvivo_segm} --temp ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_mri_resampled.nii.gz \
    --o ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_segm_resampled.nii.gz --regheader ${exvivo_segm}

    if [[ $side == "R" ]]; then
        FS_LABELS="41 42 49 50 51 52 53 54"
        FS_GM="42 53"
        FS_WM="41 49 50 51 52 54"
        c3d ${invivo_segm} -retain-labels \
        42 \
        51 \
        50 \
        52 \
        49 \
        41 \
        54 \
        53 \
        -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_relabled.nii.gz

        c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_relabled.nii.gz -replace \
        42 1 \
        51 2 \
        50 3 \
        52 4 \
        49 5 \
        41 6 \
        54 6 \
        53 7 \
        -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_relabled.nii.gz

    else 
        FS_LABELS="2 3 10 11 12 13 17 18"
        FS_GM="3 17"
        FS_WM="2 10 11 12 13 18"

        c3d ${invivo_segm} -retain-labels \
        3 \
        12 \
        11 \
        13 \
        10 \
        2 \
        18 \
        17 \
        -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_relabled.nii.gz

        c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_relabled.nii.gz -replace \
        3 1 \
        12 2 \
        11 3 \
        13 4 \
        10 5 \
        2 6 \
        18 6 \
        17 7 \
        -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_relabled.nii.gz

    fi

    ###### Lets make the labels of the same scheme resampled
    c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_segm_resampled.nii.gz -replace 7 6 8 0 9 6 10 7 -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_segm_resampled_relabled.nii.gz

    ###### resampled files
    cp ${invivo_mri} ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled.nii.gz
    exvivo_mri_resampled=${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_mri_resampled.nii.gz
    exvivo_segm_resampled=${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_segm_resampled_relabled.nii.gz
    invivo_mri_resampled=${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled.nii.gz
    invivo_segm_resampled=${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_relabled.nii.gz

    ############# Now we will do the following on the coformed space

    # Extract GM and WM-plus from postmortem deep learning segmentation
    c3d ${exvivo_segm_resampled} -retain-labels 1 7 -binarize -type uchar -o ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_gm_ds.nii.gz
    c3d ${exvivo_segm_resampled} -retain-labels 2 3 4 5 6 -binarize -type uchar -o ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_wmplus_ds.nii.gz

    # Extract segmentations from antemortem deep learning segmentation
    c3d ${invivo_segm_resampled} -retain-labels 1 2 3 4 5 6 7 -type uchar -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_hemis.nii.gz
    
    # Retain the correct hemisphere for invivo
    c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_hemis.nii.gz -binarize ${invivo_mri_resampled} -multiply -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled_hemis.nii.gz

    ###### Lets trim the invivo files
    c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled_hemis.nii.gz -trim 5vox -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled_hemis_trimmed.nii.gz
    c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_hemis.nii.gz -trim 5vox -type uchar -o ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_hemis_trimmed.nii.gz

    # Extract GM and WM-plus from antemortem deep learning segmentation
    c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_hemis_trimmed.nii.gz -retain-labels 1 7 -binarize -type uchar -o ${work_dir}/${subj_exvivo}/invivo_segm_resampled_gm_trimmed.nii.gz
    c3d ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_segm_resampled_hemis_trimmed.nii.gz -retain-labels 2 3 4 5 6 -binarize -type uchar -o ${work_dir}/${subj_exvivo}/invivo_segm_resampled_wmplus_trimmed.nii.gz


    ################################################################################################################################
    # Perform label-based moments matching, affine and deformable registration

    # moments
    greedy -d 3 \
    -i ${work_dir}/${subj_exvivo}/invivo_segm_resampled_gm_trimmed.nii.gz ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_gm_ds.nii.gz \
    -i ${work_dir}/${subj_exvivo}/invivo_segm_resampled_wmplus_trimmed.nii.gz ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_wmplus_ds.nii.gz \
    -m NCC 2x2x2 -moments \
    -o ${work_dir}/${subj_exvivo}/moments.mat

    # affine
    greedy -d 3 -a -dof 12 \
    -i ${work_dir}/${subj_exvivo}/invivo_segm_resampled_gm_trimmed.nii.gz ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_gm_ds.nii.gz \
    -i ${work_dir}/${subj_exvivo}/invivo_segm_resampled_wmplus_trimmed.nii.gz ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_wmplus_ds.nii.gz \
    -n 100x50x10 -m NCC 2x2x2 -ia ${work_dir}/${subj_exvivo}/moments.mat \
    -o ${work_dir}/${subj_exvivo}/affine.mat

    # deformable
    greedy -d 3 \
    -i ${work_dir}/${subj_exvivo}/invivo_segm_resampled_gm_trimmed.nii.gz ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_gm_ds.nii.gz \
    -i ${work_dir}/${subj_exvivo}/invivo_segm_resampled_wmplus_trimmed.nii.gz ${work_dir}/${subj_exvivo}/exvivo_segm_resampled_wmplus_ds.nii.gz \
    -it ${work_dir}/${subj_exvivo}/affine.mat -n 100x50x20 -m SSD -s 8.0mm 1.0mm -sv \
    -o ${work_dir}/${subj_exvivo}/warp.nii.gz

    ##########################################
    ###### lets warp the exvivo mri+segm
    # warp exvivo segm and mri via moments
    greedy -d 3 -rf ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled_hemis_trimmed.nii.gz \
    -ri LINEAR \
    -rm ${exvivo_mri_resampled} ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_registered_mri_moments.nii.gz \
    -ri LABEL 0.2vox \
    -rm ${exvivo_segm_resampled} ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_registered_segm_moments.nii.gz \
    -r ${work_dir}/${subj_exvivo}/moments.mat

    # warp exvivo segm and mri via affine
    greedy -d 3 -rf ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled_hemis_trimmed.nii.gz \
    -ri LINEAR \
    -rm ${exvivo_mri_resampled} ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_registered_mri_affine.nii.gz \
    -ri LABEL 0.2vox \
    -rm ${exvivo_segm_resampled} ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_registered_segm_affine.nii.gz \
    -r ${work_dir}/${subj_exvivo}/affine.mat

    # warp exvivo segm and mri via deformable
    greedy -d 3 -rf ${work_dir}/${subj_exvivo}/${subj_exvivo}_invivo_mri_resampled_hemis_trimmed.nii.gz \
    -ri LINEAR \
    -rm ${exvivo_mri_resampled} ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_registered_mri_deformable.nii.gz \
    -ri LABEL 0.2vox \
    -rm ${exvivo_segm_resampled} ${work_dir}/${subj_exvivo}/${subj_exvivo}_exvivo_registered_segm_deformable.nii.gz \
    -r ${work_dir}/${subj_exvivo}/warp.nii.gz ${work_dir}/${subj_exvivo}/affine.mat
done
