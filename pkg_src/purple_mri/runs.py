"""Serialize CLI attempts, retain provenance and validate explicit resumes."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid
import subprocess

from . import __version__
from .containers import effective_contrast, host_path, validate_run
from .lifecycle import CONTROL_TIMEOUT, RUN_LABEL, inspect_owned, save_record


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def context(args, image):
    source = host_path(args.input)
    return {
        "schema": 1, "package_version": __version__, "image_id": image["Id"],
        "stages": args.stages, "contrast": effective_contrast(args), "hemisphere": args.hemi,
        "input": str(source), "output": str(host_path(args.output)),
        "inputs_sha256": {f.name: sha(f) for f in sorted(source.glob("*.nii.gz"))},
        "dl_dir": str(host_path(args.dl_dir)) if args.dl_dir else None,
        "surface_dir": str(host_path(args.surface_dir)) if args.surface_dir else None,
        "threads": args.threads, "save_qc_volumes": args.save_qc_volumes,
        "max_roi_voxels": args.max_roi_voxels, "preflight_only": args.preflight_only,
    }


@contextmanager
def locked(path):
    # Import lazily: help, models and dry-run remain usable without POSIX locking.
    import fcntl
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(f"Another CLI process holds the run lock: {path}") from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


@contextmanager
def reuse_lock(args):
    """One writer per reused DL root for this user, even across output folders."""
    if not args.dl_dir or args.stages == ["exvivo_atlas_merge"] or args.preflight_only:
        yield
        return
    root = Path(tempfile.gettempdir()) / ("purple-mri-locks-" + str(os.getuid()))
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink() or root.stat().st_uid != os.getuid() or root.stat().st_mode & 0o077:
        raise ValueError(f"Expected a private lock directory owned by this user: {root}")
    key = hashlib.sha256(str(host_path(args.dl_dir)).encode()).hexdigest()
    with locked(root / (key + ".lock")):
        yield


def ensure_previous_stopped(old):
    """The CLI may have been killed while its container kept running."""
    if not old.get("run_id"):
        return
    found = subprocess.run([
        "docker", "container", "ls", "--all", "--no-trunc",
        "--filter", "label=" + RUN_LABEL + "=" + old["run_id"], "--format", "{{.ID}}"],
        check=True, capture_output=True, text=True, timeout=CONTROL_TIMEOUT)
    ids = found.stdout.split()
    if not ids:
        return
    expected = old.get("container_id")
    if len(ids) != 1 or (expected and ids[0] != expected):
        raise ValueError("Previous container identity is ambiguous; inspect it before resuming.")
    data = inspect_owned(old["container_name"], old["run_id"], old["image_id"], ids[0])
    state = data["State"]
    if state.get("Running") or state.get("Status") not in ("exited", "dead", "created"):
        raise ValueError("The previous container is still active or unconfirmed. Stop/check it before --resume.")


@contextmanager
def run_record(args, image):
    _, output = validate_run(args)
    output.mkdir(parents=True, exist_ok=True)
    with locked(output / ".purple_cli.lock"), reuse_lock(args):
        validate_run(args, locked=True)
        provenance = output / "purple_run.json"
        current = context(args, image)
        if args.resume:
            old_text = provenance.read_text()
            old = json.loads(old_text)
            if old.get("request") != current:
                raise ValueError("Resume inputs, image or processing options differ. Use the original "
                                 "command/options or choose a new output directory.")
            ensure_previous_stopped(old)
            history = output / "cli_history"
            history.mkdir(exist_ok=True)
            saved = history / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_") + uuid.uuid4().hex + ".json")
            saved.write_text(old_text)
        record = {
            "package_version": __version__, "image": args.image, "image_id": image["Id"],
            "repo_digests": image.get("RepoDigests", []), "stages": args.stages,
            "contrast": effective_contrast(args), "hemisphere": args.hemi,
            "kind": "preflight" if args.preflight_only else "processing",
            "started_utc": datetime.now(timezone.utc).isoformat(), "exit_code": None,
            "request": current,
        }
        if args.resume:
            record["previous_attempt"] = str(saved.relative_to(output))
        save_record(provenance, record)
        yield provenance, record
