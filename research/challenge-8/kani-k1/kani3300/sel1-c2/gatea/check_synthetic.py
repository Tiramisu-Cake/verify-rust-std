#!/usr/bin/env python3
"""Qualify observer in a synthetic copy; never bind a real source or run tools."""
from pathlib import Path
import shutil, tempfile, subprocess, os, sys
ROOT = Path(__file__).resolve().parent / 'full-export/scripts/kani3300-gate'
with tempfile.TemporaryDirectory(prefix='sel1-c2-gatea-synthetic-') as td:
    dest = Path(td) / 'gate'
    shutil.copytree(ROOT, dest)
    for path in dest.iterdir():
        if path.suffix in ('.json', '.py'):
            text = path.read_text()
            for old, new in [('PENDING_SEL1_FREEZE_SHA', '1'*40), ('PENDING_SEL1_FREEZE_TREE', '2'*40),
                             ('PENDING_SOURCE_SHA256', '3'*64), ('PENDING_SOURCE_OBJECT', '4'*40),
                             ('"state": "PENDING_FREEZE"', '"state": "SEL1_C2_FROZEN"')]:
                text = text.replace(old, new)
            path.write_text(text)
    result = subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_receipt.py', 'test_lifecycle.py'],
                            cwd=dest, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
    sys.exit(result.returncode)
