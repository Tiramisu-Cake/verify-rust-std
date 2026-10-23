#!/usr/bin/env python3
"""Static mutation test; no compiler, verifier, refiner, or capnp execution."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import inspect
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
assert module.R22_OWNED_NLL_PROFILE_SHA256 == (
    '3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88')
assert module.R22_OWNED_NLL_REFINER_SOURCE_SHA256 == (
    '11a0ff9057e6da92a684c20b1cda1e4825d986ea6d80980a7a967f236f0c9db8')
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

with tempfile.TemporaryDirectory(prefix='compat-r22-profile-service-') as temp:
    root = Path(temp)
    source = root / 'refinement_checker.ml'
    refiner = root / 'refinement-checker'
    profile = root / 'profile.json'
    refiner.write_bytes(b'synthetic exact refiner')
    valid = (module.LEGACY_DROP_DEFAULTS + '\n' +
             module.LEGACY_DROP_DEFAULTS + '\n').encode()
    source.write_bytes(valid)
    real_profile = HERE / 'GLUE-PROFILE.json'
    profile.write_bytes(__import__("subprocess").check_output(["git", "show", "733b6a7d68259787f1caf58177060589b6af779e:research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json"], cwd=HERE))
    digest = module._sha(source)
    with patch.object(module, 'R22_OWNED_NLL_REFINER_SOURCE_SHA256', digest):
        row = module._synthetic_defaults_gate(source, refiner, r11, profile)
        assert row['matched'] is True
        assert row['profile_binding'] == 'EXACT_R22_OWNED_NLL_REGISTRATION'
        assert row['synthetic_drop_count'] == 2
        assert row['explicit_unqualified_default_count'] == 2
        assert row['expected_source_sha256'] == digest

        source.write_bytes(valid + b' altered source')
        assert module._synthetic_defaults_gate(source, refiner, r11, profile)['matched'] is False
        source.write_bytes(valid)

    card = json.loads(profile.read_text())
    corrupted_cards = []
    value = json.loads(json.dumps(card)); value['profile'] = 'wrong-profile'; corrupted_cards.append(value)
    value = json.loads(json.dumps(card)); value['effective_tool_commit'] = '0' * 40; corrupted_cards.append(value)
    value = json.loads(json.dumps(card)); value['r22_owned_nll_registration'] = None; corrupted_cards.append(value)
    value = json.loads(json.dumps(card)); del value['r22_owned_nll_registration']; corrupted_cards.append(value)
    value = json.loads(json.dumps(card)); value['r22_owned_nll_registration']['tool_source_paths'] = []; corrupted_cards.append(value)
    for index, bad_card in enumerate(corrupted_cards):
        bad_profile = root / f'bad-{index}.json'
        bad_profile.write_text(json.dumps(bad_card))
        row = module._synthetic_defaults_gate(source, refiner, r11, bad_profile)
        assert row['matched'] is False
        if 'r22_owned_nll_registration' in bad_card:
            assert row['expected_source_sha256'] is None
            assert row['profile_binding'] == 'REJECTED'
        else:
            assert row['expected_source_sha256'] == module.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE[r11]
            # Removing the extension cannot reach 11a0: only the prior exact R11 pin remains.
            assert row['profile_binding'] == 'LEGACY_PROFILE_PIN'

    malformed = root / 'malformed.json'; malformed.write_text('{')
    wrong_type = root / 'wrong-type.json'; wrong_type.write_text('null')
    missing = root / 'missing.json'
    for bad_path in (malformed, wrong_type, missing):
        row = module._synthetic_defaults_gate(source, refiner, r11, bad_path)
        assert row['matched'] is False and row['profile_binding'] == 'REJECTED'

    legacy_source = root / 'legacy-source.ml'
    legacy_source.write_bytes(valid)
    wrong_source = module._synthetic_defaults_gate(legacy_source, refiner, r11, profile)
    assert wrong_source['matched'] is False
    assert wrong_source['expected_source_sha256'] == module.R22_OWNED_NLL_REFINER_SOURCE_SHA256
    assert 'SMALLSORT_MERGE_PROFILE' in inspect.getsource(module.run)
print('generated-glue compatibility mutation service test: PASS (static only)')
