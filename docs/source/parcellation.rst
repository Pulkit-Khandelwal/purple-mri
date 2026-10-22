Surface reconstruction and parcellation
===============================================

The Docker surface stage uses the MRI and corrected Purple 10-label
segmentation. Run it after DL in one command or use ``--segmentation`` to supply
an existing corrected result; see :doc:`quickstart`. Select ``--hemi lh`` or
``--hemi rh``, provide a FreeSurfer license, and choose an appropriate thread count.

The image supplies the surface tools and atlas assets. Results include white
and pial surfaces, spherical registration, annotations, regional statistics,
and atlas volumes. The working directory contains MRI copies and intermediates;
keep enough space for them. The surface script requires a fresh output directory.

For results returned by the ITK-SNAP service, see :doc:`itksnap` for the three
parcellation ZIP files containing converted NIfTIs. The local Docker output and
conversion instructions below describe the full processing directories.

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

Export NIfTI files using Docker
-------------------------------

Use the bundled FreeSurfer tools; no host FreeSurfer installation is required.
The following exports all nine volumes from one completed subject into a new
folder. Edit the paths and keep the original MGZ outputs.

.. code-block:: bash

   (
   set -euo pipefail
   SUBJECT_DIR="/absolute/path/results/exvivo_surface/SUBJECT"
   EXPORT_DIR="/absolute/path/new_nifti_export"
   LICENSE="/absolute/path/license.txt"
   test -d "$SUBJECT_DIR/mri"
   test -s "$LICENSE"
   mkdir "$EXPORT_DIR"
   docker run --rm \
     --mount "type=bind,src=$SUBJECT_DIR,dst=/subject,readonly" \
     --mount "type=bind,src=$EXPORT_DIR,dst=/export" \
     --mount "type=bind,src=$LICENSE,dst=/license.txt,readonly" \
     --env FS_LICENSE=/license.txt --env NO_FSFAST=1 \
     --entrypoint /bin/bash pulks/docker_purple_mri:v1.1.0 -c '
       set -eo pipefail
       source /opt/freesurfer/SetUpFreeSurfer.sh
       for atlas in aparc DKTatlas a2009s brainnetome HCP-MMP1.glasser \
         Schaefer2018_400Parcels_17Networks julich economo wmparc; do
         test -s "/subject/mri/$atlas.mgz"
         mri_convert "/subject/mri/$atlas.mgz" "/export/$atlas.nii.gz"
       done
     '
   )

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
