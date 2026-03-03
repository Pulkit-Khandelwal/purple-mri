purple-mri
==========

purple-mri (Penn Utilities for Registration and Parcellation of Ex Vivo MRI) is a computational framework for segmentation, registration, surface reconstruction, and atlas-based parcellation of ultra–high-resolution postmortem human brain MRI.

The toolkit is designed for ex vivo whole-hemisphere MRI acquired at submillimeter resolution (often <300µm) at ultra-high field strengths (e.g., 7T), where conventional in vivo pipelines fail due to fixation-driven contrast shifts, specimen-specific geometry, and extreme spatial resolution.

purple-mri integrates deep learning–based voxel segmentation with classical surface-based modeling to produce topology-stable cortical reconstructions and native-space atlas parcellations suitable for vertex-wise and group-level morphometric analysis.

.. image:: _static/animation.gif
   :width: 900px
   :align: center

Introductory Video
------------------
.. raw:: html

   <div style="text-align: center; margin-top: 20px;">
     <a href="https://youtu.be/DBdzbIAJBw4" target="_blank">
       <img src="https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/images/thumbnail.png?raw=true"
            style="width:75%; max-width:900px; border-radius:8px;">
     </a>
   </div>


Core Capabilities
-----------------
purple-mri enables:

* Automated multi-label tissue segmentation of postmortem MRI
* Topology-aware cortical ribbon refinement
* Native-space surface reconstruction
* Surface-based parcellation using established atlases (e.g., DKT, Schaefer, Glasser, von Economo–Koskinas)
* Ex vivo ↔ in vivo volumetric registration using classical optimization methods and modern deep learning-based ones
* Intensity-based population-specific volumetric template construction
* Vertex-wise statistical modeling (e.g., GLM analyses in template space) allowing the integration of morphometric measures with external biological variables

Scientific Context
------------------
We have applied our tools across a spectrum of high-resolution multi-modal ex vivo MRI spanning from neurodegenerative (Alzheimer’s disease and related dementias) and developmental (Sudden Infant Death Syndrome). Our toolkit purple-mri has enabled systematic analysis of high-resolution postmortem MRI linking pathology to in vivo MRI via ex vivo MRI to allow discovery of region-specific morphometry–pathology signatures that can inform the development of disease-specific in vivo biomarkers.

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   overview
   installation

.. toctree::
   :maxdepth: 1
   :caption: Workflows

   segmentation
   posthoc_correction
   parcellation
   registration
   template_construction
   group_analysis

.. toctree::
   :maxdepth: 1
   :caption: Reference

   citations




