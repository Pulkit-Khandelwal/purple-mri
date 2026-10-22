Installation
====================

The Python package is a small launcher. The Docker image supplies nnU-Net,
trained weights, FreeSurfer, Convert3D, and the custom pial tools. Installing the
package does not download the image. A Singularity SIF is a separate distribution
and is not needed to install or use this Docker CLI.

Requirements
--------------------

* Python 3.9 or newer for the CLI (Python 3.12 is a suitable choice).
* A Linux Docker host with permission to access its Docker daemon.
* An NVIDIA GPU, a compatible driver, and configured Docker GPU access for DL.
* A personal FreeSurfer license file for surface reconstruction.
* Storage for the large container image and per-subject intermediates. The
  maintainer's converted SIF is about 18 GB; Docker storage and working space are
  additional. Resource needs depend on image dimensions and the workflow.

Host Python does not need nnU-Net, PyTorch, or FreeSurfer for Docker execution.
Surface-only jobs do not request a GPU. Native macOS/Windows execution of this
container workflow has not been validated; use a suitable Linux host.

Install the release
---------------------------

Version 1.1.0 is available on `PyPI <https://pypi.org/project/purple-mri/1.1.0/>`_:

.. code-block:: bash

   python3 -m venv ~/venvs/purple-mri
   source ~/venvs/purple-mri/bin/activate
   python -m pip install 'purple-mri==1.1.0'
   purple-mri --version
   purple-mri --help

For an offline installation, use the matching wheel from the release bundle:

.. code-block:: bash

   python -m pip install --no-index --no-deps --upgrade \
     ./dist/purple_mri-1.1.0-py3-none-any.whl

Get the container
-------------------------

.. code-block:: bash

   purple-mri pull
   purple-mri doctor
   purple-mri models

The default tag is ``pulks/docker_purple_mri:v1.1.0``. ``pull`` explicitly
refreshes that tag. ``doctor`` checks Docker access and local image metadata;
it does not run inference or check GPU access, checkpoints, or scientific quality.
``models`` lists expected selections, not the checkpoint inventory.

For GPU setup, follow the `NVIDIA Container Toolkit documentation
<https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>`_.
Obtain a license from `FreeSurfer registration
<https://surfer.nmr.mgh.harvard.edu/registration.html>`_ and keep it on the host.

Upgrade or remove
-------------------------

Upgrade with ``python -m pip install --upgrade 'purple-mri==1.1.0'``. Use ``python -m pip uninstall purple-mri`` to remove the launcher.
Neither action deletes Docker images or MRI outputs. Use a new output directory
for each run; upgrading does not modify a job that is already running.

From source
-------------------

.. code-block:: bash

   git clone https://github.com/Pulkit-Khandelwal/purple-mri.git
   cd purple-mri
   python -m pip install .

Installation from ``./pkg_src`` is also supported. Development installation can
use ``python -m pip install -e .``. The optional ``legacy`` extra is only for the
older native workflow; see :doc:`legacy`.
