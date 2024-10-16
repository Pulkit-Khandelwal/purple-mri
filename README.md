# purple-mri
## **P**enn **U**tilities for **R**egistration and **P**arcel**L**ation of **E**x vivo **MRI**

We provide a set of tools packaged as `purple-mri` based on deep learning and classical surface-based modeling for segmentation and parcellation of ultra high-resolution postmortem brain tissue at native subject-space resolution. This allows us to perform vertex-wise analysis in the template space and thereby link morphometry measures with pathology measurements derived from histology.

Steps:
- bias correction
- run through the docker to get the intial 10-label map with cruise toplogvy correction
- run the surface-based parcellation scheme
- do the glm and correlation analyses

TODO:
- add the 9.4t mtl to 7t hemis registration
- exvivo to invio volumetric registration greedy script


## The package will soon be available as a `pip` package available at PyPI.
