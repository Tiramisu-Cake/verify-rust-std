#!/usr/bin/env python3
"""Independent bounded offline review. No acquisition, native execution or policy writes."""
import base64
import collections
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
TASK = '0f39a22f0148755e7ba881736e77b54f74b01cb5'
ROOT = '27cdf2a7e7895344aa3be9c47b2867a9298c3e0f'
INTAKE = '842984040e87b8b8594653634b72df7d800ca198'
BASE = 'research/challenge-8/kani-k1/'
PACKET = BASE + 'kani3300/ch8-s4/run-44481580554/'
SOURCE = Path('/root/verify-rust-std-ch8-s4p-1-w13')
CHECKS = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def blob(rev, path, repo=REPO):
    return git(repo, 'show', rev + ':' + path)

def need(value, label):
    if not value:
        raise AssertionError(label)
    CHECKS.append(label)

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def located(prop):
    return (isinstance(prop.get('file'), str) and bool(prop['file'])
            and isinstance(prop.get('line'), str)
            and re.fullmatch('[1-9][0-9]*', prop['line']) is not None)

def main():
    started = time.monotonic()
    inputs_path = BASE + 'kani3300/ch8-s4/s4p1-intake-review-network-plan-inputs/'
    root = json.loads(blob(ROOT, inputs_path + 'INPUTS.json'))
    names = git(REPO, 'ls-tree', '-r', '--name-only', INTAKE, PACKET).decode().splitlines()
    files = {name.removeprefix(PACKET): blob(INTAKE, name) for name in names}
    manifest = json.loads(files['MANIFEST.json'])
    need(len(files) == 36 and len(manifest['files']) == 35, 'exact 36 committed files / 35 manifest hashes')
    need(set(files) == set(manifest['files']) | {'MANIFEST.json'}, 'manifest covers exact committed packet')
    need(sha(files['MANIFEST.json']) == root['intake']['manifest_sha256'], 'exact root-pinned manifest digest')
    need(sha(files['HANDOFF.md']) == root['intake']['HANDOFF_sha256'], 'exact root-pinned HANDOFF digest')
    for name, info in manifest['files'].items():
        need(len(files[name]) == info['bytes'] and sha(files[name]) == info['sha256'], 'immutable intake member ' + name)
    docs = {name: json.loads(data) for name, data in files.items() if name.endswith('.json')}
    gz = files['group-evidence.json.gz']
    raw = gzip.decompress(gz)
    need(sha(gz) == root['member_sha256'] and sha(raw) == root['payload_sha256'], 'separate sealed member and payload digests')
    compact = json.loads(raw)
    members = {}
    for name, entry in compact['files'].items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name, 'safe structured member ' + name)
        data = entry['text'].encode() if entry.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(entry['text'], validate=True)
        need(sha(data) == entry['sha256'] and len(data) == entry['bytes'], 'structured member digest ' + name)
        members[name] = json.loads(data)
    need(len(members) == 119 and compact['state'] == 'PACKAGED' and compact['error'] is None, 'all 119 compact structured members; complete packaging')
    request = docs['ROOTS.json']['request']
    rows = request['rows']
    qualifications = docs['QUALIFICATION.json']['rows']
    source_sha = root['pins']['source']['sha']
    summary = []
    independent_us = []
    independent_guards = []
    for index, (row, q) in enumerate(zip(rows, qualifications)):
        rid = row['id']
        prefix = 'groups/s3-' + rid + '/'
        group = members[prefix + 'receipt.json']
        stock = members[prefix + 'export.json']
        properties_doc = members[prefix + 'properties.json']
        props = properties_doc.get('harnesses', [{}])[0].get('properties', [])
        bm = members[prefix + 'binding-metadata.json']
        need(rid == q['id'] and row['mode'] == 'Original' and row['target'] is None, rid + ' ordered Original/null')
        need(bm['invocation_id'] == group['invocation_id'] and bm['argv'] == group['argv'], rid + ' same invocation and argv')
        need(q['native_registration']['attributes']['verified_stubs'] == [] and q['providers'] == [], rid + ' no verified summary providers')
        need(q['native_registration']['attributes']['stubs'] == ([{'original': 's2_swap_seam', 'replacement': 'weak_swap'}] if index == 2 else []), rid + ' only fixed negative seam')
        need(q['strict_expected_match'] is False and q['qualification_admitted'] is False, rid + ' strict rejection and no admission retained')
        if index < 6:
            native = stock['harnesses'][0]
            need(len(props) == len({p['id'] for p in props}) == native['n_properties'] == q['native_property_count'], rid + ' complete unique native property inventory')
            need(dict(collections.Counter(p['status'] for p in props)) == q['status_counts'], rid + ' exact native status partition')
            need(native['checks']['total'] + native['covers']['total'] == len(props), rid + ' check/cover total partition')
            for cl in {p['class'] for p in props}:
                need(dict(collections.Counter(p['status'] for p in props if p['class'] == cl)) == q['class_status_counts'][cl], rid + ' class/status ' + cl)
            need(native['outcome']['verdict'] == ('FAILURE' if index < 4 else 'SUCCESS'), rid + ' expected native verdict')
            failures = [p for p in props if p['status'] == 'FAILURE']
            need(len(failures) == (1 if index < 4 else 0), rid + ' no extra failures')
            if index < 4:
                need(failures[0]['description'] == ['S2_NEG_CHECKER_ORDER', 'S2_NEG_CHECKER_COUNT', 'S2_NEG_SORT13_WEAK', 'S4_NEG_CELL_COUNT'][index], rid + ' exact negative literal')
            need(all(p['status'] in {'SUCCESS', 'FAILURE', 'UNREACHABLE', 'SATISFIED'} for p in props), rid + ' no omitted unknown/error statuses')
            for role in row['roles']:
                found = [p for p in props if p['description'] == role['description']]
                need(len(found) == 1, rid + ' exact role cardinality ' + role['description'])
                p = found[0]
                need(p['class'] == role['class'] and p['status'] == role['status'] and p['line'] == str(role['line']) and p['file'].endswith('/export/' + role['file']), rid + ' literal class/status/location ' + role['description'])
            for p in props:
                if p['status'] == 'UNREACHABLE':
                    args = [a for a in docs['U-ARGUMENTS.json']['instances'] if a['root'] == rid and a['property']['id'] == p['id']]
                    need(len(args) == 1 and args[0]['property'] == p and args[0]['invocation_id'] == group['invocation_id'], rid + ' individual U identity ' + p['id'])
                    arg = args[0]
                    src = blob(source_sha, arg['source_file'], SOURCE)
                    need(sha(src) == arg['source_sha256'] and int(p['line']) == arg['source_line'] and bool(arg['source_local_argument']), rid + ' U source hash/line/argument ' + p['id'])
                    independent_us.append({'root': rid, 'id': p['id'], 'source_file': arg['source_file'], 'line': arg['source_line'], 'assessment': 'SOURCE_LOCAL_DEFINEDNESS_SOUND_WITH_STATED_PREMISES; EMITTER_MIR_ORIGIN_UNKNOWN'})
                if p['class'] == 'unsupported_construct':
                    args = [a for a in docs['GUARD-ARGUMENTS.json']['instances'] if a['root'] == rid and a['property'] == p]
                    need(len(args) == 1 and p['status'] == 'SUCCESS' and located(p), rid + ' exact retained guard ' + p['id'])
                    need(args[0]['unsupported_operation_general_support_claim'] is False, rid + ' guard is not general operation support')
                    independent_guards.append({'root': rid, 'property': p, 'assessment': 'RETAIN_EXACT_NATIVE_SUCCESS; NO_GENERAL_SUPPORT_OR_REACHABILITY_PROOF'})
            if index >= 4:
                case = docs['LOCATION-PROPOSAL.json']['cases'][index - 4]
                bad = [p for p in props if not located(p)]
                need(bad == [case['exact_property']] and len(bad) == 1, rid + ' one exact offending property')
                need(bad[0]['id'] == row['selector'] + '.unreachable.1' and bad[0]['display_id'] == bad[0]['id'] and bad[0]['class'] == 'unreachable' and bad[0]['status'] == 'SUCCESS' and bad[0]['description'] == 'unreachable code', rid + ' exact full missing-location dictionary')
                need(all(k in bad[0] and bad[0][k] is None for k in ['file', 'line']), rid + ' present-null location keys')
                need(case['full_property_inventory_sha256'] == sha(canon(props)) and case['invocation_id'] == group['invocation_id'] and case['native_counts']['n_properties'] == len(props), rid + ' location case counts/invocation/full inventory digest')
                need(case['status'] == 'NOT_APPLIED' and case['shared_emitter_source_MIR_origin'] == 'UNKNOWN' and q['producer']['status'] == 'UNKNOWN', rid + ' proposal inactive; original producer UNKNOWN')
                covers = [p for p in props if p['class'] == 'cover']
                need(len(covers) == (8 if index == 4 else 7) and all(p['status'] == 'SATISFIED' and located(p) for p in covers), rid + ' all exact length/witness SAT')
                need(len([p for p in props if p['class'] == 'unwind']) == 1 and all(p['status'] == 'SUCCESS' for p in props if p['class'] == 'unwind'), rid + ' observed unwind success')
        else:
            need(stock['run_state'] == 'INCOMPLETE' and 'harnesses' not in stock and not props, rid + ' inventory censored UNKNOWN; not zero/NOT_RUN')
            need(q['covers'] == q['U_count'] == q['unsupported_guards'] == q['native_property_count'] == 'UNKNOWN', rid + ' no invented roles/covers/U/guards counts')
            need(all(x['native_matches'] == [] and x['exact_match'] is False for x in q['literal_roles']), rid + ' all planned positive roles remain UNKNOWN')
        summary.append({k: q[k] for k in ['id', 'selector', 'mode', 'target', 'native_verdict', 'native_property_count', 'status_counts', 'class_status_counts', 'U_count', 'strict_expected_match', 'provisional_S1', 'producer']})
    need(len(rows) == len(qualifications) == 8 and len(independent_us) == 26 and len(independent_guards) == 7, 'all eight qualifications / 26 individual U / seven guards')
    prefix = docs['PREFIX.json']
    need(type(prefix['selected_roots']) is int and prefix['selected_roots'] == 8 and prefix['completed_prefix'] == [r['id'] for r in rows] and prefix['local_upload_equal'] and not prefix['global_stop'], 'selected int8 distinct from completed prefix; both replay routes')
    costs = []
    for index, cost in enumerate(docs['COST.json']['rows']):
        mem = cost['memory_admission']
        need(cost['effective_cap_kib'] == min(6291456, 12582912, mem['available_kib'] - 2097152), cost['id'] + ' observed available-memory admission formula')
        need(cost['execution']['child_shutdown_verified'] and cost['containment']['verified'] and cost['worker_supervision']['orphan_survivors_at_worker_exit'] == [], cost['id'] + ' verified cleanup and ownership')
        if index >= 6:
            e = cost['execution']
            need(cost['cutoff_cause'] == 'CHILD600_WALL_INCLUDING_COMPILE' and e['timed_out'] and e['termination_reason'] == 'timeout' and e['original_exit_code'] == -15 and e['signal'] == 15, cost['id'] + ' exact wall cutoff original exit/signal')
            need(cost['compile']['state'] == 'COMPLETE' and cost['compile_elapsed_upper_bound_seconds'] < 180 and 600 <= e['elapsed_seconds'] < 610 and e['rss_peak_kib'] < cost['effective_cap_kib'], cost['id'] + ' compile completed; no observed memory/compile cap trigger')
            need(cost['native_verification_time_s'] == 'UNKNOWN_CENSORED' and cost['worker_supervision']['cutoff'] is None and not cost['worker_supervision']['limit_initiated'], cost['id'] + ' native time censored; no outer/slot cutoff')
        costs.append({k: cost[k] for k in ['id', 'compile_elapsed_upper_bound_seconds', 'native_verification_time_s', 'native_wall_time_s', 'execution', 'memory_admission', 'effective_cap_kib', 'cutoff_cause', 'cutoff_phase', 'censoring']})
    # Run the exact committed reporting code in a disposable copy. Only its
    # output destination/repository root are redirected; code bytes stay pinned.
    projections = ['RESULT.json', 'ROOTS.json', 'COST.json', 'QUALIFICATION.json', 'METADATA-GAP.json', 'LOCATION-PROPOSAL.json', 'NATIVE-PROPERTIES.json', 'PROVENANCE.json', 'PREFIX.json', 'U-ARGUMENTS.json', 'SOURCE-GATES.json']
    supplemental = ['DEPENDENCIES.json', 'EPOCH-AUDIT.json', 'GUARD-ARGUMENTS.json', 'LENGTH-ROLES-SAT.json', 'LOCATION-COMPARISON.json', 'PROTECTED.json', 'SERIAL-ORDER.json', 'VALIDATION.json', 'AUDIT-VALIDATION.json']
    replay_started = time.monotonic()
    output = io.StringIO()
    with tempfile.TemporaryDirectory(prefix='s4p1-w14-review-') as td:
        temporary_repo = Path(td)
        git_dir = git(REPO, 'rev-parse', '--absolute-git-dir').decode().strip()
        (temporary_repo / '.git').write_text('gitdir: ' + git_dir + '\n')
        helper_path = BASE + 'kani3300/ch8-s3-s4/run-44460583125/replay.py'
        helper = temporary_repo / helper_path
        helper.parent.mkdir(parents=True)
        helper.write_bytes(blob(TASK, helper_path))
        work = temporary_repo / PACKET
        work.mkdir(parents=True)
        for name, data in files.items():
            (work / name).write_bytes(data)
        for script in ['replay.py', 'audit.py']:
            spec = importlib.util.spec_from_file_location('w14_' + script[:-3], work / script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            with contextlib.redirect_stdout(output):
                module.main()
        matches = {n: json.loads((work / n).read_bytes()) == docs[n] for n in projections + supplemental}
        need(all(matches.values()), 'all 11 primary and nine supplemental projections reproduce exactly')
        reproduced_validation = json.loads((work / 'VALIDATION.json').read_bytes())
        need(reproduced_validation['checks_count'] == 1163 and len(reproduced_validation['adverse_tests']) == 29 and len(reproduced_validation['location_adverse_tests']) == 66, 'exact 1163 checks / 29 authentic reader adverse / 66 hypothetical location adverse')
        need(json.loads((work / 'AUDIT-VALIDATION.json').read_bytes())['checks_count'] == 220, '220 supplemental author checks independently rerun')
    write('REPLAY.json', {'status': 'PASS', 'intake_commit': INTAKE, 'code_bytes': {n: sha(files[n]) for n in ['replay.py', 'audit.py']}, 'isolation': 'Exact scripts and task-pinned helper in disposable tree; .git points to existing local objects for read-only git show; no script edits or module overrides', 'stdout': output.getvalue(), 'projection_matches': matches, 'checks': 1163, 'adverse': 29, 'location_adverse': 66, 'supplemental_checks': 220, 'elapsed_seconds': time.monotonic() - replay_started, 'full_validate': False, 'native_rerun': False, 'acquisition': False})
    write('QUALIFICATION-AUDIT.json', {'status': 'PASS', 'rows': summary, 'U': independent_us, 'guards': independent_guards, 'scope': 'All inventories independently reconciled with the sealed compact structured member; all source-local U arguments reviewed by main reviewer. No AST/MIR/emitter proof.'})
    write('COST-AUDIT.json', {'status': 'PASS', 'campaign_elapsed_seconds': docs['COST.json']['campaign_elapsed_seconds'], 'setup': docs['COST.json']['setup'], 'caps': docs['COST.json']['caps'], 'rows': costs, 'resource_scope': docs['COST.json']['rss_metric'], 'unknown': ['exact backend/symex phase and exclusive time', 'uncensored native verification time/peak for network', 'signal timestamp', 'strict physical inode/MIR causality'], 'resource_escalation_recommendation': 'NONE; wall timeout does not establish benefit of more memory'})
    write('VALIDATION.json', {'status': 'PASS', 'independent_checks_count': len(CHECKS), 'independent_checks': CHECKS, 'elapsed_seconds': time.monotonic() - started, 'intake_files_verified': 36, 'manifest_hashes_verified': 35, 'member_count': 119, 'replay': 'REPLAY.json', 'no_source_evidence_policy_ledger_edits': True})
    print(json.dumps({'status': 'PASS', 'independent_checks': len(CHECKS), 'primary_projections': 11, 'supplemental_projections': 9, 'U': len(independent_us), 'guards': len(independent_guards)}))

if __name__ == '__main__':
    main()
