Troubleshooting
=======================

Python environment setup
------------------------

If ``python3 -m venv`` fails because ``ensurepip`` is unavailable, use an existing
Python environment with pip, or create a Conda environment if Conda is available:

.. code-block:: bash

   conda create -n purple-cli python=3.12 pip
   conda activate purple-cli
   python -m pip install 'purple-mri==1.1.0'
   purple-mri --version

No root access is needed for this Conda route. If ``purple-mri`` is not found,
activate the environment where it was installed, or use
``python -m purple_mri --help`` with that environment's interpreter. Installing
the CLI does not configure Docker or download its image.

Docker or image unavailable
-----------------------------------

Run ``purple-mri doctor``. If Docker cannot be contacted, check the host's daemon
and your access with the administrator. If the image is absent, run
``purple-mri pull``. The default workflow uses the local tag unless ``--pull`` is
requested. Compare the recorded immutable image ID when results differ.

GPU errors or memory exhaustion
---------------------------------------

Check the NVIDIA driver and Docker GPU configuration, then select an appropriate
GPU with ``--gpus device=0`` if needed. ``doctor`` does not check GPU access.
Review host/GPU memory and image dimensions. The CLI currently does not expose
nnU-Net patch-size or inference-thread overrides; ``--threads`` controls the
surface thread setting. Do not change scientific settings solely to hide an error.

nnU-Net postprocessing warning
--------------------------------------

``Cannot run postprocessing because the postprocessing file is missing`` means
the model's automatic nnU-Net postprocessing step was skipped. It can occur with
a successful prediction/export, as in the maintainer's Task2732 run. The combined
Purple pipeline still performs its own explicitly implemented cleanup and merge.
Do not describe the missing step as having run. Do not create a replacement JSON
or run fold consolidation against a packaged inference-only model without the
appropriate validation results and intended postprocessing policy.

Input or output rejected
--------------------------------

Check :doc:`inputs`. Input files must end in ``_0000.nii.gz``; surface labels use
matching names without that suffix. Use corrected 10-label segmentations, not
merged labels. Pick a new output directory instead of deleting partial results
just to satisfy the empty-directory check. A failed run has no automatic resume.

Interrupted client or unexpected running container
----------------------------------------------------------

CLI 1.1.0 handles Ctrl+C by stopping its verified container. The older development
CLI could exit while Docker continued processing. A newly installed CLI does not
retroactively manage that older container. Use the recorded exact container ID
when inspecting a run:

.. code-block:: bash

   docker ps -a --no-trunc
   docker logs --tail 100 CONTAINER_ID
   docker inspect --format '{{json .State}}' CONTAINER_ID

If you decide to cancel that specific run, use
``docker stop --time 30 CONTAINER_ID``. Avoid commands that stop every container.
For an old detached run, inspect container state and output markers; the old
client's recorded status may not describe the container's final outcome.

New failed/cancelled containers are retained. After checking logs and preserving
needed outputs, an exited container can be removed with ``docker rm CONTAINER_ID``.
If provenance says ``unknown`` or ``running_after_client_exit``, check actual
Docker state before retrying. Use tmux detach, not Ctrl+C, to leave a job running.

Missing surface license or assets
---------------------------------

Supply a nonempty FreeSurfer license using ``--license`` in the CLI, or a
read-only bind and ``FS_LICENSE`` for direct Docker. The license path inside the
container differs from the host path. The published adult image already supplies
FreeSurfer, c3d, fsaverage, atlases, and the custom pial executable. Check the image
identity and mounts if those assets are missing; follow the maintainer build guide
only when rebuilding an image.

Task289 appears in ``models`` but cannot load
---------------------------------------------

``models`` lists accepted selections, not an inventory of bundled checkpoints.
Task289 is optional and may be absent. Use a compatible image containing its
intended trained assets; do not substitute another task's weights or metadata.

Direct Docker files are owned by root
-------------------------------------

Direct Docker commands use the image's default user. Check your site's Docker
and filesystem permissions before starting. Container output paths must be inside
a writable host bind mount. The CLI does not currently expose a Docker ``--user``
option, and these instructions do not claim arbitrary-user execution is validated.

Surface messages and laterality
---------------------------------------

Optimization step reductions and intersection-removal messages are not by
themselves proof of a fatal failure or of good geometry. Check stage completion
and inspect the generated surfaces. Opposite-hemisphere filenames can be
compatibility copies; see :doc:`parcellation` before interpreting them.

ITK-SNAP submissions and attachments
------------------------------------

Use :doc:`itksnap` for connection, image-tag assignment, hemisphere restrictions,
and ticket downloads. The attachment-based provider returns six bundles via
paperclips in the ticket log; it does not return another MRI or an automatically
opened result workspace. Keep the ticket until delivery is complete and retain
the original MRI for viewing. Remote DSS availability is separate from whether
``purple-mri doctor`` succeeds on your local Docker host.

Singularity startup
---------------------------

A missing FUSE helper or permission error is a host runtime configuration issue.
See :doc:`containers`. The SIF's existence alone does not show it can run on every
host; the maintainer has now passed startup and Task2732 file checks on Lambda.
