purple-mri
=========

**purple-mri (Penn Utilities for Registration and ParcelLation of Ex vivo MRI)** is a research toolkit for
registration, segmentation-to-surface processing, and anatomical parcellation of high-resolution postmortem (ex vivo)
human brain MRI.

The project targets scenarios where in vivo pipelines fail due to fixation-driven contrast shifts, ultra-high
resolution, specimen-specific geometry, and hemisphere-only acquisitions. purple-mri supports workflows that produce
**topology-stable cortical surfaces** and **native-space atlas parcellations** for downstream morphometry.

Key capabilities
----------------

* Voxel-level labeling (e.g., nnU-Net-based inference outputs)
* Topology-aware refinement for cortical ribbon stability
* Surface reconstruction and QC utilities
* Surface-based parcellation into standard atlases (e.g., DKT and others)
* Registration helpers for ex vivo alignment and atlas transfer
* Export of ROI and vertex-wise summaries for statistics

.. toctree::
   :maxdepth: 2
   :caption: Getting started

   overview
   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: Workflows

   segmentation
   posthoc_correction
   parcellation
   registration
   template_construction
   group_analysis

.. toctree::
   :maxdepth: 2
   :caption: Reference

   cli
   api
   citations
   faq
