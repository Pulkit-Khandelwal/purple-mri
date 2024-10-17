# purple-mri
## **P**enn **U**tilities for **R**egistration and **P**arcel**L**ation of **E**x vivo **MRI**

We provide a set of tools packaged as `purple-mri` for segmentation, parcellation and registration of ultra high-resolution (< 300 microns) postmortem human brain hemisphere at 7 tesla t2w MRI at native subject-space resolution. This pipeline leverages advances in both deep learning and classical surface-based modeling techniques to produce parcellations in any atlas used in neuroimaging. The developed method allows us to perform vertex-wise analysis in the template space and thereby link morphometry measures with pathology measurements derived from histology.

In particular, `purple-mri` allows you to do the following:
+ obtain an initial 10 label segmentation: cortical GM, normal appearing WM, WMH, medial temporal lobe, corpus callosum, ventricles, caudate, putamen, globus pallidus and thalamus
+ obtain surface-based native subject-space parcellation based on different brain atlases such as: DKT, Economo, Schaeffer etc
+ create population specific volumetric and surface-based templates
+ perform exvivo to invivo registration in volumetric intensity space
+ perform surface-to-surface registration between exvivo or invivo
+ perform vertex-wise and group-wise generalized linear modeling analysis for exvivo subject population and link them with histology data
+ perform intensity-based registration between 9.4 tesla MTL to 7 tesla whole hemsiphere registration

## Steps
`purple-mri` follows a series of steps with external dependencies making use of Docker and local bash scripts:

- bias correction
- run through the docker to get the intial 10-label map with cruise toplogy correction
- run the surface-based parcellation scheme
- do the glm and correlation analyses

### Notes
Note that our method has been developed for a single exvivo hemisphere.

# The package will soon be available as a `pip` install at PyPI.

## Citations
+ Khandelwal, P., Duong, M. T., Sadaghiani, S., Lim, S., Denning, A. E., Chung, E., ... & Yushkevich, P. A. (2024). Automated deep learning segmentation of high-resolution 7 tesla postmortem MRI for quantitative analysis of structure-pathology correlations in neurodegenerative diseases. Imaging Neuroscience, 2, 1-30.
+ Khandelwal, P., Duong, M. T., Fuentes, C., Denning, A., Trotman, W., Ittyerah, R., ... & Yushkevich, P. A. (2024). Surface-based parcellation and vertex-wise analysis of ultra high-resolution ex vivo 7 tesla MRI in neurodegenerative diseases. arXiv preprint arXiv:2403.19497.

