Inputs, contrast and hemisphere
=================================

Prepare 3-D single-channel NIfTI MRI with a filename such as
``SUBJECT_0000.nii.gz``. Every top-level ``*.nii.gz`` in the input folder must
follow that convention and be nonempty. Subject identifiers start with a letter
or digit and may contain letters, digits, underscores, hyphens and periods.
The ``_0000`` suffix identifies the input channel; predictions omit it.

Preserve spatial metadata, voxel spacing and anatomical orientation. Keep MRI
and segmentation files in separate folders. Symlinks must resolve inside the
mounted input root. Docker bind paths may contain spaces, but not commas or
newlines.

Contrast and hemisphere
-------------------------

Pipeline stages require ``--contrast t2w``, ``ciss``, ``flash`` or ``t2star``.
Use one contrast per batch. FLASH/T2* selects the Task278 refinement route;
T2w/CISS uses the baseline tissue route.

Surface and atlas stages also require ``--hemi lh`` or ``--hemi rh``. Every scan
in that batch must represent the selected anatomical hemisphere. Select the
actual hemisphere; do not mirror the data to choose a route. Direct container
commands accept these same contrast/hemisphere flags.

Reusing DL results
--------------------

For a standalone surface run, pass ``--dl-dir`` pointing to the complete v1.2.0
DL root, including ``11_final_merged``, ``12_surface_labels`` and reports.
MRI and labels must agree in subject identity, shape and spatial geometry.
The container uses ``12_surface_labels/SUBJECT.nii.gz`` for reconstruction.

The reconstruction label vocabulary is:

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


Output directories
--------------------

Use a new or empty output directory for a first CLI run, separate from and not
nested within the input or reused-result directories. To continue the same run,
repeat the original command with ``--resume`` and matching inputs/options.

MRI inputs are read-only. Surface processing writes checkpoints in its reused
DL root. Atlas-only reuse mounts existing DL and surface roots read-only and
writes new atlas results beneath the new output root. See :doc:`quickstart`.
