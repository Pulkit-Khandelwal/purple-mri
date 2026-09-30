# This is a bare-bones guide to use the exvivo docker via Apptainer/Singurality.
### First, read the docker instructions [here](https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md) for Docker and to see how to organize the files and which options to select.

## Docker Usage
Suppose this is what you ran for Docker:
```
docker run --gpus all --privileged \
  -v /path/to/docker_stuff/:/data/exvivo/ \
  -it pulks/docker_hippogang_exvivo_segm:v1.4.4 \
  /bin/bash -c "bash /src/commands_nnunet_inference.sh exvivo_flash_thalamus"
```

## Apptainer Usage
### Pull the Docker image into a local .sif file
```
BASE="/path/to/docker_stuff"
mkdir -p "$BASE/images"
SIF="$BASE/images/hippogang_exvivo_segm_v1.4.4.sif"
apptainer pull "$SIF" docker://pulks/docker_hippogang_exvivo_segm:v1.4.4
```

### Run image with Apptainer
```
apptainer exec \
  --nv \
  --bind /path/to/docker_stuff:/data/exvivo \
  "$SIF" \
  bash -c "bash /src/commands_nnunet_inference.sh exvivo_flash_thalamus"
```

### Alternatively, use Singularity
```
singularity pull "$SIF" docker://pulks/docker_hippogang_exvivo_segm:v1.4.4
```

```
singularity exec \
  --nv \
  --bind /path/to/docker_stuff:/data/exvivo \
  "$SIF" \
  bash -c "bash /src/commands_nnunet_inference.sh exvivo_flash_thalamus"
```

# Convert Docker to Singularity
I converted the Docker image to Singularity and it should run on a linux machine with a GPU. Functionality remains the same.

Pull the latest `sif` image:
The {LATEST_TAG} is the same as the Docker image.
`singularity pull exvivo_dl_segm_pull.sif oras://registry-1.docker.io/pulks/exvivo_dl_segm_tool:v{LATEST_TAG}`

Run the following command:
`singularity exec --nv --bind /data/username/:/data/exvivo exvivo_dl_segm_pull.sif /bin/bash -c "/src/commands_nnunet_inference.sh ${OPTION}"`

### FOR DEVELOPERS ONLY
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

