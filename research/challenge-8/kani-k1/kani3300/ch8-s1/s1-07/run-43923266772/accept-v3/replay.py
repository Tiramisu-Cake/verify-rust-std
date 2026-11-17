#!/usr/bin/env python3
"""Compose committed S1-07 components; default is byte-exact, read-only replay.

The three upstream replayers run in isolated subprocesses, without --write.
They verify their complete structured inputs and pinned git objects, not just
component summaries. No compilation, network, raw logs or archive extraction.
"""
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
ROOT = HERE.parents[7]
TASK = '831f87be704575dee4ace8f834312b5c95d43f99'
COMMITS = {'accept': 'b84003a4fdb2416d0742b21a5151b0d32d047d35',
           'accept-u': '16e36c4a2c244bb23ae71c80e5aa6db5f95e5338',
           'accept-pfc': '013f288ca5111c0587e087567d2ec4182856be1d'}
MANIFEST_SHA = 'dad405ab891a3c88871a7e39ecaa17f8abaa43794de80e0cbd0ff96a78b46315'
STD = '5be85699b8826e3286c0bf89efb9affefac0acb5'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
CONTROL = 'b37f6f75c5b7b77e84297cd7104f9c0868502fd4'
REQUEST = '6c483ce754cd8e99c01953bf4c40a145b10529d7990aa52c28ef32c00b980cd7'
PFC_ASSURANCE = 'BOUNDED_SOURCE_REPORTED_PROFILES_V4_TRUST_PINNED_STOCK_COMPILER'
U_ASSURANCE = 'PINNED_SOURCE_LOCAL_ARGUMENT; SOURCE_REPORTED_CHECK_IDENTITY'
UG = 'UNREACHABLE_APPLICABILITY_OR_ORIGIN_UNKNOWN'
PG = 'FULL_QUALIFIED_TARGET_IMPL_CONTRACT_WRAPPER_BINDING'
CG = 'COMPANION_QUALIFICATION_PENDING'
SG = 'REQUIRED_SUCCESS_SEMANTIC_BINDING'
EXACT_SUCCESS = {'EXACT_SUCCESS_SEMANTIC', 'EXACT_SUCCESS_SEMANTIC_SET'}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def index(items, key, label):
    need(isinstance(items, list) and all(isinstance(x, dict) for x in items), label + ' list')
    result = {x[key]: x for x in items}
    need(len(result) == len(items) and all(result), label + ' duplicate/empty key')
    return result


def verify_files(manifest):
    """Bind working bytes, including replay code, to the named immutable commits."""
    need(manifest['components'] == COMMITS and manifest['task_commit'] == TASK, 'component versions')
    need(manifest['admission_inputs'] == ['accept/ACCEPT.json', 'accept-u/U.json', 'accept-pfc/PFC.json'],
         'admission input scope')
    for rel, item in manifest['files'].items():
        path = ROOT / rel
        need(path.resolve() == path and path.is_file() and not path.is_symlink(), 'input path:' + rel)
        data = path.read_bytes()
        need(sha(data) == item['sha256'], 'input SHA:' + rel)
        committed = subprocess.check_output(['git', '-C', str(ROOT), 'show', item['commit'] + ':' + rel])
        need(committed == data, 'uncommitted/foreign input:' + rel)


def load():
    raw = (HERE / 'INPUTS.json').read_bytes()
    need(sha(raw) == MANIFEST_SHA, 'INPUTS.json SHA')
    manifest = json.loads(raw)
    verify_files(manifest)
    for name in COMMITS:
        result = subprocess.run([sys.executable, '-I', '-B', str(RUN / name / 'replay.py')],
                                cwd=ROOT, capture_output=True, text=True, timeout=180)
        need(result.returncode == 0, name + ' replay failed: ' + result.stderr[-2000:])
    # U's committed manifest also rehashes five accept-v2 stop-marker files.
    # They are upstream integrity-only snapshots: neither parsed nor passed to
    # compose(), and never an admission root or qualification source.
    # Detect input drift during replay as well as before it.
    verify_files(manifest)
    return tuple(json.loads((RUN / rel).read_bytes()) for rel in
                 ('CI-REQUEST.json', 'accept/ACCEPT.json', 'accept-u/U.json', 'accept-pfc/PFC.json',
                  'accept-u/INPUTS.json'))


def namespaces(request, baseline, u, pfc):
    need(baseline['schema'] == 'ch8-s1-07-offline-acceptance-v1'
         and u['schema'] == 'ch8-s1-07-u-v1'
         and pfc['schema'] == 's1-07-pfc-component-profiles-v4-v1', 'input schemas')
    need(baseline['run'] == u['run'] == int(pfc['run']) == 43923266772, 'run namespace')
    need(baseline['source_sha'] == u['source_commit'] == pfc['source_sha'] == request['std_sha'] == STD,
         'source namespace')
    need(baseline['tool_sha'] == u['tool_commit'] == pfc['tool_sha'] == request['tool_sha'] == TOOL,
         'tool namespace')
    need(baseline['control_sha'] == pfc['control_sha'] == CONTROL, 'control namespace')
    need(baseline['request_sha256'] == u['request_sha256'] == pfc['request_sha256'] == REQUEST,
         'request namespace')
    need(pfc['assurance'] == PFC_ASSURANCE and pfc['component_only'] is True
         and pfc['admission_root_recomputed'] is False, 'PFC assurance/scope')
    need(all(pfc[k] == 'NONE' for k in ('independent_proof_credit', 'B1_credit', 'B2_credit'))
         and baseline['independent_proof_credit'] == 'NONE', 'proof credit')
    rows = index(baseline['rows'], 'id', 'baseline rows')
    specs = index(request['rows'], 'id', 'request rows')
    groups = index(request['execution_groups'], 'id', 'request groups')
    need(set(rows) == set(specs), 'row namespace')
    membership = [rid for g in groups.values() for rid in g['row_ids']]
    need(len(membership) == len(set(membership)) and set(membership) == set(rows), 'group partition')
    for gid, group in groups.items():
        for rid in group['row_ids']:
            r, s = rows[rid], specs[rid]
            need((r['group'], r['selector'], r['mode'], r['variant'], r['expected'], r['domain_N']) ==
                 (gid, s['selector'], s['mode'], group['variant'], s['expected'], s.get('N')),
                 'row/group/harness namespace:' + rid)
            need(s['variant'] == r['variant'], 'request variant')
            need([x['message'] for x in r['required_success']] == s['required_success_messages']
                 and [x['message'] for x in r['required_covers']] == s['required_cover_messages'],
                 'required message namespace')
            need(r['source_reported_verdict'] == ('FAILURE' if s['expected'] == 'DETECTED' else 'SUCCESS'),
                 'source verdict versus oracle')
            need(bool(r['negative_oracle']) == (s['expected'] == 'DETECTED'), 'negative oracle presence')
    return rows, specs


def u_coverage(baseline, u, rows, u_inputs):
    original = baseline['unreachable_analysis']['records']
    key = lambda r: (r['row_id'], r['property_id'])
    old = {key(r): r for r in original}
    need(len(old) == len(original), 'duplicate baseline U')
    unknown = {k: r for k, r in old.items() if r['decision'].startswith('UNKNOWN')}
    records = {key(r): (i, r) for i, r in enumerate(u['records'])}
    need(len(records) == len(u['records']), 'duplicate U records')
    need(set(records) <= set(unknown), 'foreign U row/property namespace')
    consumed = collections.defaultdict(list)
    for k, (i, r) in records.items():
        o, row = unknown[k], rows[k[0]]
        need((r['group'], r['harness']) == (o['group'], o['selector']) == (row['group'], row['selector']),
             'U group/harness namespace')
        source_hashes = {s['path']: s['sha256'] for s in u_inputs['sources'] if s['repo'] == 'std'}
        expected_evidence = {name: {'path': '../evidence/' + row['group'] + '/' + name + '.json',
            'sha256': u_inputs['files']['../evidence/' + row['group'] + '/' + name + '.json']}
            for name in ('properties', 'export', 'receipt')}
        valid = (o['status_kind'] == 'check' and r['status'] == o['status'] == 'UNREACHABLE'
                 and all(r[f] == o[f] for f in ('class', 'description', 'site'))
                 and r['request_sha256'] == REQUEST and r['source_commit'] == STD
                 and r['variant'] == row['variant'] and r['assurance'] == U_ASSURANCE
                 and r['independent_sorting_proof_credit'] == 'NONE'
                 and r['decision'] == 'JUSTIFIED_GENERATED_SAFETY_APPLICABILITY'
                 and bool(r['premises'].get('verified_anchors')) and bool(r['premises'].get('facts'))
                 and all(a in u['source_anchors'] for a in r['premises']['verified_anchors'])
                 and r['evidence'] == expected_evidence
                 and r['source_sha256'] == source_hashes.get(o['site']['source_path']))
        if valid:
            consumed[k[0]].append({'property_id': k[1], 'pointer': '/records/' + str(i),
                                   'record_sha256': sha(encoded(r)), 'rule': r['rule']})
    return unknown, consumed


def pfc_chain(binding, row, spec, request):
    """Check consumption edges; upstream replay checks their source semantics."""
    if binding.get('status') != 'SOURCE_REPORTED_BOUND' or binding.get('gaps') != []:
        return False
    try:
        need((binding['group'], binding['harness'], binding['crate'], binding['variant'], binding['property_count']) ==
             (row['group'], row['selector'], 'core', row['variant'], row['properties']), 'PFC row edges')
        source, native, impl, c = (binding[k] for k in ('source', 'native', 'selected_impl', 'contract'))
        expected_source = request['source_bindings'][row['id']]
        effective_hashes = dict(request['changed_file_sha256'])
        effective_hashes.update(request['variants'].get(row['variant'], {}).get('changed_file_sha256', {}))
        need(source['file'] == expected_source['file'] and source['sha256'] == expected_source['sha256']
             and source['effective_target_sha256'] == effective_hashes[source['effective_target_file']], 'PFC source hashes')
        need(source['file'] and source['sha256'] and source['effective_target_sha256']
             and source['macro'] and binding['target_attribute'] and impl['attributes'] and impl['method'], 'PFC source/impl edges')
        need(native['metadata_path'] and native['sha256'] and native['pointer']
             and native['target_definition'] and binding['configuration_sha256'] and binding['invocation_id'], 'PFC native edges')
        need(c['raw_symbol'] and c['decoded_modifies_wrapper'] and c['check_wrapper'] and c['target_instance'], 'PFC wrapper edges')
        need({p['class'] for p in c['diagnostics']} == {'single_top_level_call', 'no_recursive_call'}
             and len(c['diagnostics']) == 2 and all(p['status'] == 'SUCCESS' for p in c['diagnostics']), 'PFC diagnostics')
        need(c['ensures'] and all(e['source_clause']['kind'] == 'ensures'
             and e['property']['status'] == row['source_reported_verdict'] for e in c['ensures']), 'PFC ensures')
        need(c['requires'] and all(e['semantics'] == 'ASSUMED_BY_PFC_CHECK; NOT_ASSERTED'
             and e['assertion_ids'] == [] for e in c['requires']), 'PFC requires')
        need(c['modifies']['semantics'] == 'ENFORCED_BY_SOLE_DFCC_CONTRACT'
             and c['modifies']['source_clause']['kind'] == 'modifies'
             and c['modifies']['write_site_properties']
             and all(p['status'] == 'SUCCESS' for p in c['modifies']['write_site_properties']), 'PFC frame')
        need(len(c['clause_allocation_checks']) == 2
             and all(p['status'] == 'SUCCESS' for p in c['clause_allocation_checks']), 'PFC allocation checks')
        if row['expected'] == 'DETECTED':
            need(binding['negative_oracle']['status'] == 'EXACT_PREDECLARED_SOLE_FAILURE'
                 and binding['negative_oracle']['legal_companion_binding'] == spec['companion']
                 and binding['negative_oracle']['id'] == row['negative_oracle']['property']['id'], 'PFC negative oracle')
        else:
            need(binding['negative_oracle'] is None, 'PFC positive oracle')
        return True
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def qualify(rows, specs, run):
    """Least fixed point from actual local gates. Cycles never seed credit."""
    qualified = set()
    edges = {}
    for rid, row in rows.items():
        cid = specs[rid].get('companion')
        if not cid:
            continue
        c, edge = rows.get(cid), row.get('same_run_companion', {})
        valid = bool(c and edge.get('id') == cid and edge.get('group') == c['group']
                     and edge.get('run') == run and edge.get('source_verdict') == c['source_reported_verdict'] == 'SUCCESS'
                     and edge.get('source_tool_request_pins') == 'MATCH'
                     and edge.get('binary_after') == c['binary_after'] == 'MATCH')
        edges[rid] = {'id': cid, 'valid_same_run_pins': valid}
    changed = True
    while changed:
        changed = False
        for rid, row in rows.items():
            edge = edges.get(rid)
            if rid not in qualified and not row['local_pending_gates'] and (
                    edge is None or edge['valid_same_run_pins'] and edge['id'] in qualified):
                qualified.add(rid)
                changed = True
    for rid, row in rows.items():
        gates = set(row['local_pending_gates'])
        if rid in edges:
            edge = edges[rid]
            edge['qualification'] = 'QUALIFIED' if edge['valid_same_run_pins'] and edge['id'] in qualified else 'PENDING'
            row['companion_qualification'] = edge
            if edge['qualification'] != 'QUALIFIED':
                gates.add(CG)
        row['pending_gates'] = sorted(gates)
        row['qualification'] = 'QUALIFIED' if rid in qualified else 'PENDING'
    return edges


def compose(request, baseline, u, pfc, u_inputs):
    oldrows, specs = namespaces(request, baseline, u, pfc)
    report = copy.deepcopy(baseline)
    rows = index(report['rows'], 'id', 'rows')
    unknown, consumed = u_coverage(baseline, u, rows, u_inputs)
    pbindings = index(pfc['bindings'], 'id', 'PFC bindings')
    need(set(pbindings) <= {rid for rid, r in rows.items() if r['mode'] == 'PFC'}, 'foreign PFC row')
    pfc_refs = {}
    for i, b in enumerate(pfc['bindings']):
        if pfc_chain(b, rows[b['id']], specs[b['id']], request):
            pfc_refs[b['id']] = {'pointer': '/bindings/' + str(i), 'record_sha256': sha(encoded(b)),
                'edges': ['source_macro_target', 'selected_impl', 'native', 'contract.raw_symbol',
                          'contract.target_instance', 'contract.requires', 'contract.ensures',
                          'contract.modifies', 'contract.diagnostics', 'contract.clause_allocation_checks'],
                'assurance': PFC_ASSURANCE, 'independent_proof_credit': 'NONE'}
    for rid, row in rows.items():
        gates = set(row['pending_gates']) - {CG}
        required = {pid for (r, pid) in unknown if r == rid}
        justified = {r['property_id'] for r in consumed[rid]}
        # Independently rederive the success/cover gates from frozen bindings.
        if any(s['binding'] not in EXACT_SUCCESS for s in row['required_success']):
            gates.add(SG)
        if any(c['binding'] != 'EXACT_SAT_COVER_SEMANTIC' for c in row['required_covers']):
            gates.add('REQUIRED_COVER_SEMANTIC_BINDING')
        if required - justified:
            gates.add(UG)
        else:
            gates.discard(UG)
        if row['mode'] == 'PFC':
            if rid in pfc_refs:
                gates.discard(PG)
                row['pfc_binding'] = {'static_source': 'SOURCE_BOUND', 'profiles_v4': 'SOURCE_REPORTED_BOUND',
                                      'independent_compiler_MIR_binding_credit': 'NONE'}
            else:
                gates.add(PG)
        row['local_pending_gates'] = sorted(gates)
        row['component_consumption'] = {'U': consumed[rid], 'U_required': len(required),
            'U_remaining': sorted(required - justified), 'PFC': pfc_refs.get(rid)}
        # Replace historical open-edge prose only for gates actually discharged.
        row['remaining_gate_details'] = {g: v for g, v in row['remaining_gate_details'].items() if g in gates}
        if required - justified:
            row['remaining_gate_details'][UG] = sorted(required - justified)
    edges = qualify(rows, specs, baseline['run'])
    for rid, row in rows.items():
        if CG in row['pending_gates']:
            row['remaining_gate_details'][CG] = edges[rid]
        old = oldrows[rid]
        row['transition'] = {'old_qualification': old['qualification'], 'new_qualification': row['qualification'],
            'removed_gates': sorted(set(old['pending_gates']) - set(row['pending_gates'])),
            'added_gates': sorted(set(row['pending_gates']) - set(old['pending_gates'])),
            'companion_edge': edges.get(rid)}
    # Preserve every original status/site; attach explicit component decisions.
    refs = {(rid, r['property_id']): r for rid, records in consumed.items() for r in records}
    for r in report['unreachable_analysis']['records']:
        ref = refs.get((r['row_id'], r['property_id']))
        if ref:
            r['historical_decision'] = r['decision']
            r['historical_decision_basis'] = r['decision_basis']
            r['decision'] = 'ALLOWED_GENERATED_SAFETY_APPLICABILITY'
            r['decision_basis'] = 'Exact committed U record justifies source-local generated safety applicability; status remains UNREACHABLE. See consumed_U_record.'
            r['consumed_U_record'] = ref
    for rid, row in rows.items():
        row['historical_unreachable_decisions'] = row['unreachable_decisions']
        row['unreachable_decisions'] = dict(sorted(collections.Counter(r['decision'] for r in
            report['unreachable_analysis']['records'] if r['row_id'] == rid).items()))
    decisions = dict(sorted(collections.Counter(r['decision'] for r in report['unreachable_analysis']['records']).items()))
    report['unreachable_analysis']['summary']['decisions'] = decisions
    report['unreachable_analysis']['summary']['unresolved_applicability_records'] = len(unknown) - len(refs)
    unions = index(report['replacement_unions'], 'id', 'baseline unions')
    uspecs = index(request['replacement_unions'], 'id', 'request unions')
    need(set(unions) == set(uspecs), 'union namespace')
    for uid, union in unions.items():
        spec = uspecs[uid]
        need(union['members'] == spec['member_row_ids'] and len(union['members']) == len(set(union['members'])) == 4,
             'exact union members')
        members = [rows[rid] for rid in union['members']]
        need({m['domain_N'] for m in members} == {0, 1, 2, 3}, 'union N domain')
        covers = {c['message'] for m in members for c in m['required_covers'] if c['binding'] == 'EXACT_SAT_COVER_SEMANTIC'}
        covered = set(spec['required_cover_messages']) <= covers
        success = all(set(spec['required_success_messages']) <=
                      {s['message'] for s in m['required_success'] if s['binding'] in EXACT_SUCCESS} for m in members)
        union['member_qualification'] = {m['id']: m['qualification'] for m in members}
        union['required_cover_union'] = 'BOUND' if covered else 'PENDING'
        union['required_success_members'] = 'BOUND' if success else 'PENDING'
        union['qualification'] = 'QUALIFIED_BOUNDED_UNION' if covered and success and all(
            m['qualification'] == 'QUALIFIED' for m in members) else 'PENDING'
        union['transition'] = {'old_qualification': next(x for x in baseline['replacement_unions'] if x['id'] == uid)['qualification'],
                               'new_qualification': union['qualification'], 'exact_member_edges': union['members']}
    report.update(schema='ch8-s1-07-composed-acceptance-v3', entry_g0=TASK,
                  input_manifest_sha256=MANIFEST_SHA, source_reported_assurance=PFC_ASSURANCE,
                  independent_proof_credit='NONE', B1_credit='NONE', B2_credit='NONE',
                  review={'W14_input_components': 'PENDING', 'W14_composer': 'PENDING', 'CI_GO': False},
                  components={name: {'commit': commit, 'receipt': name + '/' + file,
                    'sha256': sha(encoded(data)), 'replay': 'EXACT_READ_ONLY_MATCH'}
                    for (name, commit), file, data in zip(COMMITS.items(), ('ACCEPT.json', 'U.json', 'PFC.json'), (baseline, u, pfc))})
    report['historical_pfc_analysis'] = report.pop('pfc_analysis')
    report['pfc_analysis'] = {'policy': PFC_ASSURANCE, 'bindings_consumed': pfc_refs,
                            'independent_compiler_MIR_binding_credit': 'NONE'}
    report['historical_totals'] = copy.deepcopy(baseline['totals'])
    totals = report['totals']
    totals.pop('pfc_same_compilation_pending')
    totals.update(rows_qualified=sum(r['qualification'] == 'QUALIFIED' for r in rows.values()),
                  pending_gate_rows=dict(sorted(collections.Counter(g for r in rows.values() for g in r['pending_gates']).items())),
                  unreachable_decisions=decisions, U_consumed=len(refs), U_remaining=len(unknown)-len(refs),
                  profiles_v4_pfc_bound=len(pfc_refs), profiles_v4_pfc_pending=sum(r['mode'] == 'PFC' for r in rows.values())-len(pfc_refs),
                  unions_qualified=sum(u['qualification'] == 'QUALIFIED_BOUNDED_UNION' for u in unions.values()),
                  companions_qualified=sum(e['qualification'] == 'QUALIFIED' for e in edges.values()))
    report['qualified_acceptance'] = 'PENDING' if any(r['pending_gates'] for r in rows.values()) else 'QUALIFIED_BOUNDED_SOURCE_OBSERVATIONS_ONLY'
    report['policy']['composition'] = 'Committed S1-07 only; exact U coverage and Profiles v4 PFC chains; transitive named companions; no S1-08 labels'
    report['limits'] = [
        'Source-reported bounded Profiles v4 policy trusts the pinned stock compiler; no independent compiler/MIR proof credit.',
        'Historical PFC open-edge analysis is retained for audit, not used as the effective policy verdict.',
        'All original success-message roles, covers, statuses, oracles, inventories, snapshots, exceptions and unsupported links are retained.',
        'Only fixed initialized N0..3 fixture domains; no general sorting theorem or domain completeness.',
        'W14 review remains PENDING. READY is readiness for review, never CI GO.']
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write only this accept-v3/ACCEPT.json')
    args = parser.parse_args()
    try:
        report = compose(*load())
        data = encoded(report)
        if args.write:
            (HERE / 'ACCEPT.json').write_bytes(data)
        else:
            need((HERE / 'ACCEPT.json').read_bytes() == data, 'ACCEPT.json replay mismatch')
        print(json.dumps({'replay': 'WRITTEN' if args.write else 'MATCH', 'sha256': sha(data), 'totals': report['totals']}, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, IndexError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'replay': 'ERROR', 'reason': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
