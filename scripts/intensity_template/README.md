## Steps to build an exvivo template:
Download this folder along with the `binaries` one. The main script is `greedy_build_template.sh`.

### Pre-processing

- Make sure all the images and their segmentations are in the same orientation. You can use `orient` option in `c3d` to do that.
- Binarize and smooth all the segmentations (the 10-label deep learning-based). Using `c3d`:
  ```
  c3d segm.nii.gz -thresh 1 inf 1 0 -smooth-fast 0.4mm -o segm_binary_smooth.nii.gz
  ```

### Initial segmentation-based template
- Use one subject from the population as a reference subject, let's call this `reference_subj`.
- Based on the parameters in `ssd_params.json`, create an intial template using these bianrized and smoothed segmentations. We call this template `init-segm-template`. A sample `manifest.csv` file is provided which lists the subjects.
```
export PATH="/path/to/greedy_binaries/":$PATH

bash greedy_build_template.sh -p params_ssd.json -i manifest_segm.csv -T reference_subj -o template_init_segm
```

### MRI-based template
- Then, warp each subject's MRI to the initial `init-segm-template`. These warped mris are then used to obtain an initial mri template, called `mri_initial_template.nii.gz`. Run:
```
warp_and_mri_init_template.sh
```
- Based on the parameters in `ncc_params.json`, and the warped mris, we use the `init-mri-template` as a reference to obtain an mri-based intensity template. Create another `manifest_mri_warped.csv` file.

```
bash greedy_build_template.sh -p params_ncc.json -i manifest_mri_warped.csv -t mri_initial_template.nii.gz -o template_exvivo_mri_template
```

#### Credits
The template building script based on the [scripts](https://github.com/pyushkevich/greedy/tree/master/scripts/template) by Paul Yushkevich.
