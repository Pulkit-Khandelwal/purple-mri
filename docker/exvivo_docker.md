# Docker for postmortem imaging

## Voxel-level deep learning-based segmentation of 7T postmortem human brain hemisphere MRI

#### Author: Pulkit Khandelwal

# Some useful things

- You just need to provide a `nifti` image in the correct file format ending with `_0000.nii.gz`.

- The Docker command below is configured to use an NVIDIA GPU with `--gpus all`.

- Choose one of the following options depending on the segmentation task you want to run. See the command below for how to use `${OPTION}`.

  - `${OPTION}=exvivo_all`: Run the complete ex vivo segmentation pipeline.

  - `${OPTION}=exvivo_t2w`: Model trained on T2w MRI to obtain the 10-label segmentation.

  - `${OPTION}=exvivo_flash_more_subcort`: FLASH model with four additional segmentation labels: hypothalamus, optic chiasm, anterior commissure, and fornix.

  - `${OPTION}=exvivo_flash_thalamus`: FLASH model for thalamus segmentation.

  - `${OPTION}=invivo_flair_wmh`: White matter hyperintensity segmentation on in vivo FLAIR MRI.

  - `${OPTION}=exvivo_umc_strip_cerebellum`: Strip the cerebellum from the UMC MRI.

  - `${OPTION}=exvivo_posthoc_topology`: Model trained for post-hoc bridged-sulcus removal.

  - `${OPTION}=exvivo_multi_sequence_mtl_amygdala_subfields`: MTL and amygdala subfield segmentation trained on CISS/T2w/FLASH MRI.

  - `${OPTION}=exvivo_multi_sequence_subcortical`: Subcortical structure segmentation trained on CISS/T2w/FLASH MRI.

- Replace `${LATEST_TAG}` with the desired Docker version. The current version is `1.4.6`. See the change logs below.

# Docker image

The Docker image is available on Docker Hub:

`https://hub.docker.com/r/pulks/docker_hippogang_exvivo_segm`

# Steps

#### Step 1: Prepare the data

Place the image to be segmented inside a folder named `data_for_inference` (**do NOT give this folder any other name**).

The input NIfTI image should have a filename ending with:

```text
_0000.nii.gz
```

For example:

```text
data_for_inference/
└── 100085R_reslice_0000.nii.gz
```

Place the `data_for_inference` folder inside a directory of your choice, for example:

```text
/data/username/data_for_inference/
```

#### Step 2: Pull the Docker image

Pull the Docker image from Docker Hub:

```bash
docker pull pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG}
```

For example, for version `v1.4.6`:

```bash
docker pull pulks/docker_hippogang_exvivo_segm:v1.4.6
```

#### Step 3: Run the Docker container

Run the following command to start inference.

The directory containing `data_for_inference/` is mounted to `/data/exvivo/` inside the Docker container.

Replace:

- `${LATEST_TAG}` with the Docker version.
- `${OPTION}` with the segmentation model or pipeline you want to run.

```bash
docker run --rm --gpus all --shm-size=8g \
  -v /data/username/:/data/exvivo/ \
  pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG} \
  /bin/bash /src/commands_nnunet_inference.sh ${OPTION}
```

For example, to run an individual segmentation model:

```bash
docker run --rm --gpus all --shm-size=8g \
  -v /data/username/:/data/exvivo/ \
  pulks/docker_hippogang_exvivo_segm:v1.4.6 \
  /bin/bash /src/commands_nnunet_inference.sh exvivo_multi_sequence_subcortical
```

Alternatively, set:

```text
${OPTION}=exvivo_all
```

to run the complete ex vivo segmentation pipeline.

#### Check the output!

You might see warnings displayed in the terminal during inference; these can generally be safely ignored if the pipeline continues normally.

The outputs are written back to the mounted `data_for_inference/` directory on the local machine:

```text
/your/path/to/data_for_inference/output_from_nnunet_inference/
```

The exact output directories depend on the selected `${OPTION}`.

Because the input directory is mounted into the Docker container, the generated segmentations remain available on the host machine after the container exits.

## Note on white matter hyperintensities in `in vivo` FLAIR images

If you want to run white matter hyperintensity segmentation on `in vivo` FLAIR data, use:

```text
${OPTION}=invivo_flair_wmh
```

Make sure the input image is skull-stripped and normalized/standardized.

Inference for WMH segmentation on an `in vivo` FLAIR image typically takes approximately 1 minute.

# Post-hoc topology correction

For post-hoc topology correction, see:

https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/topology_correction_notes.md

This step addresses issues such as buried sulci and adjoining/bridged gyri.

##### Change Logs

10/06/2026:

- Updated to version `v1.4.6`.
- Added `${OPTION}=exvivo_all` for running the complete ex vivo segmentation pipeline.
- Added two new multi-sequence models:
  - `${OPTION}=exvivo_multi_sequence_mtl_amygdala_subfields`: MTL and amygdala subfields trained on CISS/T2w/FLASH MRI.
  - `${OPTION}=exvivo_multi_sequence_subcortical`: Subcortical structures trained on CISS/T2w/FLASH MRI.
- Updated the Docker execution command:
  - Added `--rm` to automatically remove the container after inference.
  - Added `--shm-size=8g`.
  - Removed the need for `--privileged`.
  - Simplified execution of `/src/commands_nnunet_inference.sh`.

02/01/2026:

- Updated version `v1.4.5` and added three new models:
  - Model trained on FLASH MRI for GM/WM segmentation.
  - Model trained for post-hoc topology correction, i.e., it helps with the bridged-sulcus problem.
  - Model to strip the cerebellum from the UMC MRI.

12/09/2025:

- Fixed the NumPy core module issue due to version mismatch (`v1.4.4`).

11/19/2025:

- Added the FLASH model for thalamus segmentation (`v1.4.3`).

05/05/2025:

- Added the latest 10-label voxel-level segmentation (`v1.4.2`). This version cleans up GM/WM mis-segmentations in the medial area, predicts missing regions corresponding to sampling cuts, and addresses some anterior/posterior signal dropout issues. The Docker image was also made more lightweight.

10/10/2024:

- Added documentation for the post-hoc topology correction Docker.

09/03/2024:

- Added support for Singularity. See the Singularity documentation for details. Latest tag for Singularity: `1.0.0`.
- Uploaded the Singularity image to Docker Hub.

08/30/2024:

- Updated `docker_hippogang_exvivo_segm:v1.4.0` with the model that includes the MTL, ventricles, and corpus callosum.
- Added models trained on CISS/T2w MRI and additional T2*w MRI segmentation labels.
- Updated the Docker run command to accept an option specifying which model to run.
- Updated the Dockerfile to support inference on Ampere GPUs (CUDA > 11).

07/16/2024:

- Version `docker_hippogang_exvivo_segm:v1.3.1` made Singularity-compatible by removing a copy command in the bash script.

10/22/2022:

- Version `docker_hippogang_exvivo_segm:v1.3.0` now automatically segments white matter.
- Version `docker_hippogang_exvivo_segm:v1.2.0` added segmentation of WMH in `in vivo` FLAIR images used for the Detre/Sandy project on ADNI data.
- A `logs.txt` file is also generated in the folder where the Docker container is run.

10/19/2022:

- First created.
- Initial bare-bones version: `docker_hippogang_exvivo_segm
