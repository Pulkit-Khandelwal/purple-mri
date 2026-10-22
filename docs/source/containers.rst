Docker and Singularity distributions
============================================

The pip package and the container have different roles. PyPI distributes the
small Python launcher. Docker distributes the scientific environment and weights.
A SIF is an alternative container artifact for a compatible Singularity or
Apptainer host. Do not include an 18 GB SIF in a Python wheel.

Docker identity
-----------------------

The release default is ``pulks/docker_purple_mri:v1.1.0``. The maintainer reported
the following Task2732 image:

.. code-block:: text

   Image ID: sha256:6c49fbf9a50e4d1f4f203a79d662517637ebf1a4cb58a12d2246bb62a5f434ec
   Registry digest: sha256:e9150a0e08da6b303ad0ec7f9a6bac6b5f545afcb41663fdf5ab10bd69da07a7

Tags can be updated. The CLI records the immutable ID actually used. ``--image``
can select a compatible digest reference, and ``--pull`` explicitly refreshes
it. Changing Python code does not rebuild or modify the image.

Singularity status
------------------

Python CLI 1.1.0 launches Docker only. The separately published SIF is hosted at
``oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.1.0``. Its download was
compared byte-for-byte with the original local image. Task2732 GPU inference
passed with a writable bookkeeping mount; the original SIF needs runtime
workarounds that are documented in the repository's
`container guide <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/exvivo_docker.md>`_.

A newer native SIF candidate is being prepared to use the same combined-stage
interface as Docker without per-model mounts. Its real model initialization and
surface-library checks passed. Full DL and the first three surface steps passed;
transform estimation then failed because FreeSurfer attempted to create
``talsrcimg.img`` in the read-only code directory. A corrected transform script
uses the subject's writable output directory. A resumed run with this script
completed surfaces, parcellation and statistics successfully.

The final rebuilt SIF has not yet been reported as passing an uninterrupted
combined run. Do not assume the existing registry tag contains these fixes.
The Docker workflow remains the documented PyPI route while this test finishes.

A compatible host runtime is required. Some unprivileged installations need
``squashfuse`` on PATH; this is a host requirement rather than a missing file in
the image. Apptainer has not been live-tested for this release. See
:doc:`release_notes` for the validation record.
