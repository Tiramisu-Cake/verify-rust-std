#!/usr/bin/env python3
"""Qualify the bound observer in a temporary copy without running a toolchain."""
from pathlib import Path
import shutil, tempfile, subprocess, os, sys
ROOT = Path(__file__).resolve().parent / 'full-export/scripts/kani3300-gate'
with tempfile.TemporaryDirectory(prefix='sel1-c2-gatea-synthetic-') as td:
    dest = Path(td) / 'gate'
    shutil.copytree(ROOT, dest)
    result = subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_receipt.py', 'test_lifecycle.py'],
                            cwd=dest, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
    sys.exit(result.returncode)
