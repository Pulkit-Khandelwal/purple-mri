Troubleshooting
=======================

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

Surface messages and laterality
---------------------------------------

Optimization step reductions and intersection-removal messages are not by
themselves proof of a fatal failure or of good geometry. Check stage completion
and inspect the generated surfaces. Opposite-hemisphere filenames can be
compatibility copies; see :doc:`parcellation` before interpreting them.

Singularity startup
---------------------------

A missing FUSE helper or permission error is a host runtime configuration issue.
See :doc:`containers`. The SIF's existence alone does not show it can run on every
host; the maintainer has now passed startup and Task2732 file checks on Lambda.
