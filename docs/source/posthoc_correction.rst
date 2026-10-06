Post-hoc Topology Correction
============================

Overview
--------

Post-hoc topology correction removes predicted buried-sulcus regions from the
``purple-mri`` segmentation before downstream cortical surface reconstruction
and anatomical parcellation.

Deep learning-based voxel-wise segmentation can occasionally introduce
erroneous cortical gray-matter connections between opposing sulcal banks.
The topology-correction model identifies regions that should be removed from
the original segmentation.


Where This Fits in the Workflow
-------------------------------

Topology correction can be run as part of the complete ``purple-mri`` workflow
or independently on an existing segmentation.

When running:

.. code-block:: text

   exvivo_all

the topology-correction stage is included in the complete ex vivo processing
workflow.

For standalone topology correction, use:

.. code-block:: text

   exvivo_posthoc_topology


Standalone Workflow
-------------------

The standalone procedure takes the original ``purple-mri`` segmentation,
creates a topology-model input, runs the topology-correction model, and removes
the predicted buried-sulcus regions from the original multi-label
segmentation.

Conceptually:

.. code-block:: text

   original purple segmentation
              |
              v
     topology-model input
              |
              v
    exvivo_posthoc_topology
              |
              v
   predicted buried-sulcus regions
              |
              v
     topology-corrected segmentation
              |
              v
        foreground mask


Outputs
-------

The main outputs are:

.. code-block:: text

   final_segm.nii.gz
   foreground_mask.nii.gz

where:

* ``final_segm.nii.gz`` is the topology-corrected ``purple-mri`` segmentation.
* ``foreground_mask.nii.gz`` is the corrected anatomical foreground mask used
  in downstream processing.

If atlas parcellations have already been generated, the corrected foreground
mask can also be applied to the parcellation outputs.

See:

:doc:`parcellation`


Detailed Instructions
---------------------

The complete standalone procedure, including the exact ``c3d`` commands,
topology-model input preparation, Docker inference, keep-mask generation, and
output creation, is maintained in:

`Topology correction notes <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/topology_correction_notes.md>`_

For general Docker usage and available segmentation options, see:

`Ex vivo Docker documentation <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md>`_


Next Steps
----------

After topology correction, proceed to cortical surface reconstruction and
anatomical parcellation:

:doc:`parcellation`
