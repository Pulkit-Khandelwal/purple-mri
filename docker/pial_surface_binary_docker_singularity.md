# Important note on pial surface placement

For **pial surface placement only**, the `purple-mri` parcellation workflow uses a custom compiled FreeSurfer `mris_place_surface` binary. To avoid requiring users to compile this binary locally, we provide it as a Docker image archive through the GitHub release:

`https://github.com/Pulkit-Khandelwal/purple-mri/releases/tag/v0.1.0-fs-binary-docker`

Download the release asset `purple-mris-place-surface_ubuntu24.tar.gz` and place it inside the `purple_mri/` folder of this repository.
Or the direct link to download:

`wget -O purple-mris-place-surface_ubuntu24.tar.gz https://github.com/Pulkit-Khandelwal/purple-mri/releases/download/v0.1.0-fs-binary-docker/purple-mris-place-surface_ubuntu24.tar.gz`

The Dockerized/Singularity-converted binary is called from inside `parcellation.sh`. See the wrapper and usage beginning here:

`https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/purple_mri/parcellation.sh#L58`

## Option 1: Docker

From inside the `purple_mri/` folder, load the Docker image:

    `docker load < purple-mris-place-surface_ubuntu24.tar.gz`

Confirm that the image loaded correctly:

    `docker images | grep purple-mris-place-surface`

You should see an image named:

    `purple-mris-place-surface:ubuntu24`

Test the image:

    `docker run --rm purple-mris-place-surface:ubuntu24`

If the command prints a FreeSurfer usage message or an argument-related error, the image is loaded and runnable.

## Option 2: Singularity

If Docker is not available on your cluster, the same archive can be converted to a Singularity image.

From inside the `purple_mri/` folder, first uncompress the Docker archive:

    `gunzip -c purple-mris-place-surface_ubuntu24.tar.gz > purple-mris-place-surface_ubuntu24.tar`

Then build the Singularity image:

    `singularity build purple-mris-place-surface_ubuntu24.sif docker-archive://purple-mris-place-surface_ubuntu24.tar`

Test the Singularity image:

    `singularity exec purple-mris-place-surface_ubuntu24.sif which mris_place_surface`

    `singularity exec purple-mris-place-surface_ubuntu24.sif mris_place_surface`

If the command prints the path to `mris_place_surface` and then a FreeSurfer usage message or an argument-related error, the Singularity image is working.

Now, please proceed to the next steps!
