glm_stuff=/path/to/working_dir
dir_vtk_files=/path/to/vtk_files_for_glm

surf_type=pial
fwhm_list=(5)
for fwhm in "${fwhm_list[@]}"
do
    echo $fwhm

    ./mesh_merge_arrays -B -c \
    -r ${dir_vtk_files}/rh.subj1.rh.thickness_5mm.${surf_type}.vtk \
    ${glm_stuff}/all_hemis.glm_merged_${fwhm}mm_${surf_type}.vtk \
    thickness \
    ${dir_vtk_files}/rh.subj1.rh.thickness_5mm.${surf_type}.vtk \
    ${dir_vtk_files}/rh.subj2.rh.thickness_5mm.${surf_type}.vtk \
    ${dir_vtk_files}/rh.subj3.rh.thickness_5mm.${surf_type}.vtk \
    ${dir_vtk_files}/rh.subj4.rh.thickness_5mm.${surf_type}.vtk
done

pathology_list=(ABETA BRAAK06 CERAD EC_CS_DGNEURONLOSS EC_CS_DGTAU EC_CS_DGASYN EC_CS_DGTDP43)
for fwhm in "${fwhm_list[@]}"
do
    for pathology in "${pathology_list[@]}"
    do
    echo $fwhm $pathology

    ./meshglm -m ${glm_stuff}/all_hemis.glm_merged_${fwhm}mm_${surf_type}.vtk ${glm_stuff}/all_hemis.glm_output_for_${pathology}_${fwhm}mm_${surf_type}.vtk \
    -a thickness -g ${glm_stuff}/design_exvivo_${pathology}.txt ${glm_stuff}/contrast.txt \
    -M .5 -B -t 2.0 -s T -e -p 1000 -d 2.0 -c

    done
done
