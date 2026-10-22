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

ITK-SNAP user guide
-------------------

An illustrated :doc:`itksnap` walkthrough documents the RH ``purple 0.1.0``
registration, InputMRI assignment, ticket monitoring, six result attachments,
and QC with the original local MRI. It distinguishes the proposed ``0.2.0``
hemisphere tags from the illustrated service and local Docker/PyPI ``1.1.0``.
This documentation does not change provider code or register a new service.

Published native SIF update: 2026-10-22
---------------------------------------

The fixed ``purple_mri_v1.1.0.sif`` is published at
``oras://registry-1.docker.io/pulks/singularity_purple_mri:v1.1.0``. It redirects
inference bookkeeping into prediction outputs, selects container CPU libraries
for surface tools within a GPU-enabled invocation, and runs transform scratch
work in a writable subject directory. Model selections and the stage interface
are retained. See :doc:`singularity` for complete commands.

.. literalinclude:: _static/releases/purple_mri_v1.1.0.sif.sha256
   :language: text

This file checksum identifies the tested and published artifact. The SIF registry
tag previously referred to an older build; verify the checksum of existing
copies. Docker/PyPI ``1.1.0`` and the Git release tag are separate artifacts.

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
   * - Published native SIF, full DL/merge
     - Exit 0; 22:58.
   * - Published native SIF, LH surfaces/parcellation
     - Exit 0; COMPLETE marker and core LH files checked; 2:14:14.
   * - Published native SIF, uninterrupted combined run
     - Exit 0; corrected and merged NIfTIs checked; 2:37:13 overall.
   * - Published native SIF, registry round trip
     - Upload completed; downloaded SIF exactly matched the tested file with cmp.

The final SIF run completed on 2026-10-22 at 15:36:29 EDT on clam using one LH
case, an NVIDIA RTX A6000, and 20 surface threads. These are observed runtimes,
not performance guarantees. They do not establish multi-host, RH, Apptainer,
Docker/SIF numerical equivalence, or general anatomical validation.

Earlier development SIFs required writable model mounts, separate surface
invocations, or a mounted transform-script correction. Those tests are
superseded for release use by the uninterrupted run of the rebuilt SIF.
The final run used one combined launcher invocation without those workarounds.

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
