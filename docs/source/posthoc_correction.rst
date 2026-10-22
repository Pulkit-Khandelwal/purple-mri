Post-hoc topology correction
====================================

The combined ``exvivo_dl`` workflow performs topology preparation, prediction,
and application automatically. This is the recommended path.

Task279 does not take the original MRI intensity image. The pipeline first
cleans the Purple prediction, then maps cortex (label 1) to 3, ventricular and
background labels to 0, and the other anatomical labels to 2. That prepared map
is named ``SUBJECT_0000.nii.gz`` for inference. Task279 label 1 is saved as the
buried-sulcus removal mask and set to background in the cleaned Purple result.

For an already prepared directory, the standalone predictor can be invoked as:

.. code-block:: bash

   purple-mri run exvivo_posthoc_topology \
     --input /path/to/prepared_topology_inputs \
     --output /path/to/topology_prediction_run1

This command only predicts topology labels. It does not clean a raw Purple
segmentation, prepare the input, apply the mask, or run the final merge. Never
substitute raw MRI for the prepared label maps.

Review ``04_buried_sulcus_mask`` together with ``05_purple_corrected``. The final
multimodel merge may refill removed regions through other model overlays; its
labels are not the surface reconstruction input.
