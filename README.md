# purple-mri

**Penn Utilities for Registration and Parcellation of Ex vivo MRI**

`purple-mri` is a computational framework for segmentation, registration,
cortical surface reconstruction, anatomical parcellation, template
construction, and group-level analysis of ultra-high-resolution postmortem
human brain MRI.

The framework combines deep learning-based volumetric segmentation with
classical registration and surface-based modeling methods to enable
native-space anatomical parcellation and quantitative morphometric analysis of
postmortem MRI.

📖 **Documentation:** https://purple-mri.readthedocs.io/en/latest/

## Capabilities

`purple-mri` supports:

- automated multi-label segmentation of postmortem MRI;
- deep learning-based post-hoc topology correction;
- cortical white- and pial-surface reconstruction;
- native-space anatomical parcellation;
- multiple cortical atlases, including DKT, Destrieux, Schaefer,
  HCP-MMP1/Glasser, Jülich, Brainnetome, and von Economo-Koskinas;
- infant-specific cortical reconstruction and parcellation, including M-CRIB-S;
- ex vivo to in vivo volumetric registration;
- population-specific volumetric template construction;
- cortical thickness, area, curvature, and regional morphometry;
- ROI-wise, vertex-wise, and deformation-based group analyses.


## Workflow

A typical workflow is:

```text
Postmortem MRI
      |
      v
Pre-processing
      |
      v
Deep learning segmentation
      |
      v
Post-hoc topology correction
      |
      v
Cortical surface reconstruction
      |
      v
Anatomical parcellation
      |
      v
Registration / morphometry
      |
      v
Group and pathology analyses
```


## Installation

Clone the repository:

```bash
git clone https://github.com/Pulkit-Khandelwal/purple-mri.git
cd purple-mri
```

Install the Python dependencies:

```bash
pip install -r dependencies.txt
```

Different workflows require additional software such as Docker, FreeSurfer,
`c3d`, ANTs, and `greedy`.

See the full installation guide:

https://purple-mri.readthedocs.io/en/latest/installation.html


## Segmentation

Input NIfTI images should be placed inside a directory named:

```text
data_for_inference/
```

with filenames ending in:

```text
_0000.nii.gz
```

The currently documented Docker image is:

```bash
docker pull pulks/docker_hippogang_exvivo_segm:v1.4.6
```

The recommended complete workflow uses:

```text
exvivo_all
```

Example:

```bash
docker run --rm --gpus all --shm-size=8g \
  -v /path/to/working_directory:/data/exvivo \
  pulks/docker_hippogang_exvivo_segm:v1.4.6 \
  /bin/bash /src/commands_nnunet_inference.sh exvivo_all
```

Individual segmentation models can also be run separately.

Detailed Docker documentation:

https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md

Segmentation documentation:

https://purple-mri.readthedocs.io/en/latest/segmentation.html


## Post-hoc Topology Correction

The topology-correction model identifies buried-sulcus regions that should be
removed from the original `purple-mri` segmentation.

Standalone topology correction uses:

```text
exvivo_posthoc_topology
```

Detailed instructions:

https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/topology_correction_notes.md

Documentation:

https://purple-mri.readthedocs.io/en/latest/posthoc_correction.html


## Cortical Surface Reconstruction and Parcellation

Once a topology-corrected segmentation has been obtained, use the
surface-based pipeline to reconstruct the cortex and generate anatomical
parcellations.

The user-facing entry point is:

```text
purple_mri/run_surface_pipeline.sh
```

Run:

```bash
cd purple_mri

bash run_surface_pipeline.sh \
  freesurfer_path \
  working_dir \
  mri_path \
  segm_path \
  external_atlases_path \
  num_threads \
  rh
```

The final argument can be either:

```text
rh
```

or:

```text
lh
```

The MRI and segmentation files must have matching `.nii.gz` filenames.

Place `fsaverage` inside the working directory.


### Pial Surface Placement

Pial-surface placement uses a custom compiled FreeSurfer
`mris_place_surface` binary distributed as a Docker/Singularity container.

Setup instructions:

https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/pial_surface_binary_docker_singularity.md

Release:

https://github.com/Pulkit-Khandelwal/purple-mri/releases/tag/v0.1.0-fs-binary-docker

Once configured, it is called automatically by the surface pipeline.


### Cortical Atlases

The standard postmortem surface pipeline supports atlases including:

- Desikan-Killiany
- Destrieux
- DKT
- Brainnetome
- HCP-MMP1 / Glasser
- Schaefer2018 400 parcels / 17 networks
- Jülich
- von Economo-Koskinas

The repository also contains a dedicated infant workflow with support for
M-CRIB-S:

https://github.com/Pulkit-Khandelwal/purple-mri/tree/main/purple_mri/infant_scripts

Full parcellation documentation:

https://purple-mri.readthedocs.io/en/latest/parcellation.html


## Ex vivo to In vivo Registration

The paired ex vivo/in vivo registration workflow uses `greedy` to register
postmortem MRI to matched antemortem MRI.

The current implementation is:

```text
scripts/registration_exvivo_invivo_greedy_v2.sh
```

Documentation:

https://purple-mri.readthedocs.io/en/latest/registration.html


## Population Template Construction

Population-specific ex vivo MRI templates are constructed using iterative
registration with `greedy`.

Scripts are located in:

```text
scripts/intensity_template/
```

Documentation:

https://purple-mri.readthedocs.io/en/latest/template_construction.html


## Group Analysis

The repository includes workflows for:

- vertex-wise cortical morphometry;
- generalized linear modeling;
- deformation-based morphometry;
- ROI-wise statistical analysis;
- integration of morphometry with neuropathological measurements.

Surface GLM scripts are located in:

```text
glm/
```

Documentation:

https://purple-mri.readthedocs.io/en/latest/group_analysis.html


## Development

`purple-mri` was conceived by **Pulkit Khandelwal and Paul A. Yushkevich**
and originated from doctoral research in the PATCH Lab within the Penn Image
Computing and Science Laboratory (PICSL) at the University of Pennsylvania.

The framework was developed through collaborations with the Penn Alzheimer's
Disease Research Center and Penn Frontotemporal Degeneration Center and has
subsequently expanded at Massachusetts General Hospital, Harvard Medical
School, and the Athinoula A. Martinos Center for Biomedical Imaging toward
high-resolution multimodal postmortem imaging of the developing human brain,
including collaborative work with Boston Children's Hospital.

See the documentation homepage for additional background:

https://purple-mri.readthedocs.io/en/latest/


## Introductory Video

<div align="center">
  <a href="https://youtu.be/DBdzbIAJBw4">
    <img src="https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/images/thumbnail.png"
         style="width:75%;">
  </a>
</div>


## Citation

If you use `purple-mri` in academic work, please cite the relevant publications
listed here:

https://purple-mri.readthedocs.io/en/latest/citations.html


## License

Please see the repository license for terms of use.
