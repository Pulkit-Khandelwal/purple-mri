Singularity / Apptainer
=======================

Run the adult pipeline with the published ``purple_mri_v1.1.0.sif`` on a Linux
AMD64 host. The SIF supplies the models, FreeSurfer, Convert3D, atlases, and pial
tools. Docker and the Python ``purple-mri`` package are not required on the host.
Python CLI 1.1.0 remains a Docker launcher; the commands on this page invoke the
container runtime directly.

The SIF uses the same stage names and ``EXVIVO_*`` settings as direct Docker.
The complete sequence is **exvivo_dl exvivo_surface**, in one invocation with
``--nv``. Runtime bookkeeping and surface-library setup are handled inside the
published image; no per-model mounts or writable overlay are needed.

Requirements
------------

* A working Singularity installation, or a compatible Apptainer installation.
* An NVIDIA GPU and compatible host driver for DL, with GPU access allowed by
  the host or scheduler. Surface-only processing uses CPUs.
* Your FreeSurfer license for surface processing.
* Space for the approximately 18 GB SIF and per-subject working files.
* Prepared hemisphere MRI named ``SUBJECT_0000.nii.gz``. Select the actual
  hemisphere, use one hemisphere per batch, and follow :doc:`inputs`.

The complete LH run was tested with Singularity on clam. Apptainer offers the
corresponding ``pull`` and ``exec`` interface, but has not been live-tested for
this release. Set ``RUNTIME=apptainer`` in the examples if using it.

Download and verify
-------------------

Run this in a directory that does not already contain the SIF:

.. code-block:: bash

   (
   set -euo pipefail
   RUNTIME=singularity
   "$RUNTIME" pull purple_mri_v1.1.0.sif \
     oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.1.0
   printf '%s  %s\n' \
     1bb444c92de404e7ecba5021d06bfb2377feaf450489a367c4f9825b1c830f12 \
     purple_mri_v1.1.0.sif | sha256sum -c -
   )

Alternatively, download :download:`the checksum file
<_static/releases/purple_mri_v1.1.0.sif.sha256>` beside the SIF and run
``sha256sum -c purple_mri_v1.1.0.sif.sha256``. This is the SHA-256 of the SIF file,
not a Docker image ID or an OCI manifest digest.

The ``v1.1.0`` SIF tag was updated on **2026-10-22**. If you downloaded an earlier
copy, pull into a new directory and verify this checksum before using these
instructions. The maintainer pushed this file, pulled it back, and confirmed a
byte-for-byte match. Converting ``docker://pulks/docker_purple_mri:v1.1.0`` is a
different build route: that Docker tag does not include these SIF-specific
runtime fixes. Use the prebuilt ORAS artifact above.

Complete adult DL and surfaces
------------------------------

Edit the four paths, select ``HEMI=lh`` or ``HEMI=rh``, and choose the surface
thread count. Use absolute paths and a new output directory separate from the
inputs. Create its parent directory first. These commands run actual processing.

.. code-block:: bash

   (
   set -euo pipefail
   RUNTIME=singularity
   SIF="/absolute/path/purple_mri_v1.1.0.sif"
   INPUT="/absolute/path/inputs"
   OUTPUT="/absolute/path/new_results"
   LICENSE="/absolute/path/license.txt"
   HEMI=lh
   THREADS=20

   test -s "$SIF"
   test -d "$INPUT"
   test -s "$LICENSE"
   mkdir "$OUTPUT"
   sha256sum "$SIF" > "$OUTPUT/sif.sha256"

   "$RUNTIME" exec --cleanenv --nv \
     --bind "$INPUT:/inputs:ro" --bind "$OUTPUT:/outputs:rw" \
     --bind "$LICENSE:/license.txt:ro" --pwd /outputs \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_DL_OUTPUT_DIR=/outputs/exvivo_dl \
     --env EXVIVO_SURFACE_OUTPUT_DIR=/outputs/exvivo_surface \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     --env FS_LICENSE=/license.txt \
     --env "EXVIVO_HEMI=$HEMI" --env "EXVIVO_THREADS=$THREADS" \
     "$SIF" /bin/bash /src/commands_nnunet_inference.sh \
     exvivo_dl exvivo_surface 2>&1 | tee "$OUTPUT/run.log"
   )

``--nv`` supplies GPU access to DL. The surface child process selects the
container's CPU mesh libraries automatically. The launcher supplies the
corrected Purple segmentation to surfaces after DL completes. ``exvivo_all``
is an alias for DL only; add ``exvivo_surface`` for reconstruction.

DL only
-------

This runs all adult DL models, topology correction, cleanup, and merge. A
FreeSurfer license and hemisphere selection are not needed for this stage.

.. code-block:: bash

   (
   set -euo pipefail
   RUNTIME=singularity
   SIF="/absolute/path/purple_mri_v1.1.0.sif"
   INPUT="/absolute/path/inputs"
   OUTPUT="/absolute/path/new_dl_results"
   test -s "$SIF"
   test -d "$INPUT"
   mkdir "$OUTPUT"
   sha256sum "$SIF" > "$OUTPUT/sif.sha256"

   "$RUNTIME" exec --cleanenv --nv \
     --bind "$INPUT:/inputs:ro" --bind "$OUTPUT:/outputs:rw" --pwd /outputs \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_DL_OUTPUT_DIR=/outputs/exvivo_dl \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     "$SIF" /bin/bash /src/commands_nnunet_inference.sh exvivo_dl \
     2>&1 | tee "$OUTPUT/run.log"
   )

Surfaces from an existing corrected segmentation
------------------------------------------------

Use the original MRI and matching ``05_purple_corrected`` labels from a completed
DL run. Label files must be named ``SUBJECT.nii.gz`` and match the corresponding
``SUBJECT_0000.nii.gz`` MRI in geometry. ``11_final_merged`` has a different label
convention and cannot substitute for corrected Purple labels.

.. code-block:: bash

   (
   set -euo pipefail
   RUNTIME=singularity
   SIF="/absolute/path/purple_mri_v1.1.0.sif"
   INPUT="/absolute/path/inputs"
   SEGMENTATION="/absolute/path/dl_results/exvivo_dl/05_purple_corrected"
   OUTPUT="/absolute/path/new_surface_results"
   LICENSE="/absolute/path/license.txt"
   HEMI=lh
   THREADS=20
   test -s "$SIF"
   test -d "$INPUT"
   test -d "$SEGMENTATION"
   test -s "$LICENSE"
   mkdir "$OUTPUT"
   sha256sum "$SIF" > "$OUTPUT/sif.sha256"

   "$RUNTIME" exec --cleanenv \
     --bind "$INPUT:/inputs:ro" --bind "$OUTPUT:/outputs:rw" \
     --bind "$SEGMENTATION:/segmentations:ro" \
     --bind "$LICENSE:/license.txt:ro" --pwd /outputs \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_SEGM_DIR=/segmentations \
     --env EXVIVO_SURFACE_OUTPUT_DIR=/outputs/exvivo_surface \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     --env FS_LICENSE=/license.txt \
     --env "EXVIVO_HEMI=$HEMI" --env "EXVIVO_THREADS=$THREADS" \
     "$SIF" /bin/bash /src/commands_nnunet_inference.sh exvivo_surface \
     2>&1 | tee "$OUTPUT/run.log"
   )

This invocation is CPU-only and omits ``--nv``. Use the same requested hemisphere
as the input specimen. Both MRI and existing labels are mounted read-only.

Subcortical segmentation only
-----------------------------

The standalone subcortical option selects Task2732:

.. code-block:: bash

   (
   set -euo pipefail
   RUNTIME=singularity
   SIF="/absolute/path/purple_mri_v1.1.0.sif"
   INPUT="/absolute/path/inputs"
   OUTPUT="/absolute/path/new_subcortical_results"
   test -s "$SIF"
   test -d "$INPUT"
   mkdir "$OUTPUT"
   sha256sum "$SIF" > "$OUTPUT/sif.sha256"

   "$RUNTIME" exec --cleanenv --nv \
     --bind "$INPUT:/inputs:ro" --bind "$OUTPUT:/outputs:rw" --pwd /outputs \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_MODEL_OUTPUT_DIR=/outputs/predictions \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     "$SIF" /bin/bash /src/commands_nnunet_inference.sh \
     exvivo_multi_sequence_subcortical 2>&1 | tee "$OUTPUT/run.log"
   )

Outputs and completion
----------------------

With the explicit mounts above, results are under the host ``OUTPUT`` directory:

.. list-table::
   :header-rows: 1

   * - Path
     - Contents
   * - ``exvivo_dl/05_purple_corrected/``
     - Corrected Purple 10-label NIfTI segmentations used for surfaces.
   * - ``exvivo_dl/11_final_merged/``
     - Merged DL NIfTI segmentations.
   * - ``predictions/``
     - NIfTI predictions for an individual-model run.
   * - ``exvivo_surface/SUBJECT/``
     - Surfaces, annotations, atlas MGZ volumes, statistics, and working MRI files.
   * - ``exvivo_surface/COMPLETE``
     - Successful surface-stage completion marker.
   * - ``timings/``, ``run.log``, ``sif.sha256``
     - Timing reports, terminal log, and the SIF file identity recorded by these examples.

See :doc:`outputs` for intermediate directories, and :doc:`parcellation` for the
nine atlas volumes, single-hemisphere conventions, and NIfTI export using the SIF.
Direct runtime execution does not create the Python CLI's ``purple_run.json``.

For a complete run, require exit 0 from the command and all three totals
(``dl``, ``surface``, ``overall``), plus ``COMPLETE`` and the expected output files.
The example blocks use ``pipefail`` so logging does not hide processing errors.
Use tmux or a scheduler for long jobs; detach tmux with Ctrl+B, then D.

.. code-block:: bash

   cat /absolute/path/new_results/timings/run_summary.tsv
   cat /absolute/path/new_results/exvivo_surface/COMPLETE

The verified SIF completed an uninterrupted full DL + LH surface/parcellation run
on **2026-10-22**: DL **22:58**, surfaces **2:14:14**, overall **2:37:13**, all exit 0.
The test checked corrected and merged NIfTIs, core LH surface files, and the
completion marker. This is one LH case on one host; RH and Apptainer runs remain
untested for this artifact. Successful processing does not replace :doc:`qc`.

Troubleshooting
---------------

If an older SIF reports a read-only model ``fold_0`` path, a VTK/host-GL library
conflict, or a transform scratch-file failure, first compare its checksum with
the published value above. These three runtime issues were fixed in this SIF.
Keep the output bind writable. Use a fresh output directory for a new run;
these examples do not implement automatic resume.

Some unprivileged host installations require ``squashfuse`` on ``PATH`` to mount
the image. A missing helper or ``Operation not permitted`` before the container
starts concerns the host runtime; ask the host administrator or use the site's
configured runtime. Rebuilding the SIF does not configure host permissions.

Task2732 may report missing automatic nnU-Net postprocessing metadata even when
prediction succeeds. The combined Purple cleanup and merge are separate steps;
see :doc:`troubleshooting` for the warning and :doc:`release_notes` for scope.

Runtime references: `Singularity exec
<https://docs.sylabs.io/guides/3.8/user-guide/cli/singularity_exec.html>`_,
`Singularity pull
<https://docs.sylabs.io/guides/3.8/user-guide/cli/singularity_pull.html>`_, and
`Apptainer exec <https://apptainer.org/docs/user/latest/cli/apptainer_exec.html>`_.
