Adult segmentation workflow
===================================

Run ``purple-mri run exvivo_dl --input INPUT --output OUTPUT`` for the combined
adult segmentation workflow. It uses the following sequence:

1. Task283 produces the original Purple 10-label segmentation.
2. Component cleanup keeps the largest face-connected component for labels
   1–5, 7, 9, and 10, preserves all WMH voxels (label 6), and retains ventricular
   components (label 8) of at least 5 cubic millimeters.
3. The cleaned labels are remapped into the Task279 input convention.
4. Task279 predicts post-hoc topology labels.
5. Its buried-sulcus label is saved as a mask and removed from the cleaned Purple
   segmentation to form ``05_purple_corrected``.
6. Task269 predicts MTL and amygdala subfields from the MRI.
7. Task2732 predicts subcortical structures from the MRI.
8. The pipeline merges and cleans residual labels into ``11_final_merged``.

The original predictions are retained. The Task2732 update changes the selected
checkpoint, while the existing merge label mapping remains in place. Review
component removal, topology masks, and model boundaries on each specimen.

``exvivo_t2w`` runs only Task283; ``exvivo_multi_sequence_subcortical`` runs only
Task2732. These do not perform the complete cleanup/merge sequence. See
:doc:`cli` for other individual models and :doc:`outputs` for output paths.

The maintainer reported a successful Task2732 standalone run and a complete
DL/merge run on Lambda using the updated image. One full DL run took 23 minutes
31 seconds for the reported scan; this is an observation, not a runtime estimate
for other scans or hardware.
