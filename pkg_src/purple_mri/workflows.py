"""Workflow names from the combined container launcher (not checkpoint assets)."""

DEFAULT_IMAGE = "pulks/docker_purple_mri:v1.1.0"
MODELS = {
    "exvivo_t2w": (283, "Purple 10-label segmentation"),
    "invivo_flair_wmh": (451, "In vivo FLAIR WMH"),
    "exvivo_flash_thalamus": (276, "Thalamus"),
    "exvivo_posthoc_topology": (279, "Post-hoc topology correction"),
    "exvivo_umc_strip_cerebellum": (101, "Cerebellum removal"),
    "exvivo_multi_sequence_mtl_amygdala_subfields": (269, "MTL and amygdala subfields"),
    "exvivo_multi_sequence_subcortical": (2732, "Flip-fixed subcortical segmentation"),
    "exvivo_flash_more_subcort": (289, "Additional FLASH subcortical model (requires asset)"),
}
STAGES = ("exvivo_dl", "exvivo_all", "exvivo_surface", *MODELS)


def validate_stages(stages):
    if not stages or any(stage not in STAGES for stage in stages):
        raise ValueError("Choose a supported adult workflow; infant container stages are not implemented.")
    if len(stages) > 1 and not (
        len(stages) == 2 and stages[0] in ("exvivo_dl", "exvivo_all")
        and stages[1] == "exvivo_surface"
    ):
        raise ValueError("The only combined sequence is exvivo_dl (or exvivo_all) exvivo_surface.")
