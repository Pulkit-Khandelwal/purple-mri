Quick start
===================

Prepare one excised hemisphere per scan, with one hemisphere per batch. Name each
3-D, single-channel NIfTI ``SUBJECT_0000.nii.gz``. Use an output directory that is
new or empty and separate from the input. See :doc:`inputs` for full requirements.

This page uses the Python CLI and the published Docker image. For equivalent
container commands without installing the Python package, see :doc:`docker`
or :doc:`singularity`.
For remote processing through the ITK-SNAP GUI, use :doc:`itksnap`.
Complete :doc:`installation`, including ``purple-mri pull``, before running.

Segmentation and surfaces
---------------------------------

Replace the example paths and select the actual anatomical hemisphere:

.. code-block:: bash

   purple-mri run exvivo_dl exvivo_surface \
     --input /path/to/inputs \
     --output /path/to/results_run1 \
     --hemi rh \
     --license /path/to/license.txt \
     --threads 20 \
     --dry-run

After reviewing the dry run, start actual processing:

.. code-block:: bash

   purple-mri run exvivo_dl exvivo_surface \
     --input /path/to/inputs \
     --output /path/to/results_run1 \
     --hemi rh \
     --license /path/to/license.txt \
     --threads 20

Use ``--hemi lh``
for a left hemisphere. Do not manually mirror the MRI to choose a hemisphere.
``--pull`` can be added to refresh the Docker tag before a real run.

A dry run validates host paths and names but does not read NIfTI voxel data,
pull an image, create outputs, or check Docker/GPU availability.

DL only
---------------

.. code-block:: bash

   purple-mri run exvivo_dl \
     --input /path/to/inputs --output /path/to/dl_run1

The corrected 10-label segmentation is under
``dl_run1/exvivo_dl/05_purple_corrected``. The final merged segmentation is under
``dl_run1/exvivo_dl/11_final_merged``. See :doc:`outputs` for the distinction.

Surfaces using that DL result
-------------------------------------

.. code-block:: bash

   purple-mri run exvivo_surface \
     --input /path/to/inputs \
     --segmentation /path/to/dl_run1/exvivo_dl/05_purple_corrected \
     --output /path/to/surface_run1 \
     --hemi rh --license /path/to/license.txt --threads 20

The MRI and corrected labels must match in geometry and subject identity.
Use a new output directory for this second command.

Subcortical model only
------------------------------

.. code-block:: bash

   purple-mri run exvivo_multi_sequence_subcortical \
     --input /path/to/inputs --output /path/to/subcortical_run1

This selects Task2732. Outputs go to ``subcortical_run1/predictions``.

Long jobs and completion
--------------------------------

Use ``tmux`` or the site's job scheduler. In tmux, detach with ``Ctrl+B``, then
``D`` to leave the job running. In CLI 1.1.0, ``Ctrl+C`` requests cancellation of
that run's container. It is not a detach command.

Immediately after the command returns, ``echo $?`` reports its exit status.
If saving terminal output through ``tee``, enable ``set -o pipefail`` first so a
pipeline failure is not hidden by successful logging. Write the log outside the
new CLI output directory; creating a log inside it before launch makes it nonempty.

Check the command exit status and ``purple_run.json``. A successful surface
stage also writes ``exvivo_surface/COMPLETE``. Inspect the outputs described in
:doc:`qc`; successful process completion alone does not establish anatomical
accuracy. The CLI does not upload results to DSS or create attachment archives.
