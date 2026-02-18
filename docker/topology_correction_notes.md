# Topology correction for cortical GM (post-hoc)
Inputs

segm.nii.gz = your original multi-label segmentation (all labels)

You will generate an intermediate binary-ish/topology input volume and then fuse corrected GM back into the full segmentation.

Step 1 — Create topology input (collapse labels)

Goal: produce segm_input_for_topo_0000.nii.gz with cortical GM as 3, “other tissue” as 2, and background as 0 (per your mapping).


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
CRUISE-based post-hoc topology correction
IMPORTANT NOTE: You don't need to run the following topology correction step and skip directly to the surface-based pipeline below. This is because CRUISE correction introduces a lot of "cracks" in the medial area which mess up the surface pipeline. Therefore, we use FreeSurfer's topology correction instead in the surface-based pipeline. However, for the sake of completeness and for user-dependent application, we mention it here, and correct for topology so that adjoining gyri and sulci are clearly separated. Copy the segmentations from `output_from_nnunet_inference` to a folder `data_for_topology_correction` in your working directory.
```
docker pull pulks/docker_nighres:v1.0.0

docker run -v /your/working/directory/:/data/cruise_files/ -it pulks/docker_nighres:v1.0.0 /bin/bash -c "bash /data/prepare_cruise_files.sh"

# Locally run the file to get the final combined label file.
bash clean_labels_final.sh
```
