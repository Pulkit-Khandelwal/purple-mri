Quick start
=============

Use one contrast and one anatomical hemisphere per batch. Place single-channel
NIfTIs named ``SUBJECT_0000.nii.gz`` in the input directory. Keep input, output
and reused-result directories separate. Complete :doc:`installation` first.

Full segmentation, surfaces and atlas merges
----------------------------------------------

.. code-block:: bash

   purple-mri run exvivo_dl exvivo_surface \
     --contrast flash --hemi rh \
     --input /absolute/path/inputs \
     --output /absolute/path/new_results \
     --license /absolute/path/license.txt \
     --threads 8 --gpus device=0

Choose ``t2w``, ``ciss``, ``flash`` or ``t2star``; T2* uses the FLASH route.
Select the actual hemisphere with ``--hemi lh`` or ``--hemi rh``. Use a new or
empty output directory for the first invocation. See :doc:`outputs` for the
``dl/``, ``surface/`` and ``atlases/`` directories.

Add ``--dry-run`` to print the command after host-path validation. Add
``--preflight-only`` to run container input/model checks without inference;
use a separate output directory for that preflight record.

DL only
---------

.. code-block:: bash

   purple-mri run exvivo_dl --contrast ciss \
     --input /absolute/path/inputs --output /absolute/path/new_dl_results \
     --gpus device=0

This writes the detailed merge to ``dl/11_final_merged`` and the reconstruction
map to ``dl/12_surface_labels``. ``exvivo_all`` is an alias for DL only.

Surfaces from completed DL results
------------------------------------

Supply the complete DL root from a v1.2.0 run:

.. code-block:: bash

   purple-mri run exvivo_surface --contrast ciss --hemi lh \
     --input /absolute/path/inputs \
     --dl-dir /absolute/path/new_dl_results/dl \
     --output /absolute/path/new_surface_results \
     --license /absolute/path/license.txt --threads 8

The container reads ``12_surface_labels`` for reconstruction and uses the
matching detailed merge for the final atlas outputs. The reused DL root is
writable because it records surface checkpoints. This CPU workflow writes new
surfaces and atlas merges beneath the new output directory.

Reuse existing atlas projections
----------------------------------

.. code-block:: bash

   purple-mri run exvivo_atlas_merge --contrast flash --hemi rh \
     --input /absolute/path/inputs \
     --dl-dir /absolute/path/completed_results/dl \
     --surface-dir /absolute/path/completed_results/surface \
     --output /absolute/path/new_atlas_results \
     --license /absolute/path/license.txt --threads 8

The existing DL and surface roots are mounted read-only. The container verifies
surface/projection provenance and hashes before reusing them.

Individual model predictions
------------------------------

.. code-block:: bash

   purple-mri run exvivo_multi_sequence_subcortical \
     --input /absolute/path/inputs --output /absolute/path/subcortical_results

   purple-mri run exvivo_flash_gm_wm --contrast flash \
     --input /absolute/path/flash_inputs --output /absolute/path/task278_results

These select Task2732 and Task278 respectively and write ``predictions/``.
Use ``exvivo_dl`` for the complete tissue cleanup and merge.

Resume and completion
-----------------------

Repeat the original pipeline command with the same image, inputs, output,
contrast, hemisphere and options, adding ``--resume``. Matching stages are
reused only when their dependencies and output hashes agree. Changed inputs or
settings require a new run directory.

Use tmux or your scheduler for long jobs. In tmux, detach with Ctrl+B, then D.
Ctrl+C requests cancellation of the CLI's container. Enable ``set -o pipefail``
when logging through ``tee``. Keep the terminal log outside a new CLI output
directory until the launcher has created its run record.

A complete full run requires exit code 0, the three markers
``dl/STRUCTURES_COMPLETE``, ``surface/COMPLETE`` and ``atlases/COMPLETE``, and the
expected files. Inspect ``purple_run.json`` and the reports, then perform
:doc:`qc`. A preflight pass is an input/model check, not a processing result.
