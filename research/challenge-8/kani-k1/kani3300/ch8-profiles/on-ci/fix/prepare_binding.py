#!/usr/bin/env python3
"""Prepare fresh static source/cover coordinates; never reads CI artifacts or runs Rust."""
import argparse
import copy
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'off-ci-batch/run-43784551069'
OLD = '9fa2f7f97760584f38738909625c064006d8a936'
ROOT = 'core::slice::sort::shared::smallsort'
DIR = 'library/core/src/slice/sort/shared/smallsort'
PROFILES = ROOT + '::verify::merge::profiles'
NEW = 'profile_merge4_contract_u8_len4'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def translate(old, new, number):
    """Only unchanged lines or unique explicit replacement inside their diff hunk."""
    if number is None:
        return None
    for tag, a, b, c, d in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if a <= number - 1 < b:
            if tag == 'equal':
                return c + number - a
            wanted = old[number - 1]
            wanted = wanted.replace('merge_profile::<LtU8>(&src, out)', 'merge4_profile::<LtU8>(&src, out)')
            wanted = wanted.replace('stub_verified(merge_profile)', 'stub_verified(merge4_profile)')
            wanted = re.sub(r'&mut arbitrary_less::<(?:T|u8)>', '&mut cmp', wanted)
            found = [i + 1 for i in range(c, d) if new[i].strip() == wanted.strip()]
            if len(found) == 1:
                return found[0]
            raise ValueError(f'Unreviewed coordinate replacement {number}: {old[number-1]!r}')
    raise ValueError(f'Coordinate absent: {number}')


def prepare(repo, sha, manifest_path):
    original_bytes = (BASE / 'accept-v2/SOURCE-MAP.json').read_bytes()
    assert digest(original_bytes) == 'de253321477ef4e6c45c7d90a0afda7bf2e4fdba3c2dbd989aa598dee08be7e7'
    original = json.loads(original_bytes)
    old_sources, sources = {}, {}
    for path, expected in original['source_files_sha256'].items():
        old_sources[path] = git(repo, 'show', OLD + ':' + path)
        assert digest(old_sources[path].encode()) == expected, path
        sources[path] = git(repo, 'show', sha + ':' + path)
    manifest = json.loads(manifest_path.read_bytes())
    assert len(manifest) == 63 and len({r['id'] for r in manifest}) == 63
    rows = {}
    for row in manifest:
        rid, path = row['id'], row['source_file']
        if rid == NEW:
            text = sources[path].splitlines()
            decl = next(i + 1 for i, line in enumerate(text) if line.startswith('fn ' + NEW + '('))
            cover_line = next(i + 1 for i in range(decl, len(text)) if 'kani::cover(' in text[i])
            call_line = next(i + 1 for i in range(decl, cover_line) if 'merge4_profile::<LtU8>' in text[i])
            prefix = row['selector']
            covers = [{'id': prefix + '.cover.1', 'source_file': path, 'source_line': cover_line,
                       'source_function': NEW, 'source_expression': text[cover_line - 1].strip(),
                       'role': 'POST_TARGET_RETURN', 'target_call_source_lines': [call_line],
                       'site_binding': 'DIRECT_SOURCE_SITE_PREDECLARED'}]
            target = PROFILES + '::merge4_profile'
            mapping = {'binding': {'source_target': {'fully_qualified': target}}, 'covers': covers,
                       'coverage': {'required_ids': [covers[0]['id']], 'post_target_ids': [covers[0]['id']]},
                       'source_function_decl_line': decl}
        else:
            prior = original['rows'][rid]
            mapping = {'binding': {'source_target': copy.deepcopy(prior['binding']['source_target'])},
                       'covers': [], 'coverage': {k: copy.deepcopy(prior['coverage'][k])
                                                for k in ('required_ids', 'post_target_ids')},
                       'source_function_decl_line': translate(old_sources[path].splitlines(), sources[path].splitlines(),
                                                              prior['source_function_decl_line'])}
            if rid == 'profile_merge_consumer_u8_len4':
                mapping['binding']['source_target'] = {'fully_qualified': PROFILES + '::merge4_profile'}
            for old_cover in prior['covers']:
                c = copy.deepcopy(old_cover)
                c.pop('status', None)
                c.pop('codegen_identity', None)
                cp = c['source_file']
                for key in ('source_line', 'macro_callsite_line', 'macro_template_line'):
                    if key in c:
                        c[key] = translate(old_sources[cp].splitlines(), sources[cp].splitlines(), c[key])
                for key in ('target_call_source_lines', 'assertion_source_lines_before_cover',
                            'caller_assertion_source_lines_before_cover'):
                    if key in c:
                        c[key] = [translate(old_sources[cp].splitlines(), sources[cp].splitlines(), n) for n in c[key]]
                mapping['covers'].append(c)
        mapping['oracle'] = {'expected': row['expected'],
                             'allowed_failure_descriptions': row['allowed_failure_descriptions'],
                             'no_additional_failures': True, 'all_emitted_covers_must_be_sat': True}
        mapping['leaf_companion'] = row.get('leaf_companion')
        mapping['profile'] = row['profile']
        mapping['mode'] = row['mode']
        mapping['state'] = 'PREDECLARED_STATIC_NOT_RUN'
        mapping['runtime_property_binding'] = 'FRESH_SAME_ROW_REQUIRED'
        mapping['historical_admissions_reused'] = 0
        mapping['proof_credit'] = 'NONE'
        rows[rid] = mapping
    sites = {}
    profile_path = DIR + '/verify/merge/profiles.rs'
    text = sources[profile_path]
    for fn in ('swap_profile', 'sort4_profile', 'insert_tail_profile', 'merge_profile', 'merge4_profile'):
        end = text.index('pub(crate) unsafe fn ' + fn + '<')
        start = text.rfind('\n}', 0, end) + 2
        attrs = text[start:end]
        sites[fn] = ('/verify/merge/profiles.rs', *[
            [text.count('\n', 0, start + m.start()) + 1
             for m in re.finditer(r'^#\[kani::' + kind + r'\(', attrs, re.M)]
            for kind in ('requires', 'modifies', 'ensures')])
        assert [len(v) for v in sites[fn][1:]] == [1, 1, 2], (fn, sites[fn])
    sites.update(stable_cell=('/verify/forwarding_contracts.rs', [95], [96], [97, 98]),
                 unstable_byte=('/verify/forwarding_contracts.rs', [111], [112], [113, 114]),
                 freeze_noncopy=('/verify/forwarding_contracts.rs', [124], [125], [126, 127]),
                 swap_if_less=('.rs', [387, 394, 401, 405, 409], [413], []))
    helper = sources[DIR + '/verify/helper_contracts.rs'].splitlines()
    frame_write = [i + 1 for i, s in enumerate(helper) if s.strip() == 'comparisons = comparisons.wrapping_add(1);']
    assert len(frame_write) == 1
    spec = {'schema': 'prof-on-02-fresh-binding-spec-v1', 'source_commit': sha,
            'source_tree': git(repo, 'rev-parse', sha + '^{tree}').strip(),
            'source_files_sha256': {p: digest(s.encode()) for p, s in sources.items()},
            'manifest_sha256': digest(manifest_path.read_bytes()), 'sites': sites,
            'frame_write_line': frame_write[0], 'rows': rows,
            'assurance': 'STATIC_SOURCE_COORDINATES_ONLY; IDs predicted, not observed; fresh exported symbols, roles, covers and frame required',
            'proof_credit': 'NONE', 'historical_admissions_reused': 0}
    write('BINDING-SPEC.json', spec)
    v4_bytes = (BASE / 'accept-v4/reclassify_v4.py').read_bytes()
    assert digest(v4_bytes) == 'cc87f6ed6b98be1ed9aeec5903c573003bc0b499c1c4054c9e8d76b1c85579dd'
    code = v4_bytes.decode()
    code = code[code.index('def relative('):code.index('\n\ndef replay(')]
    substitutions = {
        "profile == 'arbitrary_less::<u8> FnDef'": "profile == 'reading_comparator::<u8> closure'",
        "helper + 'arbitrary_less<u8>>'": "helper + 'reading_comparator<u8>::{closure#0}>'",
        "p['line'] == 276": "p['line'] == FRAME_WRITE_LINE",
        "splitlines()[275]": "splitlines()[FRAME_WRITE_LINE - 1]",
        "line276 writes": "the pinned source site writes",
    }
    for a, b in substitutions.items():
        assert code.count(a) == 1, a
        code = code.replace(a, b)
    header = '''"""accept-v4 binding functions adapted for PROF-ON-02; no replay or admission carry-forward.
Generated by prepare_binding.py from hash-pinned v4. Compiler/demangler rendering
of the new closure remains NOT_RUN: an unmatched rendering fails closed.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'off-ci-batch/run-43784551069'
sys.path.insert(0, str(BASE / 'accept-v3'))
from classifier_v3 import require
SPEC = json.loads((HERE / 'BINDING-SPEC.json').read_bytes())
ROOT = 'core::slice::sort::shared::smallsort'
DIR = 'library/core/src/slice/sort/shared/smallsort'
PROFILES = ROOT + '::verify::merge::profiles'
NETWORK = ROOT + '::verify::network'
FRAME = 'rejects_swap_comparator_writing_outside_frame_u8'
SITES = SPEC['sites']
FRAME_WRITE_LINE = SPEC['frame_write_line']

'''
    footer = '''

def bind_fresh(row, harness, records, demangled, sources):
    """Binding only, after runner and v2/v3 completeness/role policy checks.

    Caller must use fresh validated same-row stdout/export, never old ACCEPT.
    Returned BOUND does not decide acceptance or leaf dependency admission.
    """
    mapping = SPEC['rows'][row['id']]
    for key in ('mode', 'profile', 'leaf_companion'):
        require(row.get(key) == mapping.get(key), 'ROW_SPEC_MISMATCH:' + key)
    for key in ('expected', 'allowed_failure_descriptions'):
        require(row[key] == mapping['oracle'][key], 'ORACLE_SPEC_MISMATCH:' + key)
    for path, sha in SPEC['source_files_sha256'].items():
        require(hashlib.sha256(sources[path].encode()).hexdigest() == sha, 'SOURCE_HASH_MISMATCH:' + path)
    old_interface = {'binding': {'export_contract_symbol':
        (harness.get('contract') or {}).get('contracted_function_name')},
        'cover_mapping': {'post_target_ids': mapping['coverage']['post_target_ids']}}
    return bind(row, old_interface, mapping, harness, records, demangled, sources)
'''
    (HERE / 'binding_v02.py').write_text(header + code + footer)
    return {'rows': len(rows), 'source': sha, 'sites': sites, 'frame_write_line': frame_write[0]}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--sha', required=True)
    p.add_argument('--manifest', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.source, a.sha, a.manifest), indent=2))
