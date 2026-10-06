Template Construction
=====================

Overview
--------

``purple-mri`` supports construction of a population-specific ex vivo intensity
template using iterative deformable registration.

Template construction proceeds in two stages:

1. Segmentation-based initialization
2. MRI intensity-based refinement

The required scripts are included in:

``scripts/intensity_template``

The main driver script is:

``greedy_build_template.sh``


Prerequisites
-------------

The template-building workflow requires:

* ``greedy``
* ``greedy_template_average``
* ``jq``
* ``c3d``
* the scripts in ``scripts/intensity_template``

Ensure that the required binaries are available in ``PATH``:

.. code-block:: bash

   export PATH="/path/to/greedy_binaries/":$PATH


Pre-processing
--------------

Before template construction:

1. Ensure that all images and corresponding segmentations are in the same
   orientation. ``c3d`` can be used for reorientation when needed.

2. Binarize and smooth the topology-corrected ``purple-mri`` segmentations:

   .. code-block:: bash

      c3d segm.nii.gz \
        -thresh 1 inf 1 0 \
        -smooth-fast 0.4mm \
        -o segm_binary_smooth.nii.gz

This produces smoothed binary masks used for robust initial alignment.


Stage 1 - Segmentation-Based Initial Template
---------------------------------------------

Select one subject as a reference subject (``reference_subj``).

Using parameters defined in ``params_ssd.json``, build an initial
segmentation-based template:

.. code-block:: bash

   bash greedy_build_template.sh \
     -p params_ssd.json \
     -i manifest_segm.csv \
     -T reference_subj \
     -o template_init_segm

Where:

* ``manifest_segm.csv`` lists all subjects and paths to smoothed binary
  segmentations;
* ``template_init_segm`` is the output directory;
* SSD (sum of squared differences) is used as the similarity metric.

This produces the segmentation-based initialization used for the intensity
template.


Stage 2 - MRI-Based Intensity Template
--------------------------------------

Step 1 - Warp each subject MRI to the segmentation-based template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run:

.. code-block:: bash

   bash warp_and_mri_init_template.sh

This generates MRI volumes initialized in the common template space.


Step 2 - Build an initial MRI template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The initialized MRIs are averaged to create:

``mri_initial_template.nii.gz``


Step 3 - Refine with NCC-based registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using parameters defined in ``params_ncc.json`` and a manifest file
(``manifest_mri_warped.csv``), build the final ex vivo intensity template:

.. code-block:: bash

   bash greedy_build_template.sh \
     -p params_ncc.json \
     -i manifest_mri_warped.csv \
     -t mri_initial_template.nii.gz \
     -o template_exvivo_mri_template

NCC (normalized cross-correlation) is used as the similarity metric for the
intensity-based refinement.


Outputs
-------

The final outputs include:

* the population-specific ex vivo MRI intensity template;
* subject-to-template deformation fields;
* inverse mappings from template to subject space.

These mappings enable:

* voxel-wise morphometric analysis;
* deformation-based morphometry;
* template-space statistical modeling.


Credits
-------

The template-building framework is based on scripts originally developed by
Paul A. Yushkevich and adapted for ex vivo MRI analysis in ``purple-mri``.
