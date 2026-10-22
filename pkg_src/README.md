# purple-mri Python package

Penn Utilities for Registration and Parcellation of Ex vivo MRI.

This package provides a lightweight command-line interface to the adult Purple
Docker pipeline. Model weights, FreeSurfer, Convert3D and the custom pial binary
remain in the container; **pip does not install or download them**. Installing the
base package does not install PyTorch or the native surface stack.

Source: https://github.com/Pulkit-Khandelwal/purple-mri

Documentation: https://purple-mri.readthedocs.io/en/latest/

Start with the [quick start](https://purple-mri.readthedocs.io/en/latest/quickstart.html).
For commands without the Python launcher, see
[direct Docker usage](https://purple-mri.readthedocs.io/en/latest/docker.html).
For remote processing without this package, see the
[ITK-SNAP/DSS guide](https://purple-mri.readthedocs.io/en/latest/itksnap.html).
The illustrated service is an RH-only test registration; availability depends
on an active provider and account access.
This repository README receives documentation corrections after release; it does
not replace the metadata embedded in the already published 1.1.0 distributions.

## Install version 1.1.0

Use Python 3.9 or newer. Version 1.1.0 is published on PyPI:

```bash
python3 -m venv ~/venvs/purple-mri
source ~/venvs/purple-mri/bin/activate
python -m pip install 'purple-mri==1.1.0'
purple-mri --version
purple-mri --help
```

For offline installation, use the matching published release wheel:

```bash
python -m pip install --no-index --no-deps --upgrade ./dist/purple_mri-1.1.0-py3-none-any.whl
```

From a source checkout, use `python -m pip install .`. Installing from `pkg_src/`
is also supported. Both build configurations package the same source. Package
version `1.1.0` accompanies Docker tag `v1.1.0`; they are separate artifacts.

Actual container execution needs a Linux Docker host. Deep-learning stages need
an NVIDIA GPU and Docker GPU support; surface-only runs do not request a GPU.
FreeSurfer license files and MRI data must remain local, not in this package.

## Pull and inspect the image

```bash
purple-mri pull
purple-mri doctor
purple-mri models
```

The default image is `pulks/docker_purple_mri:v1.1.0`. `pull` explicitly downloads
the current tag. `doctor` checks Docker access and the local image, not GPU
compatibility, model integrity or segmentation accuracy. `models` lists expected
task selections; it is not proof that every optional checkpoint is bundled.
Task289 requires its external model asset if it is absent from your image.

Every real run resolves the local tag to its immutable image ID and records that
ID, registry digests, package version, stages and exit status in
`OUTPUT/purple_run.json`. `--pull` refreshes the tag before this resolution. The
mutable `v1.1.0` tag alone is not sufficient provenance for reproducible research.

## Combined segmentation and surfaces

Place single-channel input files such as `subject_0000.nii.gz` in an input folder.
Use **one hemisphere per batch** and a new, separate output directory:

```bash
purple-mri run exvivo_dl exvivo_surface \
  --input /path/to/data_for_inference \
  --output /path/to/purple_results \
  --hemi rh \
  --license /path/to/license.txt \
  --threads 20 \
  --pull
```

Use `--hemi lh` for left-hemisphere input; do not manually flip the MRI.
Add `--dry-run` to validate host paths and print the command without pulling,
creating output files or starting a container. Dry-run checks names and file
presence, not NIfTI contents or geometry. The container performs its own checks.

The combined workflow runs Purple Task283, cleanup, Task279 post-hoc topology
correction, Task269 MTL/amygdala inference, Task2732 flip-fixed subcortical
inference, and label merging, then reconstructs surfaces using
`exvivo_dl/05_purple_corrected`. It retains container timing reports.

Outputs under `--output`:

| Path | Contents |
| --- | --- |
| `exvivo_dl/` | Segmentation intermediates, corrected Purple and final merged labels |
| `exvivo_surface/` | Subject surfaces, atlas parcellations, statistics and fsaverage |
| `timings/` | Container timing reports |
| `purple_run.json` | Image and run provenance |

Unlike direct Docker examples, the CLI binds separate input and output folders.
Input and license mounts are read-only. Output must be new or empty; there is no
implicit overwrite or resume. `exvivo_all` remains an alias, but the CLI explicitly
uses `exvivo_dl/` as its output directory for either spelling.

## DL only and individual models

```bash
purple-mri run exvivo_dl \
  --input /path/to/data_for_inference --output /path/to/dl_results

purple-mri run exvivo_multi_sequence_subcortical \
  --input /path/to/data_for_inference --output /path/to/subcortical_results
```

Individual model outputs are written to `OUTPUT/predictions/`. All existing adult
model option names are retained. Infant container stages are not implemented.

## Surfaces from existing corrected segmentations

```bash
purple-mri run exvivo_surface \
  --input /path/to/data_for_inference \
  --segmentation /path/to/previous_results/exvivo_dl/05_purple_corrected \
  --output /path/to/new_surface_results \
  --hemi rh --license /path/to/license.txt --threads 20
```

Input `subject_0000.nii.gz` must have a corresponding corrected
`subject.nii.gz`. Use **corrected Purple 10-label** segmentations, not the final
merged multi-structure labels. Input MRI and labels must be geometrically aligned.

## Completion and cancellation

The CLI records a unique container name and ID before processing starts. It
inspects the container's actual exit status instead of assuming that an attached
client's exit means processing finished. `Ctrl+C` requests cancellation of this
run's verified container, with a 30-second stop grace period. In tmux, use
`Ctrl+B`, then `D` to detach while leaving processing running.

Successful containers are removed. Failed, cancelled, or unconfirmed containers
are retained for inspection. Check `purple_run.json` and Docker state before
retrying. A null `exit_code` with `unknown` or `running_after_client_exit` status
means completion is unconfirmed. This behavior does not retroactively manage
containers launched by the older development CLI.

## Original native surface workflow (compatibility only)

The historical seven-positional-argument invocation still works:

```bash
python -m pip install '.[legacy]'
python -m purple_mri \
  /path/to/freesurfer /path/to/output /path/to/mri /path/to/segmentation \
  /path/to/atlases 20 /path/to/autodet.gw.stats.binary.dat
```

It is equivalent to `purple-mri legacy-surface` followed by those seven arguments.
The seventh argument is a **statistics file**, not `lh`/`rh`. This compatibility
path remains **RH-only**, uses the older native scripts, and requires the host
FreeSurfer/c3d environment and external resources, including fsaverage, to be set
up as before. It is not a replacement for the current Docker surface algorithm.
Paths and subject names containing shell metacharacters or spaces are rejected.
The historical installed `.sh` command names are retained as well.

## Singularity / Apptainer

The published `purple_mri_v1.1.0.sif` supports the same stage sequence as direct
Docker, including `exvivo_dl exvivo_surface` in one invocation. Its complete
DL + LH surface run passed on 2026-10-22 (2:37:13), and a registry download
matched the tested file byte-for-byte. See the [SIF guide](https://purple-mri.readthedocs.io/en/latest/singularity.html)
for the ORAS download, checksum, and examples. No per-model mounts or writable
overlay are needed. Apptainer and RH runs remain untested for this artifact.

Python CLI 1.1.0 launches Docker only; invoke Singularity/Apptainer directly.
SIF files are distributed separately and are not included in the Python package.

## Development and verification

```bash
PYTHONPATH=pkg_src python -m unittest discover -s tests -v
python -m pip install build
python -m build
```

Keep root and `pkg_src` metadata aligned; tests compare their project definitions.
Unit tests and wheel-install checks do not establish scientific accuracy.
The published 1.1.0 wheel passed Task2732 GPU inference with exit 0 (2:31).
The development CLI also completed full DL/merge (23:31) and LH surface/parcellation
processing (2:17:06, with a COMPLETE marker) using the same Docker image.
These are observed runtimes for one case, not performance guarantees. The
surface scripts retain opposite-hemisphere compatibility copies and RH-coded
working ASEG labels; consult the documentation before interpreting laterality.
This package does not automate PyPI publication.

See the project documentation for publications, input preparation and QC.
