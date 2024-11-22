# Dots to template space
### Script to project native subject space dots nifti onto fsaverage and native pial (or inflated) vtk

Install FreeSurfer.
Download the binaries from [here](https://github.com/Pulkit-Khandelwal/purple-mri/tree/main/glm).
Make sure all the left `_cortexdots_final.nii.gz` files are flipped to right using: `c3d image_left.nii.gz -flip y image_right_flipped.nii.gz`.

This pipeline is dependent on the surface-based segentation and parcellation pipeline. Run that first as explained [here](https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/README.md).

The main script to run is `dots_to_surface_template.sh` where at the top you will see placeholders where you will provide the paths to:
```
fsaverage_files=/path/to/freesurfer_installation/subjects/fsaverage
SUBJECTS_DIR=/path/to/freesurfer/processed/files/per_subject
working_dir=/path/to/working_dir
dot_dir=/path/to/cortexdots_final_dir
```

This script will, for each `_cortexdots_final.nii.gz`, dilate every dot and save as an individual file. It will then project each dot onto the native (or fsaverage) pial (or inflated) surface.
The script `dots_to_surface_template.sh` calls `dilation_split_dots.sh` and `prepare_vtk_file_for_merge.py` internally. You might want to see the code therein.

The second script to run is `create_multi_comp_vtk_files.sh` which merge all the dots vtk files for a given subject into a single vtk (`${subj}_all_dots_fsaverage.pial.vtk`) file to load onto Paraview and visualzie!

#### Note
You might notice that some dots do not appear correctly onto the surface. This may be due to one of the following reasons: dot not present for the given subject or inadequate parcellation/registration or the dot is above label 19. For the last case, very minor edits are required in the files: `dots_to_surface_template.sh` and `create_multi_comp_vtk_files.sh`.
