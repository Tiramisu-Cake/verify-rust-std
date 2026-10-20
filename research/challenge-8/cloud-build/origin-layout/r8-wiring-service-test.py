#!/usr/bin/env python3
"""Synthetic wiring checks for R8 profile dispatch and opt-in CLI flag."""
from __future__ import annotations

import ast
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROVE = ROOT / 'research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py'
R8 = 'experimental-merge-owned-array-allocation-r8-v1'
R7 = 'experimental-merge-late-callback-recovery-r7-v1'


def load(path: Path):
    spec = importlib.util.spec_from_file_location('r8_wiring_prove', path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'missing module: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoke(module, profile: str, flag: bool):
    with tempfile.TemporaryDirectory(prefix='r8-wiring-case-') as temp:
        case = Path(temp)
        for name in ('original', 'verified'):
            (case / name).mkdir()
            (case / name / 'lib.rs').write_text('pub fn fixture() {}\n')
        args = SimpleNamespace(profile=profile, tool_home=Path('/tool'),
            compiler_sysroot=Path('/sysroot'), schema=Path('/schema/vf_mir.capnp'),
            stage_seconds=1, verifier_seconds=1, first_fnmut_continue=False,
            r8_owned_array_allocation=flag)
        calls = []
        def stage(_case, name, command, _env, **kwargs):
            calls.append((name, list(command)))
            return 0
        with patch.object(module.base, 'run_stage', side_effect=stage):
            result = module.execute_case(case, args, {})
        return result, calls


def main():
    profile_path = HERE / 'GLUE-PROFILE.json'
    with tempfile.TemporaryDirectory(prefix='r8-wiring-profile-') as temp:
        profile = Path(temp) / 'profile.json'
        profile.write_text(json.dumps({'profile': R7, 'accepted': False}))
        with patch.dict(os.environ, {'SMALLSORT_MERGE_PROFILE': str(profile)}):
            module = load(PROVE)

    result, calls = invoke(module, R8, True)
    verifast = next(command for name, command in calls if name == 'verifast')
    assert '-rust_owned_array_allocation_r8' in verifast
    assert result['r8_owned_array_allocation'] is True

    result, calls = invoke(module, R7, False)
    verifast = next(command for name, command in calls if name == 'verifast')
    assert '-rust_owned_array_allocation_r8' not in verifast
    assert result['r8_owned_array_allocation'] is False

    try:
        invoke(module, R7, True)
    except ValueError as error:
        assert 'exact R8 profile' in str(error)
    else:
        raise AssertionError('R8 option accepted under R7 profile')

    tree = ast.parse(PROVE.read_bytes())
    arguments = [node for node in ast.walk(tree)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                 and node.func.attr == 'add_argument' and node.args
                 and isinstance(node.args[0], ast.Constant)
                 and node.args[0].value == '--r8-owned-array-allocation']
    assert len(arguments) == 1
    keywords = {node.arg: node.value for node in arguments[0].keywords}
    assert isinstance(keywords.get('action'), ast.Constant) and keywords['action'].value == 'store_true'
    assert isinstance(keywords.get('default'), ast.Constant) and keywords['default'].value is False

    consumers = {
        HERE / 'first-callback.py': [R8],
        HERE / 'concrete-consumer.py': [R8],
        HERE / 'onecell-selected-drop.py': [R8],
        HERE / 'onecell-caller-composition.py': [R8],
        HERE / 'r5-addressability-controls.py': [R8],
        HERE / 'r7-late-admission-controls.py': [R8],
        ROOT / 'research/challenge-8/merge/cloud-build/provider-overlays.py': [R8],
    }
    for path, names in consumers.items():
        text = path.read_text()
        for name in names:
            assert name in text, (path, name)
    overlay_path = ROOT / 'research/challenge-8/merge/cloud-build/provider-overlays.py'
    overlay = load(overlay_path)
    assert overlay.profile_identity({'profile': R8, 'accepted': False}) == R8
    run_path = ROOT / 'research/challenge-8/merge/overnight/run.sh'
    staged_run = overlay.transform(
        'research/challenge-8/merge/overnight/run.sh', run_path.read_bytes(),
        {'network_sha': 'a' * 64}, R8)
    assert b'assert profile in ("experimental-merge-actual-glue-body-v8", "' + R8.encode() + b'")' in staged_run
    assert 'selected_profile == R7_PROFILE' in (HERE / 'first-callback.py').read_text()
    assert "selected_profile == R8_PROFILE" in (HERE / 'first-callback.py').read_text()
    print('R8 dispatch/CLI default-off/profile-binding synthetic tests PASS')


if __name__ == '__main__':
    main()
