Registration
============

Overview
--------

This workflow registers a postmortem ex vivo T2w hemisphere to its matched
antemortem in vivo T1w MRI.

Registration is driven primarily by label maps (GM and WM-plus masks), and the
resulting transforms are used to warp ex vivo MRI intensities and segmentations
into in vivo space.

The implementation is provided as a bash script:

``scripts/registration_exvivo_invivo_greedy_v2.sh``


Key Ideas
---------

* In vivo segmentations are obtained using SynthSeg on 1 mm-conformed T1w MRI.
* Ex vivo MRI and topology-corrected ``purple-mri`` segmentations are resampled
  to 1 mm for compatibility.
* Labels are harmonized across ex vivo and in vivo data to create a common
  registration scheme.
* Registration proceeds in stages using ``greedy``:

  1. Moments-based initialization
  2. Affine registration (12 DOF)
  3. Deformable registration

* Final outputs include ex vivo MRI and segmentations warped into the matched
  in vivo hemisphere space.


Requirements
------------

* ``greedy`` binaries available in ``PATH``
* ``c3d`` (Convert3D)
* FreeSurfer utilities, including ``mri_label2vol``
* SynthSeg-derived segmentation of the corresponding in vivo T1w MRI
* topology-corrected ``purple-mri`` segmentation of the ex vivo MRI


Inputs
------

You will need directories containing:

* ex vivo T2w MRI volumes;
* topology-corrected ex vivo ``purple-mri`` segmentations;
* in vivo T1w MRI volumes that have been QCed and resampled/conformed to 1 mm;
* in vivo SynthSeg segmentations derived from the 1 mm T1w MRI.

The current script expects subject naming conventions consistent with the
dataset for which it was developed and uses a ``subjects=(...)`` list to define
which cases to process.


Processing Steps
----------------

1. Clean the ex vivo segmentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each label in the ex vivo segmentation, the script retains the primary
connected component to remove small spurious islands and then merges the labels
back into a cleaned segmentation.


2. Resample ex vivo MRI and segmentation to 1 mm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ex vivo MRI is resampled to 1 mm isotropic resolution, and the segmentation
is resampled into the MRI grid using FreeSurfer ``mri_label2vol`` with
header-based alignment.


3. Harmonize in vivo SynthSeg labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SynthSeg labels are retained and remapped into a simplified hemisphere-specific
label scheme.

The mapping differs for right and left hemispheres. The current script
determines the hemisphere from the available ex vivo files.


4. Harmonize ex vivo labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ex vivo ``purple-mri`` segmentation is remapped to match the simplified
in vivo label scheme used for registration.


5. Build GM and WM-plus masks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two masks are constructed for robust registration:

* a GM mask;
* a WM-plus mask combining white matter and selected deep structures.

These masks are generated for both the ex vivo and in vivo images after the
in vivo hemisphere volume is prepared.


6. Run greedy registration
~~~~~~~~~~~~~~~~~~~~~~~~~~

The script performs:

* moments-based initialization;
* 12-DOF affine registration initialized from the moments transform;
* deformable registration initialized from the affine transform.

Registration uses the corresponding GM and WM-plus masks as paired inputs.


7. Warp ex vivo MRI and segmentation into in vivo space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the estimated transforms, the script produces:

* ex vivo MRI warped to in vivo space using intensity interpolation;
* ex vivo segmentation warped to in vivo space using label interpolation.


How to Run
----------

.. note::

   The current registration script is dataset-oriented rather than a general
   command-line interface. Paths, subject identifiers, and filename patterns
   should be reviewed and adapted to the dataset before execution.

1. Open:

   ``scripts/registration_exvivo_invivo_greedy_v2.sh``

2. Set the paths at the top of the script:

   * ``exvivo_mri_dir``
   * ``exvivo_segm_dir``
   * ``exvivo_segm_cleaned_dir``
   * ``invivo_dir_mri``
   * ``invivo_dir_segm``
   * ``work_dir``

3. Set the subject list:

   .. code-block:: bash

      subjects=(INDD_XXXXXX_count_1_acq_... INDD_YYYYYY_count_2_acq_...)

4. Run:

   .. code-block:: bash

      bash scripts/registration_exvivo_invivo_greedy_v2.sh


Outputs
-------

Per subject, the script typically writes:

* cleaned ex vivo segmentation after connected-component filtering;
* 1 mm-resampled ex vivo MRI and segmentation;
* simplified in vivo hemisphere segmentation;
* ``greedy`` transforms:

  * ``moments.mat``
  * ``affine.mat``
  * ``warp.nii.gz``

* warped ex vivo products in in vivo space:

  * ex vivo MRI registered using moments, affine, and deformable transforms;
  * ex vivo segmentation registered using moments, affine, and deformable
    transforms.


Notes
-----

* The current script is tailored to a particular file naming convention and
  directory layout. Review the script and modify paths and filename patterns
  for your dataset.
* The workflow assumes that SynthSeg is run in 1 mm space for the in vivo T1w
  MRI.
* Label mappings differ between hemispheres; the current script handles right
  and left hemispheres according to the available ex vivo files.


Next Step
---------

Proceed to:

:doc:`group_analysis`

for ROI-wise and/or voxel- or vertex-wise statistical analyses once subjects
have been aligned.
