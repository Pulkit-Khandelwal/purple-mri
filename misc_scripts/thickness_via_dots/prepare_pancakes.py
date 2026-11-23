#!/usr/bin/env python3
"""Prepare one local tissue mask per labeled dot from an automated segmentation.

Supports one specimen or a TSV batch. The default box is centered on the
first dot voxel and extends 50 voxels on either side.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from dots_common import (HERE, load_volume, read_labels, read_manifest, safe_name, same_grid,
                         save_labels, select_labels, write_csv)

FIELDS = ["specimen_id", "dot_label", "region", "status", "notes", "output_file"]


def prepare(specimen, dots_file, segmentation_file, output_dir, labels,
            tissue_labels=None, all_nonzero=False, half_width=50,
            center="first", assume_mm=False):
    safe_name(specimen)
    if half_width < 1:
        raise ValueError("half_width must be positive")
    if bool(tissue_labels) == bool(all_nonzero):
        raise ValueError("Choose explicit tissue labels OR all_nonzero")
    if tissue_labels and any(label <= 0 for label in tissue_labels):
        raise ValueError("Tissue labels must be positive integers")
    dots_image, dots, notes_dots = load_volume(dots_file, assume_mm, discrete=True)
    seg_image, seg, notes_seg = load_volume(segmentation_file, assume_mm, discrete=True)
    same_grid(dots_image, seg_image)
    tissue = seg > 0 if all_nonzero else np.isin(seg, tissue_labels)
    if not tissue.any():
        raise ValueError("Selected tissue labels are absent from the segmentation")

    # A new subject directory prevents an earlier successful mask being reused
    # after a later run finds a missing dot or invalid segmentation.
    destination = Path(output_dir) / specimen
    destination.mkdir(parents=True, exist_ok=False)
    rows = []
    boxes = {}
    for number, name in labels:
        row = dict(specimen_id=specimen, dot_label=number, region=name,
                   status="missing_dot", notes="", output_file="")
        rows.append(row)
        positions = np.argwhere(dots == number)
        if not positions.size:
            continue
        # Optional centroid chooses the dot voxel nearest the centroid; it never
        # creates a new landmark in an unlabeled voxel.
        index = 0 if center == "first" else np.argmin(
            np.sum((positions - positions.mean(axis=0)) ** 2, axis=1))
        point = positions[index]
        lower = np.maximum(point - half_width, 0)
        upper = np.minimum(point + half_width, tissue.shape)
        slices = tuple(slice(int(lo), int(hi)) for lo, hi in zip(lower, upper))
        mask = np.zeros(tissue.shape, dtype=np.uint16)
        mask[slices] = tissue[slices].astype(np.uint16) * number
        boxes[name] = {"center_voxel": point.tolist(), "start": lower.tolist(),
                       "stop_exclusive": upper.tolist()}
        notes = list(dict.fromkeys(notes_dots + notes_seg))
        overlap = mask[dots == number] != 0
        if not overlap.any():
            row.update(status="dot_outside_tissue", notes="No original dot voxel intersects the local tissue mask")
            continue
        if not overlap.all():
            notes.append("partial_dot_overlap")
        if np.any(point - half_width < 0) or np.any(point + half_width > tissue.shape):
            notes.append("box_clipped_at_image_edge")
        # Retain full-size image geometry. Only the box contains tissue.
        filename = destination / f"{specimen}_manualedit_{name}.nii.gz"
        save_labels(mask, seg_image, filename)
        row.update(status="prepared_needs_review", notes=";".join(notes), output_file=str(filename.resolve()))

    write_csv(destination / "preparation.csv", rows, FIELDS)
    (destination / "preparation.json").write_text(json.dumps({
        "specimen_id": specimen, "dots_file": str(Path(dots_file).resolve()),
        "segmentation_file": str(Path(segmentation_file).resolve()),
        "tissue_labels": tissue_labels, "all_nonzero": all_nonzero,
        "half_width_voxels": half_width, "center": center, "assume_mm": assume_mm,
        "boxes": boxes, "labels": labels,
    }, indent=2) + "\n")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--specimen", help="Prepare one specimen")
    mode.add_argument("--manifest", type=Path, help="Prepare specimens listed in a TSV")
    parser.add_argument("--dots", type=Path)
    parser.add_argument("--segmentation", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("automated_pancakes"))
    tissue = parser.add_mutually_exclusive_group()
    tissue.add_argument("--tissue-labels", nargs="+", type=int)
    tissue.add_argument("--all-nonzero", action="store_true")
    parser.add_argument("--labels", type=Path, default=HERE / "dots.txt")
    parser.add_argument("--regions", nargs="+")
    parser.add_argument("--half-width", type=int, default=50)
    parser.add_argument("--center", choices=["first", "centroid"], default="first")
    parser.add_argument("--assume-mm", action="store_true")
    args = parser.parse_args()
    if args.manifest and any((args.dots, args.segmentation, args.tissue_labels, args.all_nonzero)):
        parser.error("With --manifest, specify image paths and tissue labels in the TSV")
    if args.specimen and (not args.dots or not args.segmentation or
                         not (args.tissue_labels or args.all_nonzero)):
        parser.error("--specimen requires --dots, --segmentation, and --tissue-labels or --all-nonzero")
    try:
        labels = select_labels(read_labels(args.labels), args.regions)
        if args.manifest:
            items = read_manifest(args.manifest,
                                  ["specimen_id", "dots_file", "segmentation_file", "tissue_labels"])
            for item in items:
                item["all_nonzero"] = item["tissue_labels"] == "nonzero"
                item["selected_labels"] = (None if item["all_nonzero"] else
                                           [int(value) for value in item["tissue_labels"].split(",")])
        else:
            items = [dict(specimen_id=args.specimen, dots_file=args.dots,
                          segmentation_file=args.segmentation,
                          selected_labels=args.tissue_labels, all_nonzero=args.all_nonzero)]
        # Check the full batch before creating any masks.
        if args.half_width < 1:
            raise ValueError("--half-width must be positive")
        for item in items:
            safe_name(item["specimen_id"])
            if (args.output_dir / item["specimen_id"]).exists():
                raise ValueError("Output already exists; choose a fresh output directory")
            if item["selected_labels"] and any(value <= 0 for value in item["selected_labels"]):
                raise ValueError("Tissue labels must be positive integers")
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    rows = []
    for item in items:
        try:
            result = prepare(item["specimen_id"], item["dots_file"], item["segmentation_file"],
                             args.output_dir, labels, item["selected_labels"], item["all_nonzero"],
                             args.half_width, args.center, args.assume_mm)
        except (ValueError, OSError) as exc:
            result = [dict(specimen_id=item["specimen_id"], dot_label=number, region=name,
                           status="error", notes=str(exc), output_file="") for number, name in labels]
        rows.extend(result)
        for row in result:
            print(f"{row['specimen_id']}/{row['region']}: {row['status']} {row['notes']}")
    if args.manifest:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(args.output_dir / "preparation.csv", rows, FIELDS)
    return int(any(row["status"] in ("error", "dot_outside_tissue") for row in rows))


if __name__ == "__main__":
    sys.exit(main())
