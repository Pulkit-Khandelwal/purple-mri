Troubleshooting
=================

Python environment setup
--------------------------

If ``python3 -m venv`` fails because ``ensurepip`` is unavailable, use an existing
Python environment with pip, or create a Conda environment if Conda is available:

.. code-block:: bash

   conda create -n purple-cli python=3.12 pip
   conda activate purple-cli
   python -m pip install 'purple-mri==1.2.0'
   purple-mri --version

No root access is needed for this Conda route. If ``purple-mri`` is not found,
activate the environment where it was installed, or use
``python -m purple_mri --help`` with that environment's interpreter. Installing
the CLI does not configure Docker or download its image.

Docker or image unavailable
-----------------------------

Run ``purple-mri doctor``. If Docker cannot be contacted, check the host's daemon
and your access with the administrator. If the image is absent, run
``purple-mri pull``. The default workflow uses the local tag unless ``--pull`` is
requested. Compare the recorded immutable image ID when results differ.

GPU errors or memory exhaustion
---------------------------------

Check the NVIDIA driver and Docker GPU configuration, then select an appropriate
GPU with ``--gpus device=0`` if needed. ``doctor`` does not check GPU access.
Review host/GPU memory and image dimensions. The CLI currently does not expose
nnU-Net patch-size or inference-thread overrides; ``--threads`` controls the
surface thread setting. Do not change scientific settings solely to hide an error.

nnU-Net postprocessing warning
--------------------------------

``Cannot run postprocessing because the postprocessing file is missing`` means
the model's automatic nnU-Net postprocessing step was skipped. It can occur with
a successful prediction/export, as in the maintainer's Task2732 run. The combined
Purple pipeline still performs its own explicitly implemented cleanup and merge.
Do not describe the missing step as having run. Do not create a replacement JSON
or run fold consolidation against a packaged inference-only model without the
appropriate validation results and intended postprocessing policy.

Input or output rejected
--------------------------

Check :doc:`inputs`. MRI filenames must end in ``_0000.nii.gz``. Use the
complete v1.2.0 DL root for surface-only processing. Start with a new output
directory or use ``--resume`` for the same pipeline run with matching inputs,
image and settings. Preserve partial outputs and reports when investigating.

Interrupted client or stale run record
----------------------------------------

The CLI handles Ctrl+C by requesting cancellation of its verified container.
If the client disappears externally, the Docker job may continue and the local
JSON/log can stop updating. Inspect the exact container ID recorded in
``purple_run.json``:

.. code-block:: bash

   docker inspect --format '{{json .State}}' CONTAINER_ID
   docker logs --tail 100 CONTAINER_ID

Compare the actual exit status with the three completion markers and expected
outputs. Preserve the original run record and inspected Docker state. A stale
``running`` record alone is not a reason to rerun completed MRI processing.
If cancellation is required, use ``docker stop --time 30 CONTAINER_ID`` for
that specific container. After preserving logs, an exited container may be
removed with ``docker rm CONTAINER_ID``.

For an incomplete run, use the original command with ``--resume`` only after
confirming no earlier container is still writing to that output. Use tmux detach
(Ctrl+B, then D) or a scheduler to leave a long job running.

Missing surface license or assets
-----------------------------------

Supply a nonempty FreeSurfer license using ``--license`` in the CLI, or a
read-only bind and ``FS_LICENSE`` for direct Docker or SIF execution. The license path inside the
container differs from the host path. The published adult image already supplies
FreeSurfer, c3d, fsaverage, atlases, and the custom pial executable. Check the image
identity and mounts if those assets are missing; follow the maintainer build guide
only when rebuilding an image.

Direct Docker files are owned by root
---------------------------------------

Direct Docker commands use the image's default user. Check your site's Docker
and filesystem permissions before starting. Container output paths must be inside
a writable host bind mount. The CLI does not currently expose a Docker ``--user``
option, and these instructions do not claim arbitrary-user execution is validated.

Surface messages and laterality
---------------------------------

Optimization step reductions and intersection-removal messages are not by
themselves proof of a fatal failure or of good geometry. Check stage completion
and inspect the generated surfaces. Opposite-hemisphere filenames can be
compatibility copies; see :doc:`parcellation` before interpreting them.

ITK-SNAP submissions and attachments
--------------------------------------

Use :doc:`itksnap` for connection, image-tag assignment, hemisphere restrictions,
and ticket downloads. The attachment-based provider returns six bundles via
paperclips in the ticket log; it does not return another MRI or an automatically
opened result workspace. Keep the ticket until delivery is complete and retain
the original MRI for viewing. Remote DSS availability is separate from whether
``purple-mri doctor`` succeeds on your local Docker host.

Singularity startup
---------------------

Use the published ORAS image from :doc:`singularity`, retain its SHA-256 and
record the runtime version. Keep output paths in a writable bind mount and
supply a valid license for surface/atlas processing. Inspect GPU allocation and
host memory if a run stops unexpectedly; a missing process alone does not
identify the cause.

A missing FUSE helper or permission failure before startup concerns the host
runtime. Use your site's configured runtime or ask its administrator. Preserve
the logs and output directory before retrying with matching ``--resume``.
