Group Analysis
==============

Overview
--------

``purple-mri`` supports statistical analysis at multiple spatial scales:

1. Vertex-wise cortical analysis (surface-based)
2. Voxel-based / deformation-based morphometry (DBM)
3. ROI-wise regional analysis

Vertex-wise surface analysis and deformation-based morphometry require subjects
to be mapped into a common coordinate system such as ``fsaverage`` or a
population-specific volumetric template.

ROI-wise analyses can instead be performed from standardized regional
measurements extracted in subject space.


Vertex-Wise GLM
---------------

Cortical thickness and related surface measurements, including thickness,
curvature, and area, can be analyzed in ``fsaverage`` space using vertex-wise
generalized linear modeling (GLM).

A typical model is:

.. code-block:: text

   cortical thickness ~ pathology + covariates

Pathology variables may include, for example:

* amyloid-beta burden;
* Braak stage;
* CERAD score;
* regional neuronal loss;
* tau pathology;
* other regional or global neuropathological measurements.

Covariates may include:

* age at death;
* sex;
* postmortem interval (PMI);
* other study-specific biological or technical variables.

Scripts are located in:

``glm/``


Implementation Note
~~~~~~~~~~~~~~~~~~~

.. note::

   The scripts in ``glm/`` are reference implementations and currently contain
   dataset-specific paths, subject lists, smoothing parameters, and statistical
   contrasts. Review and modify these settings for your dataset before running
   the analysis.


Step 1 - Warp to fsaverage
~~~~~~~~~~~~~~~~~~~~~~~~~~

Warp subject-native measurements such as cortical thickness, curvature, and
surface area to ``fsaverage`` space.

.. code-block:: bash

   bash warp_to_template_space.sh

This produces surface data in the common template space for downstream
analysis.


Step 2 - Prepare VTK files
~~~~~~~~~~~~~~~~~~~~~~~~~~

Prepare VTK files for GLM compatibility:

.. code-block:: bash

   python prepare_vtk_files_for_glm.py

This step:

* ensures a consistent VTK representation;
* handles invalid vertices;
* standardizes the surface data used for statistical modeling.


Step 3 - Prepare the design matrix and contrasts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define:

* ``sample_design_matrix.txt``
* ``contrast.txt``

These encode:

* the biological or pathology variable of interest;
* covariates;
* the desired statistical contrast.

Customize these files according to the study hypothesis.


Step 4 - Run the vertex-wise GLM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The workflow uses:

* ``mesh_merge_arrays``
* ``meshglm``

Run:

.. code-block:: bash

   bash glm.sh

This performs vertex-wise GLM across the subjects defined in the analysis.


Outputs
~~~~~~~

Example outputs include:

* ``all_hemis.glm_merged_5mm_pial.vtk``
* ``all_hemis.glm_output_for_ABETA_5mm_pial.vtk``
* ``all_hemis.edges.glm_output_for_ABETA_5mm_pial.vtk``

Depending on the analysis configuration, these files can contain statistical
quantities such as:

* beta coefficients;
* T-statistics;
* P-values;
* cluster or edge information.


Visualization
~~~~~~~~~~~~~

Output VTK files can be loaded into ParaView to visualize spatial patterns and
statistical results on the cortical surface.


Deformation-Based Morphometry
-----------------------------

Deformation-based morphometry is performed in a common volumetric template
space using subject-to-template deformation fields.

A typical workflow is:

1. Register all subjects to the population template.
2. Compute Jacobian determinant maps from the deformation fields.
3. Perform voxel-wise statistical modeling on the Jacobian maps.

The statistical model can incorporate pathology variables and relevant
covariates in the same general manner as the surface-based analysis.

See:

:doc:`template_construction`

for construction of the population-specific ex vivo MRI template.


ROI-Wise Analysis
-----------------

Region-of-interest analyses can be performed using:

* atlas-based regional volumes;
* regional cortical thickness averages;
* cortical surface-area measures;
* subcortical volumetry;
* other regionally summarized imaging measurements.

A typical workflow is:

1. Extract regional measurements.
2. Assemble a subject-by-region analysis table.
3. Fit the appropriate statistical model in Python or another statistical
   environment.

Depending on the scientific question, analyses may include:

* correlations and partial correlations;
* multiple regression;
* mixed-effects models;
* multiple-comparison correction such as false discovery rate (FDR)
  procedures.

ROI-wise analyses do not inherently require all subjects to be resampled into
a common image grid, provided that regional measurements have been extracted
using a consistent anatomical definition.


Scientific Rationale
--------------------

High-resolution ex vivo MRI provides localized morphometric measurements that
can be related directly to regional neuropathology at spatial resolutions that
are difficult to achieve with conventional in vivo MRI.

By integrating:

* surface-based cortical morphometry;
* deformation-based morphometry;
* atlas-derived volumetry;

with neuropathological and other biological measurements, ``purple-mri``
supports investigation of spatially specific structure-pathology
relationships.


Dependencies
------------

The surface GLM workflow uses:

* FreeSurfer
* ``meshglm``
* ``mesh_merge_arrays``
* Python
* NumPy
* SciPy
* pandas
* VTK
* PyTorch
* PyMeshLab
* PyKeOps
* GeomLoss
* Plotly
* ParaView for visualization

Additional statistical packages may be required for study-specific ROI-wise or
voxel-wise analyses.
