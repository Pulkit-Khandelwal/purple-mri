Surface reconstruction and parcellation
===============================================

The current Docker surface stage uses the MRI and corrected Purple 10-label
segmentation. Run it after DL in one command or use ``--segmentation`` to supply
an existing corrected result; see :doc:`quickstart`. Select ``--hemi lh`` or
``--hemi rh``, provide a FreeSurfer license, and choose an appropriate thread count.

The image supplies the surface tools and atlas assets. Results include white
and pial surfaces, spherical registration, annotations, regional statistics,
and atlas volumes. The working directory contains MRI copies and intermediates;
keep enough space for them. The surface script requires a fresh output directory.

Atlas volumes
---------------------

The current script writes the following under
``OUTPUT/exvivo_surface/SUBJECT/mri``:

.. list-table::
   :header-rows: 1

   * - File
     - Atlas or labeling
   * - ``aparc.mgz``
     - Desikan–Killiany
   * - ``DKTatlas.mgz``
     - Desikan–Killiany–Tourville
   * - ``a2009s.mgz``
     - Destrieux
   * - ``brainnetome.mgz``
     - Brainnetome
   * - ``HCP-MMP1.glasser.mgz``
     - HCP-MMP1 / Glasser
   * - ``Schaefer2018_400Parcels_17Networks.mgz``
     - Schaefer 400 parcels, 17 networks
   * - ``julich.mgz``
     - Jülich
   * - ``economo.mgz``
     - von Economo–Koskinas
   * - ``wmparc.mgz``
     - White-matter parcellation

For an optional NIfTI conversion, with FreeSurfer available:

.. code-block:: bash

   mri_convert /path/to/SUBJECT/mri/DKTatlas.mgz /path/to/DKTatlas.nii.gz

This changes the storage format; it does not guarantee alignment to a different
reference grid. Compare geometry with the original MRI. If resampling labels is
needed, use an appropriate transform and nearest-neighbor interpolation.

Single-hemisphere conventions
-------------------------------------

The script creates opposite-hemisphere copies of selected surfaces and annotations
for compatibility with volume-generation commands. These copies are not a second
anatomical hemisphere. Interpret and distribute the requested hemisphere's
surfaces and annotations accordingly.

The working ASEG preparation retains an inherited RH-coded convention, including
for LH runs. Do not infer anatomical laterality from working label numbers alone.
Check LH volume labels and statistics before laterality-sensitive analysis. This
release documents that behavior and does not alter the surface algorithm or
scientific label mapping.

Validation status
-------------------------

The maintainer's LH Docker surface/parcellation run completed with exit 0 and
its COMPLETE marker in 2:17:06. It used the development CLI with the same Docker
image selected by release 1.1.0. A native SIF candidate also completed the remaining
surface steps after a transform working-directory fix was mounted for a resumed
test. The rebuilt final SIF still requires its own uninterrupted test. See
:doc:`release_notes` for exact scope. These results do not replace anatomical QC.
