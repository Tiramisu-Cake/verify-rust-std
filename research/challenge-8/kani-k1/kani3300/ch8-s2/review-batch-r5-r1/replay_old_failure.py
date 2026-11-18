#!/usr/bin/env python3
"""Reexecute immutable original reviewer synthetic repro, redirecting its output."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
original=HERE.with_name('review-batch-r5')/'reproduce_uploaded_prefix.py'
source=original.read_text()
assert source.count('OUT = Path(__file__).resolve().parent')==1
source=source.replace('OUT = Path(__file__).resolve().parent', 'OUT = '+repr(str(HERE)))
source=source.replace('OUT = '+repr(str(HERE)), 'OUT = Path('+repr(str(HERE))+')')
exec(compile(source,str(original),'exec'),{'__file__':str(original),'__name__':'review_old_reproduction'})
