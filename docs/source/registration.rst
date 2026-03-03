Registration
============

Overview
--------

This workflow registers a postmortem ex vivo T2w hemisphere to its matched antemortem in vivo T1w MRI.
Registration is driven primarily by label maps (GM and WM-plus masks), and the resulting transforms are used
to warp ex vivo MRI intensities and segmentations into in vivo space.

The implementation is provided as a bash script:

``scripts/registration_exvivo_invivo_greedy_v2.sh``

Key Ideas
---------

* In vivo segmentations are obtained using SynthSeg on 1mm-conformed T1w.
* Ex vivo MRI and 10-label segmentations are resampled to 1mm for compatibility.
* Labels are harmonized across ex vivo and in vivo to create a common registration scheme.
* Registration proceeds in stages using greedy:

  1. Moments-based initialization
  2. Affine (12 DOF)
  3. Deformable

* Final outputs include ex vivo MRI/segmentations warped into the in vivo hemisphere space.

Requirements
------------

* ``greedy`` binaries available in ``PATH``
* ``c3d`` (Convert3D)
* FreeSurfer utilities (used by the script), e.g., ``mri_label2vol``
* SynthSeg output for in vivo T1w (1mm space)

Inputs
------

You will need directories for:

* Ex vivo MRI (T2w) volumes
* Ex vivo 10-label segmentations (purple-mri output)
* In vivo MRI (T1w) volumes (QCed + resampled/conformed to 1mm)
* In vivo SynthSeg segmentations (derived from the 1mm T1w)

The script expects subject naming conventions consistent with your dataset (INDD IDs) and uses a
``subjects=(...)`` list to define which cases to process.

Processing Steps (What the Script Does)
---------------------------------------

1) Clean the ex vivo 10-label segmentation (largest connected component per label)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each label in the ex vivo segmentation, the script retains the primary connected component to remove
small spurious islands, then merges labels back into a cleaned segmentation.

2) Resample ex vivo MRI and segmentation to 1mm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ex vivo MRI is resampled to 1mm isotropic, and the segmentation is resampled into the MRI grid using
FreeSurfer ``mri_label2vol`` with header-based alignment.

3) Harmonize in vivo SynthSeg labels to a compact hemisphere label set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SynthSeg labels are retained and remapped into a simplified label scheme.
The mapping differs for right vs left hemispheres (the script auto-detects hemisphere based on file existence).

4) Harmonize ex vivo labels to the same scheme
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ex vivo 10-label map is remapped to match the simplified in vivo scheme used for registration.

5) Build GM and WM-plus binary masks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two masks are constructed for robust registration:

* GM mask (typically cortical GM plus selected GM class)
* WM-plus mask (WM and deep structures grouped)

These are extracted for both ex vivo and in vivo, after trimming the in vivo hemisphere volume.

6) Run greedy registration (moments → affine → deformable)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The script performs:

* Moments-based alignment (initialization)
* 12-DOF affine alignment initialized from moments
* Deformable alignment initialized from affine

Registration uses GM and WM-plus masks as paired inputs.

7) Warp ex vivo MRI and segmentation into in vivo space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the estimated transforms, the script produces:

* ex vivo MRI warped to in vivo space (linear interpolation)
* ex vivo segmentation warped to in vivo space (label interpolation)

How to Run
----------

1. Open:

``scripts/registration_exvivo_invivo_greedy_v2.sh``

2. Set paths at the top of the script:

* ``exvivo_mri_dir``
* ``exvivo_segm_dir``
* ``exvivo_segm_cleaned_dir``
* ``invivo_dir_mri``
* ``invivo_dir_segm``
* ``work_dir``

3. Set the subject list:

.. code-block:: bash

   subjects=(INDD_XXXXXX_count_1_acq_...  INDD_YYYYYY_count_2_acq_...)

4. Run:

.. code-block:: bash

   bash scripts/registration_exvivo_invivo_greedy_v2.sh

Outputs
-------

Per subject, the script typically writes:

* Cleaned ex vivo segmentation (connected-component filtered)
* 1mm-resampled ex vivo MRI and segmentation
* In vivo simplified segmentation (hemisphere relabeled)
* Greedy transforms:

  * ``moments.mat``
  * ``affine.mat``
  * ``warp.nii.gz``

* Warped ex vivo products in in vivo space:

  * ex vivo MRI registered (moments / affine / deformable)
  * ex vivo segmentation registered (moments / affine / deformable)

Notes
-----

* This script is opinionated to a particular file naming convention and directory layout.
  Please read the header comments and adjust variable names and file patterns as needed.
* The workflow assumes SynthSeg is run in 1mm space for the in vivo T1w.
* Label mappings differ across hemispheres; the script handles R/L by checking which ex vivo file exists.

Next Step
---------

Proceed to:

:doc:`group_analysis`

to run ROI-wise and/or voxel/vertex-wise statistical analyses once subjects are aligned.
