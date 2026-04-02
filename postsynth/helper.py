import numpy as np
from collections import OrderedDict
from scipy.ndimage import gaussian_filter, map_coordinates, binary_dilation

import numpy as np
from scipy.ndimage import gaussian_filter, binary_dilation

import numpy as np
from scipy.ndimage import gaussian_filter, binary_dilation, binary_closing, binary_opening

import numpy as np
from scipy.ndimage import (
    gaussian_filter,
    binary_dilation,
    binary_closing,
    binary_opening,
    distance_transform_edt,
)

import numpy as np
from scipy.ndimage import (
    gaussian_filter,
    binary_dilation,
    binary_closing,
    binary_fill_holes,
    distance_transform_edt,
)
import numpy as np
from scipy.ndimage import gaussian_filter

import numpy as np
from scipy.ndimage import gaussian_filter, binary_erosion

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

# -----------------------------
# stats / priors
# -----------------------------
def _robust_mean_std(x, lo=1.0, hi=99.0, eps=1e-6):
    """Robust mean/std using percentile clipping."""
    if x.size == 0:
        return np.nan, np.nan
    a = np.percentile(x, lo)
    b = np.percentile(x, hi)
    if b <= a + eps:
        a = float(np.min(x))
        b = float(np.max(x)) + eps
    xc = np.clip(x, a, b)
    mu = float(np.mean(xc))
    sd = float(np.std(xc))
    if not np.isfinite(sd) or sd < eps:
        sd = float(np.std(x)) if np.isfinite(np.std(x)) else 1.0
        sd = max(sd, eps)
    return mu, sd

def estimate_label_priors_from_subject(
    img,
    segi,
    labels=(1,2,3,4,5,6,7,8),
    lo=1.0,
    hi=99.0,
    min_vox=200
):
    """
    Returns:
      priors[label] = {"mu":..., "sd":..., "n":...}
    If a label has too few voxels, mu/sd will be nan; caller can fill/fallback.
    """
    priors = {}
    for lab in labels:
        m = (segi == lab)
        n = int(m.sum())
        if n < min_vox:
            priors[int(lab)] = {"mu": np.nan, "sd": np.nan, "n": n}
            continue
        mu, sd = _robust_mean_std(img[m], lo=lo, hi=hi)
        priors[int(lab)] = {"mu": mu, "sd": sd, "n": n}
    return priors

def fill_missing_priors_with_group_fallback(priors, groups, default_sd=0.05):
    """
    Fill missing (nan) label priors using group averages, then global average.
    groups: dict like {"WM":[1,5], "GM":[2,6], ...}
    """
    # group means
    group_mu = {}
    group_sd = {}
    for gname, labs in groups.items():
        mus = [priors[l]["mu"] for l in labs if np.isfinite(priors[l]["mu"])]
        sds = [priors[l]["sd"] for l in labs if np.isfinite(priors[l]["sd"])]
        group_mu[gname] = float(np.mean(mus)) if mus else np.nan
        group_sd[gname] = float(np.mean(sds)) if sds else np.nan

    # global fallback
    all_mus = [v["mu"] for v in priors.values() if np.isfinite(v["mu"])]
    all_sds = [v["sd"] for v in priors.values() if np.isfinite(v["sd"])]
    glob_mu = float(np.mean(all_mus)) if all_mus else 0.0
    glob_sd = float(np.mean(all_sds)) if all_sds else default_sd
    glob_sd = max(glob_sd, 1e-6)

    # fill
    lab_to_group = {}
    for gname, labs in groups.items():
        for l in labs:
            lab_to_group[int(l)] = gname

    out = {int(k): dict(v) for k, v in priors.items()}
    for lab, d in out.items():
        if np.isfinite(d["mu"]) and np.isfinite(d["sd"]):
            continue
        g = lab_to_group.get(int(lab), None)
        mu = group_mu.get(g, np.nan)
        sd = group_sd.get(g, np.nan)

        if not np.isfinite(mu):
            mu = glob_mu
        if not np.isfinite(sd):
            sd = glob_sd

        out[int(lab)]["mu"] = float(mu)
        out[int(lab)]["sd"] = float(max(sd, 1e-6))
    return out

def jitter_priors(priors, rng, mu_jitter_sd_frac=0.40, sd_jitter_sd_frac=0.25):
    """
    priors: dict label -> {"mu","sd"}
    returns jittered priors dict label -> {"mu","sd"}
    """
    out = {}
    for lab, d in priors.items():
        mu, sd = float(d["mu"]), float(d["sd"])
        mu_j = mu + rng.normal(0, abs(mu) * mu_jitter_sd_frac + 1e-6)
        sd_j = sd * (1.0 + rng.normal(0, sd_jitter_sd_frac))
        sd_j = float(max(sd_j, 1e-6))
        out[int(lab)] = {"mu": float(mu_j), "sd": sd_j}
    return out

# -----------------------------
# GRF spatial mean fields per label
# -----------------------------
def _sample_grf(shape, rng, corr_vox):
    """Zero-mean GRF via smoothing white noise."""
    z = rng.normal(0, 1, size=shape).astype(np.float32)
    # corr_vox can be scalar or 3-tuple; gaussian_filter supports tuple sigmas
    return gaussian_filter(z, sigma=corr_vox).astype(np.float32)

def spatial_means_from_grf_multi(
    segi,
    rng,
    priors,
    labels=(1,2,3,4,5,6,7,8),
    mean_amp_sd_range=(0.15, 0.70),
    corr_vox_range=(30, 120),
):
    """
    Returns:
      mu_fields[label] = np.ndarray(shape) for voxels in that label
      meta: dict describing sampled params
    """
    shape = segi.shape
    mu_fields = {}
    meta = {"labels": list(map(int, labels)), "per_label": {}}

    for lab in labels:
        lab = int(lab)
        mu = float(priors[lab]["mu"])
        sd = float(priors[lab]["sd"])

        amp = float(rng.uniform(*mean_amp_sd_range) * sd)
        corr = float(rng.uniform(*corr_vox_range))
        grf = _sample_grf(shape, rng, corr_vox=corr)

        # normalize field to unit std before scaling by amp
        gstd = float(np.std(grf)) + 1e-6
        grf = grf / gstd

        mu_fields[lab] = (mu + amp * grf).astype(np.float32)
        meta["per_label"][str(lab)] = {"mu": mu, "sd": sd, "amp": amp, "corr_vox": corr}

    return mu_fields, meta

def synth_from_spatial_means_multi(
    segi,
    rng,
    mu_fields,
    priors,
    labels=(1,2,3,4,5,6,7,8),
    noise_scale=0.25,
    noise_sigma_vox=0.7,
    background_value=0.0,
):
    """
    Build syn_raw for all labels:
      syn[x in label] ~ mu_field + noise_scale * sd * smooth_noise
    """
    shape = segi.shape
    syn = np.zeros(shape, dtype=np.float32) + float(background_value)

    # smooth noise field shared across labels (cheap, coherent texture)
    n = rng.normal(0, 1, size=shape).astype(np.float32)
    n = gaussian_filter(n, sigma=float(noise_sigma_vox)).astype(np.float32)

    for lab in labels:
        lab = int(lab)
        m = (segi == lab)
        if not np.any(m):
            continue
        sd = float(priors[lab]["sd"])
        syn[m] = mu_fields[lab][m] + float(noise_scale) * sd * n[m]

    return syn.astype(np.float32)

# -----------------------------
# augmentation building blocks
# -----------------------------
def _apply_gamma(x, gamma, eps=1e-6):
    # assumes x roughly normalized; we keep it stable by shifting to >=0
    xmin = float(np.min(x))
    y = x - xmin
    y = np.clip(y, 0.0, None)
    y = (y + eps) ** float(gamma)
    return y + xmin

def _random_bias_field(shape, rng, sigma_vox_range=(30.0, 90.0), strength_range=(0.15, 0.50)):
    """Multiplicative bias field exp(smooth noise * strength)."""
    sigma = float(rng.uniform(*sigma_vox_range))
    strength = float(rng.uniform(*strength_range))
    z = rng.normal(0, 1, size=shape).astype(np.float32)
    z = gaussian_filter(z, sigma=sigma).astype(np.float32)
    z = z / (float(np.std(z)) + 1e-6)
    bf = np.exp(strength * z).astype(np.float32)
    return bf, {"sigma_vox": sigma, "strength": strength}

def _random_displacement_field(shape, rng, max_disp_vox, smooth_sigma_vox):
    """3D displacement field (dx,dy,dz) with smoothness."""
    disp = []
    for _ in range(3):
        d = rng.normal(0, 1, size=shape).astype(np.float32)
        d = gaussian_filter(d, sigma=float(smooth_sigma_vox)).astype(np.float32)
        d = d / (float(np.std(d)) + 1e-6)
        disp.append(d)
    disp = np.stack(disp, axis=0)  # (3, X, Y, Z)
    scale = float(rng.uniform(0.0, float(max_disp_vox)))
    disp = (disp * scale).astype(np.float32)
    return disp, {"max_disp_vox": float(max_disp_vox), "smooth_sigma_vox": float(smooth_sigma_vox), "scale": scale}

def warp_image_and_label(img, seg, rng, warp_prob=0.5,
                         max_disp_vox_range=(5.0, 20.0),
                         smooth_sigma_vox_range=(5.0, 30.0)):
    """Warp img (linear) and seg (nearest) with same displacement field."""
    meta = {"did_warp": False}
    if rng.random() > warp_prob:
        return img, seg, meta

    max_disp = float(rng.uniform(*max_disp_vox_range))
    smooth_sigma = float(rng.uniform(*smooth_sigma_vox_range))
    disp, dmeta = _random_displacement_field(img.shape, rng, max_disp, smooth_sigma)

    # coordinate grid
    coords = np.meshgrid(
        np.arange(img.shape[0], dtype=np.float32),
        np.arange(img.shape[1], dtype=np.float32),
        np.arange(img.shape[2], dtype=np.float32),
        indexing="ij",
    )
    coords = np.stack(coords, axis=0)  # (3,X,Y,Z)
    new_coords = coords + disp  # (3,X,Y,Z)

    # img: trilinear
    wimg = map_coordinates(img, new_coords, order=1, mode="nearest").astype(np.float32)
    # seg: nearest
    wseg = map_coordinates(seg.astype(np.float32), new_coords, order=0, mode="nearest")
    wseg = np.round(wseg).astype(np.int16)

    meta.update({"did_warp": True, "disp": dmeta})
    return wimg, wseg, meta

def intensity_aug_by_groups(
    img,
    seg,
    rng,
    groups,
    # global affine & gamma
    do_global_first=True,
    a_global_range=(0.75, 1.35),
    b_global_range=(-0.12, 0.12),
    gamma_prob=0.85,
    gamma_global_range=(0.75, 1.60),
    # per-group affine
    a_group_range=(0.80, 1.35),
    b_group_range=(-0.12, 0.12),
    # per-group gamma
    gamma_group_range=(0.70, 1.80),
    p_group_gamma=0.90,
):
    """
    groups: dict name->list(labels)
    Applies global then per-group perturbations inside masks.
    """
    meta = {"global": None, "per_group": {}}
    x = img.astype(np.float32, copy=True)

    if do_global_first:
        a = float(rng.uniform(*a_global_range))
        b = float(rng.uniform(*b_global_range))
        x = a * x + b
        gmeta = {"a": a, "b": b}
        if rng.random() < gamma_prob:
            gamma = float(rng.uniform(*gamma_global_range))
            x = _apply_gamma(x, gamma)
            gmeta["gamma"] = gamma
        meta["global"] = gmeta

    for gname, labs in groups.items():
        labs = list(map(int, labs))
        m = np.isin(seg, labs)
        if not np.any(m):
            continue
        a = float(rng.uniform(*a_group_range))
        b = float(rng.uniform(*b_group_range))
        x[m] = a * x[m] + b

        gmeta = {"a": a, "b": b}
        if rng.random() < p_group_gamma:
            gamma = float(rng.uniform(*gamma_group_range))
            # gamma on the masked region only
            tmp = x[m]
            tmp = _apply_gamma(tmp, gamma)
            x[m] = tmp
            gmeta["gamma"] = gamma

        meta["per_group"][str(gname)] = gmeta

    return x.astype(np.float32), meta

def add_texture(img, rng, sigma_range=(0.5, 2.0), strength_range=(0.02, 0.10)):
    """Add band-limited noise texture."""
    sigma = float(rng.uniform(*sigma_range))
    strength = float(rng.uniform(*strength_range))
    z = rng.normal(0, 1, size=img.shape).astype(np.float32)
    z = gaussian_filter(z, sigma=sigma).astype(np.float32)
    z = z / (float(np.std(z)) + 1e-6)
    out = (img + strength * z).astype(np.float32)
    return out, {"sigma": sigma, "strength": strength}

def clip_to_percentiles(img, lo=0.5, hi=99.5):
    a = float(np.percentile(img, lo))
    b = float(np.percentile(img, hi))
    if b <= a + 1e-6:
        return img
    return np.clip(img, a, b).astype(np.float32)

# -----------------------------
# main "crazy" variant generator (multi-label)
# -----------------------------
def make_variant_from_frozen_raw_crazy_multi(
    syn_raw,
    segi,
    rng,
    label_groups,
    do_intensity=True,
    do_warp=True,
    warp_prob=0.5,
    warp_max_disp_vox_range=(5.0, 20.0),
    warp_smooth_sigma_vox_range=(5.0, 30.0),
    do_texture=True,
    do_bias=True,
    do_clip=True,
    intensity_kwargs=None,
    bias_sigma_vox_range=(30.0, 90.0),
    bias_strength_range=(0.15, 0.50),
):
    """
    syn_raw: float32 base synthetic
    segi: int labels
    label_groups: dict e.g. {"WM":[1,5], "GM":[2,6], "HIPPO":[3,7], "CC":[4,8]}
    Returns: syn_var, seg_var, meta
    """
    meta = {"steps": {}}
    img = syn_raw.astype(np.float32, copy=True)
    seg = segi.astype(np.int16, copy=True)

    # warp first (so intensity ops apply in warped space)
    if do_warp:
        img, seg, wmeta = warp_image_and_label(
            img, seg, rng,
            warp_prob=warp_prob,
            max_disp_vox_range=warp_max_disp_vox_range,
            smooth_sigma_vox_range=warp_smooth_sigma_vox_range
        )
        meta["steps"]["warp"] = wmeta

    # bias field
    if do_bias:
        bf, bmeta = _random_bias_field(img.shape, rng, sigma_vox_range=bias_sigma_vox_range, strength_range=bias_strength_range)
        img = (img * bf).astype(np.float32)
        meta["steps"]["bias"] = bmeta

    # texture
    if do_texture:
        img, tmeta = add_texture(img, rng)
        meta["steps"]["texture"] = tmeta

    # intensity
    if do_intensity:
        kw = dict(intensity_kwargs or {})
        # if user didn't pass group ranges, keep reasonable defaults
        img, imeta = intensity_aug_by_groups(
            img, seg, rng,
            groups=label_groups,
            do_global_first=kw.get("do_global_first", True),
            a_global_range=kw.get("a_global_range", (0.75, 1.35)),
            b_global_range=kw.get("b_global_range", (-0.12, 0.12)),
            gamma_prob=kw.get("gamma_prob", 0.85),
            gamma_global_range=kw.get("gamma_global_range", (0.75, 1.60)),
            a_group_range=kw.get("a_group_range", (0.80, 1.35)),
            b_group_range=kw.get("b_group_range", (-0.12, 0.12)),
            gamma_group_range=kw.get("gamma_group_range", (0.70, 1.80)),
            p_group_gamma=kw.get("p_group_gamma", 0.90),
        )
        meta["steps"]["intensity"] = imeta

    if do_clip:
        img = clip_to_percentiles(img, lo=0.5, hi=99.5)
        meta["steps"]["clip"] = {"lo": 0.5, "hi": 99.5}

    return img.astype(np.float32), seg.astype(np.int16), meta

def add_cortical_gm_depth_gradient(
    img,
    seg,
    label_groups=None,
    gm_label=None,
    wm_label=None,
    bg_label=0,
    strength=0.25,
    power=1.2,
    smooth_sigma=1.0,
):
    """
    Adds laminar intensity gradient inside cortical GM.
    Dark near WM boundary, brighter toward pial surface.

    Use EITHER:
      - label_groups={"GM":[...], "WM":[...]}  (recommended for your setup)
    OR:
      - gm_label=<int>, wm_label=<int>         (single-label)

    strength: 0.1–0.35 recommended
    power: >1 increases nonlinear layering
    """

    x = img.astype(np.float32, copy=True)

    if label_groups is not None:
        gm = np.isin(seg, label_groups["GM"])
        wm = np.isin(seg, label_groups["WM"])
        bg = (seg == bg_label)  # usually 0
    else:
        if gm_label is None or wm_label is None:
            raise ValueError("Provide either label_groups OR (gm_label and wm_label).")
        gm = (seg == gm_label)
        wm = (seg == wm_label)
        bg = (seg == bg_label)

    if gm.sum() == 0:
        return x

    d_to_wm = distance_transform_edt(~wm)
    d_to_bg = distance_transform_edt(~bg)

    a = d_to_wm[gm]
    b = d_to_bg[gm]

    depth = a / (a + b + 1e-8)
    depth = depth ** power

    depth_map = np.zeros_like(x, dtype=np.float32)
    depth_map[gm] = depth

    if smooth_sigma > 0:
        depth_map = gaussian_filter(depth_map, smooth_sigma)

    ramp = (1.0 - strength) + (2.0 * strength) * depth_map
    x[gm] *= ramp[gm]

    return x


def add_fomblin_residue_blobs(
    img,
    brain_mask,
    n_small=250,
    n_large=60,
    small_sigma=(0.5, 1.3),
    large_sigma=(3.0, 10.0),
    amp_small=(0.25, 0.80),
    amp_large=(0.50, 1.60),
    boundary_margin_vox=2,
    final_blur=0.2,
    seed=None,
):
    """
    Add bright residue blobs outside brain (fomblin residue).
    Produces more visible discrete blobs than repeatedly blurring one global field.
    """
    x = img.astype(np.float32, copy=True)
    rng = np.random.default_rng(seed)

    brain_mask = brain_mask.astype(bool)

    # avoid placing blobs right on brain boundary
    if boundary_margin_vox and boundary_margin_vox > 0:
        dil = binary_dilation(brain_mask, iterations=int(boundary_margin_vox))
        allowed_bg = ~dil
    else:
        allowed_bg = ~brain_mask

    coords = np.argwhere(allowed_bg)
    if coords.shape[0] == 0:
        return x

    blob = np.zeros_like(x, dtype=np.float32)

    def add_blob_once(sig_range, amp_range):
        nonlocal blob
        z, y, xx = coords[rng.integers(0, coords.shape[0])]
        amp = float(rng.uniform(*amp_range))
        sig = float(rng.uniform(*sig_range))

        tmp = np.zeros_like(blob, dtype=np.float32)
        tmp[z, y, xx] = amp
        tmp = gaussian_filter(tmp, sigma=sig)
        blob += tmp

    # many small speckles + fewer large patches
    for _ in range(int(n_small)):
        add_blob_once(small_sigma, amp_small)
    for _ in range(int(n_large)):
        add_blob_once(large_sigma, amp_large)

    if final_blur and final_blur > 0:
        blob = gaussian_filter(blob, sigma=float(final_blur))

    # apply only in allowed background
    x[allowed_bg] += blob[allowed_bg]
    return x



def add_gm_trapped_water_bubbles(
    img,
    seg,
    label_groups=None,
    gm_labels=None,
    n_small=80,
    n_large=10,
    small_sigma=(0.6, 1.5),
    large_sigma=(2.0, 5.0),
    depth_bias=0.35,
    strength_small=(0.25, 0.55),
    strength_large=(0.40, 0.80),
    boundary_margin_vox=1,
    final_blur=0.4,
    seed=None,
):
    """
    Simulate trapped-water/air bubbles inside cortical GM as sparse dark holes.
    IMPORTANT: does NOT change seg labels; only modifies intensity in GM voxels.

    Parameters
    ----------
    img : (Z,Y,X) float
    seg : (Z,Y,X) int
    label_groups : dict with key "GM" listing GM labels (e.g., [2,6]).
                  If provided, gm_labels is ignored.
    gm_labels : list[int], optional alternative to label_groups.
    n_small, n_large : number of bubble seeds
    small_sigma, large_sigma : Gaussian sigma ranges in voxels (bubble sizes)
    depth_bias : 0..1; if >0, bubbles slightly prefer nearer pial side (if you also use GM depth gradient)
                Here implemented as a bias toward GM boundary by sampling from eroded GM less often.
    strength_* : multiplicative darkening amount ranges (fraction removed). e.g. 0.6 means 60% darker.
    boundary_margin_vox : erode GM by this many voxels to avoid placing bubbles right on border
    final_blur : soften bubble edges
    seed : RNG seed
    """
    x = img.astype(np.float32, copy=True)
    rng = np.random.default_rng(seed)

    if label_groups is not None:
        gm = np.isin(seg, label_groups["GM"])
    else:
        if gm_labels is None:
            raise ValueError("Provide label_groups or gm_labels")
        gm = np.isin(seg, gm_labels)

    if gm.sum() == 0:
        return x

    # avoid boundary a bit so bubbles look internal
    gm_allowed = gm
    if boundary_margin_vox and boundary_margin_vox > 0:
        gm_allowed = binary_erosion(gm, iterations=int(boundary_margin_vox))
        if gm_allowed.sum() == 0:
            gm_allowed = gm  # fallback if cortex is thin

    coords = np.argwhere(gm_allowed)
    if coords.shape[0] == 0:
        return x

    # bubble field accumulates "darkening strength" in [0,1]
    bubble = np.zeros_like(x, dtype=np.float32)

    def sprinkle(n, sig_lo, sig_hi, str_lo, str_hi):
        nonlocal bubble
        if n <= 0:
            return

        # place impulses (each is a local darkening amount)
        for _ in range(n):
            z, y, xx = coords[rng.integers(0, coords.shape[0])]
            bubble[z, y, xx] += rng.uniform(str_lo, str_hi)

        # blur to create blob volumes
        sig = float(rng.uniform(sig_lo, sig_hi))
        bubble[:] = gaussian_filter(bubble, sigma=sig)

    # many small + a few big bubbles
    sprinkle(n_small, small_sigma[0], small_sigma[1], strength_small[0], strength_small[1])
    sprinkle(n_large, large_sigma[0], large_sigma[1], strength_large[0], strength_large[1])

    if final_blur and final_blur > 0:
        bubble = gaussian_filter(bubble, sigma=float(final_blur))

    # restrict to GM only
    bubble *= gm.astype(np.float32)

    # Convert bubble field to multiplicative mask:
    # bubble ~ 0 -> keep intensity
    # bubble ~ 1 -> strong darkening
    bubble = np.clip(bubble, 0.0, 1.0)
    mult = 1.0 - bubble  # intensity multiplier

    x[gm] *= mult[gm]

    return x


def add_fomblin_residue_patches(
    img,
    brain_mask,
    corr_sigma_vox=(25.0, 70.0),        # BIG correlation => big blobs
    thresh_quantile=(0.990, 0.996),     # lower => larger regions (not tiny peaks)
    amp_range=(1.5, 4.0),               # brighter/whiter
    boundary_bias_falloff_vox=10.0,     # keep near specimen
    boundary_margin_vox=0,              # don't push away from brain
    post_smooth_sigma=3.0,              # smooth edges into "smear"
    morph_close_iters=6,                # merge islands -> big patches
    morph_dilate_iters=3,               # enlarge
    seed=None,
):
    """
    Large, smooth, white residue patches outside brain, biased toward brain boundary.
    Designed to avoid speckle/noisy look.
    """
    x = img.astype(np.float32, copy=True)
    rng = np.random.default_rng(seed)

    brain_mask = brain_mask.astype(bool)

    # Allowed background
    if boundary_margin_vox and boundary_margin_vox > 0:
        allowed_bg = ~binary_dilation(brain_mask, iterations=int(boundary_margin_vox))
    else:
        allowed_bg = ~brain_mask

    if allowed_bg.sum() == 0:
        return x

    # Big smooth random field
    noise = rng.standard_normal(size=x.shape).astype(np.float32)
    sigma = float(rng.uniform(*corr_sigma_vox))
    field = gaussian_filter(noise, sigma=sigma)

    # Boundary bias: prefer near brain surface
    dt = distance_transform_edt(allowed_bg)  # 0 at boundary
    falloff = float(boundary_bias_falloff_vox)
    w = np.exp(-dt / (falloff + 1e-8)).astype(np.float32)
    field_bg = np.where(allowed_bg, field + np.log(w + 1e-8), -np.inf)

    finite_vals = field_bg[np.isfinite(field_bg)]
    if finite_vals.size == 0:
        return x

    # Lower quantile -> larger blobs
    q = float(rng.uniform(*thresh_quantile))
    thr = np.quantile(finite_vals, q)
    mask = (field_bg >= thr)

    # Make blobs big + contiguous
    if morph_close_iters and morph_close_iters > 0:
        mask = binary_closing(mask, iterations=int(morph_close_iters))
    if morph_dilate_iters and morph_dilate_iters > 0:
        mask = binary_dilation(mask, iterations=int(morph_dilate_iters))

    # Fill holes inside residue patches (more "smear" than ringy)
    mask = binary_fill_holes(mask)

    # Soft patch
    patch = mask.astype(np.float32)
    if post_smooth_sigma and post_smooth_sigma > 0:
        patch = gaussian_filter(patch, sigma=float(post_smooth_sigma))

    # Normalize to [0,1]
    mmax = float(patch.max())
    if mmax > 1e-8:
        patch /= mmax

    # Add as strong white smear
    amp = float(rng.uniform(*amp_range))
    x[allowed_bg] += amp * patch[allowed_bg]

    return x


def add_fomblin_residue_haze_uniform(
    img,
    brain_mask,
    haze_sigma_vox=(25.0, 90.0),   # bigger = broader blobs
    haze_amp=(0.08, 0.30),         # subtle
    post_smooth_sigma=1.5,         # extra smoothness
    clamp_bg_max=1.2,              # keep from blowing out
    seed=None,
):
    """
    Spread-out residue haze across *all* background uniformly:
    - no boundary bias
    - no exclusion ring
    - random near and far from specimen
    """
    x = img.astype(np.float32, copy=True)
    rng = np.random.default_rng(seed)

    brain_mask = brain_mask.astype(bool)
    bg = ~brain_mask
    if bg.sum() == 0:
        return x

    # smooth random field
    noise = rng.standard_normal(size=x.shape).astype(np.float32)
    sigma = float(rng.uniform(*haze_sigma_vox))
    haze = gaussian_filter(noise, sigma=sigma)

    # normalize haze within background to [0,1]
    hv = haze[bg]
    p1, p99 = np.percentile(hv, 1), np.percentile(hv, 99)
    haze = (haze - p1) / (p99 - p1 + 1e-8)
    haze = np.clip(haze, 0.0, 1.0)

    # optional extra smoothing to remove any grain
    if post_smooth_sigma and post_smooth_sigma > 0:
        haze = gaussian_filter(haze, sigma=float(post_smooth_sigma))
        haze = np.clip(haze, 0.0, 1.0)

    amp = float(rng.uniform(*haze_amp))
    x[bg] += amp * haze[bg]

    if clamp_bg_max is not None:
        x[bg] = np.minimum(x[bg], float(clamp_bg_max))

    return x


def add_large_white_fomblin_blobs(
    img,
    brain_mask,
    n_blobs=8,                 # small number → large shapes
    sigma_range=(15, 40),      # LARGE smoothing → big blobs
    amp_range=(0.5, 1.2),      # strong white
    threshold_quantile=0.995,  # high threshold → few but thick blobs
    extra_smooth=3.0,          # makes edges organic
    clamp_bg_max=1.5,
    seed=None,
):
    """
    Generates large irregular white fomblin blobs in background.
    Not noisy. Not edge-biased.
    """

    x = img.astype(np.float32, copy=True)
    rng = np.random.default_rng(seed)

    bg = ~brain_mask.astype(bool)
    if bg.sum() == 0:
        return x

    blob_field = np.zeros_like(x, dtype=np.float32)

    for _ in range(n_blobs):
        noise = rng.standard_normal(size=x.shape).astype(np.float32)

        sigma = rng.uniform(*sigma_range)
        smooth = gaussian_filter(noise, sigma=sigma)

        # threshold high values only
        thresh = np.quantile(smooth[bg], threshold_quantile)
        mask = (smooth > thresh) & bg

        amp = rng.uniform(*amp_range)
        blob_field[mask] += amp

    # Smooth edges so they look like liquid residue
    if extra_smooth > 0:
        blob_field = gaussian_filter(blob_field, sigma=extra_smooth)

    x[bg] += blob_field[bg]

    if clamp_bg_max is not None:
        x[bg] = np.minimum(x[bg], clamp_bg_max)

    return x