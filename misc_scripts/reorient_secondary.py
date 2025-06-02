import SimpleITK as sitk
import argparse
import numpy as np

def apply_reorient_to_secondary(
        fn_primary_orig: str, 
        fn_primary_reorient: str,
        fn_secondary_orig: str,
        fn_output: str):
    
    i1_o = sitk.ReadImage(fn_primary_orig)
    i1_r = sitk.ReadImage(fn_primary_reorient)
    i2 = sitk.ReadImage(fn_secondary_orig)

    # Get the physical coordinate of primary image zero voxel in original space
    x0_phys_orig = i1_o.TransformIndexToPhysicalPoint([0, 0, 0])

    # The the physical coordinate of the same point after reorientation
    x0_phys_reor = i1_r.TransformIndexToPhysicalPoint([0, 0, 0])

    # Get the voxel coordinate of the point x0_phys_orig in the secondary modality
    x0_vox_sec = i2.TransformPhysicalPointToContinuousIndex(x0_phys_orig)

    # Apply reorientation to the secondary image
    i2.SetDirection(i1_r.GetDirection())

    # Get the physical coordinate of x0_vox_sec after secondary reorientation
    x0_sec_phys_reor = i2.TransformContinuousIndexToPhysicalPoint(x0_vox_sec)

    # The vector between x0_sec_phys_reor and x0_phys_reor should be added to the origin
    i2.SetOrigin(np.array(i2.GetOrigin()) + np.array(x0_phys_reor) - np.array(x0_sec_phys_reor))

    # Save the reoriented image
    sitk.WriteImage(i2, fn_output)


if __name__ == '__main__':

    # Read the parameters
    parser = argparse.ArgumentParser(description="Apply reorientation to a second co-registered modality")
    parser.add_argument('-primary_original', type=str, help="Primary modality with original image header")
    parser.add_argument('-primary_reorient', type=str, help="Primary modality after reorientation")
    parser.add_argument('-secondary_original', type=str, help="Secondary modality with original image header")
    parser.add_argument('-output', type=str, help="Image to save reoriented secondary modality")
    args = parser.parse_args()

    apply_reorient_to_secondary(args.primary_original, args.primary_reorient, args.secondary_original, args.output)

