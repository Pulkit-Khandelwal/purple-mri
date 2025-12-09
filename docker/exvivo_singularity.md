# This is a bare-bones guide to use the exvivo docker via Apptainer/Singurality.
### First, read the docker instructions [here](https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md).

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
  
