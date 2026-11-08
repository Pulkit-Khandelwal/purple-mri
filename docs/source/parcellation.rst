Surface reconstruction and atlas merging
==========================================

The surface stage uses ``dl/12_surface_labels/SUBJECT.nii.gz``, derived from the
final detailed tissue merge. Supply the complete v1.2.0 DL root, matching MRI,
actual ``lh`` or ``rh`` hemisphere and a FreeSurfer license. See :doc:`quickstart`
for combined and surface-only commands.

The pipeline creates white/pial surfaces, spherical registration, cortical
annotations, metrics and regional statistics. Brainnetome correction uses valid
same-side labels inside the selected cortex before atlas projection. It supports
either anatomical hemisphere.

Seven final atlas merges
--------------------------

Existing surface projections are reused after provenance validation. Atlas
labels are assigned to the final cortical GM mask; remaining generic GM 101 is
assigned to nearby cortical parcels. Detailed MTL, subcortical and other
noncortical labels are preserved. Outputs use the native MRI grid.

.. list-table:: Files under ``atlases/SUBJECT/mri``
   :header-rows: 1
   :widths: 24 76

   * - Atlas
     - Final NIfTI
   * - DKT
     - ``aparc.DKTatlas+aseg_with_dl_structures.nii.gz``
   * - Destrieux
     - ``aparc.a2009s+aseg_with_dl_structures.nii.gz``
   * - Glasser / HCP-MMP1
     - ``aparc.HCP-MMP1.glasser_with_dl_structures.nii.gz``
   * - Schaefer400, 17 networks
     - ``aparc.Schaefer2018_400Parcels_17Networks_with_dl_structures.nii.gz``
   * - von Economo
     - ``aparc.economo_with_dl_structures.nii.gz``
   * - Julich
     - ``aparc.julich_with_dl_structures.nii.gz``
   * - Brainnetome
     - ``aparc.brainnetome_with_dl_structures.nii.gz``

Each atlas has its own lookup table and provenance under the subject's atlas
output directory. Use those tables when loading the final NIfTIs in ITK-SNAP.
The tissue map plus seven atlas maps make eight final segmentation outputs.

Reusing projections
---------------------

.. code-block:: bash

   purple-mri run exvivo_atlas_merge --contrast flash --hemi rh \
     --input /absolute/path/inputs \
     --dl-dir /absolute/path/completed_results/dl \
     --surface-dir /absolute/path/completed_results/surface \
     --output /absolute/path/new_atlas_results \
     --license /absolute/path/license.txt --threads 8

The container checks that surfaces, annotations and projections match the
recorded reconstruction inputs. This command performs atlas merging from the
existing projections. Keep the complete subject directories and provenance.

Surface working outputs
-------------------------

``surface/SUBJECT`` contains ``surf``, ``label``, ``mri``, ``stats`` and ``qc``.
Its projected atlas volumes include ``aparc.mgz``, ``DKTatlas.mgz``,
``a2009s.mgz``, ``HCP-MMP1.glasser.mgz``,
``Schaefer2018_400Parcels_17Networks.mgz``, ``brainnetome.mgz``,
``economo.mgz``, ``julich.mgz`` and ``wmparc.mgz``. These nine working projections
are distinct from the seven final native-grid tissue/atlas merges above.

The selected hemisphere identifies the anatomical surfaces. Opposite-hemisphere
compatibility copies can also be present for volume-generation tools; interpret
results using the requested hemisphere and provenance, not filenames alone.
Working ASEG conventions and final merged-label conventions also differ.

Review white/pial boundaries, cortical coverage, atlas boundaries, hemisphere
identity and label tables with the original MRI. See :doc:`qc`.
