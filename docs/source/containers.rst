Docker and Singularity distributions
============================================

The pip package and the container have different roles. PyPI distributes the
small Python launcher. Docker distributes the scientific environment and weights.
A SIF is an alternative container artifact for a compatible Singularity or
Apptainer host. Do not include an 18 GB SIF in a Python wheel.

Choose the Docker launcher
--------------------------

Use :doc:`installation` and :doc:`quickstart` for the Python CLI, or :doc:`docker`
for direct Docker commands. Both launch the same scientific pipeline. The CLI
adds host-path validation, a dry run, a JSON run record, and managed cancellation.
The direct examples set input and output mounts explicitly and save the image ID.

The historical pip native entry point and the repository's separate analysis
scripts have different host requirements; see :doc:`legacy`.

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

Singularity identity
--------------------

Use :doc:`singularity` for the prebuilt SIF and full, DL-only, surface-only, and
individual-model examples. It runs the same launcher and stage sequence as
Docker in one ``exec --cleanenv --nv`` invocation. The Python CLI remains
Docker-only.

The SIF is published at
``oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.1.0``.
The fixed artifact was uploaded on 2026-10-22, downloaded, and compared
byte-for-byte with the file that passed uninterrupted DL + LH surfaces.

.. literalinclude:: _static/releases/purple_mri_v1.1.0.sif.sha256
   :language: text

This is a SIF file checksum. It differs from Docker image IDs and registry
manifest digests. Download the :download:`checksum file
<_static/releases/purple_mri_v1.1.0.sif.sha256>` and retain it with the image and
run logs. The tag also named an older SIF, so a filename or tag alone cannot
establish which artifact you have.

The published SIF includes inference-bookkeeping, surface-library, and writable
transform-directory fixes. The Docker image identified above predates those
SIF-specific changes; converting that Docker tag directly does not reproduce
this SIF. The existing trained-model selections and stage interface are retained.

A compatible host runtime is required. Some unprivileged installations need
``squashfuse`` on PATH. Apptainer and RH end-to-end runs have not been live-tested
for this artifact. See :doc:`release_notes` for the validation record.
