"""Shared input validation for landmark-based thickness workflows."""

import csv
import re
from pathlib import Path

import nibabel as nib
import numpy as np

HERE = Path(__file__).resolve().parent


def safe_name(value):
    """Keep identifiers safe as single filename components; never guess aliases."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise ValueError(f"Invalid identifier {value!r}; use letters, digits, _, - or .")
    return value


def read_labels(path=HERE / "dots.txt"):
    """Read exact label/code pairs, rejecting duplicate IDs and case-folded names."""
    result = []
    ids, names = set(), set()
    for line in Path(path).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        number, name = line.split()
        number = int(number)
        safe_name(name)
        if not 1 <= number <= 65535 or number in ids or name.lower() in names:
            raise ValueError(f"Invalid or duplicate label: {line}")
        result.append((number, name))
        ids.add(number)
        names.add(name.lower())
    if not result:
        raise ValueError("The label map is empty")
    return result


def select_labels(labels, regions=None):
    if not regions:
        return labels
    lookup = {name.lower(): (number, name) for number, name in labels}
    if len({name.lower() for name in regions}) != len(regions):
        raise ValueError("Duplicate regions requested")
    try:
        return [lookup[name.lower()] for name in regions]
    except KeyError as exc:
        raise ValueError(f"Unknown region: {exc.args[0]}") from exc


def load_volume(path, assume_mm=False, discrete=False):
    """Require a 3D volume with usable spatial geometry and explicit mm units."""
    image = nib.load(str(path))
    if len(image.shape) != 3:
        raise ValueError(f"Expected a 3D volume: {path}")
    if not np.isfinite(image.affine).all() or abs(np.linalg.det(image.affine[:3, :3])) < 1e-12:
        raise ValueError(f"Invalid affine: {path}")
    unit = image.header.get_xyzt_units()[0]
    notes = []
    if unit != "mm":
        if unit == "unknown" and assume_mm:
            notes.append("unknown_units_assumed_mm")
        else:
            raise ValueError(f"Spatial units are {unit!r} in {path}; require mm. "
                             "Use --assume-mm only for unknown units known to be mm.")
    data = image.get_fdata(dtype=np.float32)
    if not np.isfinite(data).all():
        raise ValueError(f"Non-finite voxel values: {path}")
    if discrete and (np.any(data < 0) or not np.array_equal(data, np.rint(data))):
        raise ValueError(f"Expected nonnegative integer labels: {path}")
    return image, data, notes


def same_grid(first, second):
    if first.shape != second.shape or not np.allclose(first.affine, second.affine, atol=1e-4, rtol=0):
        raise ValueError("Dots and segmentation must have the same shape and affine; "
                         "align them explicitly before running this workflow")


def save_labels(data, reference, path):
    """Write integer labels without changing the image grid or header transforms."""
    header = reference.header.copy()
    header.set_data_dtype(np.uint16)
    header.set_slope_inter(1, 0)
    image = nib.Nifti1Image(data.astype(np.uint16), reference.affine, header)
    image.set_qform(reference.get_qform(), int(reference.header["qform_code"]))
    image.set_sform(reference.get_sform(), int(reference.header["sform_code"]))
    nib.save(image, str(path))


def write_csv(path, rows, fields):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_manifest(path, required):
    """Read a TSV; paths are relative to the manifest's parent directory."""
    path = Path(path).resolve()
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not set(required).issubset(reader.fieldnames or []):
            raise ValueError(f"Manifest requires columns: {', '.join(required)}")
        rows = list(reader)
    seen = set()
    for row in rows:
        for key in required:
            if not row.get(key, "").strip():
                raise ValueError(f"Empty manifest field: {key}")
        name = safe_name(row["specimen_id"])
        if name in seen:
            raise ValueError(f"Duplicate specimen_id in manifest: {name}")
        seen.add(name)
        for key in ("dots_file", "segmentation_file", "segmentation_dir"):
            if row.get(key):
                row[key] = str((path.parent / row[key]).resolve())
    if not rows:
        raise ValueError("Manifest has no specimen rows")
    return rows
