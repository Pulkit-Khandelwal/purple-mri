# purple-mri
## **P**enn **U**tilities for **R**egistration and **P**arcel**L**ation of **E**x vivo **MRI**

We perform segmentation of ex vivo MRI.

A stand-alone `pip` package available at PyPI.

Steps:
- bias correction
- run through the docker to get the intial 10-label map with cruise toplogvy correction
- run the surface-based parcellation scheme
- do the glm and correlation analyses

