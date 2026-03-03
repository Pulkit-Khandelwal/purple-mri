Group Analysis
==============

Overview
--------

purple-mri supports statistical analysis at multiple spatial scales:

1. Vertex-wise cortical analysis (surface-based)
2. Voxel-based / deformation-based morphometry (DBM)
3. ROI-wise regional analysis

All analyses are performed in a common coordinate system
(template space or fsaverage space).

Vertex-Wise GLM (Surface-Based)
--------------------------------

Cortical thickness and related surface measurements
(thickness, curvature, area) are analyzed in ``fsaverage`` space
using vertex-wise generalized linear modeling (GLM).

Typical model:

Cortical thickness (mm) ~ pathology + covariates

Where pathology variables may include:

* Global amyloid-β (Aβ)
* Braak staging
* CERAD score
* Medial temporal lobe (MTL) neuronal loss
* Tau pathology

Covariates typically include:

* Age at death
* Sex
* Postmortem interval (PMI)

Scripts are located in:

``glm/``

Step 1 — Warp to fsaverage
~~~~~~~~~~~~~~~~~~~~~~~~~~

Warp subject-native measurements (thickness, curvature, area)
to ``fsaverage`` space.

.. code-block:: bash

   bash warp_to_template_space.sh

This produces VTK files in template space.

Step 2 — Prepare VTK files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prepare VTK files for GLM compatibility:

.. code-block:: bash

   python prepare_vtk_files_for_glm.py

This step:

* Ensures consistent VTK format
* Replaces invalid vertices with NaNs
* Standardizes input for statistical modeling

Step 3 — Prepare Design Matrix and Contrasts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You must define:

* ``sample_design_matrix.txt``
* ``contrast.txt``

These encode:

* Pathology variable of interest
* Covariates (age, sex, PMI)
* Desired statistical contrast

Customize these files according to your hypothesis.

Step 4 — Run Vertex-Wise GLM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The workflow uses the binaries:

* ``mesh_merge_arrays``
* ``meshglm``

Run:

.. code-block:: bash

   bash glm.sh

This performs vertex-wise GLM across all subjects.

Outputs
~~~~~~~

Example outputs:

* ``all_hemis.glm_merged_5mm_pial.vtk``
* ``all_hemis.glm_output_for_ABETA_5mm_pial.vtk``
* ``all_hemis.edges.glm_output_for_ABETA_5mm_pial.vtk``

These files contain:

* Beta coefficients
* T-statistics
* P-values
* Cluster edges

Visualization
~~~~~~~~~~~~~

Load output VTK files into ParaView for visualization
of significant clusters and spatial patterns.

Deformation-Based Morphometry (DBM)
------------------------------------

Deformation-based morphometry is performed in template space
using subject-to-template deformation fields.

Workflow:

1. Register all subjects to the population template
2. Compute Jacobian determinant maps
3. Perform voxel-wise GLM on Jacobians

The statistical modeling follows the same structure as
the vertex-wise surface analysis, including:

* Pathology variables
* Age, sex, PMI covariates

ROI-Wise Analysis
-----------------

Region-of-interest analyses can be performed using:

* Atlas-based volumes
* Regional cortical thickness averages
* Subcortical volumetry

Typical workflow:

1. Extract regional measurements
2. Assemble CSV table
3. Fit linear models in Python (e.g., statsmodels, pingouin)

This enables:

* Partial correlations
* Multiple regression
* Mixed-effects modeling
* FDR correction

Scientific Rationale
--------------------

High-resolution ex vivo MRI provides localized morphometric
measures that are more sensitive to neuropathology than
corresponding in vivo MRI measures.

By linking:

* Surface-based thickness
* Deformation-based morphometry
* Atlas-derived volumetry

with gold-standard histopathology measures,
purple-mri enables discovery of pathology-specific
structural signatures.

Dependencies
------------

* ``meshglm`` binaries
* ``mesh_merge_arrays``
* Python (for VTK preparation and statistical scripts)
* ParaView (for visualization)
