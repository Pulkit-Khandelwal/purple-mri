#!/usr/bin/env python3
"""Measure local thickness from dot labels and regional tissue segmentations."""

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path

import numpy as np

from dots_common import (HERE, load_volume, read_labels, read_manifest, safe_name,
                         same_grid, select_labels, write_csv)

BINARIES = ["c3d", "cmrep_vskel", "mesh_smooth_curv", "qvoronoi",
            "skel_tetra_max_thick_sphere", "tetfill", "vtklevelset"]
FIELDS = ["specimen_id", "anatomical_level", "dot_label", "region", "layer",
          "thickness_mm", "radius_mm", "status", "qc_status", "notes"]


def binary_paths(directory=None):
    system = {"Linux": "linux", "Darwin": "macos"}.get(platform.system())
    if not system and directory is None and not os.environ.get("DOTS_BIN_DIR"):
        raise ValueError("Unsupported platform; use Linux or macOS")
    directory = Path(directory or os.environ.get("DOTS_BIN_DIR") or HERE / "binaries" / system).resolve()
    binaries = {name: directory / name for name in BINARIES}
    if os.environ.get("QVORONOI_BINARY"):
        binaries["qvoronoi"] = Path(os.environ["QVORONOI_BINARY"]).resolve()
    missing = [str(path) for path in binaries.values() if not path.is_file() or not os.access(path, os.X_OK)]
    if missing:
        raise ValueError("Missing or non-executable binaries:\n" + "\n".join(missing))
    return binaries


def binary_manifest(binaries):
    result = {}
    for name, path in binaries.items():
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        result[name] = {"path": str(path), "sha256": digest}
    return result


def exact_file(root, basename):
    """Match a full basename recursively; ambiguity is an error, never 'last file wins'."""
    matches = sorted(path for path in Path(root).rglob("*")
                     if path.is_file() and path.name.lower() == basename.lower())
    if len(matches) > 1:
        raise ValueError(f"Ambiguous filename {basename}: " + ", ".join(map(str, matches)))
    return matches[0] if matches else None


def segmentation_path(root, specimen, region):
    # Preserve the original precedence while removing private naming heuristics.
    for suffix, kind in [("manualedit", "label"), ("pancake", "levelset"), ("combined", "label")]:
        path = exact_file(root, f"{specimen}_{suffix}_{region}.nii.gz")
        if path:
            return path, kind
    return None, None


def parse_radius(text):
    """Preserve the original convention: fourth whitespace field on a Radius line."""
    lines = [line for line in text.splitlines() if "Radius" in line]
    if len(lines) != 1:
        raise ValueError("Expected exactly one Radius line in sphere output")
    fields = lines[0].split()
    try:
        radius = float(fields[3])
    except (IndexError, ValueError) as exc:
        raise ValueError("Sphere output does not contain a numeric fourth Radius field") from exc
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("Sphere radius must be finite and positive")
    return radius


class Runner:
    def __init__(self, binaries, log):
        self.binaries, self.log = binaries, log
        self.environment = os.environ.copy()
        directories = dict.fromkeys(str(path.parent) for path in binaries.values())
        self.environment["PATH"] = os.pathsep.join(directories) + os.pathsep + self.environment.get("PATH", "")
        self.environment["QVORONOI_BINARY"] = str(binaries["qvoronoi"])

    def run(self, tool, *arguments, stdout_file=None, outputs=()):
        command = [str(self.binaries[tool]), *map(str, arguments)]
        self.log.write("$ " + shlex.join(command) + "\n")
        self.log.flush()
        # shell=False protects paths containing spaces or shell metacharacters.
        if stdout_file:
            with Path(stdout_file).open("w") as output:
                subprocess.run(command, check=True, stdout=output, stderr=self.log, env=self.environment)
        else:
            subprocess.run(command, check=True, stdout=self.log, stderr=self.log, env=self.environment)
        for path in outputs:
            if not Path(path).is_file() or Path(path).stat().st_size == 0:
                raise ValueError(f"{tool} did not create a nonempty output: {path}")


def compute(runner, source, kind, seg_label, dots, number, prefix):
    """Issue the original numerical pipeline, with explicit expected outputs."""
    files = {key: Path(f"{prefix}_{suffix}") for key, suffix in {
        "binary": "binary.nii.gz", "raw": "bndmesh_raw.vtk", "smooth": "bndmesh_smooth.vtk",
        "skeleton": "skeleton.vtk", "tetra": "skeltetra.vtk", "radius": "thkmap.nii.gz",
        "center": "ctrmap.nii.gz", "dot": "dotbin.nii.gz", "dotmesh": "dotmesh.vtk",
        "dot_radius": "dot_thkmap.nii.gz", "dot_center": "dot_ctrmap.nii.gz",
        "sphere": "sphere.vtk", "text": "thkmax.txt"}.items()}
    run = runner.run
    if kind == "levelset":
        run("c3d", source, "-thresh", "-inf", 0, 1, 0, "-type", "uchar", "-o", files["binary"], outputs=[files["binary"]])
        run("vtklevelset", source, files["raw"], "0.0", outputs=[files["raw"]])
    else:
        # A binary mask is explicitly requested with kind=binary; do not guess
        # whether a label value of 1 is tissue or a particular landmark.
        value = 1 if kind == "binary" else seg_label
        run("c3d", source, "-thresh", value, value, 1, 0, "-type", "uchar", "-o", files["binary"], outputs=[files["binary"]])
        run("vtklevelset", files["binary"], files["raw"], "0.5", outputs=[files["raw"]])
    run("mesh_smooth_curv", "-mu", "-0.51", "-lambda", "0.5", "-iter", 200,
        files["raw"], files["smooth"], outputs=[files["smooth"]])
    run("cmrep_vskel", "-Q", runner.binaries["qvoronoi"], "-e", 10, "-p", "1.2", "-d",
        files["tetra"], files["smooth"], files["skeleton"], outputs=[files["tetra"], files["skeleton"]])
    run("tetfill", "-c", "VoronoiRadius", files["tetra"], files["binary"], files["radius"], outputs=[files["radius"]])
    run("tetfill", "-c", "VoronoiCenter", files["tetra"], files["binary"], files["center"], outputs=[files["center"]])
    run("c3d", dots, "-thresh", number, number, 1, 0, "-type", "uchar", "-o", files["dot"], outputs=[files["dot"]])
    run("vtklevelset", files["dot"], files["dotmesh"], "0.5", outputs=[files["dotmesh"]])
    # Retain the original c3d dilation token and nearest-neighbor reslicing.
    run("c3d", files["radius"], "-dup", files["dot"], "-int", 0, "-dilate", 1, "1x1x1",
        "-reslice-identity", "-times", "-o", files["dot_radius"], outputs=[files["dot_radius"]])
    run("c3d", "-mcs", files["center"], files["dot"], "-int", 0, "-dilate", 1, "1x1x1",
        "-popas", "D", "-foreach", "-dup", "-push", "D", "-reslice-identity", "-times",
        "-endfor", "-omc", files["dot_center"], outputs=[files["dot_center"]])
    run("skel_tetra_max_thick_sphere", files["dot_radius"], files["dot_center"], files["sphere"],
        stdout_file=files["text"], outputs=[files["sphere"], files["text"]])
    radius = parse_radius(files["text"].read_text())
    return radius, 2.0 * radius


def run_subject(args, labels, binaries, provenance):
    specimen = safe_name(args.specimen)
    destination = Path(args.work_root) / "thickness" / specimen
    destination.mkdir(parents=True, exist_ok=False)
    dots = Path(args.dot_file or Path(args.dots_dir or Path(args.root_dir) / "dots") / f"{specimen}_PMDots.nii.gz").resolve()
    rows = []
    (destination / "run.json").write_text(json.dumps({
        "specimen_id": specimen, "dots_file": str(dots), "segmentation_root": str(Path(args.root_dir).resolve()),
        "labels": labels, "binaries": provenance, "assume_mm": args.assume_mm,
        "platform": platform.platform(), "python": sys.version,
        "parameters": {"smoothing_mu": -0.51, "smoothing_lambda": 0.5, "smoothing_iterations": 200,
                       "skeleton_e": 10, "skeleton_p": 1.2, "dot_dilation_token": "1x1x1"},
    }, indent=2) + "\n")
    try:
        if not args.seg_file and not Path(args.root_dir).is_dir():
            raise ValueError(f"Segmentation directory does not exist: {args.root_dir}")
        dots_image, dots_data, dot_notes = load_volume(dots, args.assume_mm, discrete=True)
        dot_error = None
    except (ValueError, OSError) as exc:
        dot_error = str(exc)
    for number, region in labels:
        directory = destination / region
        directory.mkdir()
        row = dict(specimen_id=specimen, anatomical_level=args.anatomical_level,
                   dot_label=number, region=region, layer=args.layer,
                   thickness_mm="", radius_mm="", status="error", qc_status="unavailable", notes="")
        rows.append(row)
        details = {"dots_file": str(dots)}
        try:
            if dot_error:
                raise ValueError(dot_error)
            dot_mask = dots_data == number
            if not dot_mask.any():
                row.update(status="missing_dot", notes="Dot label is absent")
                continue
            if args.seg_file:
                source, kind = Path(args.seg_file).resolve(), args.seg_kind
            else:
                source, kind = segmentation_path(args.root_dir, specimen, region)
            if source is None:
                row.update(status="missing_segmentation", notes="No matching regional segmentation")
                continue
            details.update(segmentation_file=str(source.resolve()), segmentation_kind=kind)
            image, data, seg_notes = load_volume(source, args.assume_mm, discrete=kind != "levelset")
            same_grid(dots_image, image)
            seg_label = args.seg_label if args.seg_label is not None else number
            details["segmentation_label"] = 1 if kind == "binary" else seg_label
            if kind == "binary" and not np.isin(data, [0, 1]).all():
                raise ValueError("--seg-kind binary requires only 0 and 1")
            if kind == "levelset" and not (np.any(data < 0) and np.any(data > 0)):
                raise ValueError("Level-set input must contain negative interior and positive exterior values")
            tissue = data <= 0 if kind == "levelset" else data == (1 if kind == "binary" else seg_label)
            if not tissue.any():
                raise ValueError("Selected segmentation label is absent")
            overlap = tissue[dot_mask]
            if not overlap.any():
                raise ValueError("Dot does not intersect the selected tissue")
            if np.array_equal(tissue, dot_mask):
                raise ValueError("Segmentation contains only the dot voxels; provide a surrounding tissue mask")
            notes = list(dict.fromkeys(dot_notes + seg_notes))
            if not overlap.all():
                notes.append("partial_dot_overlap")
            if any(np.take(tissue, edge, axis=axis).any() for axis in range(3) for edge in (0, -1)):
                notes.append("tissue_touches_image_boundary")
            with (directory / "commands.log").open("w") as log:
                radius, thickness = compute(Runner(binaries, log), source, kind, seg_label,
                                            dots, number, directory / f"{specimen}_{region}")
            row.update(radius_mm=radius, thickness_mm=thickness, status="ok",
                       qc_status="needs_review", notes=";".join(notes))
        except (ValueError, OSError, subprocess.CalledProcessError) as exc:
            row["notes"] = str(exc)
            print(f"ERROR: {specimen}/{region}: {exc}", file=sys.stderr)
        finally:
            (directory / "result.json").write_text(json.dumps({**row, **details}, indent=2) + "\n")
            print(f"{specimen}/{region}: {row['status']}", file=sys.stderr)
    write_csv(destination / "results.csv", rows, FIELDS)
    return rows


def common_options(parser):
    parser.add_argument("--labels", type=Path, default=HERE / "dots.txt")
    parser.add_argument("--bin-dir", type=Path)
    parser.add_argument("--assume-mm", action="store_true")
    parser.add_argument("--anatomical-level", default="")
    parser.add_argument("--layer", default="")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command, aliases in [("dot", ["dot_thickness"]), ("subj", ["subj_thickness"])]:
        entry = sub.add_parser(command, aliases=aliases)
        entry.add_argument("root_dir", type=Path, help="Regional-segmentation directory")
        entry.add_argument("specimen")
        if command == "dot":
            entry.add_argument("dot")
        entry.add_argument("work_root", type=Path)
        entry.add_argument("--dot-file", type=Path)
        entry.add_argument("--dots-dir", type=Path)
        if command == "dot":
            entry.add_argument("--seg-file", type=Path)
            entry.add_argument("--seg-kind", choices=["label", "binary", "levelset"], default="label")
            entry.add_argument("--seg-label", type=int)
        else:
            entry.add_argument("--regions", nargs="+")
            entry.set_defaults(seg_file=None, seg_kind="label", seg_label=None)
        common_options(entry)
    batch = sub.add_parser("batch")
    batch.add_argument("--manifest", required=True, type=Path)
    batch.add_argument("--output-dir", required=True, type=Path)
    batch.add_argument("--regions", nargs="+")
    common_options(batch)
    table = sub.add_parser("stats_table")
    table.add_argument("work_root", type=Path)
    table.add_argument("--output", type=Path)
    check = sub.add_parser("check")
    check.add_argument("--bin-dir", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "stats_table":
            files = sorted((args.work_root / "thickness").glob("*/*/result.json"))
            if not files:
                raise ValueError("No result.json records found under work_root/thickness")
            rows = [{key: item.get(key, "") for key in FIELDS}
                    for item in (json.loads(path.read_text()) for path in files)]
            if args.output:
                write_csv(args.output, rows, FIELDS)
            else:
                writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            return 0
        binaries = binary_paths(args.bin_dir)
        if args.command == "check":
            for name, path in binaries.items():
                print(f"{name}: {path}")
            print("All seven executable files are available.")
            return 0
        provenance = binary_manifest(binaries)
        labels = read_labels(args.labels)
        labels = select_labels(labels, [args.dot] if args.command in ("dot", "dot_thickness") else args.regions)
        if args.command == "batch":
            manifest = read_manifest(args.manifest, ["specimen_id", "dots_file", "segmentation_dir"])
            for item in manifest:
                if (args.output_dir / "thickness" / item["specimen_id"]).exists():
                    raise ValueError("Output already exists; choose a fresh output directory")
            rows = []
            for item in manifest:
                subject_args = argparse.Namespace(**vars(args))
                subject_args.specimen = item["specimen_id"]
                subject_args.root_dir = Path(item["segmentation_dir"])
                subject_args.dot_file = Path(item["dots_file"])
                subject_args.dots_dir = None
                subject_args.work_root = args.output_dir
                subject_args.seg_file, subject_args.seg_kind, subject_args.seg_label = None, "label", None
                subject_args.anatomical_level = item.get("anatomical_level", "") or args.anatomical_level
                subject_args.layer = item.get("layer", "") or args.layer
                rows.extend(run_subject(subject_args, labels, binaries, provenance))
            write_csv(args.output_dir / "thickness.csv", rows, FIELDS)
        else:
            rows = run_subject(args, labels, binaries, provenance)
        return int(any(row["status"] == "error" for row in rows))
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
