# Post-hoc topology correction for cortical GM
Goal: adjoining gyri and sulci should be clearly separated

## Inputs
segm.nii.gz = your original multi-label segmentation (all labels).
You will generate an intermediate binary-ish/topology input volume and then fuse corrected GM back into the full segmentation.

### Step 1 — Create topology input (collapse labels)
Goal: produce segm_input_for_topo_0000.nii.gz with cortical GM as 3, “other tissue” as 2, and background as 0 (per your mapping).
```
c3d segm.nii.gz \
  -replace \
    1 3 \
    2 2 \
    3 2 \
    4 2 \
    5 2 \
    6 2 \
    7 2 \
    8 0 \
    9 2 \
    10 2 \
  -o segm_input_for_topo_0000.nii.gz
```

### Step 2 — Run post-hoc topology correction in purple-mri docker
Follow the docker instructions in: docker/exvivo_docker.md
Use the file: segm_input_for_topo_0000.nii.gz as input
Run with: ```${OPTION}=exvivo_posthoc_topology```
Assume the topology-corrected output produced by the pipeline is: ```segm_input_for_topo.nii.gz```

### Step 3 — Convert corrected cortical GM to label=1
Extract the cortical GM label (3) from the corrected output and remap it back to GM=1:
```
c3d segm_input_for_topo.nii.gz \
  -retain-labels 3 \
  -replace 3 1 \
  -type uchar \
  -o subj_corrected_gm.nii.gz
```
This produces a GM-only volume where voxels are 1 for corrected cortical GM and 0 elsewhere.

### Step 4 — Remove original cortical GM from the full segmentation
Zero out the original cortical GM label (1) so we can “paste” the corrected GM back in:
```
c3d segm.nii.gz \
  -replace 1 0 \
  -type uchar \
  -o segm_no_gm.nii.gz
```

### Step 5 — Fuse corrected GM back into the segmentation
Overlay the corrected GM onto the no-GM segmentation:
```
c3d subj_corrected_gm.nii.gz segm_no_gm.nii.gz \
  -add \
  -type uchar \
  -o final_segm.nii.gz
```

That's it! Use this ```final_segm.nii.gz``` as the segmentation file. You can proceed to the surface-based pipeline.

# CRUISE-based post-hoc topology correction (archived and not to be used)
The CRUISE-based topoogy correction is now archived in favor of the above deep learning-based one. This is because CRUISE correction introduces a lot of "cracks" in the medial area which mess up the surface pipeline. Copy the segmentations from `output_from_nnunet_inference` to a folder `data_for_topology_correction` in your working directory.
```
docker pull pulks/docker_nighres:v1.0.0

docker run -v /your/working/directory/:/data/cruise_files/ -it pulks/docker_nighres:v1.0.0 /bin/bash -c "bash /data/prepare_cruise_files.sh"

# Locally run the file to get the final combined label file.
bash clean_labels_final.sh
```
