#!/bin/sh

# Script to register t1w (in vivo) and ex vivo (t2w) MRI.
# This is done based on the segmentations of in vivo aseg+aparc labels derived from FreeSurfer
# and 10-label initial deep learning segmentation of postmortem MRI.
# The warps are then used to regsiter the MRIs.

# List of subjects
subjects=()
work_dir=

for subj in "${subjects[@]}"
do
    echo ${subj}
    exvivo_dir=
    exvivo_mri=${exvivo_dir}/${subj}.nii.gz
    exvivo_segm=${exvivo_segm_dir}/${subj}.nii.gz

    invivo_dir=
    invivo_aseg=${invivo_dir}/${subj}/mri/aseg.mgz
    invivo_aparc_aseg=${invivo_dir}/${subj}/mri/aparc+aseg.mgz
    invivo_mri=${invivo_dir}/${subj}/mri/brain.mgz

    # processed files for each subject will go here
    subject=subject_${subject}
    mkdir -p ${work_dir}/${subject}

    ### convert to nifti
    mri_convert ${invivo_mri} ${work_dir}/${subject}/t1.nii.gz
    mri_convert ${invivo_aseg} ${work_dir}/${subject}/aseg.nii.gz
    mri_convert ${invivo_aparc_aseg} ${work_dir}/${subject}/aparc_aseg.nii.gz

    # Extract GM and WM-plus from postmortem deep learning 10-label segmentation
    c3d ${exvivo_segm} -as X \
        -thresh 1 1 1 0 -push X -thresh 2 inf 1 0 \
        -foreach -smooth-fast 0.4mm -resample-mm 1.0mm -endfor \
        -oo ${work_dir}/${subject}/seg_gm_ds.nii.gz ${work_dir}/${subject}/seg_wmplus_ds.nii.gz

    # Prepare antemortem labels
    # Extract GM and WM-plus from ASEG (all subcortical structures)

    if [[ $side == "R" ]]; then
        FS_LABELS="41 42 49 50 51 52 53 54"
        FS_GM="42 53 54"
        FS_WM="41 49 50 51 52"
    else 
        FS_LABELS="2 3 10 11 12 13 17 18"
        FS_GM="3 17 18"
        FS_WM="2 10 11 12 13"
    fi

    c3d ${work_dir}/${subject}/aseg.nii.gz \
        -retain-labels ${FS_LABELS} -trim 5mm -type uchar \
        -o ${work_dir}/${subject}/aseg_hemi.nii.gz -as X \
        -retain-labels ${FS_GM} -binarize -type uchar \
        -o ${work_dir}/${subject}/aseg_gm.nii.gz \
        -push X -retain-labels ${FS_WM} -binarize  \
        -o ${work_dir}/${subject}/aseg_wmplus.nii.gz

    ##### Registration between exvivo and invivo segmentations
    # Perform affine registration
    greedy -d 3 -a -dof 12 \
    -i ${work_dir}/${subject}/aseg_gm.nii.gz ${work_dir}/${subject}/seg_gm_ds.nii.gz \
    -i ${work_dir}/${subject}/aseg_wmplus.nii.gz ${work_dir}/${subject}/seg_wmplus_ds.nii.gz \
    -n 100x100x100 -m NMI -ia-image-centers \
    -o ${work_dir}/${subject}/affine.mat

    # Perform deformable registration
    greedy -d 3 \
        -i ${work_dir}/${subject}/aseg_gm.nii.gz ${work_dir}/${subject}/seg_gm_ds.nii.gz \
        -i ${work_dir}/${subject}/aseg_wmplus.nii.gz ${work_dir}/${subject}/seg_wmplus_ds.nii.gz \
        -it ${work_dir}/${subject}/affine.mat -n 100x100x40 -m SSD -s 8.0mm 1.0mm -sv \
        -o ${work_dir}/${subject}/warp_smooth.nii.gz -oroot ${work_dir}/${subject}/warp_smooth_root.nii.gz

    # Warp ex vivo to T1 space
    greedy -d 3 -rf ${work_dir}/${subject}/t1.nii.gz \
        -rm ${exvivo_mri} \
        ${work_dir}/${subject}/postmortem_to_t1.nii.gz \
        -r ${work_dir}/${subject}/warp_smooth.nii.gz ${work_dir}/${subject}/affine.mat

    # Warp the ASEG (in vivo) labels to ex vivo space
    greedy -d 3 -rf ${exvivo_mri} \
        -ri LABEL 0.2mm \
        -rm ${work_dir}/${subject}/aseg_hemi.nii.gz \
            ${work_dir}/${subject}/aseg_to_exvivo.nii.gz \
        -r ${work_dir}/${subject}/affine.mat,-1 ${work_dir}/${subject}/warp_smooth_root.nii.gz,-64

    # Warp the aparc+aseg segmentations as well to ex vivo space
    c3d \
        ${work_dir}/${subject}/aseg_hemi.nii.gz -binarize -dup \
        ${work_dir}/${subject}/aparc_aseg.nii.gz -reslice-identity -times \
        -o ${work_dir}/${subject}/aparc_aseg_hemi.nii.gz

    # Warp the aparc+aseg in vivo segmentations to ex vivo space
    # Warp the in vivo (t1w) to ex vivo (t2w) MRI
    greedy -d 3 -rf ${exvivo_mri} \
        -ri LABEL 0.2mm \
        -rm ${work_dir}/${subject}/aparc_aseg_hemi.nii.gz \
            ${work_dir}/${subject}/aparc_aseg_to_exvivo.nii.gz \
        -ri LINEAR \
        -rm ${work_dir}/${subject}/t1.nii.gz \
            ${work_dir}/${subject}/t1_to_postmortem.nii.gz \
        -r ${work_dir}/${subject}/affine.mat,-1 ${work_dir}/${subject}/warp_smooth_root.nii.gz,-64

    # The GM/WM labels are retained from the postmortem segmentation
    # The nearest neighbor is used to label the postmortem segmentation with the aseg+aparc label
    c3d -verbose \
        ${exvivo_segm} -thresh 1 1 1 0 -popas X \
        ${work_dir}/${subject}/aparc_aseg_to_exvivo.nii.gz -as Y \
        -retain-labels $FS_GM -push Y -clip 1999 3000 -replace 1999 0 -add \
        -replace 0 3000 \
        -split -foreach -trim 5mm -as Z -push X -reslice-identity -push Z -fm 5 -reciprocal -insert X 1 -reslice-identity -endfor \
        -scale 0 -merge -push X -times \
        -o ${work_dir}/${subject}/seg_hemi_aparc.nii.gz

    # For making figures, create a high-res version of the resampled ex vivo MRI
    c3d ${work_dir}/${subject}/postmortem_to_t1.nii.gz -trim 3mm \
        -resample-mm 0.25mm \
        -o ${work_dir}/${subject}/t1_postmortem.nii.gz

    greedy -d 3 -rf ${work_dir}/${subject}/t1_postmortem.nii.gz \
        -rm ${exvivo_mri} \
            ${work_dir}/${subject}/${subj}_postmortem_to_t1_hr.nii.gz \
        -ri LABEL 0.1mm \
        -rm ${work_dir}/${subject}/seg_hemi_aparc.nii.gz \
            ${work_dir}/${subject}/${subj}_aparc_aseg_to_exvivo_hr.nii.gz \
        -r ${work_dir}/${subject}/warp_smooth.nii.gz ${work_dir}/${subject}/affine.mat
done
