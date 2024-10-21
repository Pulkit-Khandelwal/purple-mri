# Register each mri image to segm_based_template based on rigid, affine and deformable
# and then use the greedy_template_average

# This is a blue print. You want to change how the files are read according to your setup.
# Get the list of ids
MANIFEST=manifest_segm.csv
ALL_IDS=($(awk -F, '{print $1}' $MANIFEST))
SUBJ_IMAGE=($(awk -F, '{print $2}' $MANIFEST))

for type_init_segm in "${modalities_list[@]}"
do

# Create lists of all images and transformations
TEMPLATE_DIR=/path/to/segm_template
MRI_DIR=/path/to/mris

# template file as fixed image
segm_template=$TEMPLATE_DIR/greedy_template_iter_09_image.nii.gz
save_warped_mri=/path/to/warped_mris
mkdir -p ${save_warped_mri}

for ((i=0;i<${#ALL_IDS[*]};i++));
do
subj=${ALL_IDS[i]}
echo $subj

# affine, warp files
rigid_file=$TEMPLATE_DIR/rigid_${subj}_to_template.mat
affine_file=$TEMPLATE_DIR/affine_${subj}_to_template.mat
warp_file=$TEMPLATE_DIR/warp_${subj}_to_template.nii.gz

# mri
mri=$MRI_DIR/${subj}.nii.gz

# perform registration between each mri and the template and save the warped image
greedy -d 3 \
    -rf $segm_template \
    -rm $mri $save_warped_mri/${subj}_warped.nii.gz \
    -r $warp_file $affine_file

done

# Perform averaging
JSON=params_ssd.json
GP_OPT_AVG=$(jq -r '.options.averaging // "-U 1 -N 0 .99 0 255"' "$JSON")

ALL_IMAGES=()
for ((i=0;i<${#ALL_IDS[*]};i++));
do
subj=${ALL_IDS[i]}
MRI_PATH="${save_warped_mri}/${subj}_warped.nii.gz"
ALL_IMAGES[i]=$MRI_PATH
echo $MRI_PATH
done

greedy_template_average \
    -d 3 -i ${ALL_IMAGES[*]} mri_initial_template.nii.gz \
    $GP_OPT_AVG
done
