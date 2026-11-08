#!/usr/bin/env python3
"""Prepare the four supplied scientific screenshots without resampling anatomy.

Usage: python scripts/docs/prepare_landing_figures.py /path/to/screenshots
Requires Pillow. Input PNGs are identified by the exact names in SOURCES.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SOURCES = [
    ("7.51.51", "01_volume_atlas_comparison.png", (2, 2, 2046, 795)),
    ("7.53.45", "02_surface_parcellations_view1.png", (0, 0, 2040, 544)),
    ("7.54.18", "03_surface_parcellations_view2.png", (0, 0, 2040, 525)),
    ("7.58.29", "04_antemortem_postmortem_registration.png", (0, 12, 2048, 890)),
]
ATLAS_NAMES = ["DKT", "Destrieux", "Glasser\nHCP-MMP1", "Schaefer400\n17 networks", "von Economo", "Julich", "Brainnetome"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "docs/source/_static/examples")
    parser.add_argument("--font", type=Path, default=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(args.font), 23)
    small_font = ImageFont.truetype(str(args.font), 18)
    records = []
    for timestamp, output_name, box in SOURCES:
        matches = list(args.source_dir.glob(f"Screenshot 2026-11-07 at {timestamp}*PM.png"))
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one screenshot for {timestamp}, found {matches}")
        source = matches[0]
        original = Image.open(source).convert("RGB")
        crop = original.crop(box)
        offset = (0, 0)
        result = crop
        if output_name.startswith(("02_", "03_")):
            # Add labels above the original pixels, leaving the anatomy unchanged.
            offset = (0, 76)
            result = Image.new("RGB", (crop.width, crop.height + 76), original.getpixel((0, 0)))
            result.paste(crop, offset)
            draw = ImageDraw.Draw(result)
            for center, label in zip([224, 504, 784, 1064, 1344, 1624, 1904], ATLAS_NAMES):
                draw.multiline_text((center, 33), label, font=font, fill="#24202d", anchor="mm", align="center", spacing=4)
        elif output_name.startswith("01_"):
            # Replace the player footer with the scientifically relevant legend.
            result = Image.new("RGB", (crop.width, crop.height + 37), (10, 9, 14))
            result.paste(crop, (0, 0))
            ImageDraw.Draw(result).text((82, crop.height + 8), "Magenta: unresolved lookup-table IDs in the supplied rendering.", font=small_font, fill="#d980e3")
        output = args.output_dir / output_name
        result.save(output, optimize=True, dpi=(300, 300))
        saved = Image.open(output).convert("RGB")
        region = saved.crop((offset[0], offset[1], offset[0] + crop.width, offset[1] + crop.height))
        if region.tobytes() != crop.tobytes():
            raise AssertionError(f"Scientific pixels changed: {output_name}")
        records.append({"source": source.name, "source_sha256": sha(source), "source_pixels": list(original.size), "crop_box": list(box), "output": output_name, "output_sha256": sha(output), "output_pixels": list(saved.size), "content_offset": list(offset), "scientific_pixels_preserved": True})
        print(f"{output_name}: {saved.width} x {saved.height}; crop pixels preserved")
    manifest = {"method": "Lossless rectangular cropping with added atlas headings or a retained scientific legend. No interpolation, sharpening, denoising, generative enhancement, relabeling, or anatomical edits. PNG DPI metadata does not increase resolution.", "figures": records}
    (args.output_dir / "figure_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
