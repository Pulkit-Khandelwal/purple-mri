# Generalized linear modeling
Make sure you have the `binaries` in your local path. Follow the steps below to perform vertex-wise analyses in template space. More details in the corresponding script.

### Warp to fsaverage space
Warp the labels and measurements (thickness, curvature, area) from native subject-space to `fsaverage` space. Prepare `vtk` files for GLM analyses.
`warp_to_template_space.sh`

### Prepare vtk files with correct file format and replace with NaNs
Prepare the `vtk` files obtained above to a format that the GLM scripts accepts
`prepare_vtk_files_for_glm.py`
Check for any dependencies to be installed in the Python imports.

### Prepare contrast vector and the data from histopathology
Sample `contrast.txt` and `sample_design_matrix.txt` files are provided. You will have to customize this as per your use case. Similar files are used in the papers for GLM of point-wise thickness and pathology with age, sex and postmortem interval as covariates.

### Run the glm script
The binaries `mesh_merge_arrays` and `meshglm` are used to merge the different thickness `vtk` files and perform vertex-wise GLM. The code make use of the `vtk` files and the 
`glm.sh`

### Visualization on Paraview
You will output files similar to:
```
all_hemis.glm_merged_5mm_pial.vtk
all_hemis.glm_output_for_ABETA_5mm_pial.vtk
all_hemis.edges.glm_output_for_ABETA_5mm_pial.vtk
```
You can load these onto Paraview and look at significant clusters!
