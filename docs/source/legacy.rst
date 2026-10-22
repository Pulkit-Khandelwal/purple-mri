Legacy native surface workflow
======================================

The historical seven-argument invocation is retained:

.. code-block:: bash

   python -m pip install 'purple-mri[legacy]==1.1.0'
   python -m purple_mri \
     /path/to/freesurfer /path/to/output /path/to/mri /path/to/segmentation \
     /path/to/atlases 20 /path/to/autodet.gw.stats.binary.dat

The explicit form is ``purple-mri legacy-surface`` followed by those same seven
arguments. The seventh argument is a GM/WM statistics file, not a hemisphere.
This path is RH-only and uses the older native surface scripts. Prefer the
current Docker workflow in :doc:`quickstart` or :doc:`docker` for new adult analyses.

The optional dependencies support the native Python helpers. They do not install
FreeSurfer, Convert3D, atlas assets, the statistics file, or fsaverage. Those
resources and the host environment must be prepared separately. MRI and corrected
segmentation filenames must match as ``SUBJECT.nii.gz``. Paths and subject names
with whitespace or shell metacharacters are rejected by this compatibility path.

Packaged shell helpers resolve each other relative to their installation,
use the package's Python interpreter for decimation, and stop on command failure.
The original installed shell entry points remain available. The modern CLI's
fresh-output and container provenance guarantees apply to Docker runs, not to
arbitrary direct use of these old shell scripts.

Standalone repository scripts
-----------------------------

The source tree's ``purple_mri/run_surface_pipeline.sh`` is a separate entry
point from the Python package's historical ``legacy-surface`` command. Its
arguments end with a hemisphere selection; the packaged compatibility command's
seventh argument is a statistics file. Do not interchange these interfaces.

Direct source execution requires the host tools, atlas resources, and templates
appropriate to that script. The custom pial build and setup are described in the
`standalone pial guide <https://github.com/Pulkit-Khandelwal/purple-mri/blob/main/docker/pial_surface_binary_docker_singularity.md>`_.
The adult Docker image includes these resources and calls its bundled surface
scripts directly; container users should not repeat the standalone setup.

Infant, registration, template, and group-analysis scripts are separate research
workflows. See their respective source and documentation rather than passing
their names to the adult ``purple-mri run`` command.
