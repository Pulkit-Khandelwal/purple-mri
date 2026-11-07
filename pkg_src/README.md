# purple-mri Python package

Penn Utilities for Registration and Parcellation of Ex vivo MRI.

The lightweight Python CLI runs the Purple Docker pipeline. The container supplies
trained models, FreeSurfer, Convert3D, atlas resources and the custom pial binary.
Use Python 3.9+ on a Linux Docker host, NVIDIA Docker GPU support for inference,
and a FreeSurfer license for surface and atlas processing.

[Source](https://github.com/Pulkit-Khandelwal/purple-mri) ·
[Documentation](https://purple-mri.readthedocs.io/en/latest/) ·
[Docker](https://hub.docker.com/r/pulks/docker_purple_mri)

## Install

```bash
python3 -m venv ~/venvs/purple-mri
source ~/venvs/purple-mri/bin/activate
python -m pip install 'purple-mri==1.2.0'
purple-mri --version
purple-mri pull
purple-mri doctor
```

A downloaded release wheel can also be installed offline:

```bash
python -m pip install --no-index --no-deps ./purple_mri-1.2.0-py3-none-any.whl
```

The default image is `pulks/docker_purple_mri:v1.2.0`. Each run resolves it to an
immutable local image ID, which is recorded with registry digests and input
checksums in `purple_run.json`. `--image` selects another compatible image;
`--pull` explicitly refreshes it. `doctor` checks Docker access and image metadata.
`models` lists the named model selections. Model-file and native-grid checks run
inside the container.

## Full segmentation, surfaces and atlas merges

Prepare single-channel files named `SUBJECT_0000.nii.gz`. Use one contrast and one
hemisphere per batch. Choose the actual hemisphere with `--hemi lh` or `--hemi rh`.

```bash
purple-mri run exvivo_dl exvivo_surface \
  --contrast flash --hemi rh \
  --input /absolute/path/inputs \
  --output /absolute/path/new_results \
  --license /absolute/path/license.txt \
  --threads 8 --gpus device=0
```

Choose `t2w`, `ciss`, `flash` or `t2star`. T2* uses the FLASH route. This command
runs the DL tissue merge, creates the reconstruction label map, reconstructs the
selected hemisphere, corrects Brainnetome annotation assignments, projects atlas
labels and merges seven atlases with the detailed tissue labels.

| Contrast | DL route |
| --- | --- |
| T2w / CISS | Task283, component cleanup, Task279 topology, Task269 MTL, Task2732 subcortical, tissue merge |
| FLASH / T2* | The same foundation plus Task278 for cortical GM and buried-sulcus refinement, followed by the FLASH tissue merge |

The container applies MTL rim correction to the detailed tissue merge for all four
contrasts. The FLASH route removes disconnected GM components before surface-label
creation and atlas assignment. For either hemisphere, Brainnetome correction uses
nearby valid assignments inside the selected cortex before projection. Atlas
merging assigns residual generic cortical GM to cortical parcels while preserving
WM, MTL and subcortical labels. These algorithms run in Docker; the Python launcher
passes the contrast, hemisphere and processing options to that implementation.

Add `--dry-run` to validate host filenames and print argv without creating results
or starting Docker. Add `--preflight-only` to run container input/model checks
without processing; use a separate output directory for this preflight record.
Preflight completion is recorded as `kind: preflight`.

## Outputs

Paths are relative to `--output` for a full run:

| Path | Contents |
| --- | --- |
| `dl/05_purple_corrected/` | Baseline topology-corrected Purple segmentation |
| `dl/06_mtl/`, `dl/07_subcortical/` | Detailed model predictions |
| `dl/13_flash_task278/`, `dl/13b_flash_task278_cleaned/` | Raw and cleaned Task278 predictions for FLASH/T2* |
| `dl/11_final_merged/` | Detailed merged tissue map; cortical GM is 101 and WM is 107 |
| `dl/12_surface_labels/` | Reconstruction map with codes 0–10; detailed MTL labels collapse to 10 |
| `surface/SUBJECT/{surf,label,mri,stats,qc}/` | Meshes, annotations, projected atlases, metrics and provenance |
| `atlases/SUBJECT/` | Seven final cortical atlas merges, lookup tables and reports |
| `timings/` | Timing reports |
| `purple_run.json`, `cli_history/` | Current container status and prior resumed attempts |

`12_surface_labels` is generated from the detailed tissue merge **before** cortical
reconstruction. Codes 1–10 are the foreground vocabulary; an individual case can
have fewer nonempty labels. `11_final_merged` retains detailed structures and
cortical GM 101. The final atlas merges replace cortical GM 101 with atlas parcels.

The seven merged atlases are DKT, Destrieux, Glasser, Schaefer400, Economo, Julich
and Brainnetome. Check `dl/STRUCTURES_COMPLETE`, `surface/COMPLETE`,
`atlases/COMPLETE`, the run exit status, reports and anatomical alignment.

## DL only and individual models

```bash
purple-mri run exvivo_dl --contrast ciss \
  --input /absolute/path/inputs --output /absolute/path/new_dl_results

purple-mri run exvivo_flash_gm_wm --contrast flash \
  --input /absolute/path/inputs --output /absolute/path/task278_results

purple-mri run exvivo_multi_sequence_subcortical \
  --input /absolute/path/inputs --output /absolute/path/subcortical_results
```

`exvivo_all` is an alias for DL only. Individual models write `predictions/`.
`exvivo_flash_gm_wm` selects Task278 and accepts FLASH/T2* (defaults to FLASH).
Task278 alone produces its three-label prediction; use `exvivo_dl` for the complete
FLASH tissue merge. The single-model subcortical option selects Task2732.

## Reuse completed v1.2.0 results

Surface processing uses the **complete DL root**, including `11_final_merged` and
`12_surface_labels`. It also performs the final atlas merges:

```bash
purple-mri run exvivo_surface --contrast flash --hemi rh \
  --input /absolute/path/inputs \
  --dl-dir /absolute/path/previous_results/dl \
  --output /absolute/path/new_surface_results \
  --license /absolute/path/license.txt --threads 8
```

The reused DL root is writable because the container records surface checkpoints
there. This command writes new surfaces and atlas merges beneath its `--output`.

To merge already projected atlases without repeating reconstruction or projection:

```bash
purple-mri run exvivo_atlas_merge --contrast flash --hemi rh \
  --input /absolute/path/inputs \
  --dl-dir /absolute/path/previous_results/dl \
  --surface-dir /absolute/path/previous_results/surface \
  --output /absolute/path/new_atlas_results \
  --license /absolute/path/license.txt --threads 8
```

This mounts both reused roots read-only. The container validates surface/annotation
provenance and hashes before merging. MRI, output and reuse directories must be
separate and non-nested. Surface-only, atlas-only and merge-only commands use CPU.

`exvivo_merge --contrast ... --dl-dir ...` completes the tissue merge in a prediction
root whose final merge has not yet run. It writes the tissue merge and reconstruction
labels **in the supplied DL root**. Use the original pipeline command with `--resume`
to continue a prior CLI run. Surface/projection provenance must match the resulting labels.

## Resume and cancellation

Repeat the **same processing command** with `--resume` and the same output folder.
The CLI checks image ID, input checksums, contrast, hemisphere, paths, threads and
merge settings; the container checks stage dependencies and output hashes. Input
or processing changes require a new output directory. Resume applies to pipeline
runs started with this CLI, and preserves earlier records in `cli_history/`.

```bash
# Append this option to the original processing command:
# --resume
```

The CLI records the container ID before starting and reads its actual exit status.
`Ctrl+C` stops only this run's verified container, with 30 seconds grace. Successful
containers are removed; failed or unconfirmed containers remain available for
`docker logs` and inspection. A still-active previous container blocks resume.
Use tmux or a scheduler for long runs; detach from tmux with Ctrl+B, then D.

## Upgrade from 1.1.0

| 1.1.0 usage | 1.2.0 usage |
| --- | --- |
| Pipeline without contrast | Add `--contrast t2w`, `ciss`, `flash` or `t2star` |
| `--segmentation .../05_purple_corrected` | Use `--dl-dir` with the complete v1.2.0 DL root |
| `OUTPUT/exvivo_dl`, `OUTPUT/exvivo_surface` | `OUTPUT/dl`, `OUTPUT/surface`, `OUTPUT/atlases` |
| New output per attempt | New output initially; explicit matching `--resume` for later attempts |

## Historical native workflow

The seven-positional-argument RH-only native launcher remains available:

```bash
python -m pip install 'purple-mri[legacy]==1.2.0'
purple-mri legacy-surface \
  /path/to/freesurfer /path/to/output /path/to/mri /path/to/segmentation \
  /path/to/atlases 20 /path/to/autodet.gw.stats.binary.dat
```

Its seventh argument is a statistics file. It uses the original host scripts and
requires their FreeSurfer/c3d environment and atlas resources. The existing
installed shell commands and `python -m purple_mri` entry point are retained.

## Development

```bash
PYTHONPATH=pkg_src python -m unittest discover -s tests -v
python -m pip install build twine
python -m build
python -m twine check --strict dist/*
```

Root and `pkg_src/` builds use the same package source and metadata. CLI tests check
routing, paths, lifecycle and resume behavior; anatomical QC uses the output MRI,
label maps, surfaces and reports. Singularity is distributed separately at
`oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.2.0`.
