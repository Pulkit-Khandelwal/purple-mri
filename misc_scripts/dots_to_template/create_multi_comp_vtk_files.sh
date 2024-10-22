working_dir=
processed_files=

subjects=()
hemis=rh
surface=pial # or can be inflated

for subj in "${subjects[@]}"
do
echo "Subject: " ${subj}

c3d ${working_dir}/${subj}/${subj}_cortexdots_final.nii.gz -dup -lstat >> ${processed_files}/${subj}_dots_info.txt

./mesh_merge_arrays -B -c \
${working_dir}/${subj}/${subj}_all_dots_fsaverage.${surface}.vtk dots \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label1.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label2.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label3.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label4.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label5.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label6.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label7.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label8.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label9.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label10.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label11.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label12.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label13.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label14.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label15.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label16.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label17.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label18.fsaverage.pial_use.vtk \
${working_dir}/${subj}/${hemis}.${subj}_cortexdots_final_label19.fsaverage.pial_use.vtk

cp ${working_dir}/${subj}/${subj}_all_dots_fsaverage.${surface}.vtk ${processed_files}

done;
