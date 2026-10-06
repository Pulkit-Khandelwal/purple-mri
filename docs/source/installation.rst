Installation
============

Overview
--------

``purple-mri`` combines several neuroimaging tools and workflow-specific
dependencies. Not every dependency is required for every analysis.

The recommended way to use ``purple-mri`` is to clone the repository and run
the corresponding workflow scripts directly.


Clone the Repository
--------------------

.. code-block:: bash

   git clone https://github.com/Pulkit-Khandelwal/purple-mri.git
   cd purple-mri


Core Requirements
-----------------

The main requirements across the ``purple-mri`` workflows are:

* Linux
* Python 3.10+
* Git
* Docker
* FreeSurfer
* Convert3D / ``c3d``
* ANTs for MRI preprocessing
* ``greedy`` for registration and template construction

Additional requirements depend on the workflow being used.


Python Dependencies
-------------------

Create a Python environment if desired:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate

Install the Python dependencies:

.. code-block:: bash

   pip install -r dependencies.txt


Segmentation
------------

Deep learning-based segmentation is distributed through Docker.

The currently documented segmentation image is:

.. code-block:: text

   pulks/docker_hippogang_exvivo_segm:v1.4.6

For GPU inference, Docker must be configured to access an NVIDIA GPU.

Pull the image using:

.. code-block:: bash

   docker pull pulks/docker_hippogang_exvivo_segm:v1.4.6

The recommended complete segmentation workflow can then be run with:

.. code-block:: text

   exvivo_all

Detailed instructions are available here:

:doc:`segmentation`

For the full list of individual segmentation models and Docker options, see:

`Ex vivo Docker documentation <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md>`_


Post-hoc Topology Correction
----------------------------

Standalone post-hoc topology correction uses the same segmentation Docker
image with:

.. code-block:: text

   exvivo_posthoc_topology

The workflow also uses ``c3d`` to prepare and apply the topology-correction
masks.

See:

:doc:`posthoc_correction`

Detailed command-line instructions are maintained here:

`Topology correction notes <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/topology_correction_notes.md>`_


Surface Reconstruction and Parcellation
---------------------------------------

The surface-based pipeline requires FreeSurfer.

The workflow has been developed and tested with:

.. code-block:: text

   FreeSurfer 7.4.0

FreeSurfer installation instructions are available at:

https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

The surface pipeline also requires:

* ``fsaverage`` in the working directory
* external atlas resources used by ``parcellation.sh``
* the Python dependencies in ``dependencies.txt``
* Docker or Singularity for pial-surface placement


Custom Pial-Surface Binary
~~~~~~~~~~~~~~~~~~~~~~~~~~

Pial-surface placement uses a custom compiled version of the FreeSurfer
``mris_place_surface`` binary.

It is distributed as a container so that users do not need to compile the
binary locally.

Setup instructions:

`Pial-surface Docker/Singularity instructions <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/pial_surface_binary_docker_singularity.md>`_

GitHub release:

`purple-mris-place-surface <https://github.com/Pulkit-Khandelwal/purple-mri/releases/tag/v0.1.0-fs-binary-docker>`_

Once configured, the container is called automatically by the surface
pipeline.

See:

:doc:`parcellation`


Registration
------------

Ex vivo to in vivo registration requires:

* ``greedy`` binaries available in ``PATH``
* ``c3d`` (Convert3D)
* FreeSurfer utilities, including ``mri_label2vol``
* SynthSeg-derived segmentation of the corresponding in vivo T1w MRI
* topology-corrected ``purple-mri`` segmentation of the ex vivo MRI

See:

:doc:`registration`


Template Construction
---------------------

Population-specific volumetric template construction requires:

* ``greedy``
* ``greedy_template_average``
* ``jq``
* ``c3d``

The required commands must be available in ``PATH``.

For example:

.. code-block:: bash

   export PATH="/path/to/greedy_binaries/:$PATH"

See:

:doc:`template_construction`


Group Analysis
--------------

Vertex-wise surface analysis uses FreeSurfer-generated surface data together
with the GLM utilities provided in the repository.

Depending on the analysis, requirements include:

* FreeSurfer
* ``mesh_merge_arrays``
* ``meshglm``
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

See:

:doc:`group_analysis`


Documentation Dependencies
--------------------------

To build the Sphinx documentation locally:

.. code-block:: bash

   pip install -r docs/requirements.txt


Workflow Documentation
----------------------

After installation, proceed through the workflow-specific documentation:

* :doc:`segmentation`
* :doc:`posthoc_correction`
* :doc:`parcellation`
* :doc:`registration`
* :doc:`template_construction`
* :doc:`group_analysis`
