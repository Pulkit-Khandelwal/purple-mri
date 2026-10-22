# purple-mri

**Penn Utilities for Registration and Parcellation of Ex vivo MRI**

`purple-mri` provides segmentation, cortical surface reconstruction, anatomical
parcellation, registration, and morphometric analysis of high-resolution
postmortem human brain MRI.

[Documentation](https://purple-mri.readthedocs.io/en/latest/) ·
[PyPI 1.1.0](https://pypi.org/project/purple-mri/1.1.0/) ·
[Docker image](https://hub.docker.com/r/pulks/docker_purple_mri) ·
[Release notes](https://purple-mri.readthedocs.io/en/latest/release_notes.html)

## Start with the adult container workflow

| Route | Install on the host | Instructions |
| --- | --- | --- |
| Python CLI with Docker | Python 3.9+, Docker, and GPU access for DL | [Installation](https://purple-mri.readthedocs.io/en/latest/installation.html) and [quick start](https://purple-mri.readthedocs.io/en/latest/quickstart.html) |
| Docker directly | Docker and GPU access for DL | [Direct Docker examples](https://purple-mri.readthedocs.io/en/latest/docker.html) |

Both routes use **`pulks/docker_purple_mri:v1.1.0`**. The image contains the
trained models, FreeSurfer, Convert3D, atlas resources, and custom pial binary.
Provide a FreeSurfer license for surfaces. Installing the pip package installs
the launcher; `purple-mri pull` downloads the scientific environment separately.

The CLI is Docker-only; the SIF is separate. Final SIF validation is tracked
separately in the [container guide](docker/exvivo_docker.md#singularity--apptainer-linux-amd64).

### Install and run

Use a Linux host with an NVIDIA GPU configured for Docker. For CPU-only surface
processing, see the surface-only example below. Prepare one excised hemisphere
per scan and one hemisphere per batch. Name inputs `SUBJECT_0000.nii.gz`.

```bash
python3 -m venv ~/venvs/purple-mri
source ~/venvs/purple-mri/bin/activate
python -m pip install 'purple-mri==1.1.0'
purple-mri pull
purple-mri doctor
```

Choose the actual hemisphere (`lh` or `rh`), a new output directory, and your
license path. This runs all adult DL stages, followed by surfaces and parcellation:

```bash
purple-mri run exvivo_dl exvivo_surface \
  --input /absolute/path/inputs \
  --output /absolute/path/new_results \
  --hemi lh \
  --license /absolute/path/license.txt \
  --threads 20
```

Add `--dry-run` to inspect the command before starting. `doctor` checks Docker
access and image metadata; it does not run GPU or model checks. See
[inputs](https://purple-mri.readthedocs.io/en/latest/inputs.html) for naming,
geometry, and acquisition requirements.

### Run stages separately

```bash
# Complete DL segmentation, topology correction, and merge
purple-mri run exvivo_dl \
  --input /absolute/path/inputs --output /absolute/path/new_dl_results

# Surfaces from the corrected 10-label result; CPU only
purple-mri run exvivo_surface \
  --input /absolute/path/inputs \
  --segmentation /absolute/path/new_dl_results/exvivo_dl/05_purple_corrected \
  --output /absolute/path/new_surface_results \
  --hemi lh --license /absolute/path/license.txt --threads 20

# Task2732 subcortical segmentation only
purple-mri run exvivo_multi_sequence_subcortical \
  --input /absolute/path/inputs --output /absolute/path/new_subcortical_results
```

`exvivo_all` remains an alias for **DL only**. The complete adult sequence is
`exvivo_dl exvivo_surface`. Topology correction is included in `exvivo_dl`.
The subcortical model is **Task2732**, in both combined and individual runs.

### Find and check results

Paths below are relative to the Python CLI's `--output` directory:

| Output | Location |
| --- | --- |
| Corrected Purple 10-label segmentation used for surfaces | `exvivo_dl/05_purple_corrected/` |
| Final merged DL segmentation | `exvivo_dl/11_final_merged/` |
| Individual-model predictions | `predictions/` |
| Surfaces, atlas volumes, annotations, and statistics | `exvivo_surface/SUBJECT/{surf,mri,label,stats}/` |
| Successful surface completion marker | `exvivo_surface/COMPLETE` |
| Timings and exit codes | `timings/` |
| CLI run and Docker image identity | `purple_run.json` |

Surface inputs must use `05_purple_corrected`. The detailed merged segmentation
has a different label convention. The surface stage supplies eight cortical
atlas volumes plus `wmparc`; see [parcellations and NIfTI export](https://purple-mri.readthedocs.io/en/latest/parcellation.html).

Use tmux or a job scheduler for long runs. In tmux, detach with **Ctrl+B, then D**.
CLI 1.1.0 treats **Ctrl+C as cancellation**. Check the exit status, timing reports,
and output files, then perform [anatomical QC](https://purple-mri.readthedocs.io/en/latest/qc.html).

Docker full DL and LH surfaces completed successfully; the published 1.1.0 wheel
also passed Task2732 GPU inference. See the
[validation record](https://purple-mri.readthedocs.io/en/latest/release_notes.html)
for scope and observed runtimes.

## Documentation and other workflows

Read the Docs is the detailed user manual. The [repository container guide](docker/exvivo_docker.md)
also documents direct Docker commands using the older project-folder layout.
The [package README](pkg_src/README.md) covers the Python launcher, and the
[container build guide](docker/docker_files/README.md) is for maintainers.

The repository also contains workflows beyond the adult container commands:

| Workflow | Guide or source |
| --- | --- |
| Ex vivo to in vivo registration | [Registration](https://purple-mri.readthedocs.io/en/latest/registration.html) |
| Population template construction | [Templates](https://purple-mri.readthedocs.io/en/latest/template_construction.html) |
| ROI-wise, vertex-wise, and deformation-based analyses | [Group analysis](https://purple-mri.readthedocs.io/en/latest/group_analysis.html) |
| Infant reconstruction and M-CRIB-S mapping | [Infant scripts](purple_mri/infant_scripts) |
| Historical pip native surface launcher | [Legacy guide](https://purple-mri.readthedocs.io/en/latest/legacy.html) |
| Standalone source surface scripts | [Source workflow distinctions](https://purple-mri.readthedocs.io/en/latest/legacy.html#standalone-repository-scripts) |

Infant container stages are placeholders. Registration, templates, and group
analysis are separate research workflows. Their host dependencies and setup
are described in their guides; they are not installed by the lightweight CLI.
The adult container already supplies fsaverage, atlas assets, and the custom
pial executable, so users do not need the standalone pial container setup.

## Install from source or contribute

```bash
git clone https://github.com/Pulkit-Khandelwal/purple-mri.git
cd purple-mri
python -m pip install -e .
purple-mri --help
```

Install `dependencies.txt` only when a separate research workflow requires
those host libraries. See the [maintainer guide](https://purple-mri.readthedocs.io/en/latest/publishing.html)
for package checks, documentation builds, and release procedures.

## Development

`purple-mri` was conceived by **Pulkit Khandelwal and Paul A. Yushkevich**
and originated from doctoral research in the PATCH Lab within the Penn Image
Computing and Science Laboratory (PICSL) at the University of Pennsylvania.

The framework was developed through collaborations with the Penn Alzheimer's
Disease Research Center and Penn Frontotemporal Degeneration Center and has
subsequently expanded at Massachusetts General Hospital, Harvard Medical
School, and the Athinoula A. Martinos Center for Biomedical Imaging toward
high-resolution multimodal postmortem imaging of the developing human brain,
including collaborative work with Boston Children's Hospital.

See the documentation homepage for additional background:

https://purple-mri.readthedocs.io/en/latest/


## Introductory Video

<div align="center">
  <a href="https://youtu.be/DBdzbIAJBw4">
    <img src="https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/images/thumbnail.png"
         style="width:75%;">
  </a>
</div>


## Citation

If you use `purple-mri` in academic work, please cite the relevant publications
listed here:

https://purple-mri.readthedocs.io/en/latest/citations.html


## License

Please see the repository license for terms of use.
