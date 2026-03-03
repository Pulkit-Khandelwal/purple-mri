Segmentation
============

Overview
--------

The segmentation stage produces an initial volumetric labeling for high-resolution postmortem MRI.
These outputs are used for downstream post-hoc correction, surface reconstruction, and parcellation.

The workflow consists of:

1. Pre-processing (bias correction and normalization)
2. Deep learning–based inference via Docker
3. Generation of label maps for the requested task

Pre-processing
--------------

Prior to inference, perform bias correction and intensity normalization/standardization.

Recommended tools:

* ``N4BiasFieldCorrection`` (ANTs)
* ``c3d`` (Convert3D)

We strongly recommend providing an input mask to ``N4BiasFieldCorrection``.
A coarse mask can be obtained via thresholding.

Example reference script:
https://github.com/Pulkit-Khandelwal/upenn-picsl-brain-ex-vivo/tree/main/misc_scripts/perform_bias_correction.sh

Input Naming Convention
-----------------------

Place preprocessed image(s) inside a folder named:

``data_for_inference``

Each image must end with:

``_0000.nii.gz``

Example:

``subject01_0000.nii.gz``

Deep Learning Inference (Docker)
--------------------------------

Docker image:
https://hub.docker.com/r/pulks/docker_hippogang_exvivo_segm

Step 1 — Prepare the data
-------------------------

Create the following folder structure:

.. code-block:: text

   /data/username/data_for_inference/

Place your preprocessed image(s) in ``data_for_inference`` (do not rename this folder).

Step 2 — Pull the Docker image
------------------------------

Replace ``${LATEST_TAG}`` with the latest available version (see Docker changelog).

.. code-block:: bash

   docker pull pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG}

Step 3 — Run the Docker container
---------------------------------

Run the following command to start inference. The volume mount should point to the directory
that contains ``data_for_inference`` (here: ``/data/username/``).

.. code-block:: bash

   docker run --gpus all --privileged \
     -v /data/username/:/data/exvivo/ \
     -it pulks/docker_hippogang_exvivo_segm:v${LATEST_TAG} \
     /bin/bash -c "bash /src/commands_nnunet_inference.sh ${OPTION}" >> logs.txt

Replace:

* ``${LATEST_TAG}`` with the Docker version
* ``${OPTION}`` with one of the options listed below

Model / Task Options
--------------------

Choose one of the following options depending on the segmentation or utility you need:

* ``${OPTION}=exvivo_t2w``  
  Model trained on ex vivo T2w MRI to produce the 10-label segmentation.  
  **Note:** use this option for **FLASH MRI as well** (current recommendation; dt: 05/05/2025).

* ``${OPTION}=exvivo_flash_more_subcort``  
  FLASH (T2*) model that adds four additional labels: hypothalamus, optic chiasm,
  anterior commissure, fornix.

* ``${OPTION}=exvivo_ciss_t2w``  
  Multi-input model intended to address anterior/posterior missing segmentation issues.

* ``${OPTION}=exvivo_flash_thalamus``  
  FLASH model for thalamus segmentation.

* ``${OPTION}=invivo_flair_wmh``  
  White matter hyperintensity segmentation for in vivo FLAIR MRI. The image should be
  skull-stripped and normalized/standardized.

* ``${OPTION}=exvivo_flash_gm_wm_segm``  
  FLASH model trained for GM/WM segmentation.

* ``${OPTION}=exvivo_posthoc_topology``  
  Model for post-hoc topology correction (bridge/sulcal-GM connection mitigation).

* ``${OPTION}=exvivo_umc_strip_cerebellum``  
  Utility to strip cerebellum from UMC MRI.

Output
------

The output is written to:

``/your/path/to/data_for_inference/output_from_nnunet_inference``

Notes
-----

* You may see warnings printed during inference; these can typically be ignored.
* Expected runtime is approximately ~15 minutes for ex vivo whole-hemisphere inference
  (hardware dependent).
* For in vivo FLAIR WMH, inference typically completes in ~1 minute.

Next Step
---------

For topology stabilization prior to surface reconstruction, see:

:doc:`posthoc_correction`
