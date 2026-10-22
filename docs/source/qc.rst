Quality control
=======================

For each new acquisition or specimen, inspect the MRI and outputs together in
an image viewer. Review cortex, deep gray nuclei, MTL boundaries, ventricular
labels, cut surfaces, and damaged or missing tissue. Verify left/right identity
and spatial alignment from the data, not just filenames.

Compare the original, component-cleaned, and topology-corrected Purple results.
Inspect removed components and buried-sulcus masks; automated removal can affect
anatomically meaningful structures. Compare the merged result with the separate
MTL and subcortical predictions and retain the merge reports.

For surfaces, inspect white and pial boundaries, self-intersections, holes,
medial-wall/cut-surface behavior, atlas boundaries, and implausible thickness or
regional statistics. Distinguish the requested hemisphere from the compatibility
copies described in :doc:`parcellation`.

Record the Docker image ID or SIF checksum, acquisition details, hemisphere, software version, failed
steps, and any manual corrections. Successful tests, file readability, exit code
zero, or ``COMPLETE`` demonstrate processing behavior, not anatomical validity.

Report reproducible software failures through the repository issue tracker with
version, image ID, command, and relevant logs. Avoid posting identifiable MRI or
private credentials in public issues.
