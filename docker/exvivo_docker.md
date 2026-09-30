# Docker for postmortem imaging
## Voxel-level deep learning-based segmentation of 7T postmortem human brain hemisphere MRI.

#### Author: Pulkit Khandelwal

# Some useful things
- You just need to provide a `nifti` image in the correct file format ending with `_0000.nii.gz`
- NO need for a GPU! Any linux-based machine works.
- Choose one of the following options for the segmentations you need. See the command at the end on how to use this Docker.

    - `${OPTION}=exvivo_t2w`: Model trained on t2w mri to get the 10 labels.
    
    - `${OPTION}=exvivo_flash_more_subcort`: Added four new segmentation labels: hypothal, optic chiasm, anterior commissure, fornix trained on the flash.
      
    - `${OPTION}=exvivo_flash_thalamus`: Flash model for thalamus segmentation.
    
    - `${OPTION}=invivo_flair_wmh`: White matter hyperintensities segmentation on invivio flair.
 
    - `${OPTION}=exvivo_umc_strip_cerebellum`: strip the cerebellum from the UMC MRI.
 
    - `${OPTION}=exvivo_posthoc_topology`: model trained for post-hoc bridged sulcus removal.
 
    - `${OPTION}=exvivo_multi_sequence_mtl_amygdala_subfields`: MTL subfields trained on ciss/t2w/flash
    
    - `${OPTION}=exvivo_multi_sequence_subcortical`: Subcortical structures trained on ciss/t2w/flash

- Replace ${LATEST_TAG} with the latest version of the Docker. See change logs below.

# Docker image
My docker image is located at `https://hub.docker.com/r/pulks/docker_hippogang_exvivo_segm`

# Steps

#### Step 1: Prepare the data
Download the image from the box into a folder named `data_for_inference` (do NOT give it any other name) and then place this folder any directory of choice, for example, `/data/username/`.

#### Step 2: Pull the docker image
This should pull my docker image from docker hub,
`docker pull pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG}`

#### Step 3: Run the docker container
Run the following command to start the inference. See how the volume is mounted in the following command. We mount the volume where the folder `data_for_inference`, with the image on which to run inference, is located. Here, `data_for_inference` is located in `/data/username/`. Add the values: {LATEST_TAG} and ${OPTION}.

`docker run --gpus all --privileged -v /data/username/:/data/exvivo/ -it pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG} /bin/bash -c "bash /src/commands_nnunet_inference.sh ${OPTION}" >> logs.txt`

#### Check the output!
Note, you might see a warning displayed on the terminal, you can safely ignore that!
It takes around ~15 minutes to run the inference for the `ex vivo` T2w image. You should see a folder in your local machine at the path:
`/your/path/to/data_for_inference/output_from_nnunet_inference`

## Note on white matter hyperintensities in `in vivo` FLAIR images
If, you want to run the WMH for `in vivo` flair data then run the following command. Make sure that the image is skull-stripped and normalized/standardized.
It takes around 1 minute to get the WMH segmentations in the `in vivo` FALIR image.

# Post-hoc topology correction
After that, run the new docker for post-hoc correction. This solves the buried sulci and adjoining gyri problem:
https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/topology_correction_notes.md

##### Change Logs
09/30/2026:
- Updated version v1.4.6 and added two new models
  - MTL subfields trained on ciss/t2w/flash
  - Subcortical structures trained on ciss/t2w/flash

02/01/2026:
- Updated version v1.4.5 and added three new models
  - model trained on flash mri for gm/wm segmentation
  - model trained for postdoc topology-correction, i.e., it helps with the bridge sulcus problem
  - strip the cerebellum from the UMC MRI
  
12/09/2025:
- Fixed the numpy core module issue due to version mismatch (v1.4.4).

11/19/2025:
- Added the flash model for thalamus segmentation (v1.4.3).

05/05/2025:
- Added the latest 10-labels voxel-level segmentation (v1.4.2). This version cleans up GM/WM mis-segmentations in the medial area; predicts the missing regions (filling-up the sampling cuts) areas and to some extent the A/P signal drop-out issues. Made light-weight than before.

10/10/2024:
- Added documentation for the post-hoc topology correction docker.

09/03/2024:
- Support for Singularity added. See section on singularity below. Latest tag for singularity: `1.0.0`.
- The singuarity image has been uploaded to DockerHub.

08/30/24:
- Version `docker_hippogang_exvivo_segm:v1.4.0` updated with the model which includes the MTL, ventricles and the corpus callosum. Also updated the docker with models on ciss-t2w initial model and additonal t2*w mri segmentation labels. The docker run cmd now takes an option to select which model to run. Additionaly, updated the Dockerfile so that it can do inference on Ampere GPUs (CUDA>11).

07/16/24:
- Version `docker_hippogang_exvivo_segm:v1.3.1` make singularity compatible by removing a copy command in the bash script

10/22/22:
- Version `docker_hippogang_exvivo_segm:v1.3.0` sgements even the white matter automatically now!
- Version `docker_hippogang_exvivo_segm:v1.2.0` now also performs segmentation for WMH in `in vivo` flair images used for Detre/Sandy's project on ADNI data.
- You can now also see a `logs.txt` file in the folder where you run the docker container from.

10/19/22:
- First created!
- Version bare-bones: `docker_hippogang_exvivo_segm:v1.1.0`
