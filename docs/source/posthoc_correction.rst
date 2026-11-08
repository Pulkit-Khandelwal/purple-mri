Post-hoc topology correction
==============================

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

Review ``dl/04_buried_sulcus_mask`` together with ``dl/05_purple_corrected``.
The subsequent contrast-specific tissue merge incorporates detailed structures
and, for FLASH/T2*, Task278 refinement. Reconstruction uses
``dl/12_surface_labels``, derived from that final tissue merge; see
:doc:`segmentation` and :doc:`outputs`.
