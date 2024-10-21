
echo "Spinning up virtual environment and setting up nnUNet......"
source /ml/bin/activate 

export nnUNet_preprocessed="/src/nnunet_paths_that_it_requires"
export RESULTS_FOLDER="/src/nnunet_paths_that_it_requires"
export nnUNet_raw_data_base="/src/nnunet_paths_that_it_requires"

accepted_variable=$1
echo "Getting you pretty segmentations for ....... $accepted_variable"

if [[ "$accepted_variable" == "exvivo_t2w" ]]; then
   #nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 389 -tr nnUNetTrainerWMHV2 -m 3d_fullres --disable_mixed_precision -f all
    nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 287 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all

elif [[ "$accepted_variable" == "exvivo_flash_more_subcort" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 289 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all

elif [[ "$accepted_variable" == "exvivo_ciss_t2w" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 290 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all

elif [[ "$accepted_variable" == "invivo_flair_wmh" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 451 -tr nnUNetTrainerWMHV2 -m 3d_fullres --disable_mixed_precision -f all     

else
   echo "Please, select a valid option!"
fi
