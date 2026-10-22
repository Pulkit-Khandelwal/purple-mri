Command reference
=========================

.. code-block:: text

   purple-mri --version
   purple-mri pull [--image IMAGE]
   purple-mri doctor [--image IMAGE]
   purple-mri models
   purple-mri run STAGE [STAGE] --input DIR --output DIR [options]
   purple-mri legacy-surface FS OUTPUT MRI SEGMENTATION ATLASES THREADS STATS

``python -m purple_mri`` exposes the same interface. ``--help`` is available for
each subcommand. The historical seven-positional-argument form is preserved;
see :doc:`legacy`.

Run options
-------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Option
     - Meaning
   * - ``--input DIR``
     - Required directory of ``SUBJECT_0000.nii.gz`` scans.
   * - ``--output DIR``
     - Required new or empty, separate output directory.
   * - ``--hemi {lh,rh}``
     - Actual hemisphere; required for surfaces.
   * - ``--license FILE``
     - Host FreeSurfer license; required for surfaces.
   * - ``--segmentation DIR``
     - Corrected 10-label inputs; required only for surface-only runs.
   * - ``--threads N``
     - Positive surface thread count; default 8. Does not limit every DL worker.
   * - ``--gpus SELECTOR``
     - Docker GPU selector, default ``all``; for example ``device=0``.
   * - ``--image IMAGE``
     - Docker tag, digest reference, or local image ID; default ``pulks/docker_purple_mri:v1.1.0``.
   * - ``--pull``
     - Refresh the selected image before resolving its immutable ID.
   * - ``--dry-run``
     - Validate host paths and print the equivalent command without running.

Equivalent container settings
-----------------------------

The Python CLI constructs these settings for the Docker launcher. See :doc:`docker`
for runnable commands. Container paths must refer to locations inside bind mounts.

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - CLI option
     - Direct Docker equivalent
   * - ``--input DIR``
     - Read-only input bind and ``EXVIVO_INPUT_DIR``.
   * - ``--output DIR``
     - Writable output bind; set ``EXVIVO_DL_OUTPUT_DIR``,
       ``EXVIVO_SURFACE_OUTPUT_DIR``, ``EXVIVO_MODEL_OUTPUT_DIR``, and
       ``EXVIVO_TIMING_DIR`` for the desired layout.
   * - ``--hemi lh`` or ``rh``
     - ``EXVIVO_HEMI=lh`` or ``rh``.
   * - ``--license FILE``
     - Read-only license bind and ``FS_LICENSE`` pointing to that container path.
   * - ``--segmentation DIR``
     - Read-only corrected-label bind and ``EXVIVO_SEGM_DIR``.
   * - ``--threads N``
     - ``EXVIVO_THREADS=N``; defaults to 8 in both launchers.
   * - ``--gpus SELECTOR``
     - Docker ``--gpus SELECTOR`` for DL. Omit it for a surface-only job.
   * - ``--image IMAGE`` / ``--pull``
     - Select the Docker image / explicitly run ``docker pull IMAGE`` first.

The CLI also sets ``NO_FSFAST=1`` and an 8 GiB shared-memory limit. Its run-record
and cancellation handling are Python features, not additional stage arguments.

Stages
--------------

``exvivo_dl`` runs all adult DL steps and merge. ``exvivo_all`` is an alias;
both use the CLI's ``exvivo_dl`` output subdirectory. With the direct container
launcher and no explicit output override, ``exvivo_all`` instead retains its
historical ``exvivo_all`` output directory. Neither spelling includes surfaces. ``exvivo_surface`` runs
surface reconstruction and atlas mapping. The only supported two-stage sequence
is ``exvivo_dl exvivo_surface`` (or the alias followed by surfaces).

.. list-table:: Individual selections
   :header-rows: 1
   :widths: 58 12 30

   * - Stage
     - Task
     - Purpose
   * - ``exvivo_t2w``
     - 283
     - Original Purple 10-label segmentation
   * - ``invivo_flair_wmh``
     - 451
     - In vivo FLAIR WMH
   * - ``exvivo_flash_thalamus``
     - 276
     - FLASH thalamus
   * - ``exvivo_posthoc_topology``
     - 279
     - Prepared label-map topology input
   * - ``exvivo_umc_strip_cerebellum``
     - 101
     - Cerebellum removal
   * - ``exvivo_multi_sequence_mtl_amygdala_subfields``
     - 269
     - MTL/amygdala subfields
   * - ``exvivo_multi_sequence_subcortical``
     - 2732
     - Flip-fixed subcortical segmentation
   * - ``exvivo_flash_more_subcort``
     - 289
     - Optional model asset; may be absent

Each model needs its intended input contrast and preprocessing. In particular,
Task279 takes prepared segmentation maps, not raw MRI; see
:doc:`posthoc_correction`. Task289 availability must be checked in the selected
image. Infant stages are not implemented in this container CLI. Registration,
template construction, and group analysis remain separate repository workflows.

Execution and exit status
---------------------------------

Real runs resolve the image tag to an immutable local image ID. The CLI creates
a named, labeled container, records its ID before starting it, and attaches to
its output. Dry-run prints an equivalent ``docker run`` command.

A normal run returns the container's inspected exit code. Validation failures
return 2; Docker setup failures return a nonzero status. Ctrl+C returns 130 and
attempts ``docker stop`` on this run's verified container, with 30 seconds of
grace. The attached client is isolated from the terminal process group so the
CLI can manage cancellation. Successful containers are removed. Failed,
cancelled, or unconfirmed containers are retained for inspection.

If Docker cannot confirm completion, the CLI returns nonzero and records
``exit_code: null`` with ``unknown`` or ``running_after_client_exit`` status.
Do not treat a client's disappearance as proof that processing stopped.
