Parcellation
============

Overview
--------

Once a topology-corrected volumetric segmentation has been obtained, the
``purple-mri`` surface-based pipeline can be used to reconstruct the cortical
surfaces and generate whole-hemisphere anatomical parcellations.

The pipeline combines custom processing with FreeSurfer tools to:

* prepare the volumetric segmentation for surface reconstruction;
* create a FreeSurfer-style subject directory;
* generate and decimate the initial cortical mesh;
* compute the required spatial transformations and orientations;
* perform surface-based topology correction;
* reconstruct the white and pial cortical surfaces;
* register the cortical surface to ``fsaverage``;
* transfer multiple anatomical atlases to the subject;
* generate volumetric atlas parcellations;
* compute cortical morphometry and regional statistics.

The user-facing entry point for this workflow is:

.. code-block:: text

   run_surface_pipeline.sh

The individual scripts called by this wrapper, including ``parcellation.sh``,
are run automatically.


Input from Segmentation and Topology Correction
-----------------------------------------------

The surface pipeline should be run using the topology-corrected
``purple-mri`` segmentation.

See:

:doc:`segmentation`

and:

:doc:`posthoc_correction`

The MRI and corresponding segmentation must:

* be in the same voxel grid and spatial alignment;
* have matching filenames;
* end in ``.nii.gz``.

For example:

.. code-block:: text

   mri/
   └── subject01.nii.gz

   segmentation/
   └── subject01.nii.gz

The subject identifier is obtained automatically from the MRI filename.


Requirements
------------

The surface-based pipeline is primarily CPU-based and does **not** require a
GPU.

The following are required:

* Linux
* FreeSurfer
* Docker or Singularity for the custom pial-surface placement binary
* Python dependencies listed in ``dependencies.txt``
* a topology-corrected ``purple-mri`` segmentation
* the required external atlas resources
* ``fsaverage`` in the working directory

The pipeline has been developed and tested using FreeSurfer ``7.4.0``.

Install the Python dependencies from the repository root using:

.. code-block:: bash

   pip install -r dependencies.txt


Custom Pial-Surface Placement
-----------------------------

For **pial-surface placement only**, ``purple-mri`` uses a custom compiled
version of the FreeSurfer ``mris_place_surface`` binary.

The binary is distributed as a Docker image archive so that users do not need
to compile it locally.

Before running the surface pipeline, follow the setup instructions here:

`Pial-surface binary setup <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/pial_surface_binary_docker_singularity.md>`_

The Docker image is distributed through the following GitHub release:

`purple-mris-place-surface release <https://github.com/Pulkit-Khandelwal/purple-mri/releases/tag/v0.1.0-fs-binary-docker>`_

Once the Docker or Singularity image has been prepared, the custom binary is
called automatically from ``parcellation.sh`` during pial-surface placement.

No separate command is required during normal execution of the complete
surface pipeline.


How the Surface Pipeline Works
------------------------------

``run_surface_pipeline.sh`` coordinates the complete surface-reconstruction
and parcellation workflow.

The major stages are:

1. **Prepare the segmentation**

   Convert the topology-corrected volumetric segmentation into the files
   required for cortical surface reconstruction.

2. **Create the FreeSurfer-style subject structure**

   Generate the MRI, surface, label, transform, and statistics directories and
   files used by subsequent FreeSurfer tools.

3. **Create the initial cortical mesh**

   Generate the cortical surface mesh and prepare a decimated representation
   for downstream processing.

4. **Compute transformations and orientations**

   Generate the transformations required to place the reconstructed surface
   into the appropriate FreeSurfer coordinate systems.

5. **Perform surface topology correction**

   Correct the topology of the cortical mesh before final surface placement.

6. **Reconstruct and parcellate the cortical surface**

   Reconstruct white and pial surfaces, perform spherical registration,
   transfer anatomical atlases, create volumetric parcellations, and compute
   cortical morphometry and statistics.


Optional 1 mm Conforming
------------------------

The MRI and segmentation may optionally be conformed to 1 mm resolution before
running the surface pipeline.

A reference script is available here:

`flip_conform.sh <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/misc_scripts/flip_conform.sh>`_

This step is optional and should only be used when a 1 mm conformed workflow is
desired.


Data Organization
-----------------

A typical input organization is:

.. code-block:: text

   project/
   ├── mri/
   │   ├── subject01.nii.gz
   │   ├── subject02.nii.gz
   │   └── ...
   │
   ├── segmentation/
   │   ├── subject01.nii.gz
   │   ├── subject02.nii.gz
   │   └── ...
   │
   └── working_dir/
       └── fsaverage/

The MRI and segmentation filenames must correspond exactly.

For example:

.. code-block:: text

   mri/100085R.nii.gz
   segmentation/100085R.nii.gz

The pipeline automatically determines the list of subjects from the NIfTI
files in ``mri_path``.


External Atlas Resources
------------------------

Several parcellations require atlas files that are not part of the standard
FreeSurfer installation.

The ``external_atlases_path`` argument should point to the directory containing
the required atlas resources.

The current parcellation workflow uses external resources for atlases including:

* Brainnetome
* Schaefer
* HCP-MMP1 / Glasser
* Jülich
* von Economo-Koskinas

These resources are accessed by ``parcellation.sh`` during atlas transfer.


Running the Surface Pipeline
----------------------------

Clone the ``purple-mri`` repository and enter the ``purple_mri`` directory:

.. code-block:: bash

   git clone https://github.com/Pulkit-Khandelwal/purple-mri.git
   cd purple-mri/purple_mri

Run:

.. code-block:: bash

   bash run_surface_pipeline.sh 
     freesurfer_path 
     working_dir 
     mri_path 
     segm_path 
     external_atlases_path 
     num_threads 
     rh

The arguments are:

``freesurfer_path``
   Path to the local FreeSurfer installation.

``working_dir``
   Directory in which the FreeSurfer-style subject directories and pipeline
   outputs will be created.

``mri_path``
   Directory containing the input MRI volumes.

``segm_path``
   Directory containing the corresponding topology-corrected segmentations.

``external_atlases_path``
   Directory containing the additional atlas resources.

``num_threads``
   Number of CPU threads to use.

``hemis``
   Hemisphere being processed: ``rh`` or ``lh``.


Hemisphere
----------

Set:

.. code-block:: text

   rh

for a right hemisphere and:

.. code-block:: text

   lh

for a left hemisphere.

The pipeline handles the hemisphere-specific FreeSurfer files internally.


Surface Reconstruction
----------------------

The pipeline reconstructs the cortical white and pial surfaces.

The white surface is first generated and registered to the FreeSurfer
spherical coordinate system.

Pial-surface placement is then performed iteratively using the custom
``mris_place_surface`` binary described above.

The resulting surfaces are used to compute cortical morphometry, including:

* cortical thickness;
* surface area;
* curvature;
* sulcal measures;
* surface registration information.


Anatomical Parcellations
------------------------

The current surface pipeline generates or transfers several commonly used
cortical atlases.


FreeSurfer Atlases
~~~~~~~~~~~~~~~~~~

The standard FreeSurfer-based parcellations include:

* Desikan-Killiany
* Destrieux / ``aparc.a2009s``
* Desikan-Killiany-Tourville (DKT)


Additional Atlases
~~~~~~~~~~~~~~~~~~

The pipeline additionally supports:

* Brainnetome
* HCP-MMP1 / Glasser
* Schaefer2018 400 parcels / 17 networks
* Jülich
* von Economo-Koskinas

Atlas annotations are transferred to the subject's registered cortical surface
and stored in the subject ``label/`` directory.

The surface annotations are subsequently converted into volumetric atlas
parcellations.


Infant Postmortem MRI
---------------------

``purple-mri`` also contains a dedicated set of scripts for cortical
reconstruction and anatomical parcellation of high-resolution postmortem
infant MRI.

The infant workflow follows the same broad framework:

.. code-block:: text

   segmentation
        |
        v
   cortical surface reconstruction
        |
        v
   spherical registration
        |
        v
   anatomical parcellation
        |
        v
   cortical morphometry

Infant-specific processing scripts are maintained separately here:

`Infant scripts <https://github.com/Pulkit-Khandelwal/purple-mri/tree/main/purple_mri/infant_scripts>`_

The infant workflow also supports the M-CRIB-S infant cortical atlas.

M-CRIB-S should be considered part of the infant-specific workflow rather than
the standard adult/postmortem ``parcellation.sh`` atlas set.


Outputs
-------

Each subject is organized using a FreeSurfer-style directory structure.

Typical outputs include:

.. code-block:: text

   subject/
   ├── mri/
   │   ├── aseg.mgz
   │   ├── wmparc.mgz
   │   ├── aparc.mgz
   │   ├── DKTatlas.mgz
   │   ├── a2009s.mgz
   │   ├── brainnetome.mgz
   │   ├── HCP-MMP1.glasser.mgz
   │   ├── Schaefer2018_400Parcels_17Networks.mgz
   │   ├── julich.mgz
   │   └── economo.mgz
   │
   ├── surf/
   │   ├── rh.white
   │   ├── rh.pial
   │   ├── rh.inflated
   │   ├── rh.sphere
   │   ├── rh.sphere.reg
   │   ├── rh.thickness
   │   ├── rh.area
   │   └── rh.curv
   │
   ├── label/
   │   ├── rh.aparc.annot
   │   ├── rh.aparc.a2009s.annot
   │   ├── rh.aparc.DKTatlas.annot
   │   ├── rh.aparc.brainnetome.annot
   │   ├── rh.aparc.HCP-MMP1.glasser.annot
   │   ├── rh.aparc.Schaefer2018_400Parcels_17Networks.annot
   │   ├── rh.aparc.julich.annot
   │   └── rh.aparc.economo.annot
   │
   └── stats/
       ├── rh.aparc.stats
       ├── rh.aparc.a2009s.stats
       ├── rh.aparc.DKTatlas.stats
       ├── aseg.stats
       └── wmparc.stats

For a left hemisphere, the corresponding primary surface and annotation
filenames use the ``lh`` prefix.

The exact set of intermediate files is larger than shown above; this list
highlights the main surfaces, atlas labels, volumetric parcellations, and
statistics used for downstream analysis.


Applying the Topology-corrected Foreground Mask
------------------------------------------------

Post-hoc topology correction produces a cleaned anatomical foreground mask:

.. code-block:: text

   foreground_mask.nii.gz

If volumetric atlas parcellations have already been generated or exported as
``aparc*.nii.gz``, this mask can be applied to them so that the parcellations
remain consistent with the topology-corrected anatomy.

Set the directory containing the NIfTI atlas parcellations:

.. code-block:: bash

   APARC_DIR="/path/to/subject/mri"
   OUT_DIR="aparc_masked_by_gm_topocorrected_removed_v2/mri"

   mkdir -p "$OUT_DIR"

Then apply the corrected foreground mask:

.. code-block:: bash

   for aparc in "$APARC_DIR"/aparc*.nii.gz; do
     [[ -f "$aparc" ]] || continue

     c3d "$aparc" foreground_mask.nii.gz \
       -multiply \
       -type ushort \
       -o "$OUT_DIR/$(basename "$aparc")"
   done

This preserves the existing atlas labels wherever the corrected anatomical
foreground remains and removes labels from regions eliminated during
post-hoc topology correction.

All volumes used in this operation must share the same voxel grid and spatial
alignment.

For details on how ``foreground_mask.nii.gz`` is generated, see:

:doc:`posthoc_correction`


Implementation
--------------

The complete surface workflow is coordinated by:

`run_surface_pipeline.sh <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/purple_mri/run_surface_pipeline.sh>`_

The final surface reconstruction, atlas transfer, volumetric parcellation, and
statistics stages are implemented in:

`parcellation.sh <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/purple_mri/parcellation.sh>`_

These scripts should be treated as the implementation reference, while this
page describes the recommended user-facing workflow.


Next Step
---------

After cortical reconstruction and parcellation, proceed to:

:doc:`group_analysis`

for ROI-wise and vertex-wise statistical analysis.
