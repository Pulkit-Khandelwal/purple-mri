Docker and Singularity distributions
======================================

The Python package provides the Docker launcher. Docker and the Singularity SIF
provide the scientific environment and trained weights. Follow :doc:`quickstart`,
:doc:`docker` or :doc:`singularity` for your execution route.

Docker v1.2.0
---------------

The release image is ``pulks/docker_purple_mri:v1.2.0``. Its recorded publication
identity is:

.. code-block:: text

   Registry digest: sha256:c8df848d4649c1c0a8f8a7ccf7911ac5bd5df86442ff0e66eaf5f3dd2ce9558d
   Local image ID: sha256:fdd1e9eca00da2032aadeba8e0cbbc28bbd44b068e91249bbcf723fd9e102f3a

The CLI records the actual immutable image ID, available registry digests and
input hashes for each run. A compatible digest reference can be selected with
``--image``. An image tag is a human-readable reference; archive the resolved
identity with the analysis.

Singularity v1.2.0
--------------------

The native-runtime SIF is published at:

.. code-block:: text

   oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.2.0

Download using the ORAS URI and retain the SIF's SHA-256 alongside the runtime
version and run log. A SIF checksum, Docker image ID and OCI registry digest
identify different artifacts. The SIF includes its native-runtime setup; keep
the published image and its build provenance together.

The local CLI's ``purple_run.json`` belongs to the Python execution route.
Direct Docker and SIF examples save their image identity and logs explicitly.
All routes require specimen-level review of the scientific outputs.
