#!/usr/bin/env python3
"""Static mutation test; no compiler, verifier, refiner, or capnp execution."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
TARGET = HERE / 'generated-glue-compatibility-controls.py'
spec = importlib.util.spec_from_file_location('generated_glue_compatibility', TARGET)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

ordinary = '''      defPath = "<CopyOnDrop as core::ops::Drop>::drop",
      localDecls = [ ( mutability = (mut = void),
          id = (name = "_0"), ty = (kind = (tuple = [])) ) ],
      basicBlocks = [ ( statements = [
            ( sourceInfo = (span = (dummy = void)), kind = (storageDead = (name = "_1")) ),
            ( sourceInfo = (span = (dummy = void)), kind = (assign = (
                lhsPlace = (local = (name = "_0")), rhsRvalue = (use = (constant = void)) ) ) ) ],
          terminator = (kind = (return = void)) ) ],
      output = (kind = (tuple = []))
      defPath = "following",
'''
for nonunit in (False, True):
    mutated = module._ordinary_mutant(ordinary, nonunit, True)
    _, _, body = module._method(mutated)
    assert 'local = (name = "_0")' not in body
    assert 'kind = (return = void)' in body
    assert body.count('kind = (uInt = (u64 = void))') == (2 if nonunit else 0)
    assert 'kind = (storageDead' in body
try:
    module._ordinary_mutant(ordinary.replace('local = (name = "_0")',
                                            'local = (name = "_9")'), False, True)
except ValueError:
    pass
else:
    raise AssertionError('missing ordinary _0 assignment must fail closed')
print('generated-glue compatibility mutation service test: PASS (static only)')
