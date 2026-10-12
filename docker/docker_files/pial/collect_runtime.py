#!/usr/bin/env python3
"""Collect ldd's complete dependency closure, excluding the system glibc family."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

binary, dest = map(Path, sys.argv[1:])
(dest / 'bin').mkdir(parents=True, exist_ok=True)
(dest / 'lib').mkdir(parents=True, exist_ok=True)
shutil.copy2(binary, dest / 'bin/mris_place_surface')
output = subprocess.check_output(['ldd', str(binary)], text=True)
if 'not found' in output:
    raise SystemExit('Unresolved dependency:\n' + output)
# Keep libc and the loader supplied by the Ubuntu 20.04 runtime.
system = {'libc.so.6', 'libm.so.6', 'libpthread.so.0', 'libdl.so.2',
          'librt.so.1', 'libresolv.so.2', 'libutil.so.1', 'libanl.so.1'}
libs = {}
for name, path in re.findall(r'^\s*(\S+)\s+=>\s+(/\S+)', output, re.M):
    if name not in system:
        shutil.copy2(Path(path).resolve(), dest / 'lib' / name)
        libs[name] = path
# Remove build-tree RPATH indirectly by building without installed external paths;
# the wrapper supplies the relocatable lib directory.
manifest = {'source_commit': '80ec14cb8c3ce78d700d269e942c55ccaa09b343',
            'original_binary_sha256': 'd2b25661e370f0b2185ddf2eafc17a33cb4cf5e18a31de16a7644726bcd056f3',
            'copied_libraries': libs,
            'files_sha256': {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(dest.rglob('*')) if p.is_file()}}
(dest / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Collected', len(libs), 'runtime libraries')
