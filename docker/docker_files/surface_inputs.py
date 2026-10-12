#!/usr/bin/env python3
"""Validate all pairs before creating persistent surface input copies."""
import csv
import re
import shutil
import sys
from pathlib import Path
import nibabel as nib
import numpy as np


def prepare(mri_dir, seg_dir, work_dir, hemi):
    mri_dir, seg_dir, work_dir = map(Path, (mri_dir, seg_dir, work_dir))
    if not seg_dir.is_dir():
        raise ValueError('Corrected 10-label segmentation folder missing: ' + str(seg_dir))
    pairs = []
    subjects = set()
    for src in sorted(mri_dir.glob('*.nii.gz')):
        name = src.name[:-7]
        subject = name[:-5] if name.endswith('_0000') else name
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', subject):
            raise ValueError('Unsupported subject ID: ' + subject)
        if subject in {'fsaverage', 'inputs', 'files_prepared_for_pipeline', 'freesurfer_high_res_mesh', 'decimated_mesh'} or subject in subjects:
            raise ValueError('Reserved or duplicate subject ID: ' + subject)
        subjects.add(subject)
        seg = seg_dir / (subject + '.nii.gz')
        if not seg.is_file():
            raise ValueError('Matching segmentation missing: ' + str(seg))
        mri_img, seg_img = nib.load(src), nib.load(seg)
        if len(mri_img.shape) != 3 or mri_img.shape != seg_img.shape:
            raise ValueError('MRI/segmentation must be matching 3D volumes: ' + subject)
        if not np.allclose(mri_img.affine, seg_img.affine, atol=1e-4, rtol=0):
            raise ValueError('MRI/segmentation grids differ: ' + subject)
        arr = np.asanyarray(seg_img.dataobj)
        labels = np.unique(arr)
        if not np.isfinite(labels).all() or not np.equal(labels, np.round(labels)).all() or labels.min() < 0 or labels.max() > 10:
            raise ValueError('Expected Purple labels 0..10, not a detailed merged atlas: ' + subject)
        if 1 not in labels or 7 not in labels:
            raise ValueError('Cortical GM (1) and WM (7) must be present: ' + subject)
        pairs.append((subject, src, seg))
    if not pairs:
        raise ValueError('No .nii.gz MRI inputs')
    if work_dir.exists() and (not work_dir.is_dir() or any(work_dir.iterdir())):
        raise ValueError('Surface output must be empty: ' + str(work_dir))
    for kind in ('mri', 'segmentation'):
        (work_dir/'inputs'/kind).mkdir(parents=True, exist_ok=True)
    with (work_dir/'inputs'/'manifest.tsv').open('w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['subject', 'hemisphere', 'source_mri', 'source_segmentation'])
        for subject, src, seg in pairs:
            shutil.copy2(src, work_dir/'inputs'/'mri'/(subject+'.nii.gz'))
            shutil.copy2(seg, work_dir/'inputs'/'segmentation'/(subject+'.nii.gz'))
            writer.writerow([subject, hemi, str(src), str(seg)])
    print('Validated and staged', len(pairs), 'subject(s).')


if __name__ == '__main__':
    try:
        prepare(*sys.argv[1:])
    except (ValueError, OSError) as e:
        raise SystemExit(str(e))
