for name in "${array[@]}"
do
  echo ${name}
  c3d ${dir1}/${name}.nii.gz -stretch 0.1% 99.9% 0 1000 -clip 0 1000 -o ${dir1}/${name}_norm.nii.gz
done
