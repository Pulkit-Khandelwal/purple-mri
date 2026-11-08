Release notes: 1.2.0
======================

Version 1.2.0 provides coordinated Python, Docker and Singularity distributions
for contrast-aware adult segmentation, cortical reconstruction and atlas merging.

Processing
------------

* Explicit T2w, CISS, FLASH and T2* routing, with Task278 refinement for FLASH/T2*.
* MTL rim correction in the detailed tissue merge across all four contrasts.
* FLASH connected-component GM cleanup before reconstruction-label generation.
* ``11_final_merged`` detailed labels and ``12_surface_labels`` reconstruction
  vocabulary generated before cortical surface reconstruction.
* Brainnetome correction inside the selected LH/RH cortex before projection.
* Seven native-grid atlas merges that replace cortical GM 101 and preserve
  detailed noncortical structures.
* Reuse of existing atlas projections with surface/annotation provenance checks.

Python interface
------------------

The CLI adds ``--contrast``, ``--dl-dir``, ``--surface-dir``, ``--resume``,
``--preflight-only``, ``--save-qc-volumes`` and ``--max-roi-voxels``. Full runs use
``OUTPUT/dl``, ``OUTPUT/surface`` and ``OUTPUT/atlases``. The launcher records
immutable image identity, input hashes, container state and resumed attempts.

For migration from 1.1.0, supply the acquisition contrast and use the complete
v1.2.0 DL root with ``--dl-dir`` when reusing predictions for surfaces. The
reconstruction input is ``12_surface_labels``. See :doc:`quickstart` and
:doc:`outputs` for current commands and paths.

Distribution
--------------

* Python: ``python -m pip install purple-mri==1.2.0``.
* Docker: ``pulks/docker_purple_mri:v1.2.0``.
* Singularity: ``oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.2.0``.

The Python package remains a lightweight launcher. Native dependencies and
trained models are supplied by the container images. Documentation updates are
published from repository source independently of package/container releases.

Documentation figures
-----------------------

The README and documentation landing page share full-resolution PNGs for the
UPenn MRI/atlas comparison, two surface views and within-subject registration.
The source image pixels are preserved during cropping. These figures illustrate
the workflows; anatomical quality should be assessed for each processed case.
