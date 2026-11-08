Singularity / Apptainer
=========================

The published ``purple_mri_v1.2.0.sif`` supplies the scientific environment,
trained models, FreeSurfer, Convert3D, atlas resources and surface tools. Run it
with a compatible Linux AMD64 Singularity or Apptainer runtime, GPU access for
DL, and a FreeSurfer license for surfaces and atlas processing.

Download the image
--------------------

Use a directory without an existing file of the same name:

.. code-block:: bash

   singularity pull purple_mri_v1.2.0.sif \
     oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.2.0
   sha256sum purple_mri_v1.2.0.sif > purple_mri_v1.2.0.sif.sha256

The local checksum records the exact downloaded SIF for your run. It is distinct
from a Docker image ID or OCI registry digest. Keep it with the image and logs.
For an Apptainer installation, substitute ``apptainer`` for ``singularity``.

Complete DL, surfaces and atlas merges
----------------------------------------

Use absolute paths, one contrast and hemisphere per batch, and a new output
directory whose parent already exists. Name inputs ``SUBJECT_0000.nii.gz``.
Select a GPU allocated to your job.

.. code-block:: bash

   (
   set -euo pipefail
   RUNTIME=singularity
   SIF=/absolute/path/purple_mri_v1.2.0.sif
   INPUT=/absolute/path/inputs
   OUTPUT=/absolute/path/new_results
   LICENSE=/absolute/path/license.txt
   CONTRAST=flash
   HEMI=rh
   GPU=0

   test -s "$SIF"
   test -d "$INPUT"
   test -s "$LICENSE"
   mkdir "$OUTPUT"
   sha256sum "$SIF" > "$OUTPUT/sif.sha256"

   "$RUNTIME" exec --cleanenv --nv --pwd /output \
     --bind "$INPUT:/input:ro" --bind "$OUTPUT:/output:rw" \
     --bind "$LICENSE:/license.txt:ro" \
     --env FS_LICENSE=/license.txt --env "CUDA_VISIBLE_DEVICES=$GPU" \
     --env PYTHONUNBUFFERED=1 --env PYTHONDONTWRITEBYTECODE=1 \
     --env EXVIVO_TIMING_DIR=/output/timings \
     "$SIF" /bin/bash /src/commands_nnunet_inference.sh \
     exvivo_dl exvivo_surface \
     --contrast "$CONTRAST" --hemi "$HEMI" --threads 8 \
     --input-dir /input --dl-dir /output/dl \
     --surface-dir /output/surface --atlas-output-dir /output/atlases \
     2>&1 | tee "$OUTPUT/run.log"

   "$RUNTIME" exec --cleanenv --pwd /output \
     --bind "$INPUT:/input:ro" --bind "$OUTPUT:/output:rw" \
     --bind "$LICENSE:/license.txt:ro" --env FS_LICENSE=/license.txt \
     "$SIF" /bin/bash -c '
       set -e
       source /src/purple_surface_environment.sh
       /surface_env/bin/python /src/check_outputs.py \
         --input-dir /input --output-dir /output
     ' 2>&1 | tee "$OUTPUT/check_outputs.log"
   )

Choose ``t2w``, ``ciss``, ``flash`` or ``t2star`` and the actual ``lh`` or ``rh``
hemisphere. The full sequence creates detailed tissue labels, derives
``12_surface_labels``, reconstructs surfaces and merges seven cortical atlases.
The final checker validates file integrity and label consistency; review the MRI
and surfaces as described in :doc:`qc`.

DL only and reuse
-------------------

Use ``exvivo_dl`` for the DL stages alone with the same input/output flags and
contrast; it writes ``dl/11_final_merged`` and ``dl/12_surface_labels``.

For a later surface run, bind the completed DL root at ``/reuse_dl:rw`` and use
``exvivo_surface --dl-dir /reuse_dl`` with the matching MRI, contrast, hemisphere,
license and fresh surface/atlas output paths. The DL root receives checkpoints.

For atlas-only reuse, bind completed DL and surface roots read-only and use
``exvivo_atlas_merge --dl-dir /reuse_dl --surface-dir /reuse_surface`` with a
new ``--atlas-output-dir``. These surface/atlas stages use CPU and omit ``--nv``.
See :doc:`parcellation` for the seven final filenames and provenance checks.

Resume
--------

Repeat the original pipeline invocation with ``--resume`` and the same SIF,
inputs, container paths, contrast, hemisphere and processing settings. Reuse
the existing output directory rather than repeating ``mkdir``. Write a new log
for each attempt. Completed stages with matching hashes print ``REUSE``;
incomplete stages run again. Avoid concurrent writers to one run directory.

Keep a long job in tmux or your scheduler. Detach tmux using Ctrl+B, then D.
Use ``set -o pipefail`` when piping through ``tee`` and record the final exit
status. Direct runtime commands record logs and a SIF checksum; Python CLI
records are specific to that launcher.

Completion and runtime setup
------------------------------

A full run should finish with exit 0, all three completion markers and the
checker message ``DONE: 8 final outputs verified``. See :doc:`outputs` for the
files. Successful processing does not replace anatomical review.

Keep the output bind writable. Use the published ORAS SIF so its native-runtime
setup is included. A missing FUSE helper or a permission failure before image
startup concerns the host runtime; use your site's configured runtime and GPU
allocation. Record the runtime version with your image checksum.
