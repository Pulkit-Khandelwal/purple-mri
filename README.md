# purple-mri
## **P**enn **U**tilities for **R**egistration and **P**arcel**L**ation of **E**x vivo **MRI**

We provide a set of tools packaged as `purple-mri` for segmentation, parcellation and registration of ultra high-resolution (< 300 microns) postmortem human brain hemisphere at 7 tesla t2w MRI at native subject-space resolution. This pipeline leverages advances in both deep learning and classical surface-based modeling techniques to produce parcellations in any atlas used in neuroimaging. The developed method allows us to perform vertex-wise analysis in the template space and thereby link morphometry measures with pathology measurements derived from histology.

Check out the [project page](https://pulkit-khandelwal.github.io/exvivo-brain-upenn/) and our latest papers [here](https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00171/120741) and [here](https://arxiv.org/abs/2403.19497).

In particular, `purple-mri` allows you to do the following:
+ obtain an initial 10 label segmentation: cortical GM, normal appearing WM, WMH, medial temporal lobe, corpus callosum, ventricles, caudate, putamen, globus pallidus and thalamus
+ obtain surface-based native subject-space parcellation based on different brain atlases such as: DKT, Economo, Schaeffer etc
+ create population specific volumetric and surface-based templates
+ perform exvivo to invivo registration in volumetric intensity space
+ perform surface-to-surface registration between exvivo or invivo
+ perform intensity-based registration between 9.4 tesla MTL to 7 tesla whole hemsiphere registration
+ perform vertex-wise and group-wise generalized linear modeling analysis for exvivo subject population for morphometry and histology

## Steps (for segmentation and parcellation)
`purple-mri` follows a series of steps with external dependencies making use of Docker and bash scripts:

### Pre-processing
Perform bias correction and image normalization/standardization. We use `N4BiasFieldCorrection` as part of the CLI tool [`c3d`](http://www.itksnap.org/pmwiki/pmwiki.php?n=Convert3D.Convert3D). We highly recommend using the option of an input mask in `N4BiasFieldCorrection` which can be just obtained as a corase threhsold.
[Here](https://github.com/Pulkit-Khandelwal/upenn-picsl-brain-ex-vivo/tree/main/misc_scripts) is a sample script.

### Deep learning based initial labeling and CRUISE-based post-hoc topology correction 

### Surface-based modeling to obtain whole-hemisphere parcellations

## Other scripts
### Intensity-based volumetric template building
### Ex vivo and in vivo registration
### Perform GLM analyses

### Notes
+ Our method has been developed to work on a single exvivo hemisphere.
+ The deep learning-based segmentation was primarily trained on 7T t2w MRI. We have tested the model on t2* flash as well and it works pretty well but, if need be, we recommend re-training the model with some manual labels obtained on t2* flash MRI.


#### The package will soon be available as a `pip` install at PyPI.

## Citations
+ Khandelwal, P., Duong, M. T., Sadaghiani, S., Lim, S., Denning, A. E., Chung, E., ... & Yushkevich, P. A. (2024). Automated deep learning segmentation of high-resolution 7 tesla postmortem MRI for quantitative analysis of structure-pathology correlations in neurodegenerative diseases. Imaging Neuroscience, 2, 1-30.
+ Khandelwal, P., Duong, M. T., Fuentes, C., Denning, A., Trotman, W., Ittyerah, R., ... & Yushkevich, P. A. (2024). Surface-based parcellation and vertex-wise analysis of ultra high-resolution ex vivo 7 tesla MRI in neurodegenerative diseases. arXiv preprint arXiv:2403.19497.

