#!/usr/bin/env python3
"""Check the inference-only assets needed by the published model options."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
models = root / 'assets/nnunet_paths_that_it_requires/nnUNet/3d_fullres'
errors = []
for task in (101, 269, 2732, 276, 279, 283, 289, 451):
    matches = sorted(p for p in models.glob('Task{:03d}_*'.format(task)) if p.is_dir())
    if len(matches) != 1:
        errors.append('Expected one Task{:03d}_* folder, found {}'.format(task, len(matches)))
        continue
    trainer = 'nnUNetTrainerWMHV2' if task == 451 else 'nnUNetTrainerV2'
    base = matches[0] / (trainer + '__nnUNetPlansv2.1')
    for name in ('plans.pkl', 'all/model_final_checkpoint.model',
                 'all/model_final_checkpoint.model.pkl'):
        path = base / name
        if not path.is_file() or path.stat().st_size == 0:
            errors.append('Missing or empty: {}'.format(path.relative_to(root)))
if errors:
    print('Build inputs are incomplete:', file=sys.stderr)
    for error in errors:
        print('  ' + error, file=sys.stderr)
    print('See README.md for the external model layout.', file=sys.stderr)
    sys.exit(2)
print('All eight tasks have plans and fold-all final checkpoint files.')
