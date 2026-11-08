# Documentation figures

The README and Read the Docs landing page reference these same PNGs.
Use repository-relative paths in the README and `_static/examples/` in Sphinx.
All figures link to the full-resolution asset. Their native source width is
2048 pixels; cropped widths are 2040–2048 pixels. No anatomical upsampling or
synthetic enhancement was applied.

Order:
1. `01_volume_atlas_comparison.png`: MRI and cortical atlas overlays, UPenn 123019.
2. `02_surface_parcellations_view1.png`: first supplied seven-atlas surface view.
3. `03_surface_parcellations_view2.png`: second supplied seven-atlas surface view.
4. `04_antemortem_postmortem_registration.png`: within-subject registration.

Rows in the first three figures retain the source order: CISS, T2w, FLASH.
Atlas columns retain DKT, Destrieux, Glasser, Schaefer400, von Economo, Julich,
Brainnetome. The MRI comparison additionally includes the original MRI column.
The two surface screenshots do not identify the mesh type, so the captions use
neutral view descriptions rather than assigning white/pial identities.

The volumetric viewer's mirrored-display and overlay-smoothing notes remain in
the image. Its magenta/unknown-LUT legend is retained in the new footer and
caption. Cropping removes desktop/player elements, not scientific content.
These are supplied visual examples, not a new accuracy evaluation or a claim of
Docker/SIF numerical equivalence.

See `figure_manifest.json` for source hashes, crop boxes and output hashes.
Recreate with `python scripts/docs/prepare_landing_figures.py SOURCE_DIR`
(Pillow and a DejaVu Sans font are required). The script verifies byte-identical
retained pixels after writing the PNGs. Only headers/footer areas are added.
