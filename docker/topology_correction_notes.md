# Post-hoc topology correction for cortical GM

Remove predicted buried-sulcus regions from the original purple segmentation, then mask existing atlas parcellations.

**Input:** `segm.nii.gz` — original purple 10-label segmentation.

### Step 1 — Create topology input

Remap cortical GM to `3`, other specified tissues to `2`, and label `8` to `0`. Keep the original segmentation unchanged.

```bash
c3d segm.nii.gz \
  -replace 1 3 2 2 3 2 4 2 5 2 6 2 7 2 8 0 9 2 10 2 \
  -o segm_input_for_topo_0000.nii.gz
```

### Step 2 — Run post-hoc topology correction in purple-mri Docker

Follow the Docker instructions in [docker/exvivo_docker.md](exvivo_docker.md).

- Input: `segm_input_for_topo_0000.nii.gz`
- Set `OPTION=exvivo_posthoc_topology`
- Assume the raw prediction is: `segm_input_for_topo.nii.gz`

**Raw prediction label `1` identifies buried-sulcus regions to remove. Ignore all other prediction labels.**

### Step 3 — Remove buried-sulcus regions

Create a keep mask: `0` where the raw prediction equals `1`, and `1` everywhere else.

```bash
c3d segm_input_for_topo.nii.gz \
  -thresh 1 1 0 1 \
  -type uchar \
  -o keep_mask.nii.gz
```

Apply it to the original purple segmentation, preserving surviving anatomical labels:

```bash
c3d segm.nii.gz keep_mask.nii.gz \
  -multiply \
  -type uchar \
  -o final_segm.nii.gz
```

### Step 4 — Create the cleaned foreground mask

Include all surviving nonzero anatomical labels:

```bash
c3d final_segm.nii.gz \
  -thresh 1 inf 1 0 \
  -type uchar \
  -o foreground_mask.nii.gz
```

### Step 5 — Mask existing atlas parcellations

Set the input directory containing the subject’s `aparc*.nii.gz` files:

```bash
APARC_DIR="/path/to/subject/mri"
OUT_DIR="aparc_masked_by_gm_topocorrected_removed_v2/mri"

mkdir -p "$OUT_DIR"

for aparc in "$APARC_DIR"/aparc*.nii.gz; do
  [[ -f "$aparc" ]] || continue

  c3d "$aparc" foreground_mask.nii.gz \
    -multiply \
    -type ushort \
    -o "$OUT_DIR/$(basename "$aparc")"
done
```

**Outputs:** `final_segm.nii.gz` contains the cleaned purple segmentation; the output directory contains masked atlas parcellations with surviving atlas labels preserved.

All input volumes must already share the same voxel grid and alignment.
