#!/usr/bin/env python3
"""Cloud evidence binding and independent log checks for the FBC geometry probe."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

SOURCE = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
BLOB = '40939f922bcb6fdc7ee0d30427fa861827043827'
BLOCK = 'caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a'
OWN = '01369778e4adf0c338b1ba40d4be956cccbfad917bc99bf7a6aaf4fb07c6868f'
CONTRACT = 'b0b340a9598dd53a66bf22f0dfd8a6cc8da08dd28f7d9cbeaa443037dd05120d'
PROFILE = 'copy-on-drop-canonical-fbc-root-bounds-diagnostic-v3b'
CASES = ('positive', 'prototype_false', 'first_body_false')
STAGES = ('exporter', 'decode', 'verifast', 'refinement')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f'missing regular evidence: {path}')
    return json.loads(path.read_text())


def audit_geometry(root: Path, group: str, profile: str, proof_sha: str, build_id: str) -> dict:
    base = root / 'allprooflogs/cases' / group
    env, extraction, results, aggregate = [read(base / (n + '.json')) for n in
                                          ('environment', 'extraction', 'results', 'aggregate')]
    expected_evidence = (root / 'allprooflogs' / ('build' if profile != 'stock-26.10' else '')).resolve()
    if not (env.get('diagnostic_profile') == extraction.get('profile') ==
            results.get('diagnostic_profile') == aggregate.get('diagnostic_profile') == PROFILE and
            env.get('tool_profile') == results.get('profile') == aggregate.get('tool_profile') == profile and
            all(d.get('accepted') is False for d in (env, extraction, results, aggregate)) and
            env.get('proof_sha') == proof_sha and env.get('cloud_build_id') == build_id and
            env.get('provider') == 'cloud-build' and
            env.get('provider_info', {}).get('provider') == 'cloud-build' and
            env.get('provider_info', {}).get('build_id') == build_id and
            env.get('source_sha256') == extraction.get('source_sha256') == SOURCE and
            env.get('source_git_blob') == extraction.get('source_git_blob') == BLOB and
            extraction.get('source_block_sha256') == BLOCK and
            extraction.get('custom_own_sha256') == extraction.get('v3_full_source_own_sha256') == OWN and
            extraction.get('direct_original_contract_sha256') == CONTRACT and
            extraction.get('nonprecise_own') is True and
            env.get('schema_sha256') == 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469' and
            Path(env.get('profile_evidence', '')).resolve() == expected_evidence and
            env.get('rustc_sha256') == 'dda7234360b7f578ca8b0ddcb80145646fa61a67c1720a5abc7051b35c9fcb71' and
            env.get('capnp_sha256') == '450cbc621cf98bc9e704dd1691cdd16ebfcafe15d4122c24b3326973d4766019' and
            list(env.get('compiler_drivers', {}).values()) ==
                ['892e036a701998dd196197e2d1bcd249fd80ade067d42915b7e02ed7dfdef707'] and
            'commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f' in env.get('rustc_version', '') and
            aggregate.get('stages_collected') is True and
            all(set(d.get('cases', {})) == set(CASES) for d in (extraction, results, aggregate))):
        raise ValueError('geometry profile/source/tool/identity bindings differ')
    pins = env.get('tool_pins', {})
    common_pins = {'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
                   'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28'}
    if profile == 'stock-26.10':
        common_pins.update({'bin/verifast': '9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1',
                           'prelude_sha256': 'd7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5',
                           'spec_manifest_sha256': '4a0911303bbb087f1f50ce85524197edbb541f31c72e8133dfbcc9cf528e03a0',
                           'spec_checks_sha256': '2adb5f85e2077a96e2db6b97da9af17d9324ad3c586187292854970e63078da4',
                           'spec_resource_count': 58})
    else:
        common_pins.update({'experimental_console_sha256': '354436b99d7225e86271f211a43969b0c7f11f3c7f823a7d718abe00946a4f47',
                           'applied_patch_sha256': 'b163d3e36b695304cbc6c84d025af7bd5d679a5fb553356baa8b8362dea1b927',
                           'kernel_patched': '100eebae92c770a0b8cd57e2639588761f881316dd522fc3b9a9b1ec6fd91cd6',
                           'translator_patched': 'ffd6fe925364b8274d61f094d43211f9463e0dc3e98ae545d3f528f2da0cf6c0',
                           'parser_patched': '8ed673086183323058aac5e0e21399e4532d1e74b97c5d41105827e8643107bd',
                           'prelude_patched': 'd1079bc94ceafe6595c7ce216f9c93e3436d22d849bd31bcb0cf442dd183e751',
                           'stdlib_patched': 'd92e5044bbb2692e7b006fc649df361fe80bf878b69b5a2bb80635a27330f227'})
    if any(pins.get(k) != v for k, v in common_pins.items()):
        raise ValueError('geometry tool profile pins differ')
    module_path = Path(__file__).resolve().parents[1] / 'overnight/guard-ownership/drop-geometry/prove.py'
    spec = importlib.util.spec_from_file_location('geometry_audit_hosted', module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    reports = {}
    for name in CASES:
        case = base / 'cases' / name
        meta, row = extraction['cases'][name], results['cases'][name]
        if read(case / 'classification.json') != row['direct_body']:
            raise ValueError('geometry classification/result binding differs')
        direct, gate = row['direct_body'], row['geometry_gate']
        before, after = direct['initial_source_hashes'], direct['final_source_hashes']
        if not (direct.get('source_unchanged_at_every_stage') is True and
                before == after == read(case / 'source-before.json') and
                before.get('small_sort_source') == SOURCE and
                meta.get('runtime_source_identical_after_ghost_strip') is True and
                meta.get('custom_own_sha256') == OWN and
                meta.get('direct_original_contract_sha256') == CONTRACT and
                row['stages'] == direct['stages'] and set(row['stages']) == set(STAGES)):
            raise ValueError('geometry source/stage records differ')
        for relative, key in [('original/lib.rs', 'original_sha256'), ('verified/lib.rs', 'verified_sha256')]:
            if sha(case / relative) != meta[key] or before[relative] != meta[key]:
                raise ValueError('geometry case source hash differs')
        original, verified = [(case / relative).read_bytes() for relative in ('original/lib.rs', 'verified/lib.rs')]
        inserted = ((module.prep.PROTOTYPE_FALSE if name == 'prototype_false' else b'') +
                    module.prep.ROOT_LIMITS + module.prep.FIELD_BINDING + b''.join(module.prep.GEOMETRY) +
                    module.prep.PROTOTYPE_CALL)
        contract = module.prep.B.CONTRACT.replace(module.prep.SAFETY_OPEN, module.prep.SAFETY_OPEN + inserted, 1)
        stripped = verified.replace(module.prep.OWN, b'', 1).replace(contract, b'', 1)
        if name == 'first_body_false':
            stripped = stripped.replace(module.prep.BODY_FALSE, b'', 1)
        if stripped != original or hashlib.sha256(contract).hexdigest() != meta['direct_asserted_contract_sha256']:
            raise ValueError('geometry ghost strip or complete contract differs')
        for stage in STAGES:
            record = read(case / (stage + '-stage.json'))
            code = row['stages'][stage]
            if type(code) is not int or record.get('exit_code') != code or int((case / (stage + '-exit-code.txt')).read_text()) != code:
                raise ValueError('geometry exit records differ')
            for suffix in ('.log', '-resources.txt'):
                path = case / (stage + suffix)
                if not path.is_file() or path.is_symlink():
                    raise ValueError('geometry full stage artifact missing')
            output = case / ('compiler-mir.bin' if stage == 'exporter' else stage + '.out')
            if not output.is_file() or output.is_symlink():
                raise ValueError('geometry stage output missing')
            if record.get('status') == 'NOT_RUN':
                if stage != 'decode' or row['stages']['exporter'] == 0:
                    raise ValueError('geometry stage unjustifiably skipped')
            elif record.get('source_unchanged') is not True or record.get('source_before') != before or record.get('source_after') != after:
                raise ValueError('geometry per-stage source changed')
        if (case / 'compiler-mir-sha256.txt').read_text().strip() != sha(case / 'compiler-mir.bin'):
            raise ValueError('geometry MIR hash differs')
        recalculated = module.geometry_gate(case, name, meta, direct)
        if recalculated != gate or aggregate['cases'][name] != gate['classification']:
            raise ValueError('geometry admission/log classification differs')
        classification = gate['classification']
        if classification not in ('PASS_COMPONENT_ONLY', 'EXPECTED_FALSE_ASSERTION', 'INCONCLUSIVE') or gate.get('accepted') is not False:
            raise ValueError('geometry invalid theorem status')
        if classification != 'INCONCLUSIVE':
            if not (gate['own_ast_admission']['admitted'] is True and
                    direct['mir_admission']['admitted'] is True and
                    row['stages']['exporter'] == row['stages']['decode'] == row['stages']['refinement'] == 0 and
                    not gate['dead_code_records']):
                raise ValueError('geometry credited outcome without complete gates')
            log = (case / 'verifast.log').read_text(errors='replace')
            if classification == 'PASS_COMPONENT_ONLY':
                if name != 'positive' or row['stages']['verifast'] != 0 or gate['global_errors'] or not direct['verifier_admission']['positive_gate']:
                    raise ValueError('geometry incomplete actual Drop positive')
            else:
                oracle = (meta['intended_failure'] if name == 'prototype_false' else
                          {'line': meta['negative_target_line'], 'column_start': meta['negative_column_start'], 'column_end': meta['negative_column_end']})
                pattern = rf"verified/lib\.rs\({oracle['line']},{oracle['column_start']}-{oracle['column_end']}\): error: Assertion might not hold\. \(Cannot prove false\.\)"
                if name == 'positive' or row['stages']['verifast'] != 1 or len(gate['global_errors']) != 1 or not re.search(pattern, gate['global_errors'][0]):
                    raise ValueError('geometry unrelated negative')
        reports[name] = {'classification': classification, 'stages': row['stages'],
                         'prototype_seen': gate['prototype_seen'], 'actual_body_seen': gate['actual_body_seen'],
                         'ast_admitted': gate['own_ast_admission']['admitted'],
                         'geometry_frontier': gate['geometry_frontier'], 'global_errors': gate['global_errors'],
                         'dead_code_records': gate['dead_code_records']}
    component_pass = (reports['positive']['classification'] == 'PASS_COMPONENT_ONLY' and all(
        reports[n]['classification'] == 'EXPECTED_FALSE_ASSERTION' for n in CASES[1:]))
    if aggregate.get('component_pass') is not component_pass:
        raise ValueError('geometry aggregate credit differs')
    return {'accepted': False, 'artifact_bindings_valid': True, 'diagnostic_profile': PROFILE,
            'component_pass': component_pass, 'cases': reports, 'actual_caller_and_glue': 'OPEN'}
