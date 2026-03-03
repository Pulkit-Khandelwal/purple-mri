Parcellation
============

Overview
--------

Once you have obtained a topology-corrected volumetric segmentation,
you can proceed to the surface-based pipeline to obtain whole-hemisphere
cortical parcellations in standard neuroanatomical atlases.

This step runs locally (CPU only; no GPU required).

The pipeline prepares the data, computes necessary transformations,
performs surface modeling and topology stabilization, and generates
atlas-based parcellations.

Requirements
------------

* FreeSurfer installed locally  
  (tested with FreeSurfer 7.4.0 on Linux)

* Python dependencies listed in ``dependencies.txt``  
  Install using:

  .. code-block:: bash

     pip install -r dependencies.txt

* A topology-corrected volumetric segmentation (e.g., 10-label output)

Optional: 1mm Conforming
------------------------

You may run the pipeline at 1mm resolution by conforming the MRI and
segmentation to MNI space.

Reference snippet:
https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/misc_scripts/flip_conform.sh

Running the Surface-Based Pipeline
----------------------------------

Clone the repository and run ``run_surface_pipeline.sh`` from within
the ``purple_mri`` directory.

Inputs
~~~~~~

The script requires the following arguments:

* ``freesurfer_path`` — path to the FreeSurfer installation
* ``working_dir`` — directory where outputs will be stored
* ``mri_path`` — directory containing MRI images (NIfTI)
* ``segm_path`` — directory containing topology-corrected segmentations
* ``external_atlases_path`` — directory containing additional atlas resources
* ``num_threads`` — number of CPU threads
* ``hemis`` — hemisphere flag (``rh`` or ``lh``)

Data Organization
~~~~~~~~~~~~~~~~~

* Place MRI volumes in ``mri_path``
* Place corresponding segmentation volumes in ``segm_path``
* Ensure MRI and segmentation filenames match exactly (both ending in ``.nii.gz``)
* Place ``fsaverage`` in ``working_dir``

Command
~~~~~~~

.. code-block:: bash

   cd purple_mri

   bash run_surface_pipeline.sh \
     freesurfer_path \
     working_dir \
     mri_path \
     segm_path \
     external_atlases_path \
     num_threads \
     rh

Atlases
-------

The pipeline produces parcellations in commonly used atlases, including:

* Desikan–Killiany–Tourville (DKT)
* Schaefer
* Glasser
* von Economo–Koskinas

Outputs
-------

Typical outputs include:

* White and pial cortical surfaces
* Native-space atlas parcellations
* ROI-level statistics
* Vertex-wise cortical measures (e.g., thickness)

Next Step
---------

Proceed to:

:doc:`group_analysis`

for vertex-wise and ROI-wise statistical modeling.
