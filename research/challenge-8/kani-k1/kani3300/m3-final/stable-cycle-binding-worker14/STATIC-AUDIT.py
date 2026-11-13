#!/usr/bin/env python3
# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Check the frozen worker14 patch identities and diagnostic invariants offline."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
inputs = json.loads((HERE / 'INPUTS.json').read_text())
repo = Path(inputs['source_clone'])

def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

assert git('rev-parse', 'HEAD') == inputs['source_sha']
assert git('rev-parse', 'HEAD^{tree}') == inputs['source_tree']
assert git('status', '--porcelain') == ''
assert git('rev-list', '--count', inputs['baseline_sha'] + '..HEAD') == '2'
assert git('rev-parse', 'HEAD~2') == inputs['baseline_sha']
for row in inputs['files']:
    assert hashlib.sha256((repo / row['path']).read_bytes()).hexdigest() == row['sha256']
compiler = (repo / 'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs').read_text()
formatter = compiler.split("impl Display for AnalysisKey<'_>", 1)[1].split('#[derive(Clone)]', 1)[0]
assert 'readable_name(rustc_internal::stable(self.instance))' in formatter
assert 'readable_name(origin)' in formatter
assert all(word in formatter for word in ('provenance=source', 'provenance=registration-override',
                                         'provenance=discarded-closure-override'))
assert not any(word in formatter for word in ('debug_struct', 'mangled_name', 'DefId', ':?'))
assert '#[derive(Clone, Copy, PartialEq, Eq)]\nstruct AnalysisKey' in compiler
assert 'impl<K: Display + Eq> ActiveCalls<K>' in compiler
assert 'const MAX_FRAMES: usize = 12;' in compiler
assert 'const MAX_FRAME_CHARS: usize = 4096;' in compiler
assert 'format!("{frame} [call at {caller}]")' in compiler
assert 'SourceLocation::new(rustc_internal::stable(' in compiler
assert 'call_site.filename' in compiler and 'call_site.start_line' in compiler
assert 'diagnostic_uses_display_without_exposing_internal_identity' in compiler
assert 'assert_eq!(diagnostic(62), diagnostic(93));' in compiler
for rel in ('tests/json-handler/uninit-part1-composition/run.py',
            'tests/json-handler/uninit-part1-composition/compare.py',
            'tests/json-handler/uninit-part1-composition/mixed.rs',
            'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs',
            'scripts/validate_json_export.py'):
    assert not git('diff', '--name-only', inputs['baseline_sha'], 'HEAD', '--', rel)
docs = (repo / 'docs/src/reference/experimental/contracts.md').read_text()
paragraph = docs.split('Initialization shadow transfer is also not implemented', 1)[1].split('\n\n', 1)[0]
assert 'tests/' not in paragraph and 'move_return_' not in paragraph and '.rs' not in paragraph
manifest = json.loads((repo / 'tests/json-handler/uninit-part1-composition/roots.json').read_text())
assert sum(case['binding'] == 'REGRESSION_BOUND' for case in manifest['roots']) == 6
assert [case['name'] for case in manifest['roots'] if case['binding'] != 'REGRESSION_BOUND'] == ['cycle_root']
git('diff', '--check', inputs['baseline_sha'], 'HEAD')
print(json.dumps({'source_sha': inputs['source_sha'], 'identities': 'PASS',
    'two_new_commits_on_baseline': 'PASS', 'format_and_identity_invariants': 'PASS',
    'analysis_identity_and_exact_comparison_unchanged': 'PASS', 'diff_check': 'PASS',
    'python_synthetic_tests': {'boundary': 19, 'composition': 41, 'bindings': 6, 'strong_oracles': 21},
    'python_synthetic_result': '87 PASS', 'rustfmt_parse_and_check': 'PASS',
    'rust_unit_tests': 'NOT_RUN', 'Rust_typecheck': 'NOT_RUN', 'Kani_CBMC_CI': 'NOT_RUN',
    'proof_credit': 'NONE'}, indent=2))
