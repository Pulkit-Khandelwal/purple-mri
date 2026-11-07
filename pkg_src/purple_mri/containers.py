"""Validate host paths and construct the v1.2.0 Docker argv without a shell."""
from pathlib import Path
import re

from .workflows import MODELS, validate_stages

SAFE_CASE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*_0000\.nii\.gz\Z")


def host_path(value):
    path = Path(value).expanduser().resolve()
    if any(c in str(path) for c in (",", "\n", "\r")):
        raise ValueError("Docker mount paths must not contain commas or newlines.")
    return path


def overlaps(a, b):
    return a == b or a in b.parents or b in a.parents


def require_file(path, root):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty required file: {path}")
    if root not in path.resolve().parents:
        raise ValueError(f"File must resolve inside its mounted directory: {path}")


def effective_contrast(args):
    return args.contrast or ("flash" if args.stages == ["exvivo_flash_gm_wm"] else None)


def validate_run(args, locked=False):
    validate_stages(args.stages)
    stage = args.stages[0]
    individual = stage in MODELS
    if not individual and not args.contrast:
        raise ValueError("Pipeline stages require --contrast t2w, ciss, flash or t2star.")
    if stage == "exvivo_flash_gm_wm" and effective_contrast(args) not in ("flash", "t2star"):
        raise ValueError("Task278 requires --contrast flash or t2star.")
    if args.segmentation:
        raise ValueError("v1.2.0 uses --dl-dir pointing to the complete DL root containing "
                         "11_final_merged and 12_surface_labels; replace --segmentation.")
    if args.resume and (individual or args.preflight_only):
        raise ValueError("--resume applies to processing runs of pipeline stages.")
    if individual and (args.save_qc_volumes or args.max_roi_voxels != 64_000_000):
        raise ValueError("Merge QC/ROI options apply to pipeline stages, not individual models.")
    source, output = host_path(args.input), host_path(args.output)
    if not source.is_dir():
        raise ValueError(f"Input directory does not exist: {source}")
    if overlaps(source, output):
        raise ValueError("Input and output must be separate, non-nested directories.")
    files = sorted(source.glob("*.nii.gz"))
    if not files:
        raise ValueError("No input *.nii.gz files found.")
    if any(not f.is_file() or f.stat().st_size == 0 or not SAFE_CASE.fullmatch(f.name) for f in files):
        raise ValueError("Use nonempty single-channel files named subject_0000.nii.gz "
                         "(letters, digits, dots, _ and - only).")
    for f in files:
        require_file(f, source)
    if args.resume:
        if not (output / "purple_run.json").is_file():
            raise ValueError("--resume requires an existing v1.2.0 CLI run with purple_run.json.")
    elif output.exists() and (not output.is_dir() or any(
            p.name != ".purple_cli.lock" or not locked for p in output.iterdir())):
        raise ValueError("Output must be new or empty; use --resume only for a matching CLI run.")
    surface = "exvivo_surface" in args.stages
    atlas = stage == "exvivo_atlas_merge"
    if surface or atlas:
        if args.hemi not in ("lh", "rh"):
            raise ValueError("Surface/atlas processing requires --hemi lh or --hemi rh.")
        if not args.license:
            raise ValueError("Surface/atlas processing requires --license /path/to/license.txt.")
    if args.license:
        license_path = host_path(args.license)
        if not license_path.is_file() or license_path.stat().st_size == 0:
            raise ValueError("FreeSurfer license must be an existing nonempty file.")
    if stage in ("exvivo_surface", "exvivo_atlas_merge", "exvivo_merge") and not args.dl_dir:
        raise ValueError("This stage requires --dl-dir pointing to the existing complete DL root.")
    if args.dl_dir and stage not in ("exvivo_surface", "exvivo_atlas_merge", "exvivo_merge"):
        raise ValueError("--dl-dir is for standalone surface/atlas/merge stages; DL inference writes OUTPUT/dl.")
    if atlas and not args.surface_dir:
        raise ValueError("Atlas-only processing requires --surface-dir with existing v1.2.0 projections.")
    if args.surface_dir and not atlas:
        raise ValueError("--surface-dir is only for exvivo_atlas_merge.")
    mounted = [source, output]
    for value in (args.dl_dir, args.surface_dir):
        if not value:
            continue
        root = host_path(value)
        if not root.is_dir():
            raise ValueError(f"Reuse directory does not exist: {root}")
        if any(overlaps(root, other) for other in mounted):
            raise ValueError("Input, output, DL reuse and surface reuse directories must not overlap.")
        mounted.append(root)
    if args.dl_dir:
        dl = host_path(args.dl_dir)
        required = ["11_final_merged", "12_surface_labels"]
        if stage == "exvivo_merge":
            required = ["05_purple_corrected", "06_mtl", "07_subcortical",
                        "13_flash_task278" if args.contrast in ("flash", "t2star") else "03_topology_prediction"]
        for f in files:
            case = f.name.removesuffix("_0000.nii.gz")
            for folder in required:
                require_file(dl / folder / (case + ".nii.gz"), dl)
            if atlas:
                root = host_path(args.surface_dir)
                for rel in ("qc/surface_provenance.json", "mri/aseg.mgz",
                            f"surf/{args.hemi}.white", f"surf/{args.hemi}.pial",
                            f"label/{args.hemi}.cortex.label"):
                    require_file(root / case / rel, root)
    return source, output


def docker_command(args, image=None):
    source, output = validate_run(args)
    cmd = ["docker", "run", "--rm", "--shm-size=8g"]
    if not args.preflight_only and (args.stages[0] in MODELS or args.stages[0] in ("exvivo_dl", "exvivo_all")):
        cmd += ["--gpus", args.gpus]
    cmd += ["--mount", f"type=bind,src={source},dst=/input,readonly",
            "--mount", f"type=bind,src={output},dst=/output"]
    dl, surface = "/output/dl", "/output/surface"
    if args.dl_dir:
        # Surface checkpoints and tissue merges write into the reused DL root.
        read_only = ",readonly" if args.stages == ["exvivo_atlas_merge"] else ""
        cmd += ["--mount", f"type=bind,src={host_path(args.dl_dir)},dst=/reuse_dl{read_only}"]
        dl = "/reuse_dl"
    if args.surface_dir:
        cmd += ["--mount", f"type=bind,src={host_path(args.surface_dir)},dst=/reuse_surface,readonly"]
        surface = "/reuse_surface"
    environment = {
        "EXVIVO_INPUT_DIR": "/input", "EXVIVO_DL_OUTPUT_DIR": dl,
        "EXVIVO_SURFACE_OUTPUT_DIR": surface,
        "EXVIVO_ATLAS_OUTPUT_DIR": "/output/atlases",
        "EXVIVO_MODEL_OUTPUT_DIR": "/output/predictions",
        "EXVIVO_TIMING_DIR": "/output/timings",
        "EXVIVO_THREADS": str(args.threads), "NO_FSFAST": "1",
    }
    if args.hemi:
        environment["EXVIVO_HEMI"] = args.hemi
    if args.license:
        cmd += ["--mount", f"type=bind,src={host_path(args.license)},dst=/license.txt,readonly"]
        environment["FS_LICENSE"] = "/license.txt"
    for key, value in environment.items():
        cmd += ["--env", f"{key}={value}"]
    pipeline = [*args.stages, "--threads", str(args.threads)]
    if effective_contrast(args):
        pipeline += ["--contrast", effective_contrast(args)]
    for option in ("resume", "preflight_only", "save_qc_volumes"):
        if getattr(args, option):
            pipeline.append("--" + option.replace("_", "-"))
    pipeline += ["--max-roi-voxels", str(args.max_roi_voxels)]
    return cmd + ["--entrypoint", "/bin/bash", image or args.image,
                  "/src/commands_nnunet_inference.sh", *pipeline]
