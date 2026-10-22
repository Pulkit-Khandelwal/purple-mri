Outputs and provenance
==============================

Paths are relative to the CLI's ``--output`` directory. The :doc:`docker` and
:doc:`singularity` examples explicitly choose the same processing-output layout.
Direct runtime commands do not create the Python CLI's ``purple_run.json``;
the SIF examples instead save ``run.log`` and ``sif.sha256`` beside the results. The repository's project-folder examples use ``data_for_inference/output_from_nnunet_inference``
and timestamped timing directories instead. A single model writes
``predictions/SUBJECT.nii.gz``; the combined DL workflow retains its intermediates.

.. list-table:: Main files and directories
   :header-rows: 1
   :widths: 48 52

   * - Path
     - Contents
   * - ``purple_run.json``
     - Package/image identity, requested stages, container ID and completion status.
   * - ``exvivo_dl/01_purple_original``
     - Unmodified Task283 predictions.
   * - ``exvivo_dl/01b_purple_component_cleaned``
     - Component cleanup before topology correction.
   * - ``exvivo_dl/02_topology_input``
     - Label maps prepared for Task279.
   * - ``exvivo_dl/03_topology_prediction``
     - Task279 prediction.
   * - ``exvivo_dl/04_buried_sulcus_mask``
     - Voxels removed by the topology stage.
   * - ``exvivo_dl/05_purple_corrected``
     - Corrected Purple 10-label segmentation for surfaces.
   * - ``exvivo_dl/06_mtl``
     - Task269 prediction.
   * - ``exvivo_dl/07_subcortical``
     - Task2732 prediction.
   * - ``exvivo_dl/11_final_merged``
     - Final merged multistructure segmentation.
   * - ``exvivo_dl/reports``
     - Component cleanup and merge reports.
   * - ``exvivo_surface/SUBJECT``
     - FreeSurfer-style ``mri``, ``surf``, ``label``, and ``stats`` directories.
   * - ``exvivo_surface/surface_pipeline.log``
     - Surface processing log.
   * - ``exvivo_surface/hemisphere.txt``
     - Requested anatomical hemisphere.
   * - ``exvivo_surface/source_revision.txt``
     - Surface source revision bundled in the image.
   * - ``exvivo_surface/COMPLETE``
     - Written only after the surface script completes successfully.
   * - ``timings/step_timings.tsv``
     - Individual processing steps and exit codes.
   * - ``timings/run_summary.tsv``
     - Stage and overall elapsed times.

Corrected versus merged labels
--------------------------------------

``05_purple_corrected`` retains Purple labels 0–10. ``11_final_merged`` reserves
1–21 for Task269, selected 200-series labels for Task2732, and 100-series labels
for remaining Purple structures. Their lookup tables are not interchangeable.
The merge prioritizes Task269 over selected subcortical labels over corrected
Purple, then cleans residual labels. Model overlays can refill some voxels
removed by topology correction. Use the corrected 10-label result for surfaces.

Surface atlas volumes are MGZ files under ``SUBJECT/mri``; see
:doc:`parcellation` for their exact names and conversion. The standalone CLI does
not package or upload DSS attachments or create an ITK-SNAP workspace.
Local processing retains the full output, including MRI working copies. The
remote service's separate attachment download workflow is documented in
:doc:`itksnap`.

Check completion
----------------

For a combined run, require a successful command exit, successful ``dl``,
``surface``, and ``overall`` totals, and the surface ``COMPLETE`` marker. A single
``worker ended successfully`` message describes one worker, not the entire run.
An output folder or a vanished Docker container is not a completion check.

For CLI runs, replace ``OUTPUT`` below with the host output directory:

.. code-block:: bash

   cat OUTPUT/timings/run_summary.tsv
   cat OUTPUT/exvivo_surface/COMPLETE
   python -m json.tool OUTPUT/purple_run.json

For direct Docker or SIF runs, read the same timing and completion files; omit
the ``purple_run.json`` command. The SIF examples record the image checksum in
``OUTPUT/sif.sha256``.

DL-only and individual-model runs do not produce a surface completion marker.
Inspect the predicted NIfTIs and timing totals appropriate to that stage.

Run record (Python CLI)
-----------------------

``purple_run.json`` includes ``package_version``, the requested ``image``, resolved
``image_id``, available ``repo_digests``, ``stages``, and ``hemisphere``. Container
identity is saved as ``run_id``, ``container_name``, and ``container_id``.
``exit_code`` is the inspected container exit code; ``cli_exit_code`` is the
launcher exit code. Cancellation may therefore record 130 for the CLI and a
different container exit code. ``finished_utc`` is recorded only when Docker
reports a terminal container state; ``client_finished_utc`` describes the client.

Archive this record, logs, timing reports, and QC decisions alongside your results.
A mutable Docker tag alone cannot identify which image performed an analysis.
Neither a zero exit code nor the completion marker is a scientific QC result.
