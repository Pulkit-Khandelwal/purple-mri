# Docker/Singularity for postmortem imaging
## Deep learning-based segmentation of 7 tesla postmortem T2w & flash human brain hemisphere MRI.

#### Author: Pulkit Khandelwal

### Note: The current (09/04/2024) version of the containers is about ~48GB!!! This is huge and takes quite some time to download and convert from `sif` to `simg` for singualrity. I will reduce the file size in a future update. But, apart frrom that it works just fine!

##### Change Logs
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

# Some useful things
- You don't need any working knowledge of docker or kubernetes, but if curious, here is a great [YouTube video](https://youtu.be/3c-iBn73dDE).
- You just need to provide a `nifti` image in the correct file format ending with `_0000.nii.gz`
- NO need for a GPU! Any linux-based machine works.
- Choose one of the following options for the segmentations you need. See the command at the end on how to use this Docker.

    - `${OPTION}=exvivo_t2w`: Model trained on t2w mri to get the 10 labels.
    
    - `${OPTION}=exvivo_flash_more_subcort`: Added four new segmentation labels: hypothal, optic chiasm, anterior commissure, fornix. This model has been trained on the flash t2* mri.
    
    - `${OPTION}=exvivo_ciss_t2w`: Multi-input segmentation to solve the anterior/posterior missing segmentation issue.
    
    - `${OPTION}=invivo_flair_wmh`: White matter hyperintensities segmentation on invivio flair

- Replace ${LATEST_TAG} with the latest version of the Docker. See change logs above.

# Docker image
My docker image is located at `https://hub.docker.com/r/pulks/docker_hippogang_exvivo_segm`

# Docker files
I have provided some files in the folder `docker_files` for your reference only but we do not need those for running the demo.

# Steps

#### Step 1: Prepare the data
Download the image from the box into a folder named `data_for_inference` (do NOT give it any other name) and then place this folder any directory of choice, for example, `/data/username/`.

#### Step 2: Pull the docker image
This should pull my docker image from docker hub. It is a really huge file.
`docker pull pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG}`

#### Step 3: Run the docker container
Run the following command to start the inference. See how the volume is mounted in the following command. We mount the volume where the folder `data_for_inference`, with the image on which to run inference, is located. Here, `data_for_inference` is located in `/data/username/`. Add the values: {LATEST_TAG} and ${OPTION}.

`docker run --gpus all --privileged -v /data/username/:/data/exvivo/ -it pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG} /bin/bash -c "bash /src/commands_nnunet_inference.sh ${OPTION}" >> logs.txt`

#### Check the output!
Note, you might see a warning diaplyed on the temrinal, you can safely ignore that!
It takes around ~15 minutes to run the inference for the `ex vivo` T2w image. You should see a folder in your local machine at the path:
`/your/path/to/data_for_inference/output_from_nnunet_inference`

## Note on white matter hypeintensities in `in vivo` FLAIR images
If, you want to run the WMH for `in vivo` flair data then run the following command. Make sure that the image is skull-stripped and normalized/standardized.
It takes around 1 minute to get the WMH segmentations in the `in vivo` FALIR image.

# Post-hoc topology correction
After that, run the new docker for post-hoc topology correction. This solves the buried sulci and adjoining gyri problem.
Here is the second docker for post-hoc topology correction and below are the instructions:
https://github.com/Pulkit-Khandelwal/upenn-picsl-brain-ex-vivo/blob/main/nighres_docker

### Pull the docker
`docker pull pulks/docker_nighres:v1.0.0`

Run the docker to get the cruise-nighres topology correction.
Make directory data_for_topology_correction in let's say `/your/path/docker_stuff/docker_nighres/check/`.
This directory should consist of only your segmentation output from the first segmentation docker.

# Run docker
docker run -v /your/path/docker_stuff/docker_nighres/check/:/data/cruise_files/ -it pulks/docker_nighres:v1.0.0 /bin/bash -c "bash /data/prepare_cruise_files.sh"

# Locally run the file to get the final combined label file which is located in the above GitHub directory
bash clean_labels_final.sh

# Convert Docker to Singularity
I converted the Docker image to Singularity and it should run on a linix machine with a GPU. Functionality remains the same.

Pull the latest `sif` image:
`singularity pull exvivo_dl_segm_pull.sif oras://registry-1.docker.io/pulks/exvivo_dl_segm_tool:v{LATEST_TAG}`

Run the following command:
`singularity exec --nv --bind /data/username/:/data/exvivo exvivo_dl_segm_pull.sif /bin/bash -c "/src/commands_nnunet_inference.sh ${OPTION}"`

### FOR DEVELOPERS
#### How did I build the Singularity container?
#### Native no-root installation of Singularity

## Install
```
# Install go
# Grab the tar file from: https://go.dev/doc/install
tar -C /path/to/installation_dir/go_files -xzf go1.23.0.linux-amd64.tar.gz
export PATH=$PATH:/path/to/installation_dir/go_files/go/bin

# Install singularity:
echo 'export GOPATH=${HOME}/go' >> ~/.bashrc
echo 'export PATH=/path/to/installation_dir/go_files/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc
source ~/.bashrc

mkdir -p /path/to/installation_dir/singularity
./mconfig --prefix=/path/to/installation_dir/singularity --without-seccomp --without-conmon --without-squashfuse --without-suid
make -C ./builddir
make -C ./builddir install

chmod +x /path/to/installation_dir/singularity/bin/singularity
```

Next, since I've a native installation, I also found it useful to set some `ENVIRONMENT` variables so that the `cache` and the `tmp` build files are in a specified 
```
export SINGULARITY_TMPDIR=/path/to/installation_dir
export SINGULARITY_CACHEDIR=/path/to/installation_dir
export SINGULARITY_ENVIRONMENT=/path/to/installation_dir
```

## build, convert and run singualrity container
Then, run this to convert the docker container to singularity:
`singularity build exvivo_dl_segm_tool.sif docker://pulks/docker_hippogang_exvivo_segm:v1.4.0`

Then, convert to `sandbox`:
`singularity build --sandbox exvivo_dl_segm_tool.simg exvivo_dl_segm_tool.sif`

Then, execute the following command to run the container:
`singularity exec --nv --bind /data/username/:/data/exvivo exvivo_dl_segm_tool.img /bin/bash -c "/src/commands_nnunet_inference.sh ${OPTION}"`

## Upload singularity container to DockerHub
Prepare the file to upload to Docker registry:
```
singularity remote login
singularity key newpair
singularity sign exvivo_dl_segn_tool.sif
singularity verfiy exvivo_dl_segn_tool.sif

singularity registry login --username pulks oras://registry-1.docker.io
Password / Token: get it from Docker account.
```

Then, push the image to the Docker registry:
`singularity push exvivo_dl_segn_tool.sif oras://registry-1.docker.io/pulks/exvivo_dl_segm_tool:v1.0.0`

Now, see the commands above to `pull` and `exec` the `sif` image.

### Notes:
- Here is a good reference for some of the cmds I used: https://foss.cyverse.org/10_reproducibility_IV/#pulling-an-image-from-singularity-hub
- YouTube playlist: https://youtu.be/nQTMJ9hqKNI?si=dFW3TGNDjN_FEmXM
