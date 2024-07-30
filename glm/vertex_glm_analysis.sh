#### merge mesh arrays and then run glm
glm_stuff=/path/to/dir
dir_vtk_files_output_with_nans=/path/to/dir

surf_type=pial #or inflated
fwhm_list=(5) #3,5,7,10

for fwhm in "${fwhm_list[@]}"
do
    echo $fwhm
    ./mesh_merge_arrays -B -c \
    -r ${dir_vtk_files_output_with_nans}/rh.subject_one.rh.thickness_5mm.pial.vtk \
    ${glm_stuff}/pulkit/all_hemis.glm_ready_merged_${fwhm}mm_${surf_type}_with_nans_all_right_flipped_ones.vtk \
    thickness \
    ${dir_vtk_files_output_with_nans}/rh.subject_one.rh.thickness_5mm.pial.vtk \
    ${dir_vtk_files_output_with_nans}/rh.subject_two.rh.thickness_5mm.pial.vtk \
    ${dir_vtk_files_output_with_nans}/rh.subject_three.rh.thickness_5mm.pial.vtk \
    ${dir_vtk_files_output_with_nans}/rh.subject_four.rh.thickness_5mm.pial.vtk
done

pathology_list=(ABETA BRAAK06 CERAD EC_CS_DGNEURONLOSS EC_CS_DGTAU EC_CS_DGASYN EC_CS_DGTDP43)

for fwhm in "${fwhm_list[@]}"
do
    for pathology in "${pathology_list[@]}"
    do
    echo $fwhm $pathology

    ./meshglm -m ${glm_stuff}/all_hemis.glm_ready_merged_${fwhm}mm_${surf_type}_with_nans_all_right_flipped_ones.vtk ${glm_stuff}/glm_outputs_perm_testing_with_nans/all_hemis.glm_output_for_${pathology}_${fwhm}mm_${surf_type}_with_nans_all_right_flipped_ones.vtk \
    -a thickness -g ${glm_stuff}/design_matrices/design_pulkit_exvivo_all_hemis_AD_for_${pathology}.txt ${glm_stuff}/design_matrices/contrast_pulkit.txt \
    -M .5 -B -t 2.0 -s T -e -p 1000 -d 2.0 -c

    done
done
