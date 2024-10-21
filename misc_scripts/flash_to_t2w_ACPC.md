### Steps to convert the FLASH space voxel coordinates to T2w image, i.e., in the AC/PC aligned orientation, aka, the `_resliced.nii.gz` T2w image where the dots are placed.


#### Let's follow an example use case for the case `INDD119454L` to understand what is needed and the steps required to the same. The script was tested on a Macbook.
#### All files to reproduce the trasformation are at this box link:
https://upenn.box.com/s/1cc00mjrp35c6nki5ojjmwk481xaiwqb

#### Requirements:
- The FLASH image where the voxel coordinates are listed: `INDD119454L_FLASH_combined_average_reoriented_cleared_norm_0000.nii.gz`
- The T2w image in the AC/PC orientation: `119454L_reslice_v2_cleared_norm.nii.gz`
- `greedy`: Use the binary which I provide in the box folder
- `c3d_affine_tool`: This comes with c3d from itk-snap
- `flash_to_t2_mask.mat`: This was provided by Sandy and is essentially an affine transformation matrix between t2 to flash registration.
- `warp.nii.gz`: I then used `flash_to_t2_mask.mat` to get do a quick deformable registration and obtained `warp.nii.gz` as follows:

***NOTE*** We do not need to perform the deformable registration step and thereby we don't have use the `warp.nii.gz` file as such.

```
./greedy -d 3 \
    -m NMI \
    -i INDD119454L_FLASH_combined_average_reoriented_cleared_norm_0000.nii.gz 119454L_reslice_v2_cleared_norm.nii.gz \
    -it flash_to_t2_mask.mat \
    -o warp.nii.gz \
    -n 100x50x10
```
- The input coordinates as provided by Dylan:
```
Motor: 224, 286, 505
Superior frontal layer 2 iron: 139, 221, 823
Temporal lobe (speckling): 569, 221, 726
OFC (speckling): 511, 179, 884
```

#### Step 1: Get the coordinates in the correct orientation
Note the FLASH image has dimensions: `1148, 352, 770`
Note the T2w AC/PC image has dimensions: `756, 448, 874`

We need to switch `x` and `z` coordinates from above. For example here the Motor cortex:
`224, 286, 505` becomes `505, 286, 224` and then we subtract `x` and `z` from the maximum dimension value of the FALSH image to get:
`1148-505, 286, 770-224` (recall that the ) to get `643,66,546` as below. Repeat for the rest of the voxel coordinates to btain the following voxel coordinates:


```
643,66,546,0,1,Motor
325,131,631,0,2,Superior frontal layer 2 iron
422,131,201,0,3,Temporal lobe (speckling)
264,173,259,0,4,OFC (speckling)
```

#### Step 2: Convert the above voxel coordinates to VTK format to obtain:
```
# vtk DataFile Version 4.0
vtk output
ASCII
DATASET POLYDATA
POINTS 4 float
643 66 546
325 131 631
422 131 201
264 173 259
```
Find the file `coords_flash_voxel.vtk` which is the above listed vtk format coordinates.

#### Step 3: Get world coordinates

```c3d_affine_tool -sform INDD119454L_FLASH_combined_average_reoriented_cleared_norm_0000.nii.gz -o sform_warp_image.mat```
(Note that the `warp.nii.gz` image and the flash image has the same `sform` matrix)

```greedy -d 3 -rf INDD119454L_FLASH_combined_average_reoriented_cleared_norm_0000.nii.gz -rs coords_flash_voxel.vtk flash_input_world_coords.vtk -r sform_warp_image.mat```

#### Step 4: Apply the warp and affine matrix to bring the world coordinates from flash to T2w AC/PC space

```greedy -d 3 -rf INDD119454L_FLASH_combined_average_reoriented_cleared_norm_0000.nii.gz -rs flash_input_world_coords.vtk out_warp_world_fixed.vtk -r flash_to_t2_mask.mat warp.nii.gz```

#### Step 5: Get the inverse sform for the T2w AC/PC image

```c3d_affine_tool -sform 119454L_reslice_v2_cleared_norm.nii.gz -inv -o sform_inverse_moving_image.mat```

#### Step 6: Bring the transformed world coordinates to the T2w AC/PC space which is the final output

```greedy -d 3 -rf INDD119454L_FLASH_combined_average_reoriented_cleared_norm_0000.nii.gz -rs out_warp_world_fixed.vtk voxel_coord_t2w_output.vtk -r sform_inverse_moving_image.mat```

Here is what `voxel_coord_t2w_output.vtk` looks like:
```
# vtk DataFile Version 4.2
vtk output
ASCII
DATASET POLYDATA
POINTS 4 float
378.323 189.804 551.758 206.234 249.111 552.059 306.432 206.672 338.74 
219.856 242.573 346.45 
```

#### The voxel coordinates in the T2w AC/PC space looks like:

```
Motor: 378, 189, 551
Superior frontal layer 2 iron: 206, 249, 552
Temporal lobe (speckling): 306, 206, 338
OFC (speckling): 219, 242, 346
```
