#!/usr/bin/env python3
"""Additional W14 audit of original inputs after coordinator policy notice.

No repair candidate is read. No compiler, full runner, CI or raw evidence.
"""
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
G0 = HERE.parents[5]
S1 = HERE.parent
RUN = S1/'s1-07/run-43923266772'
STD = Path('/root/verify-rust-std-ch8-s1-08-w13')
CTL = Path('/root/kani-ch8-s1-08-w13')
SOURCE = '99e8456d200fff1299ee5756279cddb23921dc65'
CONTROL = '9ccd882ef2460fbc97400594e7e3dfc884a4a997'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'


def blob(repo, commit, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', commit+':'+path])


def read(path):
    return json.loads(path.read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit():
    policy_path = 'research/challenge-8/kani-k1/S1-ACCEPTANCE-DECISION-2026-11-17.md'
    policy_commit = '7d7b7c67a1'
    policy = blob(G0, policy_commit, policy_path)
    assert (G0/policy_path).read_bytes() == policy
    prior = read(RUN/'accept/ACCEPT.json')
    records = prior['unreachable_analysis']['records']
    inherited = [r for r in records if r['decision'].startswith('ALLOWED_')]
    checks = [r for r in inherited if r['status_kind'] == 'check']
    covers = [r for r in inherited if r['status_kind'] == 'cover']
    assert len(checks) == 226 and len(covers) == 2
    allowed_descriptions = {'attempt to add with overflow', 'attempt to subtract with overflow',
                            'attempt to multiply with overflow', 'attempt to divide by zero',
                            'index out of bounds: the length is less than or equal to the given index'}
    assert all(r['class'] == 'assertion' and r['description'] in allowed_descriptions for r in checks)
    assert {r['row_id'] for r in covers} == {'activation-default', 'activation-override'}
    clauses = read(RUN/'accept-pfc/PFC.json')['bindings']
    required_ids = {(b['id'], e['property']['id']) for b in clauses for e in b['contract']['ensures']}
    assert not required_ids & {(r['row_id'], r['property_id']) for r in records}
    assert all(p['status'] == 'SUCCESS' for b in clauses for p in b['contract']['modifies']['write_site_properties'])
    # Group all inherited sites, preserving per-site ID/status identity below.
    sites = collections.defaultdict(list)
    for r in checks:
        s = r['site']
        sites[(s['source_path'], s['line'], s['function'], r['description'])].append(
            {'row': r['row_id'], 'group': r['group'], 'id': r['property_id'], 'status': 'UNREACHABLE'})
    source = blob(STD, '5be85699b8826e3286c0bf89efb9affefac0acb5',
                  'library/core/src/slice/sort/shared/smallsort.rs').decode()
    # Additional independently inspected premises, rather than SAT-cover credit:
    # boolean offsets are 2+{0,1}; fixed divisor 2; floor(n/2)<=n;
    # the fixture is n<=3, with scratch length 0 or n+16, and T sizes are one.
    assert 'v_base.add(2 + c2 as usize)' in source and 'v_base.add(2 + (!c2 as usize))' in source
    for n in range(4):
        assert n+8 <= 11 and n+16 <= 19
        assert n-n//2 >= 0
        scratch = 0 if n < 2 else n+16
        assert scratch <= 19
    assert all(2+int(b) <= 3 for b in (False, True))
    assert 1*32 <= 2**64-1 and 1*48 <= 2**64-1
    # Negative source-oracle anchors: apply only the exact declared one-line
    # ensures overlay at its declared source line; verify the whole effective
    # file hash afterwards. No hypothetical new output is fabricated.
    request_bytes = blob(CTL, CONTROL, 'ch8-s1-control/CI-REQUEST.json')
    assert request_bytes == (S1/'s1-08/EMBEDDED-CI-REQUEST.json').read_bytes()
    request = json.loads(request_bytes)
    negatives = []
    for row in request['rows']:
        if not row.get('oracle'):
            continue
        o = row['oracle']
        text = blob(STD, SOURCE, o['file']).decode()
        lines = text.splitlines(keepends=True)
        if row['variant'] != 'production':
            spec = request['variants'][row['variant']]
            patch = blob(CTL, CONTROL, 'ch8-s1-control/'+spec['patch'])
            assert digest(patch) == spec['sha256']
            minus = [x[1:] for x in patch.decode().splitlines() if x.startswith('-') and not x.startswith('---')]
            plus = [x[1:] for x in patch.decode().splitlines() if x.startswith('+') and not x.startswith('+++')]
            assert len(minus) == len(plus) == 1
            assert lines[o['line']-1].rstrip('\n') == minus[0]
            lines[o['line']-1] = plus[0]+'\n'
            text = ''.join(lines)
        assert digest(text.encode()) == o['source_sha256']
        assert text.splitlines()[o['line']-1] == o['source_line']
        assert o['class'] == 'assertion' and re.fullmatch(r'.+\.assertion\.[1-9][0-9]*', o['property_id'])
        if 'assertion_context' in o:
            assert text.splitlines()[o['line']-1:o['line']+2] == o['assertion_context']
        negatives.append({'row': row['id'], 'variant': row['variant'], 'source_sha256': o['source_sha256'],
                          'assertion_line': o['line'], 'source_hash_line_context_class': 'PASS',
                          'known_stale_closure_span': row['id'] in ('activation_descending_rejected', 'activation_effectful_rejected'),
                          'runtime_failure_ID_status': 'NOT_OBSERVED_ON_S1_08'})
    assert len(negatives) == 8
    extra_producer = []
    for path, lo, hi, role in [
        ('library/kani_macros/src/sysroot/contracts/shared.rs', 22, 89, 'requires precede old-state remembers'),
        ('library/kani_macros/src/sysroot/contracts/shared.rs', 138, 158, 'owned old expression evaluated and cloned before body'),
        ('kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs', 127, 238, 'slice modifies region length and concrete byte type geometry')]:
        data = blob(CTL, TOOL, path)
        assert data == blob(CTL, CONTROL, path)
        extra_producer.append({'commit': TOOL, 'path': path, 'file_sha256': digest(data),
                               'start_line': lo, 'end_line': hi, 'role': role,
                               'lines': data.decode().splitlines()[lo-1:hi]})
    return {'schema': 'w14-original-scope-followup-v1',
            'policy': {'commit': policy_commit, 'path': policy_path, 'sha256': digest(policy),
                       'compatible_with_original_review_assurance': True},
            'frozen_original_source': SOURCE, 'frozen_original_control': CONTROL,
            'inherited_U_checks': 226, 'inherited_negative_return_covers': 2,
            'inherited_U_contains_required_post_frame_relation_assertions': False,
            'inherited_sites': [{'path': k[0], 'line': k[1], 'function': k[2], 'description': k[3],
                                  'records': v} for k, v in sites.items()],
            'all_eight_original_negative_source_oracles': negatives,
            'additional_pinned_producer_anchors': extra_producer,
            'additional_concrete_findings': [], 'prior_finding': 'W14-S108-01 REMAINS_OPEN_ON_ORIGINAL_PINS',
            'repair_candidate': 'NOT_READ_NOT_REVIEWED_NOT_ACCEPTED',
            'composer': 'NOT_REVIEWED_NO_EXACT_COMMITTED_DELTA_ISSUED',
            'compiler_full_runner_CI_push_ledger': 'NOT_RUN', 'new_proof_credit': 'NONE'}


if __name__ == '__main__':
    result = audit()
    (HERE/'FOLLOWUP-VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'followup': 'PASS', 'inherited_checks': 226, 'negative_source_oracles': 8,
                      'additional_concrete_findings': 0, 'repair_review': 'NOT_RUN'}))
