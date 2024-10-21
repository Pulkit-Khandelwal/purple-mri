import numpy as np
import nibabel as nib

def read_nifti(filepath_image, filepath_label=False):

    img = nib.load(filepath_image)
    image_data = img.get_fdata()

    try:
        lbl = nib.load(filepath_label)
        label_data = lbl.get_fdata()
    except:
        label_data = 0

    return image_data, label_data, img

def save_nifti(image, filepath_name, img_obj):

    img = nib.Nifti1Image(image, img_obj.affine, header=img_obj.header)
    nib.save(img, filepath_name)


mri_path = '/path/to/data/subject_mri.nii.gz'
segm_path = '/path/to/data/subject_segm.nii.gz'

mri, segm, img_obj = read_nifti(mri_path, segm_path)
_, _, img_obj_segm = read_nifti(segm_path)
print(np.shape(mri))

# These are the ITK-SNAP coordinates around which a patch is to be sampled of size patch_size*2.
coords = [(590, 165, 611),
(444, 256, 380),
(361, 179, 354),
(319, 268, 456),
(224, 339, 545),
(546, 189, 647)]

patch_size=32
count=1
for cord in coords:
    print(cord)
    x,y,z = cord[0], cord[1], cord[2]

    mri_patch = mri[x-patch_size:x+patch_size, y-patch_size:y+patch_size, z-patch_size:z+patch_size]
    segm_patch = segm[x-patch_size:x+patch_size, y-patch_size:y+patch_size, z-patch_size:z+patch_size]
    segm_patch = segm_patch.astype(np.uint8)
    print(np.shape(mri_patch), np.shape(segm_patch))

    coords_string = '_' + str(x) + '_' + str(y) + '_' + str(z)

    save_nifti(mri_patch, '/path/to/save/subject_mri_patch_' + str(count) + coords_string + '.nii.gz', img_obj)
    img_obj_segm.set_data_dtype(np.uint8)
    save_nifti(segm_patch, '/path/to/save/subject_segm_patch_' + str(count) + coords_string + '.nii.gz', img_obj)

    count+=1
