Steps to build an exvivo template:

- Binarize and smooth all the segmenations.
- Use one subject from the population as a reference subject.
- Based on the parameters in `ssd_params.json`, create an intial template using these bianrized and smoothed segmentations. We call this template `init-segm-template`.
- Then, warp each subject's MRI to the initial `init-segm-template`. These warped mris are then used to obtain an initial mri template, called `init-mri-template`.
- Based on the parameters in `ncc_params.json`, the warped mris, we use the `init-mri-template` as a reference to obtain an mri-based intensity template.
