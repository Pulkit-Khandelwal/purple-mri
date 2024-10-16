# purple-mri
## **P**enn **U**tilities for **R**egistration and **P**arcel**L**ation of **E**x vivo **MRI**

We provide a set of tools packaged as `purple-mri` for segmentation, parcellation and registration of ultra high-resolution (< 300 microns) postmortem human brain at 7 tesla MRI. tissue at native subject-space resolution. The developed pipeline leverages both advances in deep learning and classical surface-based modeling techniques to produce parcellations in any atlas used in neuroimaging. The developed method allows us to perform vertex-wise analysis in the template space and thereby link morphometry measures with pathology measurements derived from histology.

In particular, `purple-mri` allows you to do the following:
+ segment postmortem human brain at 7 tesla MRI into initial 10 label segmentation: cortical GM,
+ 

Steps:
- bias correction
- run through the docker to get the intial 10-label map with cruise toplogvy correction
- run the surface-based parcellation scheme
- do the glm and correlation analyses

TODO:
- add the 9.4t mtl to 7t hemis registration
- exvivo to invio volumetric registration greedy script


## The package will soon be available as a `pip` package available at PyPI.
