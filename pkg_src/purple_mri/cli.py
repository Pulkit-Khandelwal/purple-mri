"""Public CLI. Container images own scientific dependencies and model weights."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

from . import __version__
from .containers import docker_command, host_path, validate_run
from .lifecycle import execute_container
from .workflows import DEFAULT_IMAGE, MODELS, STAGES


def positive_int(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a positive integer")
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def image_ref(value):
    if not value or value.startswith("-") or any(c.isspace() for c in value):
        raise argparse.ArgumentTypeError("invalid container image reference")
    return value


def parser():
    p = argparse.ArgumentParser(prog="purple-mri", description="Purple ex vivo MRI workflow CLI")
    p.add_argument("--version", action="version", version=__version__)
    commands = p.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Run the current Docker workflow")
    run.add_argument("stages", nargs="+", choices=STAGES)
    run.add_argument("--input", required=True, help="Directory of subject_0000.nii.gz inputs")
    run.add_argument("--output", required=True, help="New or empty directory, separate from input")
    run.add_argument("--hemi", choices=("lh", "rh"))
    run.add_argument("--license", help="Host FreeSurfer license file")
    run.add_argument("--segmentation", help="Corrected Purple 10-label directory for surface-only runs")
    run.add_argument("--threads", type=positive_int, default=8)
    run.add_argument("--gpus", default="all", help="Docker GPU selector (default: all)")
    run.add_argument("--image", type=image_ref, default=DEFAULT_IMAGE)
    run.add_argument("--pull", action="store_true", help="Explicitly refresh the image before running")
    run.add_argument("--dry-run", action="store_true", help="Print argv without pulling, creating output, or running")
    pull = commands.add_parser("pull", help="Pull the published Docker image")
    pull.add_argument("--image", type=image_ref, default=DEFAULT_IMAGE)
    doctor = commands.add_parser("doctor", help="Check Docker access and local image; no inference")
    doctor.add_argument("--image", type=image_ref, default=DEFAULT_IMAGE)
    commands.add_parser("models", help="Show expected model selections; does not inspect image assets")
    legacy = commands.add_parser("legacy-surface", help="Compatibility launcher for the old RH-only native pipeline")
    for name in ("freesurfer", "output", "mri", "segmentation", "atlases"):
        legacy.add_argument(name)
    legacy.add_argument("threads", type=positive_int)
    legacy.add_argument("stats", help="GM/WM statistics file (not a hemisphere flag)")
    legacy.add_argument("--dry-run", action="store_true")
    return p


def checked(argv, **kwargs):
    return subprocess.run(argv, check=True, **kwargs)


def inspect_image(image):
    result = checked(["docker", "image", "inspect", image], capture_output=True, text=True)
    data = json.loads(result.stdout)[0]
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", data.get("Id", "")):
        raise ValueError("Docker did not return a valid immutable image ID.")
    return data


def run_container(args):
    command = docker_command(args)
    if args.dry_run:
        if args.pull:
            print(shlex.join(["docker", "pull", args.image]))
        print(shlex.join(command))
        return 0
    if not shutil.which("docker"):
        raise ValueError("Docker is not installed or not on PATH.")
    if args.pull:
        checked(["docker", "pull", args.image])
    image = inspect_image(args.image)
    command = docker_command(args, image["Id"])
    _, output = validate_run(args)
    output.mkdir(parents=True, exist_ok=True)
    record = {
        "package_version": __version__, "image": args.image, "image_id": image["Id"],
        "repo_digests": image.get("RepoDigests", []), "stages": args.stages,
        "hemisphere": args.hemi, "started_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": None,
    }
    provenance = output / "purple_run.json"
    # Exclusive creation prevents two CLI runs from using this output.
    with provenance.open("x") as stream:
        json.dump(record, stream, indent=2)
    return execute_container(command, provenance, record)


def legacy_surface(args):
    print("WARNING: legacy native scripts are RH-only and are not the current Docker pipeline. "
          "The seventh positional argument is the statistics file.", file=sys.stderr)
    values = [args.freesurfer, args.output, args.mri, args.segmentation, args.atlases, args.stats]
    paths = [str(host_path(value)) for value in values]
    if any(not re.fullmatch(r"/[A-Za-z0-9_./-]+", value) for value in paths):
        raise ValueError("Legacy scripts require paths without whitespace or shell metacharacters.")
    fs, out, mri, seg, atlas, stats = paths
    for directory in (fs, mri, seg, atlas):
        if not Path(directory).is_dir():
            raise ValueError(f"Missing legacy input directory: {directory}")
    if not Path(stats).is_file():
        raise ValueError("Legacy mode requires a GM/WM statistics file as argument seven.")
    scans = list(Path(mri).glob("*.nii.gz"))
    if not scans or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.nii\.gz", f.name) for f in scans):
        raise ValueError("Legacy input requires safely named *.nii.gz MRI files.")
    if any(not (Path(seg) / f.name).is_file() for f in scans):
        raise ValueError("Legacy MRI and segmentation filenames must match.")
    scripts = Path(__file__).resolve().parent / "scripts"
    command = ["bash", str(scripts / "run_surface_pipeline.sh"), fs, out, mri, seg, atlas, str(args.threads), stats]
    if args.dry_run:
        print(shlex.join(command))
        return 0
    env = os.environ.copy()
    env["PURPLE_PYTHON"] = sys.executable
    env["FREESURFER_HOME"] = fs
    env["PATH"] = fs + "/bin" + os.pathsep + env.get("PATH", "")
    return checked(command, env=env).returncode


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) == 7 and argv[0] not in ("run", "pull", "doctor", "models", "legacy-surface") and not argv[0].startswith("-"):
        argv.insert(0, "legacy-surface")
    p = parser()
    if not argv:
        p.print_help()
        return 0
    args = p.parse_args(argv)
    try:
        if args.command == "models":
            print("Expected selections for the updated image (not an asset availability check):")
            for name, (task, description) in MODELS.items():
                print(f"{name}\tTask{task}\t{description}")
            return 0
        if args.command == "run":
            return run_container(args)
        if args.command == "legacy-surface":
            return legacy_surface(args)
        if not shutil.which("docker"):
            raise ValueError("Docker is not installed or not on PATH.")
        if args.command == "pull":
            return checked(["docker", "pull", args.image]).returncode
        checked(["docker", "info"], capture_output=True, text=True)
        image = inspect_image(args.image)
        print(f"Docker is accessible. Local image: {args.image}\nImage ID: {image['Id']}")
        print("Host/image checks only; GPU, checkpoints and scientific outputs are not validated.")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"Command failed (exit {exc.returncode}): {shlex.join(exc.cmd)}", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 128 - exc.returncode if exc.returncode < 0 else exc.returncode
    except (OSError, ValueError, KeyError, IndexError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
