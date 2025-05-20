
import nibabel as nib
import numpy as np
import os
import sys

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

segm_path=str(sys.argv[1])
subj=str(sys.argv[2])
segm_path_full=segm_path+subj+'_cortexdots_final.nii.gz'
segm, _, img_obj = read_nifti(segm_path_full)

unique_labels = np.unique(segm)
print(f"Unique labels found in image: {unique_labels}")
# Save to a text file
unique_labels_uint = np.array(unique_labels, dtype=np.uint8)
with open(segm_path + "unique_labels_"  + subj + ".txt", "w") as f:
    f.write(str(unique_labels_uint[1:]))

for label in range(1, 20):
    if label in unique_labels:
        print("Splitting label: ", label, " for subject ", subj)
        mask = (segm == label).astype(np.uint8)
        save_nifti(mask, segm_path+subj+f'_cortexdots_final_label{label:02d}.nii.gz', img_obj)
    else:
        print(f"Label {label} not found in image. Skipping.")
