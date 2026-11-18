"""Narrow same-W14 integration gate; inherit components only by byte identity."""
import copy
import json
from pathlib import Path
import sys
from verify_components import C, G, PACK, S, SOURCE, CONTROL, OLD_SOURCE, git, packet, replay, sha

PACKAGE_COMMIT = '5a9e715ad9e303fbd10600ee379313301c87e9b3'
FINAL = '2ce62b5bb31abd44824dc8e358f77e63d539ed98'
TREE = 'dadbd710770720cd360529188c81c6d19a8de61c'
REQUEST = '008c6868bd466fc7dfb2c1e3239f94157262b0d5c5ac14fac00be0e37fdaae38'

def main():
    p = PACK/'batch-r2-r1'
    binding = packet('batch-r2-r1', PACKAGE_COMMIT, 45)
    ids = json.loads((p/'IDENTITIES.json').read_text())
    assert ids['source']['sha'] == SOURCE
    assert ids['source_component_g0'] == '714c1ca56dd7cf352ae6feebe5e252178cdb63b2'
    assert ids['repaired_runner_package_g0'] == 'a8e3cb30c617a6dee07fa847f1f23470d59783e3'
    assert ids['control']['sha'] == FINAL and ids['control']['tree'] == TREE
    assert ids['control']['request_sha256'] == REQUEST
    assert git(C, 'rev-parse', FINAL+'^{tree}').decode().strip() == TREE
    assert git(C, 'rev-parse', FINAL+'^').decode().strip() == ids['control']['parent'] == '9e14e033f9ee31522b571c127609dcdff76d230b'
    q = Path(ids['control']['worktree'])/'ch8-s1-control'
    assert git(q.parent, 'rev-parse', 'HEAD').decode().strip() == FINAL
    assert not git(q.parent, 'status', '--porcelain=v1').strip()
    inherited = []
    for name in ('SOURCE-CANDIDATE.patch', 'SOURCE-DELTA.patch', 'CFG-PFC-MAP.json', 'MODEL-MAP.json',
                 'ROOT-BINDINGS.json', 'ROW-STUB-MAP.json', 'QUALIFICATION-ASSUMPTIONS.json', 'COMPILED-ITEMS-MAP.json'):
        assert (p/name).read_bytes() == (PACK/'batch-r2'/name).read_bytes()
        inherited.append({'file': name, 'sha256': sha((p/name).read_bytes())})
    same = []
    for rel in ('ch8-s1-control/pack_evidence.py', 'ch8-s1-control/rustc_diagnostics.py',
                'ch8-s1-control/test_rustc_diagnostics.py', 'ch8-s1-control/check_package.py',
                'ch8-s1-control/test_runner.py', '.github/workflows/ch8-s2.yml'):
        assert git(C, 'show', FINAL+':'+rel) == git(C, 'show', CONTROL+':'+rel)
        same.append({'file': rel, 'sha256': sha(git(C, 'show', FINAL+':'+rel))})
    old_runner = git(C, 'show', CONTROL+':ch8-s1-control/runner.py').decode()
    new_runner = git(C, 'show', FINAL+':ch8-s1-control/runner.py').decode()
    assert old_runner.replace(OLD_SOURCE, SOURCE).replace('64d96010b0b4b896322e26d700c253f834ba9fd6', ids['source']['tree']) == new_runner
    old = json.loads(git(C, 'show', CONTROL+':ch8-s1-control/CI-REQUEST.json'))
    new = json.loads(git(C, 'show', FINAL+':ch8-s1-control/CI-REQUEST.json'))
    assert sha((p/'CI-REQUEST.json').read_bytes()) == REQUEST
    assert (p/'CI-REQUEST.json').read_bytes() == (q/'CI-REQUEST.json').read_bytes()
    allowed = {'entry_g0', 'std_sha', 'std_tree', 'source_bindings', 'rows', 'changed_file_sha256',
               'cfg_pfc_source_sha256', 'ci_changed_paths', 'ci_payload_sha256'}
    changed = [k for k in old if old[k] != new[k]]
    assert old.keys() == new.keys() and set(changed) <= allowed
    for a, b in zip(old['rows'], new['rows']):
        a, b = copy.deepcopy(a), copy.deepcopy(b)
        if 'oracle' in a:
            a['oracle'].pop('source_sha256'); b['oracle'].pop('source_sha256')
        assert a == b
    for rel, digest in new['ci_payload_sha256'].items():
        assert sha(git(C, 'show', FINAL+':'+rel)) == digest
    draft = '2d00b9cc14f5a093ccaa0288a0f691fddf3ee84a'
    source_delta = git(C, 'diff', '--name-only', CONTROL, FINAL).decode().splitlines()
    assert source_delta == [x['path'] for x in json.loads((p/'CHANGED-FILES.json').read_text())['control_vs_W11']]
    draft_delta = git(C, 'diff', '--name-only', draft, FINAL).decode().splitlines()
    assert draft_delta == ['ch8-s1-control/CI-REQUEST.json', 'ch8-s1-control/pack_evidence.py',
                           'ch8-s1-control/rustc_diagnostics.py', 'ch8-s1-control/test_rustc_diagnostics.py']
    for rel in source_delta:
        if rel != 'ch8-s1-control/CI-REQUEST.json':
            assert git(C, 'show', FINAL+':'+rel) == git(C, 'show', draft+':'+rel)
    frozen = json.loads(git(C, 'show', '2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8:ch8-s1-control/CI-REQUEST.json'))
    assert frozen['budgets'] == new['budgets']
    assert len(new['rows']) == 11 and sum(r['required_cover_count'] for r in new['rows']) == 20
    assert sum(r['expected'] == 'DETECTED' for r in new['rows']) == 6
    # Validate exact final request/source/fixture binding through unchanged APIs.
    sys.path.insert(0, str(q))
    import runner, cfg_pfc, s2_policy
    request = runner.load_request()
    assert s2_policy.validate_source(S, request)
    check = runner.verify_source(S, Path('/root/kani-upstream-ch8-s1'), request)
    matrix = cfg_pfc.check(S, request)
    assert matrix == json.loads((p/'CFG-PFC-MAP.json').read_text())
    for rel, text in json.loads((q/'S2-SOURCE.json').read_text()).items():
        assert text == git(S, 'show', SOURCE+':'+rel).decode()
    assert (q/'fixtures/s2-r1-batch.rs.txt').read_bytes() == git(S, 'show', OLD_SOURCE+':'+s2_policy.BATCH)
    patches = [replay(S if x['path'].startswith('SOURCE-') else C, p, x,
                      SOURCE if x['path'].startswith('SOURCE-') else FINAL)
               for x in json.loads((p/'PATCHES.json').read_text())]
    provenance = json.loads((p/'TEST-PROVENANCE.json').read_text())
    assert provenance['execution_source_sha'] == SOURCE
    assert provenance['execution_control_sha'] == FINAL
    assert provenance['execution_request_sha256'] == REQUEST
    return {'state': 'PASS', 'integration_gate': 'CLOSED', 'package': binding,
            'source_sha': SOURCE, 'source_tree': ids['source']['tree'], 'control_sha': FINAL, 'control_tree': TREE,
            'control_parent': ids['control']['parent'], 'request_sha256': REQUEST,
            'workflow_sha256': ids['control']['workflow_sha256'], 'tool': ids['tool'],
            'source_components_byte_identity': inherited, 'runner_components_byte_identity': same,
            'runner_difference': 'ONLY_TWO_SOURCE_IDENTITY_LITERALS', 'changed_request_fields': changed,
            'source_delta_paths_from_repaired_runner': source_delta, 'repair_delta_paths_from_source_draft': draft_delta,
            'source_check': check, 'patches': patches, 'budgets': new['budgets'],
            'roots': 11, 'covers': 20, 'exact_negatives': 6,
            'author79_provenance': provenance, 'author79_independently_rerun': False,
            'inherited_independent_tests': {'runner': 33, 'source_cfg_model': 19},
            'native': 'NOT_RUN', 'historical_cause': 'UNKNOWN', 'proof_credit': 'NONE'}

if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
