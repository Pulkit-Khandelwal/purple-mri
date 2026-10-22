"""Validate host inputs and construct Docker argv without shell interpolation."""
from pathlib import Path
import re

from .workflows import validate_stages

SAFE_CASE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*_0000\.nii\.gz\Z")


def host_path(value):
    path = Path(value).expanduser().resolve()
    if any(c in str(path) for c in (",", "\n", "\r")):
        raise ValueError("Docker mount paths must not contain commas or newlines.")
    return path


def overlaps(a, b):
    return a == b or a in b.parents or b in a.parents


def validate_run(args):
    validate_stages(args.stages)
    source, output = host_path(args.input), host_path(args.output)
    if not source.is_dir():
        raise ValueError(f"Input directory does not exist: {source}")
    if overlaps(source, output):
        raise ValueError("Input and output must be separate, non-nested directories.")
    files = sorted(source.glob("*.nii.gz"))
    if not files:
        raise ValueError("No input *.nii.gz files found.")
    if any(not f.is_file() or f.stat().st_size == 0 or not SAFE_CASE.fullmatch(f.name) for f in files):
        raise ValueError("Use nonempty single-channel files named subject_0000.nii.gz (letters, digits, dots, _ and - only).")
    if any(source not in f.resolve().parents for f in files):
        raise ValueError("Input symlinks must resolve within the mounted input directory.")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Output must be new or empty; existing results are never overwritten.")
    if "exvivo_surface" in args.stages:
        if args.hemi not in ("lh", "rh"):
            raise ValueError("Surface processing requires --hemi lh or --hemi rh.")
        if not args.license:
            raise ValueError("Surface processing requires --license /path/to/license.txt.")
        license_path = host_path(args.license)
        if not license_path.is_file() or license_path.stat().st_size == 0:
            raise ValueError("FreeSurfer license must be an existing nonempty file.")
        if args.stages == ["exvivo_surface"] and not args.segmentation:
            raise ValueError("Surface-only processing requires --segmentation pointing to corrected Purple 10-label files.")
    if args.segmentation:
        if args.stages != ["exvivo_surface"]:
            raise ValueError("--segmentation is only supported with surface-only processing.")
        segmentation = host_path(args.segmentation)
        if not segmentation.is_dir():
            raise ValueError("Segmentation directory does not exist.")
        if overlaps(output, segmentation):
            raise ValueError("Segmentation and output directories must not overlap.")
        for f in files:
            seg = segmentation / (f.name.removesuffix("_0000.nii.gz") + ".nii.gz")
            if not seg.is_file() or seg.stat().st_size == 0:
                raise ValueError(f"Missing or empty corrected segmentation: {seg.name}")
            if segmentation not in seg.resolve().parents:
                raise ValueError("Segmentation symlinks must resolve within their mounted directory.")
    return source, output


def docker_command(args, image=None):
    source, output = validate_run(args)
    cmd = ["docker", "run", "--rm", "--shm-size=8g"]
    if any(stage != "exvivo_surface" for stage in args.stages):
        cmd += ["--gpus", args.gpus]
    cmd += ["--mount", f"type=bind,src={source},dst=/inputs,readonly",
            "--mount", f"type=bind,src={output},dst=/outputs"]
    environment = {
        "EXVIVO_INPUT_DIR": "/inputs",
        "EXVIVO_DL_OUTPUT_DIR": "/outputs/exvivo_dl",
        "EXVIVO_SURFACE_OUTPUT_DIR": "/outputs/exvivo_surface",
        "EXVIVO_MODEL_OUTPUT_DIR": "/outputs/predictions",
        "EXVIVO_TIMING_DIR": "/outputs/timings",
        "EXVIVO_THREADS": str(args.threads),
        "NO_FSFAST": "1",
    }
    if args.hemi:
        environment["EXVIVO_HEMI"] = args.hemi
    if "exvivo_surface" in args.stages:
        cmd += ["--mount", f"type=bind,src={host_path(args.license)},dst=/license.txt,readonly"]
        environment["FS_LICENSE"] = "/license.txt"
    if args.segmentation:
        cmd += ["--mount", f"type=bind,src={host_path(args.segmentation)},dst=/segmentations,readonly"]
        environment["EXVIVO_SEGM_DIR"] = "/segmentations"
    for key, value in environment.items():
        cmd += ["--env", f"{key}={value}"]
    return cmd + ["--entrypoint", "/bin/bash", image or args.image,
                  "/src/commands_nnunet_inference.sh", *args.stages]
