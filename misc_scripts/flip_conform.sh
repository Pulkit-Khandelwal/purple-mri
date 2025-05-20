# Check the hemisphere
  hemis_check=${subj: -1}
  echo $hemis_check
  var=R
  if [ "$hemis_check" == "$var" ]; then
          echo "Right hemis"
      else
          echo "Left hemis"
      # flip if left and over-write the mri and segm files
      c3d ${src_mri}/${subj}.nii.gz -flip y -o ${src_mri}/${subj}.nii.gz
      c3d ${src_segm}/${subj}.nii.gz -flip y -o ${src_segm}/${subj}.nii.gz
  fi
    
# conform the files to MNI space
mri_convert ${src_mri}/${subj}.nii.gz ${dst_for_mni_mri}/${subj}_mri_conform.mgz --conform
mri_convert ${src_segm}/${subj}.nii.gz ${dst_for_mni_segm}/${subj}_segm_conform.mgz --conform

mri_convert ${dst_for_mni_mri}/${subj}_mri_conform.mgz ${dst_for_mni_mri}/${subj}.nii.gz
mri_convert ${dst_for_mni_segm}/${subj}_segm_conform.mgz ${dst_for_mni_segm}/${subj}.nii.gz

mri_label2vol --seg ${src_segm}/${subj}_reslice.nii.gz --temp ${dst_for_mni_mri}/${subj}_mri_conform.mgz --o ${dst_for_mni_segm_via_label2vol}/${subj}_segm_conform_via_label2vol.mgz --regheader ${src_segm}/${subj}_reslice.nii.gz
mri_convert ${dst_for_mni_segm_via_label2vol}/${subj}_segm_conform_via_label2vol.mgz ${dst_for_mni_segm_via_label2vol}/${subj}.nii.gz
c3d ${dst_for_mni_segm_via_label2vol}/${subj}.nii.gz -type uchar -o ${dst_for_mni_segm_via_label2vol}/${subj}.nii.gz
