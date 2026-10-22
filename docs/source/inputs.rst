Inputs and hemisphere selection
=======================================

Input files
-------------------

The adult DL workflow takes 3-D, single-channel NIfTI MRI. Put files directly in
the input directory, for example ``donor123_0000.nii.gz``. The subject identifier
may contain letters, digits, underscores, hyphens, and periods; it must start
with a letter or digit. Avoid spaces in filenames. Every top-level ``*.nii.gz``
file in that directory must follow this naming convention and be nonempty.

The suffix ``_0000`` denotes the input channel. Outputs remove that suffix:
``donor123.nii.gz``. Do not place raw MRI and segmentation NIfTIs together in the
input folder. Symlinks must resolve within their respective mounted directory.
The CLI accepts host directory names with spaces, but rejects commas and newlines
in Docker bind paths.

Preserve the MRI's spatial metadata, voxel spacing, and anatomical orientation.
The CLI does not determine the hemisphere from a filename, resample the scan, or
verify its acquisition domain. Use data appropriate to the selected model and
inspect atypical contrast, damaged tissue, or unusual geometry individually.

Hemisphere
------------------

``--hemi lh`` or ``--hemi rh`` is required for surface stages. Every scan in a
surface batch must belong to that hemisphere. DL-only runs do not require this
flag. Task2732 is the flip-fixed subcortical model selected by both the combined
DL stage and the standalone subcortical option.

Surface-only segmentation
---------------------------------

``--segmentation`` must point to corrected Purple 10-label files named
``SUBJECT.nii.gz``, matching every MRI's identifier. Their shape, affine, and
spacing must agree with the MRI. The container checks these conditions and label
values. Use the ``05_purple_corrected`` output, not ``11_final_merged`` and not a
standalone Task2732 result. The surface path treats WMH as white matter in a
separate working copy while retaining the corrected segmentation.

The corrected Purple label convention is:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Value
     - Structure
   * - 0
     - Background
   * - 1
     - Cortical gray matter
   * - 2
     - Putamen
   * - 3
     - Caudate
   * - 4
     - Pallidum
   * - 5
     - Thalamus
   * - 6
     - White matter hyperintensities (WMH)
   * - 7
     - White matter
   * - 8
     - Ventricle
   * - 9
     - Corpus callosum
   * - 10
     - Medial temporal lobe (MTL)

Output location
-----------------------

Output must be new or empty. It cannot equal, contain, or be contained within
the input directory. Surface segmentation inputs must also remain separate from
output. There is no automatic resume or overwrite. The CLI binds MRI inputs,
segmentation inputs, and the license read-only; results are written to the
separate output mount.
