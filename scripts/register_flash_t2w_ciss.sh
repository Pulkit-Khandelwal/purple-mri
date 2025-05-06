# A general purpose script to register ciss/t2w/flash mri based on initial (GM/WM+) labels.
# Can be modified to get the mri as an additional channel and/or split labels to go as additional channels.

mri_dir=
segm_dir=
flash_mri=${mri_dir}/flash_reslice_0000.nii.gz
t2w_mri=${mri_dir}/reslice_0000.nii.gz
flash_segm=${segm_dir}/flash_reslice.nii.gz
t2w_segm=${segm_dir}/reslice.nii.gz
output_dir=

# Extract GM and WM-plus from postmortem deep learning segmentation
# -resample-mm 1.0mm
c3d ${flash_segm} -as X \
    -thresh 1 1 1 0 -push X -thresh 2 inf 1 0 \
    -foreach -smooth-fast 0.4mm -endfor \
    -oo ${output_dir}/flash_segm_gm_ds.nii.gz ${output_dir}/flash_segm_wmplus_ds.nii.gz

c3d ${t2w_segm} -as X \
    -thresh 1 1 1 0 -push X -thresh 2 inf 1 0 \
    -foreach -smooth-fast 0.4mm -endfor \
    -oo ${output_dir}/t2w_segm_gm_ds.nii.gz ${output_dir}/t2w_segm_wmplus_ds.nii.gz

# Perform moments matching and affine and deformable registration
greedy -d 3 \
-i ${output_dir}/t2w_segm_gm_ds.nii.gz ${output_dir}/flash_segm_gm_ds.nii.gz \
-i ${output_dir}/t2w_segm_wmplus_ds.nii.gz ${output_dir}/flash_segm_wmplus_ds.nii.gz \
-m NCC 2x2x2 -moments \
-o ${output_dir}/moments.mat

greedy -d 3 -a -dof 12 \
-i ${output_dir}/t2w_segm_gm_ds.nii.gz ${output_dir}/flash_segm_gm_ds.nii.gz \
-i ${output_dir}/t2w_segm_wmplus_ds.nii.gz ${output_dir}/flash_segm_wmplus_ds.nii.gz \
-n 100x100x100 -m NCC 2x2x2 -ia ${output_dir}/moments.mat \
-o ${output_dir}/affine.mat

greedy -d 3 \
-i ${output_dir}/t2w_segm_gm_ds.nii.gz ${output_dir}/flash_segm_gm_ds.nii.gz \
-i ${output_dir}/t2w_segm_wmplus_ds.nii.gz ${output_dir}/flash_segm_wmplus_ds.nii.gz \
-it ${output_dir}/affine.mat -n 100x50x20 -m SSD -s 8.0mm 1.0mm -sv \
-o ${output_dir}/warp_smooth.nii.gz

# warp conformed exvivo segm
greedy -d 3 -rf ${t2w_mri} \
-rm ${flash_mri} ${output_dir}/flash_mri_warped_to_t2w.nii.gz \
-r ${output_dir}/warp_smooth.nii.gz ${output_dir}/affine.mat
