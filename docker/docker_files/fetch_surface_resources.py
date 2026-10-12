#!/usr/bin/env python3
"""Fetch only pinned atlas/template files, checking their Git blob hashes."""
import concurrent.futures
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
dest = Path(sys.argv[2])
revision = manifest['revision']

def fetch(item):
    target = dest/item['path']
    target.parent.mkdir(parents=True, exist_ok=True)
    url = 'https://raw.githubusercontent.com/Pulkit-Khandelwal/purple-mri/' + revision + '/' + item['path']
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
            digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if len(data) != item['size'] or digest != item['sha']:
                raise ValueError('Resource integrity mismatch: ' + item['path'])
            target.write_bytes(data)
            return item['path']
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for name in pool.map(fetch, manifest['files']):
        print('Downloaded', name, flush=True)
(dest/'SOURCE_REVISION').write_text(revision+'\n')
