#!/usr/bin/env python3
"""Offline policy replay. Reads structured artifacts and bounded stdout projections only.

No verifier, collector, control mutation, or ordinal-based property binding.
UNKNOWN is intentional when this run did not retain the necessary records.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
K1 = HERE.parents[4]
CONTROL = Path('/root/kani-ch8-s1-04-depth-w13')
STD = Path('/root/verify-rust-std-ch8-s1-04-w13')
ART = Path('/root/ch8-s1-04-intake-w13/run-43830757263/artifacts')
CONTROL_SHA = '205b0e98c771a7e6c6b8ec28414494868bcca4e0'
SOURCE = '5be85699b8826e3286c0bf89efb9affefac0acb5'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
MACRO_ROWS = ('model_u8_n0_3', 'model_cell_n0_3', 'model_noncopy_n0_3')
REQUIRED_ROLES = {'postcondition', 'frame', 'relation', 'required_section'}
TOOL_FILES = (
    'kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs',
    'kani-compiler/src/codegen_cprover_gotoc/codegen/foreign_function.rs',
    'kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs',
    'kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs',
    'kani-driver/src/frontend/schema_utils.rs',
    'kani-driver/src/cbmc_property_renderer.rs',
)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    return json.loads(path.read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def binding_fixed(request):
    fixed = copy.deepcopy(request)
    for rid, invocation in zip(MACRO_ROWS, (66, 67, 68)):
        b = fixed['source_bindings'][rid]
        lines = (STD / b['file']).read_text().splitlines()
        require(sha(STD / b['file']) == b['sha256'], 'MACRO_SOURCE_HASH')
        require(b['locations'] == [{'line': invocation, 'source': lines[invocation-1]}], 'INVOCATION_ANCHOR')
        require(lines[28] == '        fn $name() {', 'MACRO_DECLARATION')
        require(lines[invocation-1].startswith('positive!('+rid+','), 'MACRO_ROW_INVOCATION')
        b['locations'].append({'line': 29, 'source': lines[28]})
    return fixed


def unsupported_link(p, h):
    """An embedded same-harness PropertyExport is richer than a success count."""
    require(p['class'] == 'unsupported_construct', 'UNSUPPORTED_CLASS')
    require(re.fullmatch(r'.+\.unsupported_construct\.[1-9][0-9]*', p['id']), 'UNSUPPORTED_ID')
    require(p['status'] == 'SUCCESS', 'REACHABLE_OR_UNKNOWN_UNSUPPORTED')
    require(p['id'] not in h['checks']['failure'] + h['checks']['unreachable'], 'UNSUPPORTED_BUCKET_CONFLICT')
    require(isinstance(p['description'], str) and p['description'], 'UNSUPPORTED_DESCRIPTION')
    require(isinstance(p['file'], str) and p['file'].startswith('/home/runner/work/kani/kani/export/'), 'UNSUPPORTED_FILE')
    require(isinstance(p['line'], str) and p['line'].isdigit(), 'UNSUPPORTED_LINE')
    return dict(p, decision='ALLOWED_UNREACHABLE_CONSTRUCT_IN_THIS_MODEL',
                same_row_selector=h['name'], semantics='assert(false); assume(false)',
                tool_sha=TOOL, generator_sites=[
                    'assert.rs:129-145,214-220,278-324', 'foreign_function.rs:256-261',
                    'intrinsic.rs:91-95 -> assert.rs:224-231', 'overrides/hooks.rs:228-240'],
                export_site='schema_utils.rs:768-772; PropertyExport::from_property:495-505',
                assurance='PINNED_GENERATOR_CHAIN_AND_SAME_ROW_EXACT_ID_CLASS_STATUS_SITE')


def role_decision(review):
    """No helper exemption; a mandatory unreachable property is always a blocker."""
    if not review or not review.get('exact_source_site_bound'):
        return 'UNKNOWN'
    if review.get('role') in REQUIRED_ROLES:
        return 'BLOCKED_MANDATORY_OBLIGATION_UNREACHABLE'
    if review.get('role') == 'defensive_branch' and review.get('reason'):
        return 'ALLOWED_REVIEWED_DEFENSIVE_BRANCH'
    return 'UNKNOWN'


def cover_message_table(row, h, records):
    """Bind by retained exact description, never by cover number or list order."""
    table = []
    for message in row.get('required_cover_messages', []):
        found = [p for p in records if p.get('description') == message and p.get('id') in h['covers']['satisfied']]
        bound = len(found) == 1 and found[0].get('status') == 'SATISFIED'
        table.append({'message': message, 'property_id': found[0]['id'] if bound else None,
                      'status': 'BOUND' if bound else 'UNKNOWN_DESCRIPTION_NOT_RETAINED',
                      'source_message': 'REVIEWED_SOURCE_LITERAL_OR_BRIDGE_CONCAT_STRINGIFY',
                      'post_target_source_review': 'SOURCE_ONLY_NOT_EXPORT_BOUND'})
    return table


def inventory(h):
    checks, covers = h['checks'], h['covers']
    for bucket in (checks, covers):
        require(type(bucket['total']) is int and bucket['total'] >= 0, 'TOTAL')
    cb = ('failure', 'unreachable', 'undetermined', 'error', 'unknown', 'other')
    vb = ('satisfied', 'unsatisfiable', 'unreachable', 'undetermined', 'error', 'unknown', 'other')
    for bucket, names in ((checks, cb), (covers, vb)):
        for key in names:
            require(isinstance(bucket[key], list), 'BUCKET_LIST')
            require(all(isinstance(p, str) and p for p in bucket[key]), 'ID_TYPE_OR_UNKNOWN_STATUS')
    require(type(checks['success']) is int and checks['success'] >= 0, 'SUCCESS_COUNT')
    require(checks['total'] == checks['success'] + sum(len(checks[k]) for k in cb), 'CHECK_PARTITION')
    require(covers['total'] == sum(len(covers[k]) for k in vb), 'COVER_PARTITION')
    ids = [p for k in cb for p in checks[k]] + [p for k in vb for p in covers[k]]
    require(len(ids) == len(set(ids)), 'DUPLICATE_PROPERTY_ID')
    require(h['n_properties'] == checks['total'] + covers['total'], 'PROPERTY_TOTAL')
    require(type(h['n_failed']) is int and h['n_failed'] == len(checks['failure']) == len(h['failed_properties']), 'FAILURE_COUNT')
    require({p['id'] for p in h['failed_properties']} == set(checks['failure']), 'FAILURE_IDS')
    require(all(not checks[k] for k in ('undetermined', 'error', 'unknown', 'other')), 'INCOMPLETE_CHECK_STATUS')
    require(all(not covers[k] for k in ('unsatisfiable', 'undetermined', 'error', 'unknown', 'other')), 'INCOMPLETE_COVER_STATUS')


def bounded_output_audit(path, group):
    queries = {}
    for key, pattern, cap in (
        ('rich_property_records', r'^Check [0-9]+:|^[ \t]+- (Description|Location|Status):', 20),
        ('harness_markers', r'^Checking harness ', 20),
        ('terse_counts', r'^ \*\* .* (failed|cover properties satisfied)', 40),
    ):
        cp = subprocess.run(['rg', '--color', 'never', '--no-heading', '-n', '-m', str(cap), pattern, str(path)],
                            capture_output=True, text=True)
        require(cp.returncode in (0, 1) and len(cp.stdout.encode()) < 12000, 'BOUNDED_QUERY')
        queries[key] = {'pattern': pattern, 'max_matches': cap, 'exit': cp.returncode,
                        'projection': cp.stdout, 'projection_sha256': digest(cp.stdout.encode())}
    require(queries['rich_property_records']['exit'] == 1, 'UNEXPECTED_RICH_RECORDS_REVIEW_NEEDED')
    # Hash bytes without inspecting/copying raw contents. No complete raw log read into Python.
    actual = subprocess.check_output(['sha256sum', str(path)], text=True).split()[0]
    require(actual == group['stdout']['sha256'], 'STDOUT_HASH')
    require(path.stat().st_size == group['stdout']['captured_bytes'] == group['stdout']['original_bytes'], 'STDOUT_CAPTURE')
    markers = re.findall(r'^\d+:Checking harness (.+)\.\.\.$', queries['harness_markers']['projection'], re.M)
    require(len(markers) == len(set(markers)) == len(group['selectors']) and set(markers) == set(group['selectors']), 'MARKER_SET')
    return {'file': str(path), 'sha256': actual, 'method': 'BOUNDED_TARGETED_RG_ONLY; NO_FULL_LOG_CONTENT_READ', 'queries': queries}


def main():
    payload = CONTROL / 'ch8-s1-control'
    require(git(CONTROL, 'rev-parse', 'HEAD').decode().strip() == CONTROL_SHA, 'CONTROL_SHA')
    require(git(STD, 'rev-parse', 'HEAD').decode().strip() == SOURCE, 'SOURCE_SHA')
    require(not git(CONTROL,'status','--porcelain') and not git(STD,'status','--porcelain'), 'DIRTY_PINNED_CHECKOUT')
    request = read(payload / 'CI-REQUEST.json')
    require(request['std_sha'] == SOURCE and request['tool_sha'] == TOOL, 'PINS')
    require(git(STD, 'rev-parse', SOURCE+'^{tree}').decode().strip() == request['std_tree'], 'SOURCE_TREE')
    require(git(CONTROL, 'rev-parse', TOOL+'^{tree}').decode().strip() == request['tool_tree'], 'TOOL_TREE')
    for rel, expected in request['ci_payload_sha256'].items():
        require(sha(CONTROL / rel) == expected, 'CONTROL_FILE:'+rel)
    for rel, expected in request['changed_file_sha256'].items():
        require(sha(STD / rel) == expected and digest(git(STD, 'show', SOURCE+':'+rel)) == expected, 'SOURCE_FILE:'+rel)
    tool_sources = {p: git(CONTROL, 'show', TOOL+':'+p) for p in TOOL_FILES}
    for rel, data in tool_sources.items():
        require(data == git(CONTROL, 'show', CONTROL_SHA+':'+rel), 'TOOL_CHAIN_DRIFT')
    sys.path.insert(0, str(payload))
    runner = load('s104_runner', payload / 'runner.py')
    fixed = binding_fixed(request)
    subprocess.run(['git', '-C', str(CONTROL), 'apply', '--check', str(BASE/'source-binding-fix.patch')], check=True)
    # Establish exact equality of the provided patch and the in-memory classifier adjustment.
    import difflib
    patch = ''.join(difflib.unified_diff((payload/'CI-REQUEST.json').read_text().splitlines(True),
                  (json.dumps(fixed, indent=2)+'\n').splitlines(True),
                  fromfile='a/ch8-s1-control/CI-REQUEST.json', tofile='b/ch8-s1-control/CI-REQUEST.json'))
    require(patch == (BASE/'source-binding-fix.patch').read_text(), 'PATCH_EXACT_DELTA')
    original_rows = {r['id']: r for r in read(BASE/'ROWS.json')}
    collected = read(BASE/'collected.json')
    require(len(original_rows) == len(collected['rows']) == 35 and collected['missing_groups'] == [], 'INTAKE_SET')
    out, audits, groups = [], [], []
    for ep in sorted(ART.glob('*/groups/*/export.json')):
        gp = ep.parent
        e, g = read(ep), read(gp/'receipt.json')
        gid = g['group']
        saved = BASE/'evidence'/gid/'export.json'
        require(ep.read_bytes() == saved.read_bytes() and sha(ep) == g['export_sha256'], 'EXPORT_HASH')
        expected_source = {k: request[k] for k in ('std_sha','std_tree','tool_sha','tool_tree','changed_file_sha256')}
        require(g['source_before'] == g['source_after'] == expected_source, 'SOURCE_SNAPSHOTS')
        expected_files = dict(request['changed_file_sha256'])
        if g['variant'] != 'production':
            variant = request['variants'][g['variant']]
            expected_files.update(variant['changed_file_sha256'])
            require(g['source_under_test']['patch_sha256'] == variant['sha256'] and
                    sha(payload/variant['patch']) == variant['sha256'], 'VARIANT_PATCH')
        require(g['source_under_test']['base_std_sha'] == SOURCE and
                g['source_under_test']['variant'] == g['variant'] and
                g['source_under_test']['file_sha256'] == expected_files, 'SOURCE_UNDER_TEST')
        require(g['request_sha256'] == sha(payload/'CI-REQUEST.json') and g['state'] == 'COMPLETE', 'GROUP_COMPLETE')
        ex = g['execution']
        require(all(ex[k] is False for k in ('timed_out','stdout_truncated','stderr_truncated','output_truncated')) and ex['signal'] is None and ex.get('termination_reason') is None, 'INTERRUPTED_GROUP')
        require('--output-format=terse' in g['argv'], 'OUTPUT_FORMAT')
        before, after = (g['tool_fingerprints_'+s] for s in ('before','after'))
        require(before['required_hashes_present'] and after['required_hashes_present'], 'BINARIES_MISSING')
        require({k:v['sha256'] for k,v in before['binaries'].items()} == {k:v['sha256'] for k,v in after['binaries'].items()}, 'BINARY_DRIFT')
        audits.append(bounded_output_audit(gp/'stdout.log', g))
        groups.append({'id': gid, 'export_sha256': sha(ep), 'receipt_sha256': sha(gp/'receipt.json'),
                       'source_tool_config': 'MATCHED_REQUEST_AND_UNCHANGED_WITHIN_GROUP', 'original_exit': ex['original_exit_code']})
        for h in e['harnesses']:
            row, = [r for r in request['rows'] if r['selector'] == h['name'] and r['variant'] == g['variant']]
            rid = row['id']
            inventory(h)
            binding = fixed['source_bindings'][rid]
            for loc in binding['locations']:
                require((STD/binding['file']).read_text().splitlines()[loc['line']-1] == loc['source'], 'SOURCE_ANCHOR')
            parsed = runner.parse_export(ep, row, source_binding=binding,
                std=Path('/home/runner/work/kani/kani/export'), group_selectors=g['selectors'])
            require(parsed['state'] in {'INCOMPLETE_CHECK_INVENTORY','COVERAGE_INCOMPLETE','VALIDATED_OBSERVATION','NEGATIVE_ORACLE_UNBOUND'}, 'PREFLIGHT:'+parsed['state'])
            require(h['attributes']['stubs'] == [] and h['attributes']['verified_stubs'] == [], 'STUBS')
            source = (STD/binding['file']).read_text()
            require(sha(STD/binding['file']) == binding['sha256'], 'BINDING_SOURCE_HASH')
            for message in row.get('required_success_messages', []) + row.get('required_cover_messages', []):
                if rid == 'ordinary-bridge':
                    ty = message.removeprefix('efficient swap predicate for ')
                    require(message.startswith('efficient swap predicate for ') and
                            'check!('+ty.replace(' ', '')+',' in source.replace(' ', '') and
                            'concat!("efficient swap predicate for ", stringify!($t))' in source,
                            'BRIDGE_SOURCE_MESSAGE')
                else:
                    require('"'+message+'"' in source, 'REQUIRED_SOURCE_LITERAL:'+rid+':'+message)
            unsupported = [unsupported_link(p, h) for p in h['unsupported_constructs']]
            unreachable = [{'id': pid, 'status': 'UNREACHABLE', 'function_from_id': pid.rsplit('.assertion.',1)[0],
                            'file': None, 'line': None, 'description': None, 'role': 'UNKNOWN',
                            'exact_source_site_bound': False, 'decision': role_decision(None),
                            'target_wrapper_relation': 'UNRESOLVED_SAME_ROW_SOURCE_SITE',
                            'reason': 'Export retains ID only; terse output has no property record. No helper or ordinal exemption.'}
                           for pid in h['checks']['unreachable']]
            covers = [{'id': pid, 'status': key.upper(), 'description': None, 'file': None, 'line': None,
                       'message_binding': 'UNKNOWN_DESCRIPTION_NOT_RETAINED'}
                      for key, values in h['covers'].items() if isinstance(values, list) for pid in values]
            reasons = []
            if unreachable:
                reasons.append('UNREACHABLE_EXACT_SOURCE_SITE_AND_ROLE_NOT_RETAINED')
            cover_table = cover_message_table(row, h, [])
            if any(c['property_id'] is None for c in cover_table):
                reasons.append('COVER_MESSAGE_TO_EXACT_ID_NOT_RETAINED')
            if row.get('required_success_messages'):
                reasons.append('REQUIRED_SUCCESS_EXACT_ID_DESCRIPTION_SITE_NOT_RETAINED')
            if row['mode'] == 'PFC':
                reasons.append('EXACT_CHECK_MODIFIES_WRAPPER_AND_REQUIRED_CONTRACT_PROPERTIES_PENDING')
            observation = h['outcome']['verdict']
            oracle = row.get('oracle')
            if row['expected'] == 'DETECTED' and oracle:
                require(runner.negative_oracle.matches(h, oracle), 'PREDECLARED_NEGATIVE_ORACLE')
                # This frozen oracle is ID/file/line/class based: the stock
                # assert! description is the pre-existing runtime-message placeholder.
                require('"'+oracle['intended_message']+'"' in '\n'.join(oracle['assertion_context']), 'NEGATIVE_SOURCE_MESSAGE')
                require(sha(STD/oracle['file']) == oracle['source_sha256'], 'ORACLE_SOURCE_HASH')
                lines = (STD/oracle['file']).read_text().splitlines()
                start = oracle['line']-1
                require(lines[start] == oracle['source_line'] and
                        lines[start:start+len(oracle['assertion_context'])] == oracle['assertion_context'], 'ORACLE_SOURCE_CONTEXT')
                observation = 'EXPECTED_EXACT_PREDECLARED_ORACLE'
            attachment = row['variant'] in ('activation-default','activation-override')
            if attachment:
                require(oracle is None and len(h['failed_properties']) == 1, 'ATTACHMENT_ORACLE_HISTORY')
                reasons += ['NO_PREDECLARED_ATTACHMENT_ORACLE', 'ATTACHMENT_POST_RETURN_COVER_UNREACHABLE']
                observation = 'OBSERVED_UNQUALIFIED'
            if row['expected'] == 'SUCCESS':
                require(h['outcome'] == {'kind':'COMPLETED','verdict':'SUCCESS'} and not h['checks']['failure'], 'POSITIVE_VERDICT')
                require(not h['covers']['unreachable'], 'POSITIVE_COVER_UNREACHABLE')
            status = ('OBSERVED_UNQUALIFIED' if attachment else
                      'ACCEPTED_NEGATIVE_OBSERVATION' if observation == 'EXPECTED_EXACT_PREDECLARED_ORACLE' and not reasons else
                      'UNKNOWN')
            result = {'id': rid, 'group': gid, 'selector': row['selector'], 'variant': row['variant'],
                      'mode': row['mode'], 'expected': row['expected'], 'status': status,
                      'observation': observation, 'pending_reasons': reasons, 'proof_credit': 'NONE',
                      'preflight_state': parsed['state'], 'original_oracle_state': original_rows[rid]['oracle_state'],
                      'source_binding': binding, 'macro_adjustment': rid in MACRO_ROWS,
                      'contract_export': h['contract'],
                      'contract_binding_assurance': 'EXACT_SOURCE_ATTRIBUTE_ONLY; WRAPPER_CHAIN_PENDING' if row['mode']=='PFC' else 'NOT_APPLICABLE_ORIGINAL_MODE',
                      'checks': h['checks'], 'covers': covers, 'cover_message_table': cover_table,
                      'required_success': [{'message': m, 'property_id': None, 'binding': 'UNKNOWN_NOT_RETAINED'} for m in row.get('required_success_messages',[])],
                      'unsupported': unsupported, 'unreachable': unreachable, 'failures': h['failed_properties'],
                      'predeclared_oracle': oracle, 'source_reported_outcome': h['outcome'],
                      'assurance': 'OFFLINE_SOURCE_REPORTED_BOUNDED_OBSERVATION; NO_INDEPENDENT_B1_OR_B2',
                      'per_root_rss_status': original_rows[rid]['per_root_rss_status']}
            if attachment:
                result['future_oracle_proposal'] = {'status':'PROPOSED_NEXT_PACKAGE_ONLY; NOT_CURRENT_DETECTION',
                    'selector': row['selector'], 'mode': row['mode'], 'target': binding['target'],
                    'variant': row['variant'], 'variant_spec': request['variants'][row['variant']],
                    'property': h['failed_properties'][0], 'require_only_this_failure': True,
                    'requires': ['Freeze and independently review before next dispatch',
                                 'Bind exact check/modifies wrapper to this target/type/source/tool/config',
                                 'Include same-pin unmutated positive companion and reachable return covers',
                                 'Record mutant-return cover as expected UNREACHABLE after false ensures; not positive vacuity evidence']}
            out.append(result)
    order = {r['id']: i for i,r in enumerate(request['rows'])}
    out.sort(key=lambda r: order[r['id']])
    require(len(groups) == 14 and len(out) == len({r['id'] for r in out}) == 35, 'FINAL_SET')
    totals = {'rows':len(out), 'accepted_positive':0,
              'accepted_negative_observations':sum(r['status']=='ACCEPTED_NEGATIVE_OBSERVATION' for r in out),
              'unknown':sum(r['status']=='UNKNOWN' for r in out),
              'observed_unqualified':sum(r['status']=='OBSERVED_UNQUALIFIED' for r in out),
              'positive_success':sum(r['source_reported_outcome']['verdict']=='SUCCESS' for r in out),
              'expected_predeclared_negatives':sum(r['observation']=='EXPECTED_EXACT_PREDECLARED_ORACLE' for r in out),
              'unsupported_success_linked':sum(len(r['unsupported']) for r in out),
              'unreachable_checks_unresolved':sum(len(r['unreachable']) for r in out),
              'covers_satisfied':sum(p['status']=='SATISFIED' for r in out for p in r['covers']),
              'covers_unreachable':sum(p['status']=='UNREACHABLE' for r in out for p in r['covers'])}
    require(totals == {'rows':35,'accepted_positive':0,'accepted_negative_observations':3,
                      'unknown':30,'observed_unqualified':2,'positive_success':27,
                      'expected_predeclared_negatives':6,'unsupported_success_linked':76,'unreachable_checks_unresolved':413,
                      'covers_satisfied':113,'covers_unreachable':2}, 'EXPECTED_TOTALS')
    unions = [dict(u, status='PENDING', eligible_for_review=False,
                   reason='Every member requires exact successful property/cover/wrapper and unreachable-role binding')
              for u in request['replacement_unions']]
    report = {'schema':'ch8-s1-04-offline-acceptance-v1', 'run':43830757263,
              'stage':'COMPLETE_OFFLINE_ACCEPTANCE_REVIEW', 'qualified_acceptance':'PENDING', 'proof_credit':'NONE',
              'source_sha':SOURCE,'tool_sha':TOOL,'control_sha':CONTROL_SHA,
              'request_sha256':sha(payload/'CI-REQUEST.json'), 'entry_g0':'90e4c41b6f4e2dbe33c347afa7f5c286783c94a5',
              'intake_g0':git(K1,'rev-parse','149a94c8fa').decode().strip(),
              'policy_sha256':sha(K1/'ACCEPTANCE-POLICY-BATCH.md'),
              'input_sha256':{p.name:sha(p) for p in [BASE/'ROWS.json',BASE/'collected.json',BASE/'RESULT.md',BASE/'source-binding-fix.patch']},
              'tool_source_sha256':{p:digest(b) for p,b in tool_sources.items()}, 'totals':totals,
              'groups':groups,'rows':out,'replacement_unions':unions,'bounded_output_audits':audits,
              'limits':['Success count is not a complete named success inventory',
                        'Same-run rich records are absent; cross-run or ordinal guesses are not substitutes',
                        'Coordinates and receipts do not establish AST/MIR/parser-input binding',
                        'Artifact ZIP digest source-reported only; no independent proof credit'],
              'historical_receipts_and_ledgers_changed':False,'control_changed':False,'local_verifier_execution':'NOT_RUN'}
    (HERE/'ACCEPT.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(totals))


if __name__ == '__main__':
    main()
