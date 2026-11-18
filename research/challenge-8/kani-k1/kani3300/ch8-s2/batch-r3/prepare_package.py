#!/usr/bin/env python3
"""Materialize review metadata from committed local objects; never dispatches."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.with_name('batch-r2-r1')
SOURCE = Path('/root/verify-rust-std-ch8-s2-r3-w13')
CONTROL = Path('/root/kani-ch8-s2-r3-final-w13')
Q = CONTROL / 'ch8-s1-control'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
OLD_SOURCE = 'efb1aba7fc6445cba6cd75154713b598c9e2579d'
OLD_CONTROL = '2ce62b5bb31abd44824dc8e358f77e63d539ed98'
ENTRY = '91cd41b3fdbffe36ed5d14806c390bf0b0c16bbb'
BASE = '99e8456d200fff1299ee5756279cddb23921dc65'
PARENT = '9e14e033f9ee31522b571c127609dcdff76d230b'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def blob(repo, rev, rel):
    return subprocess.check_output(['git', '-C', str(repo), 'show', rev + ':' + rel])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=2) + '\n')


def main():
    sys.path.insert(0, str(Q))
    import runner
    import cfg_pfc as c
    import contract_stacks as cs
    r = runner.load_request()
    source = {'worktree': str(SOURCE), 'sha': git(SOURCE, 'rev-parse', 'HEAD'),
              'tree': git(SOURCE, 'rev-parse', 'HEAD^{tree}'),
              'parent': git(SOURCE, 'rev-parse', 'HEAD^'), 'base': BASE,
              'derivation_source': OLD_SOURCE}
    control = {'worktree': str(CONTROL), 'sha': git(CONTROL, 'rev-parse', 'HEAD'),
               'tree': git(CONTROL, 'rev-parse', 'HEAD^{tree}'),
               'parent': git(CONTROL, 'rev-parse', 'HEAD^'),
               'derivation_control': OLD_CONTROL, 'base': PARENT,
               'request_sha256': sha(Q / 'CI-REQUEST.json'),
               'workflow_sha256': sha(CONTROL / '.github/workflows/ch8-s2.yml')}
    assert control['parent'] == PARENT
    assert source['parent'] == '97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'
    assert git(SOURCE, 'diff', '--name-only', OLD_SOURCE, 'HEAD') == cs.SMALLSORT
    for repo in (SOURCE, CONTROL):
        assert not git(repo, 'status', '--porcelain=v1')
    ids = {'schema': 'ch8-s2-r3-identities-v1', 'task_id': 'task' + ENTRY,
           'entry_g0': ENTRY, 'frozen_package_g0': '5a9e715ad9e303fbd10600ee379313301c87e9b3',
           'frozen_review_g0': 'a2d6428b35930282b03f91eeadba72eaf3cbef9b',
           'source': source, 'control': control,
           'tool': {'sha': TOOL, 'tree': git(CONTROL, 'rev-parse', TOOL + '^{tree}'), 'change': 'NONE'},
           'readiness': 'READY_FOR_INDEPENDENT14_DELTA_REVIEW',
           'review14': 'PENDING', 'GO_request': 'NOT_ISSUED_REVIEW_FIRST',
           'compile': 'NOT_RUN', 'qualification': 'NOT_RUN', 'proof_credit': 'NONE'}
    write('IDENTITIES.json', ids)
    for name, path in [('CI-REQUEST.json', Q / 'CI-REQUEST.json'),
                       ('WORKFLOW.yml', CONTROL / '.github/workflows/ch8-s2.yml')]:
        shutil.copyfile(path, HERE / name)
    for name in ('cfg_pfc.py', 's2_policy.py', 'contract_stacks.py', 'test_contract_stacks.py'):
        shutil.copyfile(Q / name, HERE / name)
    for name in ('ENVELOPE.json', 'MEASUREMENTS.json', 'ROOT-BINDINGS.json', 'COMPILED-ITEMS-MAP.json'):
        shutil.copyfile(PREVIOUS / name, HERE / name)
    inherited = []
    for name in ('MODEL-MAP.json', 'QUALIFICATION-ASSUMPTIONS.json'):
        d = json.loads((PREVIOUS / name).read_text())
        assert d.pop('source_sha') == OLD_SOURCE
        d['source_sha'] = source['sha']
        write(name, d)
        inherited.append({'file': name, 'reference_sha256': sha(PREVIOUS / name),
                          'candidate_sha256': sha(HERE / name), 'delta': 'source_sha identity only'})
    cfg = c.check(SOURCE, r)
    write('CFG-PFC-MAP.json', cfg)
    audit = cs.check(SOURCE, r)
    # Preserve source cfg spellings and explicit availability in the review map.
    raw = {}
    lexical, attributed = 0, 0
    for module in audit['modules']:
        rel = module['file']
        text = (SOURCE / rel).read_text()
        ts = c.tokens(text)
        lexical += sum(t in cs.OPS and i > 0 and ts[i-1][0] == '::'
                       and i+1 < len(ts) and ts[i+1][0] == '(' for i, (t, _) in enumerate(ts))
        for name, item, attrs in cs.declarations(text, set(audit['contexts'][0]['effective_cfg'])):
            attributed += sum(t in cs.OPS and i > 0 and a[i-1][0] == '::'
                              and i+1 < len(a) and a[i+1][0] == '('
                              for a in item['attrs'] for i, (t, _) in enumerate(a))
            raw[module['module'] + '::' + '::'.join(name)] = [c.spelling(a) for a in item['attrs']]
    assert lexical == attributed, (lexical, attributed)
    for rec in audit['functions'] + audit['contract_stacks']:
        rec['declared_attrs_before_cfg'] = raw[rec['function']]
        rec['cfg_availability'] = {'module_chain_active': True,
                                   'effective_cfg': audit['contexts'][0]['effective_cfg'],
                                   'context_rows': [x['row'] for x in audit['contexts']]}
    audit['opaque_contract_coverage'] = {'lexical_contract_paths': lexical,
                                        'attributed_to_enumerated_functions': attributed,
                                        'unattributed_contract_paths': 0,
                                        'macro_generated_harnesses': 'Not compiler expanded; no literal function-contract clauses hidden in opaque items/bodies'}
    write('CONTRACT-STACK-MAP.json', audit)
    rows = json.loads((PREVIOUS / 'ROW-STUB-MAP.json').read_text())
    for row, checked in zip(rows, cfg['rows']):
        assert row['id'] == checked['id']
        row['cfg_stub'] = checked
    write('ROW-STUB-MAP.json', rows)
    files = sorted(set(r['changed_file_sha256']) | set(r['cfg_pfc_source_sha256']) |
                   set(r['contract_stack_source_sha256']) |
                   {'library/contracts/safety/src/lib.rs', 'library/contracts/safety/src/kani.rs',
                    'library/contracts/safety/src/runtime.rs', 'library/contracts/safety/build.rs'})
    write('SOURCE-MAP.json', {'source_sha': source['sha'], 'source_tree': source['tree'],
                             'files': {rel: sha(SOURCE / rel) for rel in files},
                             'delta_from_efb': [cs.SMALLSORT],
                             'body_signature_runtime_preservation': 'Exact fixed normalization plus eight effective-cfg differential projections',
                             'unchanged_models_harnesses_providers': 'All files except smallsort.rs byte-identical to efb'})
    invariance = []
    for rel in git(CONTROL, 'ls-tree', '-r', '--name-only', OLD_CONTROL, '--', 'ch8-s1-control').splitlines():
        if not rel.endswith('.py'):
            continue
        old = blob(CONTROL, OLD_CONTROL, rel)
        new = (CONTROL / rel).read_bytes()
        kind = 'BYTE_IDENTICAL'
        if rel.endswith('/runner.py'):
            assert old.decode().replace(OLD_SOURCE, source['sha']).replace(
                '4563e06722871ae5eafdf6d288afa21a406b6ba8', source['tree']) == new.decode()
            kind = 'TWO_SOURCE_IDENTITY_LITERALS_ONLY'
        elif rel.endswith('/s2_policy.py'):
            kind = 'TARGETED_GATE_INTEGRATION_ONLY'
        else:
            assert old == new, rel
        invariance.append({'file': rel, 'reference_sha256': hashlib.sha256(old).hexdigest(),
                           'candidate_sha256': sha(CONTROL / rel), 'status': kind})
    write('RUNNER-INVARIANCE.json', {'reference': OLD_CONTROL, 'candidate': control['sha'],
                                    'files': invariance,
                                    'B01_B02': 'INHERITED_CLOSED_BY_FROZEN_REVIEW; collector/packer/tests byte identical',
                                    'producer_universality': 'NOT_CLAIMED; r2 production retention observed by coordinator'})
    write('INHERITANCE.json', {'reference_package': ids['frozen_package_g0'],
                              'reference_source': OLD_SOURCE, 'reference_control': OLD_CONTROL,
                              'reference_review': ids['frozen_review_g0'],
                              'byte_identical_package_files': {n: sha(HERE / n) for n in
                                  ('ENVELOPE.json', 'MEASUREMENTS.json', 'ROOT-BINDINGS.json', 'COMPILED-ITEMS-MAP.json')},
                              'identity_only_rebound_maps': inherited,
                              'source_delta_paths': [cs.SMALLSORT], 'new_proof_credit': 'NONE'})
    patches = []
    for name, repo, base, target in [
        ('SOURCE-CANDIDATE.patch', SOURCE, BASE, source),
        ('SOURCE-DELTA.patch', SOURCE, OLD_SOURCE, source),
        ('SOURCE-PARENT.patch', SOURCE, source['parent'], source),
        ('CONTROL-CANDIDATE.patch', CONTROL, TOOL, control),
        ('CONTROL-PARENT.patch', CONTROL, PARENT, control),
        ('CONTROL-DELTA.patch', CONTROL, OLD_CONTROL, control)]:
        (HERE / name).write_bytes(subprocess.check_output(
            ['git', '-C', str(repo), 'diff', '--binary', '--full-index', base, target['sha']]))
        patches.append({'path': name, 'base': base, 'target': target['sha'],
                        'target_tree': target['tree'], 'sha256': sha(HERE / name)})
    write('PATCHES.json', patches)
    changed = {}
    for label, repo, base in [('source', SOURCE, OLD_SOURCE), ('control', CONTROL, OLD_CONTROL)]:
        changed[label] = [{'path': rel, 'sha256': sha(repo / rel)} for rel in
                          git(repo, 'diff', '--name-only', base, 'HEAD').splitlines()]
    write('CHANGED-FILES.json', changed)
    write('CHECKPOINT.json', {'schema': 'ch8-s2-r3-checkpoint-v1', 'task_id': ids['task_id'],
                             'state': ids['readiness'], 'source': source, 'control': control,
                             'claims': ['All12 safety predicates preserved; source bodies/signatures identical',
                                        'All19 literal active contract stacks audited across11 identical effective cfg contexts',
                                        'Ordinary sort8 relation/model/harness/provider bytes inherited exactly',
                                        '33 targeted Python/static/synthetic tests PASS once; no native compiler'],
                             'assurance': 'STATIC_SOURCE_AND_SYNTHETIC_ONLY',
                             'open': ['Independent14 exact delta review', 'Root GO-request after APPROVE',
                                      'Separate owner/coordinator GO for retry/publication/accounting',
                                      'R3 compilation/qualification NOT_RUN; exact causal repair unverified',
                                      'R1 actual cause UNKNOWN'],
                             'blocker': None, 'proof_credit': 'NONE', 'closed_proof_obligations': 0,
                             'accounting_reference': {'item1': '29/29', 'item2': '9/14', 'total': '38/43',
                                                      'changed_by13': False},
                             'external_actions': {'compiler': 0, 'CI': 0, 'push': 0, 'PR': 0, 'ledger': 0,
                                                  'reservation': 0, 'cancel': 0},
                             'subagents': 0, 'Fast': 'OFF_PER_OWNER; NOT_TOGGLED', 'model_tier': 'UNCHANGED',
                             'next_step': 'Separate14 review of exact READY pins; no dispatch authority'})
    (HERE / 'CURRENT-TASK.md').write_text('Runtime: Codex. W13 task' + ENTRY +
        '. READY_FOR_INDEPENDENT14_DELTA_REVIEW. See CHECKPOINT.json / HANDOFF.md. No compiler/CI/push/ledger/subagents.\n')
    (HERE / 'STATUS.md').write_text('READY for independent14 delta review. Source-supported repair only; compilation/qualification NOT_RUN, proof credit NONE.\n')
    print(json.dumps({'source': source, 'control': control,
                      'active_stacks': len(audit['contract_stacks']),
                      'opaque_contract_coverage': audit['opaque_contract_coverage']}, indent=2))


if __name__ == '__main__':
    main()
