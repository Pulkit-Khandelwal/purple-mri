Command reference
===================

.. code-block:: text

   purple-mri --version
   purple-mri pull [--image IMAGE]
   purple-mri doctor [--image IMAGE]
   purple-mri models
   purple-mri run STAGE [STAGE] --input DIR --output DIR [options]
   purple-mri legacy-surface FS OUTPUT MRI SEGMENTATION ATLASES THREADS STATS

``python -m purple_mri`` exposes the same interface. Use each subcommand's
``--help`` for its installed version. The default Docker image is
``pulks/docker_purple_mri:v1.2.0``.

Run options
-------------

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Option
     - Meaning
   * - ``--input DIR``
     - Required directory of ``SUBJECT_0000.nii.gz`` inputs.
   * - ``--output DIR``
     - New/empty results, or the matching prior run with ``--resume``.
   * - ``--contrast {t2w,ciss,flash,t2star}``
     - Required for pipeline stages; one contrast per batch.
   * - ``--hemi {lh,rh}``
     - Actual hemisphere; required for surface/atlas processing.
   * - ``--license FILE``
     - Host FreeSurfer license for surface/atlas stages.
   * - ``--dl-dir DIR``
     - Existing DL root for standalone surface, tissue merge or atlas stages.
   * - ``--surface-dir DIR``
     - Existing surface/projection root for atlas-only reuse.
   * - ``--resume``
     - Resume the same pipeline run with matching image, inputs and settings.
   * - ``--preflight-only``
     - Run container input/model checks without processing.
   * - ``--save-qc-volumes``
     - Save optional tissue-merge QC volumes.
   * - ``--max-roi-voxels N``
     - Merge ROI size limit; default 64000000.
   * - ``--threads N``
     - Surface/merge threads; default 8. Does not cap every DL worker.
   * - ``--gpus SELECTOR``
     - Docker GPU selector; default ``all``, for example ``device=0``.
   * - ``--image IMAGE``
     - Compatible Docker tag, digest or local image ID.
   * - ``--pull``
     - Refresh the image before resolving its immutable ID.
   * - ``--dry-run``
     - Validate host paths and print the command without starting processing.

Pipeline stages
-----------------

* ``exvivo_dl``: model inference, topology correction, tissue merging and cleanup.
* ``exvivo_all``: compatibility alias for DL only.
* ``exvivo_surface``: reconstruction, annotation correction, projection and atlas merges.
* ``exvivo_atlas_merge``: merge validated existing projections with tissue labels.
* ``exvivo_merge``: complete tissue merging in a supplied prediction root.

The combined sequence is ``exvivo_dl exvivo_surface``. Standalone surface/atlas/
merge stages require ``--dl-dir``; atlas-only also requires ``--surface-dir``.
Tissue-only merging writes its results in the supplied DL root.

Individual model selections
-----------------------------

.. list-table::
   :header-rows: 1

   * - Stage
     - Task
     - Input/use
   * - ``exvivo_t2w``
     - 283
     - Baseline Purple tissue prediction.
   * - ``exvivo_posthoc_topology``
     - 279
     - Prepared topology label maps; see :doc:`posthoc_correction`.
   * - ``exvivo_multi_sequence_mtl_amygdala_subfields``
     - 269
     - Detailed MTL/amygdala prediction.
   * - ``exvivo_multi_sequence_subcortical``
     - 2732
     - Subcortical prediction.
   * - ``exvivo_flash_gm_wm``
     - 278
     - FLASH/T2* GM/WM/sulcus prediction.

Individual selections write ``predictions/``. Use ``purple-mri models`` to list
the full named model selections for the installed package, and use the selected
image's preflight to check its assets. Each model requires its intended input.

Direct container settings
---------------------------

The Python launcher maps input/output roots to container binds and sets
``EXVIVO_INPUT_DIR``, ``EXVIVO_DL_OUTPUT_DIR``, ``EXVIVO_SURFACE_OUTPUT_DIR``,
``EXVIVO_ATLAS_OUTPUT_DIR``, ``EXVIVO_MODEL_OUTPUT_DIR`` and ``EXVIVO_TIMING_DIR``.
It passes contrast and processing options to the image launcher and supplies
``FS_LICENSE``, ``EXVIVO_HEMI``, ``EXVIVO_THREADS`` and ``NO_FSFAST=1``.
Direct examples use explicit path flags; see :doc:`docker` and :doc:`singularity`.

Execution and exit status
---------------------------

The CLI resolves the image to an immutable local ID, records a named container
before starting it, and inspects its exit state. Ctrl+C requests cancellation
of that verified container. Successful containers are removed; failed or
unconfirmed containers are retained for inspection.

A normal run returns the inspected container exit code. Validation errors return
2; cancellation returns CLI status 130. The run record distinguishes container
exit status from client exit status. Inspect the recorded container if the
client was interrupted externally; see :doc:`troubleshooting`.
