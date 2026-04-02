import os, glob, json, gzip
import numpy as np
import nibabel as nib
from collections import OrderedDict

from helper import (
    estimate_label_priors_from_subject,
    fill_missing_priors_with_group_fallback,
    jitter_priors,
    spatial_means_from_grf_multi,
    synth_from_spatial_means_multi,
    make_variant_from_frozen_raw_crazy_multi,
    add_cortical_gm_depth_gradient,
    add_fomblin_residue_blobs,
    add_gm_trapped_water_bubbles,
    add_fomblin_residue_patches,
    add_fomblin_residue_haze_uniform,
    add_large_white_fomblin_blobs
)

# -----------------------------
# tiny helpers
# -----------------------------
def gz_ok(path):
    """Return True if gzip stream is readable (fast corruption check)."""
    try:
        with gzip.open(path, "rb") as f:
            f.read(1)
        return True
    except Exception:
        return False

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)
    return p

def save_nifti_like(ref_nii, data, out_path, dtype):
    out = nib.Nifti1Image(data.astype(dtype), affine=ref_nii.affine, header=ref_nii.header)
    out.set_data_dtype(dtype)
    nib.save(out, out_path)

def parse_subject_and_modality(stem):
    """
    Depends on how your input filenames are
    """
    base = stem
    if base.endswith("_norm"):
        base = base[:-len("_norm")]
    parts = base.split("_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return base, "UNKNOWN"

# -----------------------------
# configurations
# -----------------------------
base_path = ""
mri_dir = os.path.join(base_path, "mri")
seg_dir = os.path.join(base_path, "segm")

out_root = ensure_dir(base_path)  # keep writing into base_path (you can change)

K = 1  # number of variants per input

#### Number of labels
LABELS = tuple(range(1, 9))

# label groups (your mapping)
LABEL_GROUPS = OrderedDict({
    "WM":    [1, 5],
    "GM":    [2, 6],
    "HIPPO": [3, 7],
    "CC":    [4, 8],
})

# prior jitter (optional)
use_style = False
style_mu_jitter = 0.40
style_sd_jitter = 0.25

# GRF spatial means
use_grf_means = True
grf_mean_amp_sd_range = (0.15, 0.70)   # multiplier * label_sd
grf_corr_vox_range = (30, 120)

# base noise on top of mu field
base_noise_scale = 0.25
base_noise_sigma_vox = 0.7

# variant aug knobs
intensity_kwargs = dict(
    do_global_first=True,
    a_global_range=(0.75, 1.35),
    b_global_range=(-0.12, 0.12),
    gamma_prob=0.85,
    gamma_global_range=(0.75, 1.60),
    # per-group (WM/GM/HIPPO/CC) ranges
    a_group_range=(0.80, 1.35),
    b_group_range=(-0.12, 0.12),
    gamma_group_range=(0.70, 1.80),
    p_group_gamma=0.90,
)

# -----------------------------
# collect files and match MRI->SEG
# -----------------------------
mri_glob = os.path.join(mri_dir, "*_0000.nii.gz")
seg_glob = os.path.join(seg_dir, "*.nii.gz")

mri_files = sorted(glob.glob(mri_glob))
seg_files = sorted(glob.glob(seg_glob))

if not mri_files:
    raise RuntimeError(f"No MRIs found: {mri_glob}")
if not seg_files:
    raise RuntimeError(f"No smoothed segs found: {seg_glob}")

import os

# mri_files = list of full paths to *_0000.nii.gz
# seg_files = list of full paths to *.nii.gz (no _0000)

# ---- Build seg map ----
seg_map = {}
for f in seg_files:
    stem = os.path.basename(f).replace(".nii.gz", "")
    seg_map[stem] = f

# ---- Match MRI to seg ----
pairs = []
missing = []

for mri_path in mri_files:
    stem = os.path.basename(mri_path).replace(".nii.gz", "")
    
    if stem.endswith("_0000"):
        key = stem[:-len("_0000")]
    else:
        key = stem

    seg_path = seg_map.get(key)

    if seg_path is None:
        missing.append(stem)
        continue

    pairs.append((mri_path, seg_path, key))

print(f"Matched pairs: {len(pairs)}")
print(f"Missing segs: {len(missing)}")

if missing:
    print("Missing examples:", missing[:10])

# -----------------------------
# main loop
# -----------------------------
global_summary = []

for idx, (mri_path, seg_path, stem) in enumerate(pairs, 1):
    subj, modality = parse_subject_and_modality(stem)

    print(f"\n[{idx}/{len(pairs)}] Processing {stem}  (subj={subj}, mod={modality})")
    print("  MRI:", mri_path)
    print("  SEG:", seg_path)

    # corruption checks
    if mri_path.endswith(".nii.gz") and not gz_ok(mri_path):
        print(f"  ❌ Corrupted MRI gzip, skipping: {mri_path}")
        continue
    if seg_path.endswith(".nii.gz") and not gz_ok(seg_path):
        print(f"  ❌ Corrupted SEG gzip, skipping: {seg_path}")
        continue

    # load
    try:
        img_nii = nib.load(mri_path)
        seg_nii = nib.load(seg_path)
        img = img_nii.get_fdata(dtype=np.float32)
        seg = np.round(seg_nii.get_fdata()).astype(np.int16)
    except Exception as e:
        print(f"  ❌ Failed to load: {e}")
        continue

    # (optional) enforce label set: 0..8 only
    bad = np.setdiff1d(np.unique(seg), np.array([0] + list(LABELS)))
    if bad.size > 0:
        print(f"  ❌ Found unexpected labels {bad.tolist()} in {seg_path}. Fix/remap first.")
        continue

    # estimate priors per label (1..8), then fill missing via group/global fallback
    priors = estimate_label_priors_from_subject(img, seg, labels=LABELS, lo=1, hi=99, min_vox=200)
    priors = fill_missing_priors_with_group_fallback(priors, LABEL_GROUPS)

    rng_base = np.random.default_rng()

    priors_used = priors
    if use_style:
        priors_used_simple = {l: {"mu": priors[l]["mu"], "sd": priors[l]["sd"]} for l in LABELS}
        priors_used_simple = jitter_priors(
            priors_used_simple, rng_base,
            mu_jitter_sd_frac=style_mu_jitter,
            sd_jitter_sd_frac=style_sd_jitter
        )
        # put back into same structure
        priors_used = {l: {"mu": priors_used_simple[l]["mu"], "sd": priors_used_simple[l]["sd"], "n": priors[l]["n"]} for l in LABELS}

    # build base syn_raw (for all labels)
    if use_grf_means:
        mu_fields, grf_meta = spatial_means_from_grf_multi(
            segi=seg,
            rng=rng_base,
            priors=priors_used,
            labels=LABELS,
            mean_amp_sd_range=grf_mean_amp_sd_range,
            corr_vox_range=grf_corr_vox_range,
        )
        syn_raw = synth_from_spatial_means_multi(
            segi=seg,
            rng=rng_base,
            mu_fields=mu_fields,
            priors=priors_used,
            labels=LABELS,
            noise_scale=base_noise_scale,
            noise_sigma_vox=base_noise_sigma_vox,
            background_value=0.0,
        )
    else:
        grf_meta = None
        # fallback: flat means per label
        syn_raw = np.zeros(seg.shape, dtype=np.float32)
        for l in LABELS:
            m = (seg == l)
            if not np.any(m):
                continue
            syn_raw[m] = float(priors_used[l]["mu"])

    base_meta = {
        "stem": stem,
        "subject": subj,
        "modality": modality,
        "source_mri": mri_path,
        "source_seg": seg_path,
        "labels": list(LABELS),
        "label_groups": LABEL_GROUPS,
        "priors_from_subject": {str(l): priors[l] for l in LABELS},
        "priors_used": {str(l): {"mu": float(priors_used[l]["mu"]), "sd": float(priors_used[l]["sd"])} for l in LABELS},
        "use_grf_means": bool(use_grf_means),
        "grf_meta": grf_meta,
        "K": int(K),
    }

    # output folder per SUBJECT (same as your prior layout)
    subj_out_dir = ensure_dir(os.path.join(out_root, subj))
    variants_meta = []

    # generate K variants
    #for j in range(K):
    for j in range(6, 8):
        rng_j = np.random.default_rng()

        syn_var, seg_var, meta_var = make_variant_from_frozen_raw_crazy_multi(
            syn_raw=syn_raw,
            segi=seg,
            rng=rng_j,
            label_groups=LABEL_GROUPS,
            do_intensity=True,
            intensity_kwargs=intensity_kwargs,
            do_warp=True,
            warp_prob=0.5,
            warp_max_disp_vox_range=(5.0, 20.0),
            warp_smooth_sigma_vox_range=(5.0, 30.0),
            do_texture=True,
            do_bias=True,
            do_clip=True,
        )

        
        syn_var = add_cortical_gm_depth_gradient(
            syn_var,
            seg_var,
            label_groups=LABEL_GROUPS,     # uses GM=[2,6], WM=[1,5]
            strength=0.45,                 # try 0.15–0.35
            power=1.3,                     # try 1.1–1.7
            smooth_sigma=1.0
        )


        syn_var = add_large_white_fomblin_blobs(
            syn_var,
            brain_mask=(seg_var > 0),
            n_blobs=6,
            sigma_range=(20, 50),
            amp_range=(0.8, 1.6),
            threshold_quantile=0.997,
            extra_smooth=4.0,
            clamp_bg_max=1.5,
            seed=None
        )


        """
        syn_var = add_gm_trapped_water_bubbles(
            syn_var, seg_var,
            label_groups=LABEL_GROUPS,
            n_small=80, n_large=10,
            seed=20000 + j
        )
        """

        # (optional) keep intensity in sane range if your pipeline expects [0,1]
        syn_var = np.clip(syn_var, 0.0, 1.0)

        # filenames
        out_img_name = f"{subj}_{modality}_synvar_{j:03d}_0000.nii.gz"
        out_seg_name = f"{subj}_{modality}_synvar_{j:03d}.nii.gz"   # labels do NOT get _0000
        out_img_path = os.path.join(subj_out_dir, out_img_name)
        out_seg_path = os.path.join(subj_out_dir, out_seg_name)

        # save
        save_nifti_like(img_nii, syn_var, out_img_path, dtype=np.float32)
        save_nifti_like(seg_nii, seg_var, out_seg_path, dtype=np.int16)

        vmeta = {
            "variant_index": int(j),
            "out_image": out_img_path,
            "out_label": out_seg_path,
            "augment_meta": meta_var,
        }

        vmeta["exvivo_effects"] = {
        "gm_depth_gradient": {"strength": 0.25, "power": 1.3, "smooth_sigma": 1.0},
        "fomblin_residue": {"n_small": 120, "n_large": 20, "seed": int(10_000 + j)}}

        variants_meta.append(vmeta)

        print(f"  ✅ saved {j+1}/{K}: {os.path.basename(out_img_path)}")

    # write per-pair JSON
    json_path = os.path.join(subj_out_dir, f"{subj}_{modality}_metadata.json")
    with open(json_path, "w") as f:
        json.dump({"base": base_meta, "variants": variants_meta}, f, indent=2)

    print(f"  ✅ Wrote metadata JSON: {json_path}")

    global_summary.append({
        "stem": stem,
        "subject": subj,
        "modality": modality,
        "out_dir": subj_out_dir,
        "json": json_path,
        "K": int(K),
    })

# global index
global_json = os.path.join(out_root, "ALL_metadata_index.json")
with open(global_json, "w") as f:
    json.dump(global_summary, f, indent=2)
print(f"\n✅ Wrote global index JSON: {global_json}")
