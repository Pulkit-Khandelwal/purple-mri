# Build purple-mri from source

Build target: `pulks/docker_purple_mri:v1.1.0` (Linux AMD64).

This folder combines the adult DL pipeline, surface reconstruction, timing
updates, and custom pial build. It starts from NVIDIA CUDA 11.8 / Ubuntu 20.04
and does not require the old `docker_hippogang_exvivo_segm` image.

## Files included

| File or folder | Purpose |
| --- | --- |
| `Dockerfile`, `build.sh`, `.dockerignore` | Build the combined image and limit its build context. |
| `check_build_inputs.py` | Check external inference models before building. |
| `requirements.txt`, `surface_requirements.txt` | Separate DL and surface dependencies. |
| `sitecustomize.py` | Existing NumPy checkpoint compatibility aliases. |
| `commands_nnunet_inference.sh` | Adult DL, surface, individual-model, and placeholder infant options. |
| `merge_exvivo.py` | Component cleanup, topology helpers, and merging. |
| `run_exvivo_surface.sh`, `surface_inputs.py` | Surface setup and input validation. |
| `exvivo_timing.sh` | Step and total timing reports. |
| `network_architecture/`, `network_trainer/` | Custom nnU-Net modules, including `modules_pulkit.py`. |
| `surface/` | The container's working surface scripts and `autodet.gw.stats.binary.dat`. |
| `fetch_surface_resources.py`, `resource_manifest.json` | Download pinned atlas and template resources. |
| `pial/` | Compile, collect, and validate the custom pial executable. |
| `assets/` | Ignored location for separately supplied inference models. |

The container surface scripts are included here because they contain the direct
pial invocation and timing integration used by the published image. They do not
replace the repository's standalone `purple_mri/` scripts.

## External assets

The source archive does not contain model weights, compiled binaries,
FreeSurfer/Convert3D installations, MRI data, or license files.

Place the trained model files under:

```text
docker/docker_files/assets/nnunet_paths_that_it_requires/nnUNet/3d_fullres/
```

Preserve the original Task folder names and trainer subfolders. Each task needs:

```text
Task283_<original-task-name>/
  nnUNetTrainerV2__nnUNetPlansv2.1/
    plans.pkl
    postprocessing.json                 # if provided by the trained model
    all/
      model_final_checkpoint.model
      model_final_checkpoint.model.pkl
      postprocessing.json               # if provided by the trained model
```

Include Tasks **101, 269, 273, 276, 279, 283, 289, and 451** to support every
launcher option. Task451 uses `nnUNetTrainerWMHV2__nnUNetPlansv2.1`; the other
tasks use `nnUNetTrainerV2__nnUNetPlansv2.1`.

The launcher selects `-f all` and the final checkpoint. Numbered folds, training
images, validation outputs, and training logs are not required by these commands.
The Docker build context permits only plans, postprocessing JSON, and the
fold-all final checkpoint pair from the model tree. Do not rename or substitute
checkpoint metadata files.

FreeSurfer 7.4.0, Convert3D 1.0.0, and the atlas/template resources are downloaded
during the build. Custom pial source is fetched at the pinned FreeSurfer revision
and patched during compilation. Existing repository atlas directories do not
need to be copied into this build context.

## Build

Requirements: Docker with the standard local build backend, Python 3 for the
input checker, internet access, and sufficient disk space for the full image,
downloaded archives, and build cache. An NVIDIA GPU is needed for GPU inference,
not for compiling the image.

```bash
cd docker/docker_files
bash build.sh
```

This first builds the local `purple-pial:ubuntu20-test` image, then copies its
validated runtime into the combined image. It does not run Docker inside a
container. Running `docker build` on the main Dockerfile directly requires that
the local pial image has already been built.

To test a rebuild without replacing the published version's local tag:

```bash
IMAGE_TAG=pulks/docker_purple_mri:build-test BUILD_JOBS=4 bash build.sh
```

`BUILD_JOBS` controls pial compilation. `EXVIVO_THREADS` controls supported
surface tools when running the image; they are separate settings.

The pial recipe retains the working fixes: shallow source fetch without
`--filter`, and copying `LICENSE.txt` from the pinned FreeSurfer source.

## Dependency and build status

The uploaded DL requirements and package version specifications are preserved.
They include unpinned packages and legacy version constraints, so they are not
an exact lockfile of the published image. A fresh package installation may
resolve differently or encounter dependency conflicts; this source bundle does
not claim a byte-identical rebuild of the existing image.

The combined from-source Dockerfile has been assembled and checked for local
file completeness and shell/Python syntax. A full Docker build and GPU inference
have not been run for this reorganized recipe. The source scripts came from the
working DL/surface and timed-update build folders.

The public Dockerfile verifies HTTPS certificates. The machine-specific
certificate bundle and download verification bypass from the original local
build are not included. On a network with TLS interception, configure the
institution's trusted CA in the build environment before downloading resources.

## Pipeline behavior preserved

- Adult stages: `exvivo_dl`, `exvivo_surface`, or `exvivo_dl exvivo_surface`.
- `exvivo_all` retains the legacy output folder default.
- Infant stages remain explicit unimplemented placeholders.
- Largest-component cleanup preserves all WMH components; ventricular
  components smaller than **5 mm³** are removed, matching the supplied code.
- Raw Task279 label `1` removes voxels from the cleaned Purple segmentation.
- Surface processing uses `05_purple_corrected`, and copies `fsaverage` alongside
  output subjects.
- The supplied surface preparation retains the existing right-coded anatomical
  volume-label convention; `EXVIVO_HEMI` selects the surface hemisphere.
- `NO_FSFAST=1`, per-step timing, and the custom pial wrapper are included.

## Run and publish

Use [the Docker user guide](../exvivo_docker.md) for MRI preparation, license
mounting, workflow commands, and outputs. A FreeSurfer license is supplied at
runtime, not embedded in the image.

After validating a rebuild, publish explicitly:

```bash
docker login -u pulks
docker push pulks/docker_purple_mri:v1.1.0
```

The build scripts do not push images automatically.

## Apply this folder to the GitHub repository

In your local clone, rename the existing folder:

```bash
git mv docker/segmentation_docker docker/docker_files
```

Then copy this archive's `docker/docker_files/` contents into that renamed folder,
including `.dockerignore` and `.gitignore`. Review `git diff` before committing.
Update any repository links referencing `docker/segmentation_docker/` to the new
`docker/docker_files/` path. This archive does not change the remote repository.

[Project](https://github.com/Pulkit-Khandelwal/purple-mri) ·
[Documentation](https://purple-mri.readthedocs.io/en/latest/)
