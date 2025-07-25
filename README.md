# purple-mri: **P**enn **U**tilities for **R**egistration and **P**arcel**L**ation of **E**x vivo **MRI**

We provide a set of tools packaged as `purple-mri` for segmentation, parcellation and registration of ultra high-resolution (< 300 microns) postmortem human brain hemisphere at 7 tesla t2w MRI at native subject-space resolution. This pipeline leverages advances in both deep learning and classical surface-based modeling techniques to produce parcellations in any atlas used in neuroimaging. The developed method allows us to perform vertex-wise analysis in the template space and thereby link morphometry measures with pathology measurements derived from histology.

Check out the [project page](https://pulkit-khandelwal.github.io/exvivo-brain-upenn/) and our latest papers [here](https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00171/120741) and [here](https://arxiv.org/abs/2403.19497).

In particular, `purple-mri` allows you to do the following:
+ obtain an initial 10 label segmentation: cortical GM, normal appearing WM, WMH, medial temporal lobe, corpus callosum, ventricles, caudate, putamen, globus pallidus and thalamus
+ obtain surface-based native subject-space parcellation based on different brain atlases such as: DKT, Economo, Schaeffer etc
+ create population specific volumetric and surface-based templates
+ perform exvivo to invivo registration in volumetric intensity space
+ perform surface-to-surface registration between exvivo or invivo
+ perform intensity-based registration between 9.4 tesla MTL to 7 tesla whole hemsiphere registration
+ perform vertex-wise and group-wise generalized linear modeling analysis for exvivo subject population for morphometry and histology

## Steps (for segmentation and parcellation)
`purple-mri` follows a series of steps making use of bash scripts and Docker.

### Pre-processing
Perform bias correction and image normalization/standardization. We use `N4BiasFieldCorrection` as part of the CLI tool [ANTs](https://github.com/ANTsX/ANTs) and [`c3d`](http://www.itksnap.org/pmwiki/pmwiki.php?n=Convert3D.Convert3D). We highly recommend using the option of an input mask in `N4BiasFieldCorrection` which can be obtained via corase threhsolding.
[Here](https://github.com/Pulkit-Khandelwal/upenn-picsl-brain-ex-vivo/tree/main/misc_scripts/perform_bias_correction.sh) is a sample script.

### Deep learning-based initial labeling and CRUISE-based post-hoc topology correction
Currently, we have two Docker images. The first image provides the segmentation and the second employs [Nighres/CRUISE](https://nighres.readthedocs.io/en/latest/installation.html) for post-hoc topology correction. 
Please follow the [link](https://github.com/Pulkit-Khandelwal/upenn-picsl-brain-ex-vivo/blob/main/exvivo-segm-demo-docker.md) for detailed instructions on how to use Docker to get the segmentations. For this, we also have the singularity image at the same link. Some key commands are emphasized here:

Place the pre-processed image(s) (with a suffix _0000.nii.gz to your filenames) in a folder named `data_for_inference` within your working directory as `/your/working/directory`.
```
docker pull pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG}

docker run --gpus all --privileged -v /your/working/directory/:/data/exvivo/ -it pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG} /bin/bash -c "bash /src/commands_nnunet_inference.sh ${OPTION}" >> logs.txt
```
You will see the output in `/your/working/directory/data_for_inference/output_from_nnunet_inference`.


IMPORTANT NOTE: You don't need to run the following topology correction step and skip directly to the surface-based pipeline below. This is because CRUISE correction introduces a lot of "cracks" in the medial area which mess up the surface pipeline. Therefore, we use FreeSurfer's topology correction instead in the surface-based pipeline. However, for the sake of completeness and for user-dependent application, we mention it here, and correct for topology so that adjoining gyri and sulci are clearly separated. Copy the segmentations from `output_from_nnunet_inference` to a folder `data_for_topology_correction` in your working directory.
```
docker pull pulks/docker_nighres:v1.0.0

docker run -v /your/working/directory/:/data/cruise_files/ -it pulks/docker_nighres:v1.0.0 /bin/bash -c "bash /data/prepare_cruise_files.sh"

# Locally run the file to get the final combined label file.
bash clean_labels_final.sh
```

### Surface-based modeling to obtain whole-hemisphere parcellations
Once, you have obtained an initial 10-label topology-corrected volumetric segmentation, you can proceed to the surface-based pipeline to obtain parcellations based on your favorite atlas. This step will be on your local machine. No GPUs are required. To do this, you should have FreeSurfer installed locally. We have used FreeSurfer version 7.4.0 on linux obtained from [here](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall). Moreover, there are some Python dependencies that can be found in the `dependencies.txt` file and installed using `pip`.

Run the following file which calls in several bash scripts which prepare the data, computes appropriate transformations and re-orients the images, corrects surface topology, and perform the parcellation into Desikan-Killiany-Tourville (DKT), Schaefer, Glasser, and the Von Economo-Koskinos atlases.

For the surface-based modeling step, we assume that all the hemispheres are right hemispheres. So, we suggest flipping the left t2w MRI and its corresponding segmentation to left using the following `c3d` command: `c3d image_left.nii.gz -flip y image_right_flipped.nii.gz`. You can also run `purple-mri` in 1mm by conforming the MRI and the deep learning-based segmentation to MNI space using [this](https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/misc_scripts/flip_conform.sh) code snippet.

Clone the current repository and then run the following script `run_surface_pipeline.sh` from within the `purple_mri` folder which takes the following mandatory arguments:
`freesurfer_path`: path to the FreeSurfer installation
`working_dir`: directory which will have the outputs for each subject stored
`mri_path`: mri images path
`segm_path`: 10-label segmentation path
`external_atlases_path`: directory with files for other atlases
`num_threads`: number of threads

Place your t2w MRI in a folder `mri_path` and the initial deep learning-based segmentations in `segm_path`.
Make sure your mri images and segmentation files have the same names ending with `.nii.gz`.
Place the `fsaverage` in the `working_dir` folder.

```
cd purple_mri

bash run_surface_pipeline.sh freesurfer_path working_dir mri_path segm_path external_atlases_path num_threads
```

### Installation using `pip`
This might not be up-to-date, so please use the bash scripts directly. You have the option to run the surface-based pipeline as a `pip` package available at [PyPI](https://pypi.org/project/purple-mri/0.0.1/) and can be installed as:

```
pip3 install purple-mri
```

Or, using the latest development code:

```
git clone https://github.com/Pulkit-Khandelwal/purple-mri.git
cd purple-mri
pip3 install pkg_src
```

Place the `fsaverage` in the `working_dir` folder. The CLI options remain the same as above but this time you have to pass in the last argument as the path to `autodet.gw.stats.binary.rh.dat`.

Once, installed you can run, `purple_mri` as:
```
python3 -m purple_mri freesurfer_path working_dir mri_path segm_path external_atlases_path num_threads /path/to/autodet.gw.stats.binary.rh.dat
```

## Other scripts
### Intensity-based volumetric template building
We build intensity-based volumetric templates using the [greedy](https://sites.google.com/view/greedyreg/about?authuser=0) tool. The required binaries (for Linux) and the scripts are located in the `intensity_template` within the `scripts` directory. Follow the instructions [here](https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/scripts/intensity_template/README.md).


### Ex vivo and in vivo registration
Script `exvivo_invivo_greedy_registration.sh` to register in vivo (t1w) and ex vivo (t2w) MRI is located in the folder `scripts`. We use [greedy](https://sites.google.com/view/greedyreg/about?authuser=0) to register the segmentations of in vivo aseg+aparc labels derived from FreeSurfer and 10-label initial deep learning segmentation of postmortem MRI. The warps are then used to register the MRIs.

### Perform GLM analyses
We perform vertex-wise analysis in `fsaverage` space to fit a generalized linear model (GLM) between cortical thickness (mm) and with global ratings of amyloid-β, Braak staging, CERAD, and semiquantitative ratings of the medial temporal lobe (MTL) neuronal loss and tau pathology, with age, sex and postmortem interval (PMI) as covariates. You can follow the steps detailed [here](https://github.com/Pulkit-Khandelwal/purple-mri/tree/main/glm). The same can be repeated for the Deformation-based morphometry.

## Notes
+ Our method has been developed to work on a single exvivo hemisphere.
+ The deep learning-based segmentation was primarily trained on 7T T2w MRI. We are currently working on a 7T T2* FLASH segmentation model.


## Introductory video
<div align="center">
      <a href="https://youtu.be/0BOeUtlWlYw?si=7NeNDsoePOW3_J4Y">
         <img src="https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/images/thumbnail.png" style="width:75%;">
      </a>
</div>

## Citations
+ Khandelwal, P., Duong, M. T., Sadaghiani, S., Lim, S., Denning, A. E., Chung, E., ... & Yushkevich, P. A. (2024). Automated deep learning segmentation of high-resolution 7 tesla postmortem MRI for quantitative analysis of structure-pathology correlations in neurodegenerative diseases. Imaging Neuroscience, 2, 1-30. 2024.
+ Khandelwal, Pulkit, et al. "Surface-Based Parcellation and Vertex-wise Analysis of Ultra High-resolution ex vivo 7 tesla MRI in Alzheimer’s disease and related dementias." International Workshop on Machine Learning in Clinical Neuroimaging. Springer, Cham, MICCAI 2024.
