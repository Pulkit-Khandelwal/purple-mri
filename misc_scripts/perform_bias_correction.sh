# output files
interm_files=
modalities_list=(t2w ciss flash)

for modality in "${modalities_list[@]}"
do
    if [[ "$modality" == "t2w" ]]; then
        echo "t2w"
        src_segm=
        src=
        tgt=
        
    elif [[ "$modality" == "ciss" ]]; then
        echo "ciss"
        src_segm=
        src=
        tgt=
        
    elif [[ "$modality" == "flash" ]]; then
        echo "flash"
        src_segm=
        src=
        tgt=
        
    else
        echo "incorrect choice"
    fi

    for subj in $(ls $src)
    do
        subj=${subj: :-12}
        echo ${subj}

        c3d ${src_segm}/${subj}.nii.gz -thresh 1 inf 1 0 -dilate 1 2x2x2vox -holefill 1 -o ${interm_files}/${subj}_mask.nii.gz

        N4BiasFieldCorrection -d 3 \
            -i ${src}/${subj}_0000.nii.gz \
            -x ${interm_files}/${subj}_mask.nii.gz -t 0.3 0.01 200 \
            -o ${interm_files}/${subj}_bias_corrected.nii.gz

        c3d ${interm_files}/${subj}_bias_corrected.nii.gz -stretch 0.1% 99.9% 0 1000 -clip 0 1000 -o ${tgt}/${subj}_bias_corrected_norm.nii.gz

    done
done
