Quickstart
==========

This page describes the conceptual flow from an ex vivo MRI volume to surfaces and atlas parcellations.
Exact commands depend on your dataset layout and compute environment.

Inputs
------

* One subject MRI (NIfTI)
* (Optional) brain mask for ex vivo bias correction / normalization
* Output directory per subject

Outputs
-------

* A multi-class segmentation (label map)
* Topology-corrected surfaces suitable for downstream analysis
* One or more surface-based atlas parcellations
* QC snapshots and summary tables

Next
----

See the workflow pages:

* :doc:`segmentation`
* :doc:`topology_and_surfaces`
* :doc:`parcellation`
* :doc:`registration`
* :doc:`qc`
