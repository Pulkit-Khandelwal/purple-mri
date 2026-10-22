Run Docker directly
===================

These examples use the same image and stage launcher as the Python CLI. They
require Docker, NVIDIA GPU access for DL, and a FreeSurfer license for surfaces.
The host does not need the Python package, FreeSurfer, c3d, or atlas installations.
For the managed CLI, use :doc:`quickstart`.

Prepare paths and pull the image
--------------------------------

Use absolute host paths. Put MRI files named ``SUBJECT_0000.nii.gz`` directly in
the input directory. Choose the actual hemisphere and one hemisphere per batch;
see :doc:`inputs`. Set these variables in the terminal where you will run Docker:

.. code-block:: bash

   INPUT="/absolute/path/inputs"
   LICENSE="/absolute/path/license.txt"
   HEMI=lh
   THREADS=20
   IMAGE=pulks/docker_purple_mri:v1.1.0
   docker pull "$IMAGE"

Use ``HEMI=rh`` for right-hemisphere input. Each example creates a new output
directory with ``mkdir`` and stops if that path already exists; its parent must
exist. Keep input, output, and any supplied segmentation directories separate.
Surface-only jobs omit the GPU option. DL-only jobs do not need the license.

Complete adult DL and surfaces
------------------------------

This runs real MRI processing, including Task2732 subcortical segmentation:

.. code-block:: bash

   (
   set -euo pipefail
   OUTPUT="/absolute/path/new_combined_results"
   test -d "$INPUT"
   test -s "$LICENSE"
   mkdir "$OUTPUT"
   IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE")
   printf '%s\n' "$IMAGE_ID" > "$OUTPUT/docker_image_id.txt"
   docker run --rm --gpus all --shm-size=8g \
     --mount "type=bind,src=$INPUT,dst=/inputs,readonly" \
     --mount "type=bind,src=$OUTPUT,dst=/outputs" \
     --mount "type=bind,src=$LICENSE,dst=/license.txt,readonly" \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_DL_OUTPUT_DIR=/outputs/exvivo_dl \
     --env EXVIVO_SURFACE_OUTPUT_DIR=/outputs/exvivo_surface \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     --env "EXVIVO_HEMI=$HEMI" --env "EXVIVO_THREADS=$THREADS" \
     --env FS_LICENSE=/license.txt --env NO_FSFAST=1 \
     --entrypoint /bin/bash "$IMAGE_ID" \
     /src/commands_nnunet_inference.sh exvivo_dl exvivo_surface \
     2>&1 | tee "$OUTPUT/run.log"
   test -s "$OUTPUT/exvivo_surface/COMPLETE"
   cat "$OUTPUT/timings/run_summary.tsv"
   )

The surface stage automatically uses ``exvivo_dl/05_purple_corrected``. The
``exvivo_all`` compatibility alias runs DL only; use both stage names above to
include surface reconstruction and parcellation.

DL only
-------

.. code-block:: bash

   (
   set -euo pipefail
   OUTPUT="/absolute/path/new_dl_results"
   test -d "$INPUT"
   mkdir "$OUTPUT"
   IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE")
   printf '%s\n' "$IMAGE_ID" > "$OUTPUT/docker_image_id.txt"
   docker run --rm --gpus all --shm-size=8g \
     --mount "type=bind,src=$INPUT,dst=/inputs,readonly" \
     --mount "type=bind,src=$OUTPUT,dst=/outputs" \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_DL_OUTPUT_DIR=/outputs/exvivo_dl \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     --entrypoint /bin/bash "$IMAGE_ID" \
     /src/commands_nnunet_inference.sh exvivo_dl \
     2>&1 | tee "$OUTPUT/run.log"
   cat "$OUTPUT/timings/run_summary.tsv"
   )

Surfaces from an existing DL result
-----------------------------------

Use matching MRI and corrected 10-label segmentations. For
``SUBJECT_0000.nii.gz``, the label file must be ``SUBJECT.nii.gz``. The detailed
merged segmentation is not a surface input. This command runs on CPU:

.. code-block:: bash

   (
   set -euo pipefail
   SEGMENTATION="/absolute/path/new_dl_results/exvivo_dl/05_purple_corrected"
   OUTPUT="/absolute/path/new_surface_results"
   test -d "$INPUT"
   test -d "$SEGMENTATION"
   test -s "$LICENSE"
   mkdir "$OUTPUT"
   IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE")
   printf '%s\n' "$IMAGE_ID" > "$OUTPUT/docker_image_id.txt"
   docker run --rm --shm-size=8g \
     --mount "type=bind,src=$INPUT,dst=/inputs,readonly" \
     --mount "type=bind,src=$OUTPUT,dst=/outputs" \
     --mount "type=bind,src=$SEGMENTATION,dst=/segmentations,readonly" \
     --mount "type=bind,src=$LICENSE,dst=/license.txt,readonly" \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_SEGM_DIR=/segmentations \
     --env EXVIVO_SURFACE_OUTPUT_DIR=/outputs/exvivo_surface \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     --env "EXVIVO_HEMI=$HEMI" --env "EXVIVO_THREADS=$THREADS" \
     --env FS_LICENSE=/license.txt --env NO_FSFAST=1 \
     --entrypoint /bin/bash "$IMAGE_ID" \
     /src/commands_nnunet_inference.sh exvivo_surface \
     2>&1 | tee "$OUTPUT/run.log"
   test -s "$OUTPUT/exvivo_surface/COMPLETE"
   cat "$OUTPUT/timings/run_summary.tsv"
   )

Subcortical segmentation only
-----------------------------

.. code-block:: bash

   (
   set -euo pipefail
   OUTPUT="/absolute/path/new_subcortical_results"
   test -d "$INPUT"
   mkdir "$OUTPUT"
   IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE")
   printf '%s\n' "$IMAGE_ID" > "$OUTPUT/docker_image_id.txt"
   docker run --rm --gpus all --shm-size=8g \
     --mount "type=bind,src=$INPUT,dst=/inputs,readonly" \
     --mount "type=bind,src=$OUTPUT,dst=/outputs" \
     --env EXVIVO_INPUT_DIR=/inputs \
     --env EXVIVO_MODEL_OUTPUT_DIR=/outputs/predictions \
     --env EXVIVO_TIMING_DIR=/outputs/timings \
     --entrypoint /bin/bash "$IMAGE_ID" \
     /src/commands_nnunet_inference.sh exvivo_multi_sequence_subcortical \
     2>&1 | tee "$OUTPUT/run.log"
   cat "$OUTPUT/timings/run_summary.tsv"
   )

This selects Task2732 and writes ``predictions/SUBJECT.nii.gz``. Other individual
selections are listed in :doc:`cli`; each requires its intended input data.

Outputs and operational differences
-----------------------------------

The examples explicitly choose the processing-output layout described in
:doc:`outputs`. They record the resolved Docker image ID and run that exact image.
Direct Docker does not produce ``purple_run.json`` or provide the Python CLI's
container lifecycle management. ``--rm`` removes a stopped container; the bind
mount preserves files and the saved log on the host. Use tmux or your scheduler
for long jobs and inspect timing totals and results before interpreting success.

The older project-folder examples in the
`repository container guide <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md>`_
mount the parent of ``data_for_inference`` at ``/data/exvivo`` and use the
container's default output paths. Those defaults differ from the explicit mounts
above. :doc:`cli` maps launcher options to environment variables.
