Release notes: 1.1.0
============================

This release aligns the Python package with Docker tag ``v1.1.0`` and the
Task2732 subcortical update. It adds a lightweight Docker CLI, validated stage
selection and paths, separate read-only input mounts, explicit image pulling,
dry-run support, immutable image provenance, and complete installation/usage docs.

Both combined and standalone subcortical selections in the repository launcher
use Task2732. Existing merge label mappings and surface placement parameters are
preserved. Heavy native dependencies are isolated in the optional ``legacy`` extra;
the historical seven-argument RH-only entry point remains available.

Container lifecycle tracking records the container ID before start, inspects its
actual exit state, stops only its verified container on Ctrl+C, and retains failed
or uncertain jobs for inspection. This fixes the earlier development CLI behavior
where interrupting the Python client could leave its container running. Existing
jobs launched by that older version are unaffected by installing this release.

Documentation refresh after publication
---------------------------------------

The repository documentation now distinguishes the Python CLI, direct Docker, and
separate native research workflows. It adds complete direct Docker examples,
container-based export of the nine atlas volumes, output/provenance differences,
and environment troubleshooting. The package README and changelog now reflect
that Python 1.1.0 is published and the reported Docker surface run completed.

This is a documentation-only update. It does not replace the PyPI distributions,
change package version or runtime code, rebuild the Docker image, or move the
existing ``v1.1.0`` Git tag.

Validation reported through 2026-10-22
---------------------------------------

Python 1.1.0 is published on `PyPI <https://pypi.org/project/purple-mri/1.1.0/>`_.
The release CLI launches Docker; it does not expose a Singularity/Apptainer backend.

.. list-table:: Maintainer runs on Lambda
   :header-rows: 1
   :widths: 44 56

   * - Test
     - Result
   * - Release wheel 1.1.0, Docker Task2732
     - Exit 0; prediction present; 2:31.
   * - Development CLI, Docker complete DL/merge
     - Exit 0; 23:31.
   * - Development CLI, Docker LH surfaces/parcellation
     - Exit 0; COMPLETE marker; 2:17:06.
   * - Original SIF, Task2732 GPU inference
     - Exit 0; 1:46, using a writable model bookkeeping mount.
   * - Native SIF candidate setup
     - All four real trainers/weights loaded, GPU calculation and surface imports passed.
   * - Native SIF candidate full run
     - DL and surface steps 01–03 passed; transform step failed on a read-only scratch path.
   * - Candidate continuation with corrected transform script
     - Surface steps 04–06 passed; COMPLETE marker; 2:13:29.
   * - Rebuilt final SIF, uninterrupted DL and surfaces
     - Final result not yet reported; not marked validated or published here.

These runs used one LH case on clam. They do not establish multi-host, RH,
Apptainer, or general anatomical validation. The native SIF continuation required
a temporary corrected-script mount, so it is not an uninterrupted test of the
published SIF. The original registry SIF was downloaded and compared byte-for-byte;
that check does not establish runtime equivalence of later candidates.

Package unit tests, clean installation and documentation builds are separate from
MRI processing and specimen-level scientific QC.

Known boundaries
------------------------

The CLI currently launches Docker only. Infant stages are not implemented.
Task289 may require an additional checkpoint asset. Surface outputs retain
single-hemisphere compatibility copies and RH-coded working ASEG labels, as
explained in :doc:`parcellation`. The inherited nnU-Net postprocessing JSON may be
absent; see :doc:`troubleshooting`. The PyPI package, GitHub source, hosted documentation and container artifacts
are separate releases. Updating documentation does not replace an uploaded SIF.
