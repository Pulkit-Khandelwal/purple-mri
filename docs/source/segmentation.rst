Adult segmentation and tissue merging
=======================================

Run the complete DL route with an explicit acquisition contrast:

.. code-block:: bash

   purple-mri run exvivo_dl --contrast flash \
     --input /absolute/path/inputs --output /absolute/path/new_results

The workflow retains intermediate predictions and performs these steps:

1. Task283 predicts the baseline Purple tissue labels.
2. Component cleanup prepares those labels for topology correction.
3. The cleaned labels are remapped into the Task279 input convention.
4. Task279 predicts the post-hoc topology labels.
5. The topology correction creates ``05_purple_corrected``.
6. Task269 predicts detailed MTL/amygdala labels and Task2732 predicts subcortical
   structures from the MRI.
7. FLASH/T2* additionally runs Task278 for GM/WM and buried-sulcus refinement.
8. The contrast-specific merge combines the predictions, applies MTL rim
   correction, and writes ``11_final_merged``. FLASH/T2* includes disconnected-GM
   component cleanup.
9. The pipeline derives ``12_surface_labels`` from the final tissue merge for
   subsequent cortical reconstruction.

The MTL rim correction applies to T2w, CISS, FLASH and T2*. It operates in the
detailed tissue merge before the reconstruction-label collapse and atlas
assignment. The tissue and seven atlas outputs therefore share that correction.
Existing protected structures are retained according to the merge rules.

FLASH/T2* refinement
----------------------

Task278 refines cortical GM, WM and sulcus/background decisions while the merge
protects detailed MTL and subcortical structures. The raw prediction is retained
in ``13_flash_task278`` and the cleaned output in ``13b_flash_task278_cleaned``.
GM island cleanup precedes reconstruction-label creation and atlas assignment.
Review the change masks and reports together with the MRI.

For a Task278 prediction alone, use ``exvivo_flash_gm_wm --contrast flash``.
For the complete tissue result and reconstruction map, use ``exvivo_dl``.
See :doc:`outputs`, :doc:`posthoc_correction` and :doc:`qc`.
