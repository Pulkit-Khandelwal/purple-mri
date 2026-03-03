purple-mri
==========

purple-mri (**P**enn **U**tilities for **R**egistration and **P**arce**L**lation of **E**x vivo **MRI**) is a computational framework for segmentation, registration, surface reconstruction, and atlas-based parcellation of ultra–high-resolution postmortem human brain MRI.

The toolkit is designed for ex vivo whole-hemisphere MRI acquired at submillimeter resolution (often <300µm) at ultra-high field strengths (e.g., 7T), where conventional in vivo pipelines fail due to fixation-driven contrast shifts, specimen-specific geometry, and extreme spatial resolution.

purple-mri integrates deep learning–based voxel segmentation with classical surface-based modeling to produce topology-stable cortical reconstructions and native-space atlas parcellations suitable for vertex-wise and group-level morphometric analysis.

Core Capabilities
-----------------

purple-mri enables:

* Automated multi-label tissue segmentation of postmortem MRI
* Topology-aware cortical ribbon refinement
* Native-space surface reconstruction
* Surface-based parcellation using established atlases (e.g., DKT, Schaefer, Glasser, von Economo–Koskinas)
* Ex vivo ↔ in vivo volumetric registration
* Intensity-based volumetric template construction
* Vertex-wise statistical modeling (e.g., GLM analyses in template space)

The framework supports the construction of population-specific templates and the integration of morphometric measures with external biological variables.

Scientific Context
------------------

Alzheimer’s disease and related neurodegenerative disorders are heterogeneous, age-related conditions characterized by the co-occurrence of multiple pathologies that evolve decades before clinical symptoms emerge. While in vivo imaging biomarkers (e.g., cortical thickness, volumetry) detect early structural changes, they lack specificity for disentangling mixed pathologies.

purple-mri was developed to enable systematic analysis of high-resolution postmortem MRI linked directly to gold-standard neuropathology. By aligning morphometry derived from ex vivo MRI with histological measurements, the framework enables discovery of region-specific morphometry–pathology signatures that can inform the development of disease-specific in vivo biomarkers.

The tools released in purple-mri emerged from a body of work focused on:

* High-resolution 7T postmortem whole-hemisphere MRI
* Surface-based parcellation in diseased populations
* Population-level ex vivo template construction
* Matched postmortem ↔ antemortem MRI alignment
* Linking morphometry with tau pathology, neuronal loss, and amyloid burden

While originally developed in the context of Alzheimer’s disease research, purple-mri provides a generalizable platform for postmortem neuroimaging analysis across neurodegenerative and developmental disorders.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   overview
   installation

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




