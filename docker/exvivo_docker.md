# Docker and Singularity for postmortem brain MRI

**Author: Pulkit Khandelwal**

Run adult ex vivo MRI segmentation, post-hoc topology correction, cortical surface reconstruction, and atlas parcellation with **`pulks/docker_purple_mri:v1.1.0`**.

[Docker Hub](https://hub.docker.com/r/pulks/docker_purple_mri) · [GitHub](https://github.com/Pulkit-Khandelwal/purple-mri) · [Read the Docs](https://purple-mri.readthedocs.io/en/latest/)

## Choose a workflow

| Option | What it runs |
| --- | --- |
| `exvivo_dl` | Complete adult DL segmentation, component cleanup, post-hoc topology correction, and label merging. |
| `exvivo_surface` | Surface reconstruction and atlas parcellation from an existing corrected Purple segmentation. |
| `exvivo_dl exvivo_surface` | Both workflows, sequentially. |
| `exvivo_all` | Compatibility alias for `exvivo_dl`; retains the legacy `exvivo_all/` output folder. |
| `exvivo_dl_infant`, `exvivo_surface_infant` | Reserved placeholders; not implemented and exit with an explanatory message. |

## 1. Prepare the inputs

Place preprocessed MRI images inside a folder named `data_for_inference`, within your project directory. Input filenames must end in `_0000.nii.gz`, for example:

```text
/data/username/project/data_for_inference/subject_0000.nii.gz
```

Use one hemisphere per image. For surface reconstruction, process left and right hemispheres in separate runs, using `EXVIVO_HEMI=lh` or `EXVIVO_HEMI=rh`. Use absolute paths without spaces.

- **DL inference:** requires an NVIDIA GPU and Docker configured for GPU access for the commands below.
- **Surface reconstruction:** runs on CPU. Provide your FreeSurfer `license.txt` and choose the number of CPU threads.
- **Included in the image:** nnU-Net models, FreeSurfer 7.4.0, Convert3D, Python dependencies, atlas resources, the GM/WM statistics file, and the custom Purple pial-placement binary. No separate FreeSurfer installation or nested Docker invocation is needed.

See [input preprocessing](https://purple-mri.readthedocs.io/en/latest/segmentation.html) before running inference.

## 2. Pull the image

```bash
docker pull pulks/docker_purple_mri:v1.1.0
```

The published image is for **Linux AMD64**. The current `v1.1.0` image selects the updated Task2732 subcortical model in both the combined and standalone workflows.

## 3. Run the complete workflow

Replace `/data/username/project` and `/path/to/license.txt` with your host paths. The directory containing `data_for_inference/` is mounted at `/data/exvivo` inside the container.

```bash
docker run --rm --gpus all --shm-size=8g \
  -v /data/username/project:/data/exvivo \
  -v /path/to/license.txt:/license.txt:ro \
  -e FS_LICENSE=/license.txt \
  -e NO_FSFAST=1 \
  -e EXVIVO_HEMI=rh \
  -e EXVIVO_THREADS=24 \
  pulks/docker_purple_mri:v1.1.0 \
  /bin/bash /src/commands_nnunet_inference.sh exvivo_dl exvivo_surface
```

For a left hemisphere, change `EXVIVO_HEMI=rh` to `EXVIVO_HEMI=lh`. Adjust `EXVIVO_THREADS` to your available CPU resources; this setting controls supported surface-processing tools.

### Adult DL workflow (`exvivo_dl`)

1. Predict the original Purple 10-label segmentation (Task283).
2. Clean connected components: retain the largest component for each anatomical label except WMH and ventricles; preserve WMH components and remove very small ventricular components.
3. Prepare the topology input from the cleaned segmentation: map GM `1 → 3`, labels `2–7, 9, 10 → 2`, and ventricle label `8 → 0`.
4. Run the post-hoc bridged-sulcus model (Task279).
5. Use **label `1` from the raw topology prediction** as the buried-sulcus removal mask. Zero those voxels in the component-cleaned Purple segmentation, preserving all surviving anatomical label values. Raw topology labels `2` and `3` do not mark removal regions.
6. Predict MTL and amygdala subfields (Task269).
7. Predict subcortical structures (Task2732: `Task2732_exvivo_supersynth_lisa_deepgray_flipfixed`).
8. Merge the anatomical predictions and clean residual labels to produce the final merged segmentation.

**Post-hoc topology correction is included automatically in `exvivo_dl`.** It addresses buried sulci and adjoining/bridged gyri; no separate topology command is required for this workflow. For the standalone procedure and remapping details, see [topology correction notes](https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/topology_correction_notes.md).

### Surface workflow (`exvivo_surface`)

The surface stage uses **`05_purple_corrected`**, the corrected Purple 10-label segmentation, together with the original preprocessed MRI. The detailed `11_final_merged` segmentation is a separate output and is not the surface input.

The pipeline prepares segmentation-derived volumes, creates and decimates meshes, computes spatial transforms, corrects surface topology, places white and pial surfaces, and performs atlas parcellation and morphometric measurements.

Required resources are already configured inside the image:

| Resource | Container path |
| --- | --- |
| FreeSurfer | `/opt/freesurfer` |
| External atlas resources | `/opt/purple-mri/freesurfer_atlases/` |
| GM/WM statistics | `/opt/purple-mri/purple_mri/autodet.gw.stats.binary.dat` |
| Custom pial wrapper | `/opt/purple_pial/run-pial.sh` |
| Custom pial executable | `/opt/purple_pial/bin/mris_place_surface` |

The custom pial binary runs directly inside this container. A full `fsaverage/` subject is copied into the surface output directory, alongside the processed subjects, and overlaid with the repository's supplied template surfaces.

## Run either workflow separately

### Segmentation only

No FreeSurfer license mount is needed for DL-only processing.

```bash
docker run --rm --gpus all --shm-size=8g \
  -v /data/username/project:/data/exvivo \
  pulks/docker_purple_mri:v1.1.0 \
  /bin/bash /src/commands_nnunet_inference.sh exvivo_dl
```

### Surface reconstruction from existing corrected segmentations

Keep the corresponding MRI files in `data_for_inference/`. For an MRI named `subject_0000.nii.gz`, the segmentation must be named `subject.nii.gz`, with matching dimensions and spatial geometry.

```bash
docker run --rm --shm-size=8g \
  -v /data/username/project:/data/exvivo \
  -v /path/to/license.txt:/license.txt:ro \
  -e FS_LICENSE=/license.txt \
  -e NO_FSFAST=1 \
  -e EXVIVO_HEMI=rh \
  -e EXVIVO_THREADS=24 \
  -e EXVIVO_SEGM_DIR=/data/exvivo/data_for_inference/output_from_nnunet_inference/exvivo_dl/05_purple_corrected \
  pulks/docker_purple_mri:v1.1.0 \
  /bin/bash /src/commands_nnunet_inference.sh exvivo_surface
```

For outputs from the legacy `exvivo_all` option, change the segmentation path to `.../exvivo_all/05_purple_corrected`. `EXVIVO_SEGM_DIR` must be a path visible inside the container. A GPU is not required for surface-only processing.

## Outputs, logs, and timing

By default, outputs are saved on the host under:

```text
/data/username/project/data_for_inference/output_from_nnunet_inference/
```

| Output | Location beneath that directory |
| --- | --- |
| Original Purple segmentation | `exvivo_dl/01_purple_original/` |
| Component-cleaned Purple segmentation | `exvivo_dl/01b_purple_component_cleaned/` |
| Remapped topology input | `exvivo_dl/02_topology_input/` |
| Raw topology prediction | `exvivo_dl/03_topology_prediction/` |
| Buried-sulcus removal mask | `exvivo_dl/04_buried_sulcus_mask/` |
| Corrected Purple segmentation; surface input | `exvivo_dl/05_purple_corrected/` |
| MTL and amygdala predictions | `exvivo_dl/06_mtl/` |
| Subcortical predictions | `exvivo_dl/07_subcortical/` |
| Merge intermediates | `exvivo_dl/08_initial_merge/` through `10_cleanup_map/` |
| Final merged segmentation | `exvivo_dl/11_final_merged/` |
| Subject surfaces, volumes, parcellations, and statistics | `exvivo_surface/<subject>/{surf,mri,label,stats,scripts}/` |
| Template subject | `exvivo_surface/fsaverage/` |
| Surface processing log | `exvivo_surface/surface_pipeline.log` |
| Surface completion marker | `exvivo_surface/COMPLETE` |
| Per-step timings and workflow totals | `timings_<UTC timestamp>_<process ID>/` |

All intermediate NIfTI files are retained. Results persist on the host after `--rm` removes the container.

Progress and timings print to the terminal. Each timing directory contains:

- `step_timings.tsv`: DL steps, surface setup, and the six main surface stages.
- `run_summary.tsv`: DL, surface, and overall totals for the workflows run.

Both files record UTC start/end times, elapsed seconds, and exit codes. Surface white/pial placement and parcellation are timed together as the final surface stage; individual pial iterations do not have separate timing rows.

To follow the surface log from another terminal:

```bash
tail -F /data/username/project/data_for_inference/output_from_nnunet_inference/exvivo_surface/surface_pipeline.log
```

The surface log is created after input staging and template copying. Check the final exit status and timing records; a successful surface run also writes `COMPLETE`. Inspect the resulting segmentations and surfaces for anatomical quality.

### New runs and output locations

Use fresh DL and surface output directories for new runs. These workflows reject nonempty output directories instead of silently overwriting an earlier run.

Optional Docker environment settings (`-e NAME=/container/path`) are:

| Variable | Purpose |
| --- | --- |
| `EXVIVO_INPUT_DIR` | Override the default `/data/exvivo/data_for_inference` input directory. |
| `EXVIVO_DL_OUTPUT_DIR` | Choose a fresh DL output directory; the combined workflow uses its `05_purple_corrected/` automatically. |
| `EXVIVO_SURFACE_OUTPUT_DIR` | Choose a fresh surface output directory. |
| `EXVIVO_SEGM_DIR` | Select existing corrected segmentations for surface processing. |
| `EXVIVO_TIMING_DIR` | Choose the timing report directory. |
| `EXVIVO_MODEL_OUTPUT_DIR` | Override the output directory for an individual model. |

Keep output paths inside a mounted directory so files remain accessible on the host.

## Individual model options

All existing individual model options remain available. They run the selected model rather than the full DL workflow.

| Option | Model |
| --- | --- |
| `exvivo_t2w` | T2w MRI to Purple 10-label segmentation. |
| `exvivo_flash_more_subcort` | FLASH model with hypothalamus, optic chiasm, anterior commissure, and fornix labels. |
| `exvivo_flash_thalamus` | Thalamus segmentation from FLASH MRI. |
| `invivo_flair_wmh` | WMH segmentation from in vivo FLAIR MRI. |
| `exvivo_umc_strip_cerebellum` | Cerebellum stripping for UMC MRI. |
| `exvivo_posthoc_topology` | Raw post-hoc bridged-sulcus prediction from a prepared segmentation input; see the topology workflow above. |
| `exvivo_multi_sequence_mtl_amygdala_subfields` | MTL and amygdala subfields; trained on CISS/T2w/FLASH MRI. |
| `exvivo_multi_sequence_subcortical` | Subcortical structures; trained on CISS/T2w/FLASH MRI. |

For example:

```bash
docker run --rm --gpus all --shm-size=8g \
  -v /data/username/project:/data/exvivo \
  pulks/docker_purple_mri:v1.1.0 \
  /bin/bash /src/commands_nnunet_inference.sh exvivo_multi_sequence_subcortical
```

Individual model outputs default to `data_for_inference/output_from_nnunet_inference/`.

## Note on WMH segmentation in in vivo FLAIR MRI

Use `invivo_flair_wmh` as the option in the individual-model command above. The input must be skull-stripped and normalized/standardized. Inference has typically taken approximately one minute; runtime depends on the GPU and input volume.

## Singularity / Apptainer (Linux AMD64)

Use the same `purple_mri_v1.1.0.sif` file with Singularity or Apptainer. Docker is not required to run the SIF. The Python `purple-mri` CLI currently launches Docker; invoke Singularity/Apptainer directly for these examples.

The SIF distribution target is **`pulks/singularity_purple_mri:v1.1.0`** on Docker Hub. Publication and a fresh pull must be confirmed before announcing this URL as available. The existing Docker image stays at `pulks/docker_purple_mri:v1.1.0`.

### Download the SIF

After the maintainer publishes the artifact:

```bash
singularity pull purple_mri_v1.1.0.sif \
  oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.1.0
```

For Apptainer, replace `singularity` with `apptainer`. This downloads the prebuilt SIF (approximately 18 GB). Do not use `docker pull` for this artifact. If a release checksum file is provided, verify it with `sha256sum -c purple_mri_v1.1.0.sif.sha256`.

Alternatively, build a SIF from the Docker image; this requires downloading and converting its layers:

```bash
singularity pull purple_mri_v1.1.0.sif \
  docker://pulks/docker_purple_mri:v1.1.0
```

The converted file need not have the same checksum as the distributed SIF.

### Example: complete adult DL, then surfaces

Edit the four paths below and choose `HEMI=lh` or `rh`. Input files must be named `subject_0000.nii.gz`. Use a new output directory for each run. The commands run actual MRI processing; they are not preflight checks.

DL uses an NVIDIA GPU via `--nv`. Surfaces run in a separate CPU invocation **without `--nv`**. This avoids importing host OpenGL libraries that can conflict with the container's glibc and break VTK.

The per-model writable `fold_0` mounts are required because nnU-Net initializes these directories even when loading the packaged `all` checkpoint. They contain runtime scratch files; the model weights remain inside the SIF.

```bash
(
set -euo pipefail
RUNTIME=singularity   # or: apptainer
SIF="/absolute/path/purple_mri_v1.1.0.sif"
INPUT="/absolute/path/data_for_inference"
OUTPUT="/absolute/path/new_purple_results"
LICENSE="/absolute/path/license.txt"
HEMI=lh
THREADS=20

# Prevent inherited runtime flags from adding GPU libraries to the CPU stage.
unset SINGULARITY_NV APPTAINER_NV
[[ -s "$SIF" && -d "$INPUT" && -s "$LICENSE" ]]
if [[ -e "$OUTPUT" ]]; then
  echo "Choose a new OUTPUT directory: $OUTPUT" >&2
  exit 2
fi
mkdir -p "$OUTPUT"

MODEL_ROOT=/src/nnunet_paths_that_it_requires/nnUNet/3d_fullres
TRAINER=nnUNetTrainerV2__nnUNetPlansv2.1
MODEL_BINDS=()
for TASK in \
  Task283_exvivo_cuts_prediction_medial_cleaned_single_channel \
  Task279_exvivo_flash_mri_gm_wm_sulcus_patches_posthoc_topology_correction \
  Task269_exvivo_mtl_hemis_subfields_fmv2_multi_sequence \
  Task2732_exvivo_supersynth_lisa_deepgray_flipfixed; do
  mkdir -p "$OUTPUT/nnunet_runtime/$TASK/fold_0"
  MODEL_BINDS+=(--bind "$OUTPUT/nnunet_runtime/$TASK/fold_0:$MODEL_ROOT/$TASK/$TRAINER/fold_0:rw")
done

"$RUNTIME" exec --cleanenv --nv \
  --bind "$INPUT:/inputs:ro" --bind "$OUTPUT:/outputs:rw" \
  "${MODEL_BINDS[@]}" --pwd /outputs \
  --env EXVIVO_INPUT_DIR=/inputs \
  --env EXVIVO_DL_OUTPUT_DIR=/outputs/exvivo_dl \
  --env EXVIVO_TIMING_DIR=/outputs/timings_dl \
  "$SIF" /bin/bash /src/commands_nnunet_inference.sh exvivo_dl \
  2>&1 | tee "$OUTPUT/dl.log"

"$RUNTIME" exec --cleanenv \
  --bind "$INPUT:/inputs:ro" --bind "$OUTPUT:/outputs:rw" \
  --bind "$LICENSE:/license.txt:ro" --pwd /outputs \
  --env EXVIVO_INPUT_DIR=/inputs \
  --env EXVIVO_SEGM_DIR=/outputs/exvivo_dl/05_purple_corrected \
  --env EXVIVO_SURFACE_OUTPUT_DIR=/outputs/exvivo_surface \
  --env EXVIVO_TIMING_DIR=/outputs/timings_surface \
  --env "EXVIVO_HEMI=$HEMI" --env "EXVIVO_THREADS=$THREADS" \
  --env FS_LICENSE=/license.txt --env NO_FSFAST=1 \
  "$SIF" /bin/bash /src/commands_nnunet_inference.sh exvivo_surface \
  2>&1 | tee "$OUTPUT/surface.log"
)
```

For DL only, omit the second runtime invocation. For surfaces only, use the second invocation with a fresh surface output directory, and bind an existing corrected-label directory at `/segmentations:ro`, setting `EXVIVO_SEGM_DIR=/segmentations`. Match `subject.nii.gz` labels to `subject_0000.nii.gz` MRI files. Use the corrected 10-label result, not `11_final_merged`.

Outputs under `OUTPUT`:

- `exvivo_dl/05_purple_corrected/`: corrected Purple 10-label NIfTI segmentations used for surfaces.
- `exvivo_dl/11_final_merged/`: merged DL NIfTI segmentations.
- `exvivo_surface/<subject>/`: FreeSurfer-style surfaces, annotations, statistics and parcellation volumes.
- `exvivo_surface/COMPLETE`: successful surface-stage completion marker.
- `timings_dl/`, `timings_surface/`, `dl.log`, `surface.log`: timings and logs.

### Example: subcortical segmentation only (Task2732)

```bash
(
set -euo pipefail
RUNTIME=singularity
SIF="/absolute/path/purple_mri_v1.1.0.sif"
INPUT="/absolute/path/data_for_inference"
OUTPUT="/absolute/path/new_subcortical_results"
MODEL=/src/nnunet_paths_that_it_requires/nnUNet/3d_fullres/Task2732_exvivo_supersynth_lisa_deepgray_flipfixed/nnUNetTrainerV2__nnUNetPlansv2.1
[[ ! -e "$OUTPUT" ]] || { echo "Choose a new OUTPUT directory" >&2; exit 2; }
mkdir -p "$OUTPUT/fold_0"
"$RUNTIME" exec --cleanenv --nv \
  --bind "$INPUT:/inputs:ro" --bind "$OUTPUT:/outputs:rw" \
  --bind "$OUTPUT/fold_0:$MODEL/fold_0:rw" --pwd /outputs \
  --env EXVIVO_INPUT_DIR=/inputs \
  --env EXVIVO_MODEL_OUTPUT_DIR=/outputs/predictions \
  --env EXVIVO_TIMING_DIR=/outputs/timings \
  "$SIF" /bin/bash /src/commands_nnunet_inference.sh \
  exvivo_multi_sequence_subcortical 2>&1 | tee "$OUTPUT/run.log"
)
```

### Runtime requirements and tested scope

- NVIDIA GPU and compatible host driver for DL; a user-supplied FreeSurfer license for surfaces.
- A working Singularity/Apptainer installation. Some unprivileged installations require `squashfuse` on `PATH` to mount SIF images. This is a host runtime dependency, not a missing file inside the SIF.
- If the runtime reports `Read-only file system` at a model's `fold_0`, check the writable model mounts above.
- If VTK reports `GLIBC_2.38 not found` from `/.singularity.d/libs/libGLdispatch.so.0`, run surfaces without `--nv`; do not combine both stages into one GPU-enabled SIF invocation.
- The Task2732 package lacks nnU-Net automatic postprocessing metadata. Inference can finish successfully while reporting that automatic postprocessing was skipped.

Validation on 2026-10-21: Docker standalone Task2732, full DL, and LH surface/parcellation runs completed successfully. Singularity Task2732 GPU inference completed successfully; all four checkpoints were CPU-readable; GPU computation and LH surface dependency/input/conversion preflights passed. **Full Singularity DL plus surface reconstruction has not been run end to end.** Apptainer commands use the equivalent interface but have not been live-tested for this release.

Maintainer reference: [Singularity SIF push](https://docs.sylabs.io/guides/3.8/user-guide/cli/singularity_push.html) and [Docker Hub OCI artifacts](https://docs.docker.com/docker-hub/repos/manage/hub-images/oci-artifacts/).

## Change Logs

### 10/12/2026 — `docker_purple_mri:v1.1.0`

- Published the combined DL and surface image under `pulks/docker_purple_mri:v1.1.0`; image contents match the previous `docker_hippogang_exvivo_segm:v1.4.7`.
- Added `exvivo_dl`, `exvivo_surface`, and sequential `exvivo_dl exvivo_surface` usage; retained `exvivo_all` as a compatibility alias.
- Included mandatory component cleanup and post-hoc buried-sulcus removal in the full DL workflow, retaining intermediate NIfTI outputs.
- Bundled FreeSurfer, Convert3D, atlas resources, GM/WM statistics, and the custom Ubuntu 20.04-compatible pial binary.
- Added hemisphere selection, surface CPU-thread configuration, per-step timing reports, and workflow totals.
- Reserved infant workflow names as unimplemented placeholders.

### Historical releases — `docker_hippogang_exvivo_segm` through `v1.4.6`

The entries below describe the previous repository and version numbering. Use the new image name in the instructions above for current runs. Historical Singularity entries do not imply that a matching `v1.1.0` Singularity image is published.

#### 10/06/2026

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

#### 02/01/2026

- Updated version `v1.4.5` and added three new models:
  - Model trained on FLASH MRI for GM/WM segmentation.
  - Model trained for post-hoc topology correction, i.e., it helps with the bridged-sulcus problem.
  - Model to strip the cerebellum from the UMC MRI.

#### 12/09/2025

- Fixed the NumPy core module issue due to version mismatch (`v1.4.4`).

#### 11/19/2025

- Added the FLASH model for thalamus segmentation (`v1.4.3`).

#### 05/05/2025

- Added the latest 10-label voxel-level segmentation (`v1.4.2`). This version cleans up GM/WM mis-segmentations in the medial area, predicts missing regions corresponding to sampling cuts, and addresses some anterior/posterior signal dropout issues. The Docker image was also made more lightweight.

#### 10/10/2024

- Added documentation for the post-hoc topology correction Docker.

#### 09/03/2024

- Added support for Singularity. See the Singularity documentation for details. Latest tag for Singularity: `1.0.0`.
- Uploaded the Singularity image to Docker Hub.

#### 08/30/2024

- Updated `docker_hippogang_exvivo_segm:v1.4.0` with the model that includes the MTL, ventricles, and corpus callosum.
- Added models trained on CISS/T2w MRI and additional T2*w MRI segmentation labels.
- Updated the Docker run command to accept an option specifying which model to run.
- Updated the Dockerfile to support inference on Ampere GPUs (CUDA > 11).

#### 07/16/2024

- Version `docker_hippogang_exvivo_segm:v1.3.1` made Singularity-compatible by removing a copy command in the bash script.

#### 10/22/2022

- Version `docker_hippogang_exvivo_segm:v1.3.0` now automatically segments white matter.
- Version `docker_hippogang_exvivo_segm:v1.2.0` added segmentation of WMH in `in vivo` FLAIR images used for the Detre/Sandy project on ADNI data.
- A `logs.txt` file is also generated in the folder where the Docker container is run.

#### 10/19/2022

- First created.
- Initial bare-bones version: `docker_hippogang_exvivo_segm`.
