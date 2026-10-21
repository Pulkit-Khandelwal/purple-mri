#!/usr/bin/env bash
# PURPLE: prepared FS/PURPLE label-based registration, one case per call.
# UPenn: ex vivo -> in vivo. UMC: ex vivo -> in situ.
# Requires bash >= 3.2, greedy, c3d, Python 3, numpy, nibabel.
# See docs/source/registration.rst for the input contract and exception policy.
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  bash registration_exvivo_invivo_greedy_v3.sh \
    --cohort upenn|umc --hemi lh|rh \
    --fixed-labels FILE --moving-labels FILE --out-dir NEW_DIRECTORY \
    [--threads N] [--omit-hippocampus] [--moving-mri FILE] [--dry-run]

Inputs are PREPARED, single-hemisphere, nominal 1 mm NIfTI label maps:
  0 background; 1 GM; 2 putamen; 3 caudate; 4 pallidum; 5 thalamus;
  6 WM + amygdala + corpus callosum; 7 hippocampus.
The fixed and moving maps may have different grids. Header geometry must
describe the correct physical space. --hemi records laterality; it does not
extract a hemisphere or flip/remap an image.

--omit-hippocampus is ONLY for the documented UPenn exception. It requires
moving label 7 to be absent, fixed label 7 to be present, and labels 1-6 to
be nonempty in both maps. No other empty channel is omitted automatically.

--moving-mri optionally reslices an MRI already in the moving label map's
physical space, using LINEAR interpolation. It never affects registration.
--threads defaults to 8. --dry-run validates inputs and prints commands;
it requires Python dependencies but does not run c3d/greedy or create output.
Existing output directories are refused, including for --dry-run.
USAGE
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
cohort='' hemi='' fixed='' moving='' out='' moving_mri=''
threads=8 omit=0 dry=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cohort|--hemi|--fixed-labels|--moving-labels|--out-dir|--threads|--moving-mri)
            [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || die "Missing value for $1"
            case "$1" in
                --cohort) cohort=$2 ;; --hemi) hemi=$2 ;;
                --fixed-labels) fixed=$2 ;; --moving-labels) moving=$2 ;;
                --out-dir) out=$2 ;; --threads) threads=$2 ;;
                --moving-mri) moving_mri=$2 ;;
            esac
            shift 2 ;;
        --omit-hippocampus) omit=1; shift ;;
        --dry-run) dry=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) die "Unknown argument: $1 (use --help)" ;;
    esac
done
[[ "$cohort" == upenn || "$cohort" == umc ]] || die '--cohort must be upenn or umc'
[[ "$hemi" == lh || "$hemi" == rh ]] || die '--hemi must be lh or rh'
[[ -n "$fixed" && -n "$moving" && -n "$out" ]] || die 'Provide both label maps and --out-dir'
[[ "$threads" =~ ^[1-9][0-9]*$ ]] || die '--threads must be a positive integer'
[[ "$omit" == 0 || "$cohort" == upenn ]] || die '--omit-hippocampus is allowed only for UPenn'
command -v python3 >/dev/null 2>&1 || die 'python3 is required'
python3 -c 'import numpy, nibabel' 2>/dev/null || die 'Install Python dependencies: numpy and nibabel'
abspath() { python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$1"; }
fixed=$(abspath "$fixed"); moving=$(abspath "$moving"); out=$(abspath "$out")
if [[ -n "$moving_mri" ]]; then moving_mri=$(abspath "$moving_mri"); fi
[[ ! -e "$out" && ! -L "$out" ]] || die "Output already exists: $out; use a new directory"
if [[ "$dry" == 0 ]]; then
    command -v c3d >/dev/null 2>&1 || die 'c3d is not on PATH'
    command -v greedy >/dev/null 2>&1 || die 'greedy is not on PATH'
fi

manifest=$(mktemp "${TMPDIR:-/tmp}/purple-registration-v3.XXXXXX")
started=0
cleanup() {
    status=$?
    if [[ "$started" == 1 && "$status" != 0 ]]; then
        printf 'Run failed with exit status %s. Inspect run.log; rerun into a new directory.\n' "$status" > "$out/FAILED.txt"
        printf 'Registration failed. Log: %s/run.log\n' "$out" >&2
    fi
    rm -f "$manifest"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Validate before creating any outputs. Exact integers matter because c3d
# thresholds each class exactly. No upstream label identities are inferred.
python3 - "$fixed" "$moving" "$cohort" "$hemi" "$omit" "$threads" "$moving_mri" "$0" > "$manifest" <<'PY'
import hashlib, json, os, shutil, sys
from datetime import datetime, timezone
import nibabel as nib
import numpy as np

fixed, moving, cohort, hemi, omit, threads, mri, script = sys.argv[1:]
omit = bool(int(omit))
names = ['background', 'GM', 'PUT', 'CAUD', 'PALL', 'THAL', 'WM_AMYG_CC', 'HIPPO']
def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def inspect(path, labels=True):
    if not os.path.isfile(path):
        raise ValueError(f'Missing input: {path}')
    im = nib.load(path)
    if not isinstance(im, (nib.Nifti1Image, nib.Nifti2Image)) or len(im.shape) != 3:
        raise ValueError(f'Expected a 3D NIfTI image: {path}')
    if any(n <= 0 for n in im.shape):
        raise ValueError(f'Empty image dimensions: {path}')
    aff = im.affine
    if not np.isfinite(aff).all() or abs(np.linalg.det(aff[:3, :3])) < 1e-12:
        raise ValueError(f'Invalid physical-space affine: {path}')
    q, qc = im.get_qform(coded=True)
    s, sc = im.get_sform(coded=True)
    if not qc and not sc:
        raise ValueError(f'No coded qform or sform: {path}; establish geometry upstream')
    if qc and sc and not np.allclose(q, s, rtol=0, atol=1e-4):
        raise ValueError(f'Conflicting qform/sform: {path}; resolve upstream')
    spacing = np.asarray(im.header.get_zooms()[:3], dtype=float)
    units = im.header.get_xyzt_units()[0]
    if units not in ('mm', 'unknown'):
        raise ValueError(f'Expected millimeter geometry, found {units}: {path}')
    if not np.isfinite(spacing).all() or np.any(spacing <= 0):
        raise ValueError(f'Invalid voxel spacing: {path}')
    if not np.allclose(spacing, nib.affines.voxel_sizes(aff), rtol=0, atol=1e-4):
        raise ValueError(f'Header spacing disagrees with affine: {path}')
    data = np.asanyarray(im.dataobj)
    if not np.isfinite(data).all():
        raise ValueError(f'Nonfinite image values: {path}')
    result = dict(path=os.path.abspath(path), sha256=sha256(path), shape=list(im.shape),
                  spacing_mm=spacing.tolist(), affine=aff.tolist(),
                  spatial_units=units, orientation=list(nib.aff2axcodes(aff)))
    if units == 'unknown':
        print(f'WARNING: unspecified spatial units; assuming mm: {path}', file=sys.stderr)
    if labels:
        values, counts = np.unique(data, return_counts=True)
        if np.any(values != np.rint(values)) or np.any((values < 0) | (values > 7)):
            raise ValueError(f'Expected exact integer labels 0-7: {path}; raw aseg/DKT/10-label maps are invalid')
        result['label_counts'] = {str(k): int(counts[values == k].sum()) for k in range(8)}
        if not np.allclose(spacing, 1, rtol=0, atol=0.05):
            print(f'WARNING: grid is not nominal 1 mm ({spacing.tolist()}): {path}. '
                  'This deviates from the reported protocol; no resampling is performed.', file=sys.stderr)
    return result

try:
    f, m = inspect(fixed), inspect(moving)
    if os.path.samefile(fixed, moving):
        raise ValueError('Fixed and moving inputs must be distinct files')
    for k in range(1, 8):
        if f['label_counts'][str(k)] == 0:
            raise ValueError(f'Fixed label {k} ({names[k]}) is empty')
        if k <= 6 and m['label_counts'][str(k)] == 0:
            raise ValueError(f'Moving label {k} ({names[k]}) is empty')
    if omit:
        if cohort != 'upenn' or m['label_counts']['7'] != 0:
            raise ValueError('The UPenn exception requires absent moving hippocampus (label 7)')
    elif m['label_counts']['7'] == 0:
        raise ValueError('Moving label 7 (HIPPO) is empty; no automatic channel omission. '
                         'Use --omit-hippocampus only for the documented UPenn exception')
    tools = {}
    for name in ('greedy', 'c3d'):
        path = shutil.which(name)
        tools[name] = {'path': path, 'sha256': sha256(path) if path else None}
    result = dict(schema_version=1, status='validated',
                  created_utc=datetime.now(timezone.utc).isoformat(),
                  cohort=cohort, hemisphere=hemi,
                  fixed_context='in_vivo' if cohort == 'upenn' else 'in_situ',
                  moving_context='ex_vivo',
                  channels=list(range(1, 7 if omit else 8)),
                  channel_names={str(k): names[k] for k in range(1, 8)},
                  omit_hippocampus=omit, threads=int(threads),
                  fixed=f, moving=m, moving_mri=inspect(mri, labels=False) if mri else None,
                  software=dict(python=sys.version, numpy=np.__version__, nibabel=nib.__version__, **tools),
                  script_sha256=sha256(script),
                  protocol=dict(moments_metric='NCC 2x2x2', affine_dof=12,
                                affine_metric='NCC 2x2x2', affine_iterations='100x50x10',
                                deformable_metric='SSD', deformable_iterations='100x50x20',
                                smoothing=['8.0mm', '1.0mm'], stationary_velocity=True,
                                channel_weights='equal/default; no -w supplied',
                                label_interpolation='LABEL 0.2vox',
                                reslice_transform_arguments=['warp.nii.gz', 'affine.mat']))
    json.dump(result, sys.stdout, indent=2); print()
except (ValueError, OSError, nib.filebasedimages.ImageFileError) as e:
    sys.exit(f'ERROR: {e}')
PY

if [[ "$dry" == 0 ]]; then
    # mkdir (without -p on the final component) prevents concurrent overwrite.
    mkdir -p "$(dirname "$out")"
    mkdir "$out"
    started=1
    mkdir "$out/registration_channels"
    cp "$manifest" "$out/run.json"
    : > "$out/run.log"
    printf '#!/usr/bin/env bash\nset -euo pipefail\nexport ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=%s\n' "$threads" > "$out/commands.sh"
fi
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS="$threads"
run() {
    if [[ "$dry" == 1 ]]; then
        printf '%q ' "$@"; printf '\n'
    else
        { printf '%q ' "$@"; printf '\n'; } >> "$out/commands.sh"
        "$@" >> "$out/run.log" 2>&1
    fi
}
needfile() { [[ "$dry" == 1 || -s "$1" ]] || die "Missing or empty output: $1"; }
if [[ "$dry" == 1 ]]; then
    printf '# Validated dry run; these commands were NOT executed.\n'
    printf 'export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=%s\n' "$threads"
    printf 'mkdir -p %q\n' "$out/registration_channels"
fi
CH_ARGS=()
names=(background GM PUT CAUD PALL THAL WM_AMYG_CC HIPPO)
last=7
if [[ "$omit" == 1 ]]; then last=6; fi
for ((k=1; k<=last; k++)); do
    fch="$out/registration_channels/fixed_ch${k}_${names[$k]}.nii.gz"
    mch="$out/registration_channels/moving_ch${k}_${names[$k]}.nii.gz"
    run c3d "$fixed" -threshold "$k" "$k" 1 0 -o "$fch"
    run c3d "$moving" -threshold "$k" "$k" 1 0 -o "$mch"
    needfile "$fch"; needfile "$mch"
    CH_ARGS+=( -i "$fch" "$mch" )
done
printf 'Using %s channels for %s (%s).\n' "$last" "$cohort" "$hemi" >&2
run greedy -d 3 "${CH_ARGS[@]}" -m NCC 2x2x2 -moments -o "$out/moments.mat"
needfile "$out/moments.mat"
run greedy -d 3 -a -dof 12 "${CH_ARGS[@]}" -n 100x50x10 \
    -m NCC 2x2x2 -ia "$out/moments.mat" -o "$out/affine.mat"
needfile "$out/affine.mat"
run greedy -d 3 "${CH_ARGS[@]}" -it "$out/affine.mat" -n 100x50x20 \
    -m SSD -s 8.0mm 1.0mm -sv -o "$out/warp.nii.gz"
needfile "$out/warp.nii.gz"
run greedy -d 3 -rf "$fixed" -ri LABEL 0.2vox \
    -rm "$moving" "$out/moving_labels_in_fixed.nii.gz" \
    -r "$out/warp.nii.gz" "$out/affine.mat"
needfile "$out/moving_labels_in_fixed.nii.gz"
if [[ -n "$moving_mri" ]]; then
    run greedy -d 3 -rf "$fixed" -ri LINEAR \
        -rm "$moving_mri" "$out/moving_mri_in_fixed.nii.gz" \
        -r "$out/warp.nii.gz" "$out/affine.mat"
    needfile "$out/moving_mri_in_fixed.nii.gz"
fi
if [[ "$dry" == 1 ]]; then exit 0; fi

# A completion marker denotes successful execution/output checks, not QC approval.
python3 - "$out" >> "$out/run.log" 2>&1 <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
import nibabel as nib
import numpy as np
p = Path(sys.argv[1]); manifest = json.loads((p/'run.json').read_text())
im = nib.load(p/'moving_labels_in_fixed.nii.gz'); data = np.asanyarray(im.dataobj)
if list(im.shape) != manifest['fixed']['shape'] or not np.allclose(im.affine, manifest['fixed']['affine'], rtol=0, atol=1e-4):
    sys.exit('ERROR: resliced labels do not match the fixed grid')
if not np.isfinite(data).all() or np.any(data != np.rint(data)) or np.any((data < 0) | (data > 7)) or not np.any(data > 0):
    sys.exit('ERROR: resliced label values are invalid or entirely empty')
if manifest['omit_hippocampus'] and np.any(data == 7):
    sys.exit('ERROR: hippocampus appeared in exception output unexpectedly')
if manifest['moving_mri']:
    mi = nib.load(p/'moving_mri_in_fixed.nii.gz')
    if mi.shape != im.shape or not np.allclose(mi.affine, im.affine, rtol=0, atol=1e-4) or not np.isfinite(np.asanyarray(mi.dataobj)).all():
        sys.exit('ERROR: resliced MRI has invalid values or grid')
manifest['output_label_counts'] = {str(k): int(np.count_nonzero(data == k)) for k in range(8)}
manifest['status'] = 'completed_requires_visual_qc'
manifest['completed_utc'] = datetime.now(timezone.utc).isoformat()
(p/'run.json').write_text(json.dumps(manifest, indent=2)+'\n')
(p/'SUCCESS.txt').write_text('Registration and output checks completed. Visual QC remains required.\n')
PY
printf 'Completed: %s\n' "$out"
