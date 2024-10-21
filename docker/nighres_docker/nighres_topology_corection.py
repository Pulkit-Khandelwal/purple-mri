import numpy as np
import os
import os.path
import nibabel as nib
import nighres

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


input_path = '/data/cruise_files/data_for_topology_correction/'
subjects = [f for f in os.listdir(input_path) if f.endswith('.nii.gz')]
print(subjects, len(subjects))

output_path = '/data/cruise_files/data_for_topology_correction/output_corrected_topology/'
for subj in subjects:
    subj=subj[:-7]
    print(subj)

    gm = output_path + subj + '_gm.nii.gz'
    wm = output_path + subj + '_wm.nii.gz'
    csf = output_path + subj + '_csf.nii.gz'

    cruise = nighres.cortex.cruise_cortex_extraction(
                            init_image=wm,
                            wm_image=wm,
                            gm_image=gm,
                            csf_image=csf,
                            normalize_probabilities=True,
                            save_data=False)

    cruise_to_save = cruise['cortex']
    nib.save(cruise_to_save, output_path + subj + '_cortex_cruise.nii.gz')

    full_segm, _, img_obj = read_nifti(input_path + subj + '.nii.gz')
    gm_segm, _, _ = read_nifti(output_path + subj + '_cortex_cruise.nii.gz')
    wm_filled_segm, _, _ = read_nifti(output_path + subj + '_wm_plus_binarized.nii.gz')

    gm_segm[wm_filled_segm == 7] = 0
    save_nifti(gm_segm, output_path + subj + '_gm_cortex_cruise_retained_overlap.nii.gz', img_obj)
