#!/usr/bin/env python3
"""Topology helpers and merge for exvivo_all; inference is run by the Bash script.

Mandatory component cleanup follows Task283, before topology preparation.
Labels 1-5, 7, 9, 10 keep their largest 6-connected component; label 6 (WMH)
is preserved; label 8 keeps components of at least 1 mm^3. Removed voxels
become background. Raw Task279 label 1 then removes voxels from this cleaned
Purple segmentation. The original Task283 prediction is saved unchanged.
Merge priority: Task269 > selected Task273 > corrected Purple.
The merge preserves the supplied finalizer: model overlays can refill removed
voxels. No additional global topology mask is applied to the final merge.
Cleanup map: 1=subcortical repair, 2=residual to WM, 3=MTL propagation.
"""
import argparse
import csv
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.ndimage import distance_transform_edt, convolve, label, generate_binary_structure

SUBCORT = {
    2: ('Putamen', 3, 203),
    3: ('Caudate', 2, 202),
    4: ('Pallidum', 4, 204),
    5: ('Thalamus', 1, 201),
}


SUBCORT_MAP = {1: 201, 2: 202, 3: 203, 4: 204, 7: 207}


ALLOWED = set(range(1, 22)) | {101, 106, 107, 108, 109, 201, 202, 203, 204, 207}

VENTRICLE_MIN_MM3 = 1.0
PURPLE_NAMES = {
    1: 'Cortical gray matter', 2: 'Putamen', 3: 'Caudate', 4: 'Pallidum',
    5: 'Thalamus', 6: 'WMH', 7: 'White matter', 8: 'Ventricle',
    9: 'Corpus callosum', 10: 'MTL',
}


def load_seg(path):
    img = nib.load(str(path))
    if len(img.shape) != 3:
        raise RuntimeError('Expected a 3-D segmentation: {}'.format(path))
    x = np.asarray(img.dataobj)
    if (not np.isfinite(x).all() or np.any(x < 0) or np.any(x > 32767)
            or not np.allclose(x, np.rint(x), atol=1e-4, rtol=0)):
        raise RuntimeError('Expected finite, nonnegative integer labels: {}'.format(path))
    return img, np.rint(x).astype(np.int16)


def same_grid(a, b):
    return (tuple(a.shape) == tuple(b.shape)
            and np.allclose(a.header.get_zooms()[:3], b.header.get_zooms()[:3], atol=1e-5, rtol=0)
            and np.allclose(a.affine, b.affine, atol=1e-3, rtol=0))


def save_like(ref, x, path):
    hdr = ref.header.copy()
    hdr.set_data_dtype(np.int16)
    out = nib.Nifti1Image(x.astype(np.int16), ref.affine.copy(), hdr)
    q, qc = ref.get_qform(coded=True)
    s, sc = ref.get_sform(coded=True)
    if q is not None:
        out.set_qform(q, int(qc))
    if s is not None:
        out.set_sform(s, int(sc))
    nib.save(out, str(path))


def check_labels(x, allowed, name):
    unexpected = sorted(set(np.unique(x).tolist()) - set(allowed))
    if unexpected:
        raise RuntimeError('{} has unexpected labels: {}'.format(name, unexpected))


def clean_purple_components(ref, purple):
    """Mandatory pre-topology cleanup; preserve label values and all WMH voxels.

    Components use face connectivity (6 neighbors in 3-D). For equal largest
    components, retain the first in array scan order. Unknown NIfTI spatial
    units are treated as mm, consistent with this pipeline's MRI convention.
    The 1 mm^3 ventricular cutoff is a small-island heuristic, not a learned
    threshold; every ventricular component below it is removed.
    """
    check_labels(purple, range(11), 'Task283')
    units = ref.header.get_xyzt_units()[0]
    mm_per_unit = {'unknown': 1.0, 'mm': 1.0, 'meter': 1000.0, 'micron': 0.001}[units]
    spacing_mm = np.asarray(ref.header.get_zooms()[:3], dtype=float) * mm_per_unit
    voxel_mm3 = float(np.prod(spacing_mm))
    if not np.isfinite(spacing_mm).all() or np.any(spacing_mm <= 0):
        raise RuntimeError('Invalid voxel spacing for component cleanup')
    cleaned = np.zeros_like(purple)
    structure = generate_binary_structure(3, 1)
    rows = []
    for value, name in PURPLE_NAMES.items():
        components, count = label(purple == value, structure=structure)
        sizes = np.bincount(components.ravel(), minlength=count + 1)
        sizes[0] = 0
        keep = np.zeros(count + 1, dtype=bool)
        if value == 6:
            policy = 'preserve_all'
            keep[1:] = True
        elif value == 8:
            policy = 'minimum_volume'
            # Tolerance avoids deleting a component exactly on the threshold
            # due to NIfTI float32 voxel-spacing roundoff.
            keep[1:] = sizes[1:] * voxel_mm3 >= VENTRICLE_MIN_MM3 * (1.0 - 1e-6)
        else:
            policy = 'largest_component'
            if count:
                keep[int(np.argmax(sizes))] = True
        cleaned[keep[components]] = value
        original_voxels = int(sizes.sum())
        kept_voxels = int(sizes[keep].sum())
        removed_voxels = original_voxels - kept_voxels
        rows.append({
            'label': value, 'structure': name, 'policy': policy,
            'connectivity': 6, 'components_before': int(count),
            'components_kept': int(keep.sum()),
            'original_voxels': original_voxels, 'kept_voxels': kept_voxels,
            'removed_voxels': removed_voxels,
            'removed_mm3': round(removed_voxels * voxel_mm3, 6),
            'voxel_volume_mm3': voxel_mm3,
            'ventricle_min_mm3': VENTRICLE_MIN_MM3 if value == 8 else '',
            'spatial_units': units,
        })
    return cleaned, rows


def bbox(mask, pad=0):
    c = np.argwhere(mask)
    if c.size == 0: return None
    lo = np.maximum(c.min(0)-pad, 0)
    hi = np.minimum(c.max(0)+pad+1, np.array(mask.shape))
    return tuple(slice(int(a),int(b)) for a,b in zip(lo,hi))


def clean_subcort(final, residual, t273, ref, gap_mm, qc, rows):
    sp = np.asarray(ref.header.get_zooms()[:3], float)
    for plab,(name,tlabel,flabel) in SUBCORT.items():
        r = residual == plab
        n = int(r.sum())
        if n == 0:
            rows.append([name,n,0,0,gap_mm])
            continue
        target = t273 == tlabel
        if not target.any():
            final[r] = 107; qc[r] = 2
            rows.append([name,n,0,n,gap_mm])
            continue
        pad = int(np.ceil(gap_mm/max(float(sp.min()),1e-6))) + 2
        b = bbox(target|r, pad)
        tc, rc = target[b], r[b]
        d = distance_transform_edt(~tc, sampling=sp)
        repair = rc & (d <= gap_mm)
        wm = rc & ~repair
        fv, qv = final[b], qc[b]
        fv[repair] = flabel; qv[repair] = 1
        fv[wm] = 107; qv[wm] = 2
        rows.append([name,n,int(repair.sum()),int(wm.sum()),gap_mm])


def fill_mtl(final, residual, t269, qc, majority_iters):
    r = residual == 10
    n = int(r.sum())
    if n == 0: return n, ''
    seeds = (t269 >= 1) & (t269 <= 21)
    if not seeds.any(): raise RuntimeError('Task269 has no labels 1-21')
    b = bbox(seeds|r, 2)
    sc, tc, rc = seeds[b], t269[b], r[b]
    _, idx = distance_transform_edt(~sc, return_indices=True)
    nearest = tc[idx[0], idx[1], idx[2]].astype(np.int16)
    prop = np.zeros_like(tc, np.int16)
    prop[sc] = tc[sc]
    prop[rc] = nearest[rc]
    ker = np.ones((3,3,3), np.int16)
    for _ in range(max(0, majority_iters)):
        bestc = np.zeros(prop.shape, np.int16)
        bestl = prop.copy()
        for lab in range(1,22):
            c = convolve((prop==lab).astype(np.int16), ker, mode='constant', cval=0)
            better = rc & (c > bestc)
            bestc[better] = c[better]; bestl[better] = lab
        prop[rc] = bestl[rc]
        prop[sc] = tc[sc]
    fv, qv = final[b], qc[b]
    fv[rc] = prop[rc]; qv[rc] = 3
    fv[sc] = tc[sc]
    vals,cnts = np.unique(prop[rc], return_counts=True)
    dist = ','.join(f'{int(v)}:{int(c)}' for v,c in zip(vals,cnts))
    return n, dist


def make_safe_merge(purple, t269, t273):
    """Reserve 100+ for Purple, 200+ for selected Task273, 1..21 for MTL."""
    safe = np.where(purple > 0, purple + 100, 0).astype(np.int16)
    covered = np.zeros(purple.shape, dtype=bool)
    for tl, fl in SUBCORT_MAP.items():
        m = t273 == tl
        safe[m] = fl
        covered |= m
    m = (t269 >= 1) & (t269 <= 21)
    safe[m] = t269[m]
    covered |= m
    residual = np.where(covered, 0, purple).astype(np.int16)
    return safe, residual


def merge_case(case, purple_path, t269_path, t273_path, topo_path, out_dir,
               gap_mm=0.6, majority_iters=2):
    ref, purple = load_seg(purple_path)
    i269, t269 = load_seg(t269_path)
    i273, t273 = load_seg(t273_path)
    itopo, topo = load_seg(topo_path)
    for img, name in [(i269, 'Task269'), (i273, 'Task273'), (itopo, 'Task279')]:
        if not same_grid(ref, img):
            raise RuntimeError('{}: {} grid mismatch'.format(case, name))
    check_labels(purple, range(11), 'Purple')
    check_labels(t269, range(22), 'Task269')
    check_labels(topo, range(4), 'Task279')
    # Task273 labels other than 1,2,3,4,7 are ignored, as in the supplied finalizer.
    safe, residual = make_safe_merge(purple, t269, t273)
    final = safe.copy()
    qc = np.zeros_like(final, np.int16)
    subrows = []
    clean_subcort(final, residual, t273, ref, gap_mm, qc, subrows)
    mtl_n, mtl_dist = fill_mtl(final, residual, t269, qc, majority_iters)

    # Preserve the supplied finalizer's priority, including outside Purple foreground.
    for tl, fl in SUBCORT_MAP.items():
        final[t273 == tl] = fl
    m = (t269 >= 1) & (t269 <= 21)
    final[m] = t269[m]
    check_labels(final, {0} | ALLOWED, 'Final merge')

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        'safe': out_dir / '08_initial_merge' / (case + '.nii.gz'),
        'residual': out_dir / '09_purple_residuals' / (case + '.nii.gz'),
        'final': out_dir / '11_final_merged' / (case + '.nii.gz'),
        'cleanup': out_dir / '10_cleanup_map' / (case + '.nii.gz'),
    }
    for key, x in [('safe', safe), ('residual', residual), ('final', final), ('cleanup', qc)]:
        save_like(ref, x, outputs[key])
    report = out_dir / 'reports' / (case + '_final_cleanup_report.tsv')
    with report.open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['case', 'structure', 'residual_voxels', 'gap_repair_voxels',
                    'to_WM_107', 'gap_mm', 'mtl_propagated_distribution'])
        for name, n, rep, wm, g in subrows:
            w.writerow([case, name, n, rep, wm, g, ''])
        w.writerow([case, 'MTL', mtl_n, '', '', '', mtl_dist])
    return {
        'case': case, 'status': 'FINALIZED', 'final_path': str(outputs['final']),
        'buried_sulcus_voxels': int(np.count_nonzero(topo == 1)),
        'merged_foreground_in_buried_sulcus': int(np.count_nonzero((topo == 1) & (final > 0))),
        'subcortical_repaired_voxels': sum(row[2] for row in subrows),
        'subcortical_to_WM_voxels': sum(row[3] for row in subrows),
        'mtl_propagated_voxels': mtl_n,
        'labels': ','.join(str(int(v)) for v in np.unique(final)),
    }


def discover_cases(input_dir):
    if not input_dir.is_dir():
        raise RuntimeError('Missing input directory: {}'.format(input_dir))
    files = sorted(input_dir.glob('*.nii.gz'))
    if not files:
        raise RuntimeError('No *_0000.nii.gz inputs in {}'.format(input_dir))
    bad = [p.name for p in files if not p.name.endswith('_0000.nii.gz')]
    if bad:
        raise RuntimeError('All inputs must use the single-channel *_0000.nii.gz format: {}'.format(bad))
    cases = {}
    for p in files:
        case = p.name[:-12]
        if not case:
            raise RuntimeError('Input case ID cannot be empty: {}'.format(p))
        img = nib.load(str(p))
        if len(img.shape) != 3 or any(n <= 0 for n in img.shape):
            raise RuntimeError('Expected a nonempty 3-D MRI: {}'.format(p))
        if not np.isfinite(img.affine).all() or any(z <= 0 for z in img.header.get_zooms()[:3]):
            raise RuntimeError('Invalid image geometry: {}'.format(p))
        cases[case] = p
    return cases


FOLDERS = [
    '01_purple_original', '01b_purple_component_cleaned',
    '02_topology_input', '03_topology_prediction',
    '04_buried_sulcus_mask', '05_purple_corrected', '06_mtl',
    '07_subcortical', '08_initial_merge', '09_purple_residuals',
    '10_cleanup_map', '11_final_merged',
]


def checked_seg(path, mri, allowed=None):
    ref, labels = load_seg(path)
    if not same_grid(ref, nib.load(str(mri))):
        raise RuntimeError('Prediction/MRI grid mismatch: {}'.format(path))
    if allowed is not None:
        check_labels(labels, allowed, str(path))
    return ref, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'clean-components', 'prepare-topology', 'apply-topology', 'merge'])
    parser.add_argument('--input-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    cases = discover_cases(args.input_dir)
    root = args.output_dir.resolve()
    if args.action == 'init':
        inputs = args.input_dir.resolve()
        if root == inputs or root in inputs.parents:
            raise RuntimeError('Output directory must not equal or contain the input directory')
        if root.exists():
            raise RuntimeError('Output already exists; choose a new EXVIVO_ALL_OUTPUT_DIR: {}'.format(root))
        root.mkdir(parents=True)
        for folder in FOLDERS + ['reports']:
            (root / folder).mkdir()
        print('Processing {} cases. Outputs: {}'.format(len(cases), root), flush=True)
        return
    if not all((root / folder).is_dir() for folder in FOLDERS + ['reports']):
        raise RuntimeError('Run init before processing')
    rows = []
    for case, mri in cases.items():
        name = case + '.nii.gz'
        original = root / '01_purple_original' / name
        component_cleaned = root / '01b_purple_component_cleaned' / name
        topology = root / '03_topology_prediction' / name
        corrected = root / '05_purple_corrected' / name
        if args.action == 'clean-components':
            ref, purple = checked_seg(original, mri, range(11))
            cleaned, component_rows = clean_purple_components(ref, purple)
            save_like(ref, cleaned, component_cleaned)
            report = root / 'reports' / (case + '_component_cleanup_report.tsv')
            with report.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['case'] + list(component_rows[0]), delimiter='\t')
                writer.writeheader()
                writer.writerows(dict(case=case, **row) for row in component_rows)
            removed = sum(row['removed_voxels'] for row in component_rows)
            print('{}: component cleanup removed {} voxels; all WMH preserved'.format(case, removed), flush=True)
        elif args.action == 'prepare-topology':
            ref, purple = checked_seg(component_cleaned, mri, range(11))
            # Simultaneous remapping of original anatomical labels.
            lut = np.array([0, 3, 2, 2, 2, 2, 2, 2, 0, 2, 2], dtype=np.int16)
            save_like(ref, lut[purple], root / '02_topology_input' / (case + '_0000.nii.gz'))
        elif args.action == 'apply-topology':
            ref, purple = checked_seg(component_cleaned, mri, range(11))
            _, topo = checked_seg(topology, mri, range(4))
            removal = topo == 1
            save_like(ref, removal, root / '04_buried_sulcus_mask' / name)
            purple[removal] = 0
            save_like(ref, purple, corrected)
        else:
            mtl = root / '06_mtl' / name
            subcortical = root / '07_subcortical' / name
            for path in [corrected, topology, mtl, subcortical]:
                checked_seg(path, mri)
            row = merge_case(case, corrected, mtl, subcortical, topology, root)
            rows.append(row)
            print('FINAL: {}'.format(row['final_path']), flush=True)
    if rows:
        with (root / 'reports' / 'merge_summary.tsv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR: {}'.format(exc), file=sys.stderr)
        sys.exit(1)
