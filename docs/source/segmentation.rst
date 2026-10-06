Segmentation
============

Overview
--------

The segmentation stage produces volumetric anatomical label maps from high-resolution
postmortem MRI. These segmentations are used for downstream correction, cortical surface
reconstruction, anatomical parcellation, and quantitative analysis.

The recommended workflow consists of:

1. Pre-processing the MRI using bias-field correction and intensity normalization.
2. Running the ``purple-mri`` deep learning segmentation pipeline using Docker.
3. Using the generated label maps for downstream processing.

The complete ex vivo segmentation pipeline can be run using the ``exvivo_all`` option.
Individual segmentation models can also be run separately; see the detailed Docker
documentation for the complete list of available models and options.

Current Docker version: ``v1.4.6``.


Pre-processing
--------------

Before segmentation, perform bias-field correction and intensity
normalization/standardization of the MRI.

Recommended tools include:

* ``N4BiasFieldCorrection`` from ANTs
* ``c3d`` from Convert3D

We strongly recommend providing an input mask to ``N4BiasFieldCorrection``.
A coarse mask can be generated using intensity thresholding.

An example bias-correction script is available here:

https://github.com/Pulkit-Khandelwal/upenn-picsl-brain-ex-vivo/tree/main/misc_scripts/perform_bias_correction.sh


Input Naming Convention
-----------------------

Place the preprocessed MRI inside a directory named:

.. code-block:: text

   data_for_inference

Do **not** rename this directory.

Each input image must end with:

.. code-block:: text

   _0000.nii.gz

For example:

.. code-block:: text

   data_for_inference/
   └── 100085R_reslice_0000.nii.gz


Deep Learning Inference
-----------------------

The ``purple-mri`` segmentation models are distributed as a Docker image:

https://hub.docker.com/r/pulks/docker_hippogang_exvivo_segm

The recommended approach is to run the complete ex vivo pipeline using
``exvivo_all``.


Step 1 - Prepare the Data
-------------------------

Place ``data_for_inference`` inside a directory that will be mounted into the
Docker container.

For example:

.. code-block:: text

   /data/pulkit/docker_stuff/data_for_inference_v146/
   └── data_for_inference/
       └── 100085R_reslice_0000.nii.gz

In this example, the directory:

.. code-block:: text

   /data/pulkit/docker_stuff/data_for_inference_v146/

will be mounted to ``/data/exvivo`` inside the Docker container.


Step 2 - Pull the Docker Image
------------------------------

Pull version ``v1.4.6`` of the Docker image:

.. code-block:: bash

   docker pull pulks/docker_hippogang_exvivo_segm:v1.4.6


Step 3 - Run the Complete Ex Vivo Pipeline
------------------------------------------

The following is an example command for running the complete ex vivo segmentation
pipeline:

.. code-block:: bash

   docker run --rm --gpus all --shm-size=8g 
     -v /data/pulkit/docker_stuff/data_for_inference_v146:/data/exvivo 
     pulks/docker_hippogang_exvivo_segm:v1.4.6 
     /bin/bash /src/commands_nnunet_inference.sh exvivo_all

Here:

* ``--rm`` removes the Docker container automatically after the run finishes.
* ``--gpus all`` makes the available NVIDIA GPU(s) accessible to the container.
* ``--shm-size=8g`` provides additional shared memory for inference.
* ``-v`` mounts the host directory containing ``data_for_inference`` to
  ``/data/exvivo`` inside the container.
* ``v1.4.6`` specifies the Docker image version.
* ``exvivo_all`` runs the complete ex vivo segmentation pipeline.


Running Individual Segmentation Models
--------------------------------------

The example above uses ``exvivo_all`` because this is the recommended option for
running the complete segmentation workflow.

Individual segmentation models can also be run separately by replacing
``exvivo_all`` with the corresponding model option.

Available models include segmentation of cortical and subcortical structures,
MTL and amygdala subfields, thalamus, additional FLASH structures, and other
specialized tasks.

For the complete list of available ``${OPTION}`` values and instructions for
running individual models, see:

`Detailed Docker documentation <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md>`_


Output
------

Segmentation outputs are written back to the mounted ``data_for_inference``
directory on the host machine.

The main output directory is:

.. code-block:: text

   data_for_inference/
   └── output_from_nnunet_inference/

The exact contents of ``output_from_nnunet_inference`` depend on whether the
complete ``exvivo_all`` pipeline or an individual segmentation model is run.

Because the input directory is mounted into the Docker container, all generated
outputs remain available on the host machine after the container exits.


Notes
-----

* Input NIfTI files must follow the ``*_0000.nii.gz`` naming convention.
* The input directory must be named ``data_for_inference``.
* The current documented Docker version is ``v1.4.6``.
* Warnings may appear in the terminal during inference; if the pipeline continues
  normally, these can generally be ignored.
* Runtime depends on the selected model, image size, and available GPU hardware.
* Use ``exvivo_all`` when the complete ex vivo segmentation workflow is desired.
* Use an individual model option when only a particular segmentation task is needed.


Additional Docker Documentation
-------------------------------

Detailed documentation for the Docker image, including all available model options
and the Docker version change log, is available here:

`Ex vivo Docker documentation <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md>`_


Post-hoc Topology Correction
----------------------------

Documentation for standalone post-hoc topology correction is available here:

:doc:`posthoc_correction`
