Outputs and provenance
========================

Paths below are relative to a full v1.2.0 run's output directory. The CLI and the
explicit Docker/Singularity examples use the same ``dl``, ``surface`` and
``atlases`` layout. Individual model selections write ``predictions/``.

.. list-table:: Main outputs
   :header-rows: 1
   :widths: 45 55

   * - Path
     - Contents
   * - ``dl/01_purple_original``
     - Raw Task283 prediction.
   * - ``dl/01b_purple_component_cleaned``
     - Component-cleaned baseline segmentation.
   * - ``dl/02_topology_input``
     - Prepared Task279 label maps.
   * - ``dl/03_topology_prediction``
     - Task279 prediction.
   * - ``dl/04_buried_sulcus_mask``
     - Baseline topology-removal mask.
   * - ``dl/05_purple_corrected``
     - Baseline topology-corrected Purple map.
   * - ``dl/06_mtl``, ``dl/07_subcortical``
     - Task269 MTL and Task2732 subcortical predictions.
   * - ``dl/13_flash_task278``, ``dl/13b_flash_task278_cleaned``
     - Raw and cleaned Task278 outputs for FLASH/T2*.
   * - ``dl/11_final_merged``
     - Detailed merged tissue segmentation.
   * - ``dl/12_surface_labels``
     - Reconstruction map with codes 0–10.
   * - ``dl/reports``, ``dl/checkpoints``, ``dl/pipeline_inputs.json``
     - Cleanup/merge reports and stage/input provenance.
   * - ``surface/SUBJECT/{surf,label,mri,stats,qc}``
     - Meshes, annotations, projected atlas volumes, metrics and provenance.
   * - ``atlases/SUBJECT/mri``
     - Seven ``*_with_dl_structures.nii.gz`` atlas merges.
   * - ``atlases/SUBJECT/lookup_tables``, ``atlases/SUBJECT/provenance``
     - Output-specific label tables and atlas provenance.
   * - ``timings``
     - Timing records produced by the processing scripts.
   * - ``purple_run.json``, ``cli_history``
     - Current CLI run record and prior resumed-attempt records.

The three tissue maps
-----------------------

``05_purple_corrected`` is the baseline topology-corrected map. The multimodel
merge uses it with MTL, subcortical and contrast-specific predictions.

``11_final_merged`` retains detailed MTL and subcortical labels together with
cortical GM 101, WM 107 and other tissue labels. MTL rim correction applies to
all four contrasts; FLASH/T2* also receives the Task278-based correction and
GM connected-component cleanup.

``12_surface_labels`` is derived from that final tissue map before reconstruction.
Detailed MTL labels collapse to code 10 and the other structures map to the
Purple reconstruction vocabulary. Codes 1–10 are the ten foreground classes,
plus background 0; a particular specimen may have fewer nonempty classes.
This is the surface reconstruction input.

The seven final atlas maps replace generic cortical GM 101 with cortical parcel
labels while preserving the detailed noncortical structures. Use the LUT for
each particular output. Surface working MGZ files and final native-grid atlas
merges are separate outputs; see :doc:`parcellation`.

Check completion
------------------

For a full run, require command exit 0 and all three markers:

.. code-block:: bash

   OUTPUT=/absolute/path/results
   test -f "$OUTPUT/dl/STRUCTURES_COMPLETE"
   test -f "$OUTPUT/surface/COMPLETE"
   test -f "$OUTPUT/atlases/COMPLETE"
   python -m json.tool "$OUTPUT/purple_run.json"

The JSON command applies to Python CLI runs. Direct Docker/SIF examples instead
save the image identity and terminal log. A worker-completion message describes
one worker, not completion of the pipeline. Check files, reports and :doc:`qc`
in addition to markers.

Run records
-------------

The Python record includes package version, selected image, immutable image ID,
registry digests, input hashes, contrast, hemisphere, requested stages and
container identity. It records the container's inspected exit code separately
from the CLI exit code. ``cli_history`` retains prior attempts when resuming.

If the client disappears, inspect the exact recorded container using
``docker inspect`` and ``docker logs``. Its state can differ from an unfinished
client-side JSON record; see :doc:`troubleshooting`. Preserve the original record
and the inspected state with your analysis provenance.
