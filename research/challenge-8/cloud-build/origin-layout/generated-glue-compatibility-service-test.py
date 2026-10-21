#!/usr/bin/env python3
"""Static mutation test; no compiler, verifier, refiner, or capnp execution."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch


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

r11 = 'experimental-merge-label-storage-r11-v1'
assert module.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE[r11] == (
    '48d02bf44f4a082709a427e3e0d78af5498c1f240082fb27c7891dc8a3a283b0')
assert module.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE['experimental-merge-moving-gap-r10-v1'] == (
    'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1')
with tempfile.TemporaryDirectory(prefix='compat-pin-service-') as temp:
    root = Path(temp)
    source = root / 'refinement_checker.ml'
    refiner = root / 'refinement-checker'
    refiner.write_bytes(b'synthetic refiner')
    valid = (module.LEGACY_DROP_DEFAULTS + '\n' +
             module.LEGACY_DROP_DEFAULTS + '\n').encode()
    source.write_bytes(valid)
    digest = module._sha(source)
    with patch.dict(module.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE, {r11: digest}):
        assert module._synthetic_defaults_gate(source, refiner, r11)['matched'] is True
        assert module._synthetic_defaults_gate(source, refiner, 'unknown-profile')['matched'] is False
        source.write_bytes(valid + b' changed')
        assert module._synthetic_defaults_gate(source, refiner, r11)['matched'] is False
        missing = valid.replace(module.LEGACY_DROP_DEFAULTS.encode(), b'', 1)
        source.write_bytes(missing)
        with patch.dict(module.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE,
                        {r11: module._sha(source)}):
            row = module._synthetic_defaults_gate(source, refiner, r11)
            assert row['matched'] is False and row['explicit_unqualified_default_count'] == 1
print('generated-glue compatibility mutation service test: PASS (static only)')
