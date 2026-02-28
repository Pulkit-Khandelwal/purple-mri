Post-hoc Topology Correction
============================

Goal
----

Ensure adjoining gyri and sulci are clearly separated prior to surface reconstruction.

Deep learning–based voxel-wise segmentation of high-resolution postmortem MRI
can introduce spurious gray-matter (GM) bridges between opposing sulcal banks.
These bridges violate cortical ribbon topology and destabilize surface extraction.

This page describes the recommended **deep learning–based post-hoc topology correction**
workflow used in purple-mri.

Inputs
------

* ``segm.nii.gz`` — original multi-label segmentation (all labels present)

The workflow generates an intermediate topology-specific input volume and then
fuses the corrected cortical GM back into the full segmentation.

Step 1 — Create topology input (collapse labels)
-----------------------------------------------

Goal: produce ``segm_input_for_topo_0000.nii.gz`` with:

* Cortical GM → label 3
* Other tissue → label 2
* Background → label 0

.. code-block:: bash

   c3d segm.nii.gz \
     -replace \
       1 3 \
       2 2 \
       3 2 \
       4 2 \
       5 2 \
       6 2 \
       7 2 \
       8 0 \
       9 2 \
       10 2 \
     -o segm_input_for_topo_0000.nii.gz

Step 2 — Run post-hoc topology correction (Docker)
---------------------------------------------------

Follow the Docker instructions in:

``docker/exvivo_docker.md``

Use:

* Input file: ``segm_input_for_topo_0000.nii.gz``
* Option: ``${OPTION}=exvivo_posthoc_topology``

Assume the topology-corrected output produced by the pipeline is:

``segm_input_for_topo.nii.gz``

Step 3 — Convert corrected cortical GM back to label=1
------------------------------------------------------

Extract cortical GM (label 3) from the corrected output
and remap it back to GM=1:

.. code-block:: bash

   c3d segm_input_for_topo.nii.gz \
     -retain-labels 3 \
     -replace 3 1 \
     -type uchar \
     -o subj_corrected_gm.nii.gz

This produces a GM-only volume where:

* 1 = corrected cortical GM
* 0 = elsewhere

Step 4 — Remove original cortical GM from full segmentation
------------------------------------------------------------

Zero out original cortical GM (label 1) so the corrected GM
can be inserted cleanly.

.. code-block:: bash

   c3d segm.nii.gz \
     -replace 1 0 \
     -type uchar \
     -o segm_no_gm.nii.gz

Step 5 — Fuse corrected GM back into segmentation
--------------------------------------------------

Overlay corrected GM onto the GM-removed segmentation:

.. code-block:: bash

   c3d subj_corrected_gm.nii.gz segm_no_gm.nii.gz \
     -add \
     -type uchar \
     -o final_segm.nii.gz

Output
------

Use:

``final_segm.nii.gz``

as the segmentation file for downstream surface-based reconstruction and parcellation.

Summary
-------

This workflow:

1. Collapses labels to create topology input.
2. Applies learned post-hoc correction.
3. Restores corrected cortical GM.
4. Produces a topology-consistent segmentation suitable for surface extraction.
