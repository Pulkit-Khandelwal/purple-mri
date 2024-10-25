working_dir=/data/pulkit/exvivo_reg_reconstruct/surface_stuff_freesurfer/dbm
gm_wm_segm_split_dir=${working_dir}/gm_wm_segm_split
gm_smooth_resample_dir=${working_dir}/gm_smooth_resample
segm_dir=${working_dir}/segm_dir
trans_dir=${working_dir}/transformations

subjects=()
for subj in "${subjects[@]}"
do
    echo ${subj}

    c3d ${segm_dir}/${subj}.nii.gz -as X \
        -thresh 1 1 1 0 -push X -thresh 2 inf 1 0 \
        -foreach -smooth-fast 0.4mm -endfor \
        -oo ${gm_wm_segm_split_dir}/${subj}_seg_gm.nii.gz ${gm_wm_segm_split_dir}/${subj}_seg_wmplus.nii.gz

    c3d ${gm_wm_segm_split_dir}/${subj}_seg_gm.nii.gz -smooth-fast 0.4mm -resample-mm 1.0x1.0x1.0mm ${gm_smooth_resample_dir}/${subj}_seg_gm.nii.gz
done

# copy, resample and binarize the gm_template (obtain this from the template building code in purple-mri)
c3d greedy_template_iter_05_image.nii.gz -resample-mm 1.0x1.0x1.0mm ${working_dir}/gm_segm_temp_1mm.nii.gz
c3d ${working_dir}/gm_segm_temp_1mm.nii.gz -threshold -inf 0.05 0 1 -o ${working_dir}/gm_segm_temp_1mm_binarized.nii.gz

# warp each gm_segm to temp (all in resample-space)
for subj in "${subjects[@]}"
do
    echo ${subj}

    greedy -d 3 -a \
        -m NCC 2x2x2 \
        -i ${working_dir}/gm_segm_temp_1mm.nii.gz ${gm_smooth_resample_dir}/${subj}_seg_gm.nii.gz \
        -o ${trans_dir}/${subj}_affine.mat \
        -ia-image-centers -n 100x50x10

    greedy -d 3 \
    -m NCC 2x2x2 \
    -i ${working_dir}/gm_segm_temp_1mm.nii.gz ${gm_smooth_resample_dir}/${subj}_seg_gm.nii.gz \
    -it ${trans_dir}/${subj}_affine.mat \
    -o ${trans_dir}/${subj}_warp.nii.gz \
    -n 100x50x10 \

    greedy -d 3 \
    -rf ${working_dir}/gm_segm_temp_1mm.nii.gz \
    -rm ${gm_smooth_resample_dir}/${subj}_seg_gm.nii.gz ${trans_dir}/${subj}_seg_gm_warped.nii.gz \
    -r ${trans_dir}/${subj}_warp.nii.gz ${trans_dir}/${subj}_affine.mat \
    -rj ${trans_dir}/${subj}_jac.nii.gz
done

# modulated_jacobian = jacobian * gm_warped
for subj in "${subjects[@]}"
do
    echo ${subj}
    c3d ${trans_dir}/${subj}_jac.nii.gz ${trans_dir}/${subj}_seg_gm_warped.nii.gz -times -o ${trans_dir}/${subj}_mod_jac.nii.gz
done

for subj in "${subjects[@]}"
do
    echo ${subj}
    echo ${subj}_mod_jac.nii.gz >> mod_jac_list.txt
done

cd ${trans_dir}
fslmerge -t ../fsl_mod_jac_merged.nii.gz $(cat ../mod_jac_list.txt)

cd ${working_dir}
Text2Vest design_files/contrast.txt design_files/contrast.con

pathology_list=(ABETA BRAAK06 CERAD EC_CS_DGNEURONLOSS EC_CS_DGTAU EC_CS_DGASYN EC_CS_DGTDP43)
for pathology in "${pathology_list[@]}"
do
echo $pathology
Text2Vest design_files/design_matrix_${pathology}.txt design_files/design_matrix_${pathology}.mat

randomise -i fsl_mod_jac_merged.nii.gz -o ${pathology}_n1000 -m gm_segm_temp_1mm_binarized.nii.gz \
-d design_files/design_matrix_${pathology}.mat -t design_files/pulkit.con -n 1000 -T
done
