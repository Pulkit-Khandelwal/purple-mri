dir=$1
ID=$2
INDDID=${dir}/INDD${ID}/${ID}

echo 'Reslicing' ${ID}'...'

# Applies AC-PC alignment to the FLASH reorient scan -> FLASH_reslice
./greedy -d 3 -rf ${INDDID}_flash_reorient.nii.gz \
    -rm ${INDDID}_flash_reorient.nii.gz ${INDDID}_flash_reslice.nii.gz \
    -r ${INDDID}_reslice.mat

# Map dots from T2_reslice space to FLASH_reslice space
./greedy -d 3 -rf ${INDDID}_flash_reslice.nii.gz \
    -ri LABEL 0.2vox \
    -rm ${INDDID}_cortexdots_final.nii.gz ${INDDID}_cortexdots_final_in_flash_reslice_space.nii.gz \
    -r identity.mat

# Map dots from T2_reslice space to FLASH_reorient space
./greedy -d 3 -rf ${INDDID}_flash_reorient.nii.gz \
    -ri LABEL 0.2vox \
    -rm ${INDDID}_cortexdots_final.nii.gz ${INDDID}_cortexdots_final_in_flash_reorient_space.nii.gz \
    -r ${INDDID}_reslice.mat,-1