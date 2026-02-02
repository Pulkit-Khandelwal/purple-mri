
echo "Spinning up virtual environment and setting up nnUNet......"
source /ml/bin/activate

export nnUNet_preprocessed="/src/nnunet_paths_that_it_requires"
export RESULTS_FOLDER="/src/nnunet_paths_that_it_requires"
export nnUNet_raw_data_base="/src/nnunet_paths_that_it_requires"

accepted_variable=$1
echo "Getting you pretty segmentations for ....... $accepted_variable"

if [[ "$accepted_variable" == "exvivo_t2w" ]]; then
   #nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 389 -tr nnUNetTrainerWMHV2 -m 3d_fullres --disable_mixed_precision -f all
   #nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 287 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 283 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all

:<<'SKIP'
elif [[ "$accepted_variable" == "exvivo_flash_more_subcort" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 289 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all

elif [[ "$accepted_variable" == "exvivo_ciss_t2w" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 290 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all
SKIP

elif [[ "$accepted_variable" == "invivo_flair_wmh" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 451 -tr nnUNetTrainerWMHV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_flash_thalamus" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 276 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

######## Feb 1st 2026
elif [[ "$accepted_variable" == "exvivo_posthoc_topology" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 279 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_flash_gm_wm_segm" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 278 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_umc_strip_cerebellum" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 101 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

else
   echo "Please, select a valid option!"
fi
