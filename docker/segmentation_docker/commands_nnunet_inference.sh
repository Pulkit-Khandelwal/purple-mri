#!/usr/bin/env bash
echo "Spinning up virtual environment and setting up nnUNet......"
source /ml/bin/activate || exit 1

export nnUNet_preprocessed="/src/nnunet_paths_that_it_requires"
export RESULTS_FOLDER="/src/nnunet_paths_that_it_requires"
export nnUNet_raw_data_base="/src/nnunet_paths_that_it_requires"

accepted_variable=$1
echo "Getting you pretty segmentations for ....... $accepted_variable"

if [[ "$accepted_variable" == "exvivo_all" ]]; then
   set -eo pipefail
   SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
   INPUT_DIR="${EXVIVO_INPUT_DIR:-/data/exvivo/data_for_inference}"
   OUT_DIR="${EXVIVO_ALL_OUTPUT_DIR:-${INPUT_DIR}/output_from_nnunet_inference/exvivo_all}"

   helper() {
      python "$SCRIPT_DIR/merge_exvivo.py" "$1" --input-dir "$INPUT_DIR" --output-dir "$OUT_DIR"
   }
   predict() {
      nnUNet_predict -i "$2" -o "$3" -t "$1" -tr nnUNetTrainerV2 \
         -m 3d_fullres --disable_mixed_precision -f all
   }

   command -v nnUNet_predict >/dev/null
   helper init
   echo "[1/7] Original Purple 10-label segmentation"
   predict 283 "$INPUT_DIR" "$OUT_DIR/01_purple_original"
   echo "[2/7] Prepare topology input"
   helper prepare-topology
   echo "[3/7] Post-hoc topology prediction"
   predict 279 "$OUT_DIR/02_topology_input" "$OUT_DIR/03_topology_prediction"
   echo "[4/7] Save buried sulcus mask and corrected Purple segmentation"
   helper apply-topology
   echo "[5/7] MTL and amygdala subfields"
   predict 269 "$INPUT_DIR" "$OUT_DIR/06_mtl"
   echo "[6/7] Subcortical structures"
   predict 273 "$INPUT_DIR" "$OUT_DIR/07_subcortical"
   echo "[7/7] Merge and clean residual labels"
   helper merge
   echo "Complete. All intermediate NIfTI files: $OUT_DIR"
   echo "Corrected Purple: $OUT_DIR/05_purple_corrected"
   echo "Final merge:      $OUT_DIR/11_final_merged"

elif [[ "$accepted_variable" == "exvivo_t2w" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 283 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all

elif [[ "$accepted_variable" == "invivo_flair_wmh" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 451 -tr nnUNetTrainerWMHV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_flash_thalamus" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 276 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_posthoc_topology" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 279 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_umc_strip_cerebellum" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 101 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_multi_sequence_mtl_amygdala_subfields" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 269 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_multi_sequence_subcortical" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 273 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all     

elif [[ "$accepted_variable" == "exvivo_flash_more_subcort" ]]; then
   nnUNet_predict -i /data/exvivo/data_for_inference/ -o /data/exvivo/data_for_inference/output_from_nnunet_inference -t 289 -tr nnUNetTrainerV2 -m 3d_fullres --disable_mixed_precision -f all

else
   echo "Please, select a valid option!"
fi
