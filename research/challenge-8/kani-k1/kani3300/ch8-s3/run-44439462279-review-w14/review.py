#!/usr/bin/env python3
"""W14 bounded reporting review; no native execution or policy activation."""
import base64
import collections
import copy
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
INTAKE = '5d9439a7641c929838bf075c6aa6533a353ee92d'
TASK = 'e5a9d8f40c82408abf033466e0d50e94d77fad31'
PREFIX = 'research/challenge-8/kani-k1/kani3300/ch8-s3/'
AUTHOR = PREFIX + 'run-44439462279/'
SOURCE = Path('/root/verify-rust-std-ch8-s3-2-r1-w13')
TOOL = Path('/root/kani-upstream-ch8-s1')
CONTROL = Path('/root/kani-ch8-s3-2-r1-control-w13')
STD = Path('/home/runner/work/kani/kani/export')
CHECKS = []


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':')).encode()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def blob(repo, rev, path):
    return git(repo, 'show', rev + ':' + path)


def read(name):
    return json.loads(blob(REPO, INTAKE, AUTHOR + name))


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def need(value, label):
    if not value:
        raise AssertionError(label)
    CHECKS.append(label)


def located(p):
    return (isinstance(p.get('file'), str) and bool(p['file']) and
            isinstance(p.get('line'), str) and re.fullmatch('[1-9][0-9]*', p['line']) is not None)


def main():
    manifest = read('MANIFEST.json')
    tracked = git(REPO, 'ls-tree', '-r', '--name-only', INTAKE, AUTHOR).decode().splitlines()
    need(len(tracked) == 35, 'exact intake35 tracked files')
    need(len(manifest['files']) == 33, 'exact intake33 manifest entries')
    for name, entry in manifest['files'].items():
        b = blob(REPO, INTAKE, AUTHOR + name)
        need(len(b) == entry['bytes'] and sha(b) == entry['sha256'], 'intake manifest ' + name)
        need((REPO / AUTHOR / name).read_bytes() == b, 'working copy exact intake ' + name)
    expected_manifest_lines = [entry['sha256'] + '  ' + name for name, entry in manifest['files'].items()]
    need(blob(REPO, INTAKE, AUTHOR + 'MANIFEST.sha256').decode().splitlines() == expected_manifest_lines,
         'manifest sha256 view matches JSON')
    pins = json.loads(blob(REPO, TASK, PREFIX + 'postrun-s3-2-r1-terminal/INPUTS.json'))
    deps = read('DEPENDENCIES.json')
    dependency_count = 0
    for d in deps['g0_dependencies']:
        need(git(REPO, 'rev-parse', d['commit'] + '^{tree}').decode().strip() == d['tree'], 'dependency tree ' + d['name'])
        for name, entry in d['files'].items():
            b = blob(REPO, d['commit'], name)
            need(len(b) == entry['bytes'] and sha(b) == entry['sha256'], 'dependency blob ' + d['name'] + '/' + name)
            dependency_count += 1
    need(dependency_count == 55, '55 committed dependency blobs')
    repos = {'source': SOURCE, 'tool': TOOL, 'control': CONTROL, 'trigger': CONTROL}
    for kind, identity in deps['source_tool_control_trigger'].items():
        repo = repos[kind]
        need(git(repo, 'rev-parse', identity['sha'] + '^{tree}').decode().strip() == identity['tree'], kind + ' tree')
        need(git(repo, 'show', '-s', '--format=%P', identity['sha']).decode().strip() == identity['sole_parent'], kind + ' sole parent')
    source = pins['source']['sha']
    tool = pins['tool']['sha']
    ctrl = pins['control_candidate']['sha']
    head = pins['trigger']['sha']
    for group, repo, rev, prefix in [
        ('source_files_sha256', SOURCE, source, ''),
        ('tool_source_trace_sha256', TOOL, tool, ''),
        ('frozen_control_source_closure', CONTROL, ctrl, 'ch8-s1-control/')]:
        for name, entry in deps[group].items():
            b = blob(repo, rev, prefix + name)
            need(sha(b) == (entry if isinstance(entry, str) else entry['sha256']), group + '/' + name)
            if isinstance(entry, dict):
                need(len(b) == entry['bytes'], 'closure size ' + name)
    need([len(deps[k]) for k in ['source_files_sha256', 'tool_source_trace_sha256', 'frozen_control_source_closure']] == [41, 6, 84], '41source6tool84control closure')
    request_bytes = blob(CONTROL, head, pins['request']['path'])
    request = json.loads(request_bytes)
    need(sha(request_bytes) == pins['request']['sha256'] == deps['request_sha256'], 'request exact fullpin')
    need(request_bytes == blob(CONTROL, ctrl, pins['request']['path']), 'executed/reviewed request same bytes')
    workflow = blob(CONTROL, head, pins['request']['workflow_path'])
    need(sha(workflow) == pins['request']['workflow_sha256'] == deps['workflow_sha256'], 'workflow exact fullpin')
    need(workflow == blob(CONTROL, ctrl, pins['request']['workflow_path']), 'executed/reviewed workflow same bytes')
    need(request['s3']['caps'] == pins['caps'], 'exact requested caps')
    need(request['unreachable_admission'] == pins['policy']['unreachable_admission'] and
         request['unreachable_admission']['mode'] == 'REJECT_ALL' and not request['unreachable_admission']['enabled'], 'strict U reject-all disabled proposal')

    gz = blob(REPO, INTAKE, AUTHOR + 'group-evidence.json.gz')
    need(sha(gz) == '324cfc84365d23ccca6113f97686cbf780f836fdb4adcd124e198ee191886556', 'owner exact compact payload')
    raw = gzip.decompress(gz)
    packet = json.loads(raw)
    need(packet['schema'] == 'ch8-s1-05-artifact-v1' and packet['state'] == 'PACKAGED' and packet['error'] is None, 'compact schema/state')
    members = {}
    data = {}
    for name, entry in packet['files'].items():
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts and '\\' not in name and path.suffix == '.json', 'bounded structured member ' + name)
        b = entry['text'].encode() if entry.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(entry['text'], validate=True)
        need(len(b) == entry['bytes'] and sha(b) == entry['sha256'], 'compact member digest ' + name)
        members[name] = b
        data[name] = json.loads(b)
    need(len(members) == 119, '119 authenticated structured members')
    integrity = read('artifact-integrity.json')
    need(integrity['digest_checked_before_zip_open'] and not integrity['transport_saved'] and
         integrity['bytes'] == 422238 and 'sha256:' + integrity['sha256'] == pins['artifact']['digest'], 'source-reported transport digest-first receipt; no reacquisition')
    need(sha(raw) == integrity['uncompressed_sha256'] and sha(gz) == integrity['payload_sha256'], 'compact provenance hashes')
    run = read('github-run.json')
    need((run['id'], run['run_attempt'], run['status'], run['conclusion'], run['event'], run['head_sha'], run['head_branch'], run['path']) ==
         (44439462279, 1, 'completed', 'failure', 'push', head, pins['branch'], pins['request']['workflow_path']), 'frozen connected run exact terminal metadata')
    art = read('github-artifacts.json')['artifacts']
    need(len(art) == 1 and all(art[0][k] == pins['artifact'][v] for k, v in [('id', 'id'), ('name', 'name'), ('size_in_bytes', 'transport_bytes'), ('digest', 'digest')]), 'artifact metadata identity')
    need(data['campaign-start.json']['request_data'] == request, 'compact embedded canonical request')
    need(data['baseline.json']['control'] == {'sha': head, 'tree': pins['trigger']['tree'], 'parent': pins['trigger']['sole_parent'], 'dirty': ''}, 'actual control checkout source-reported clean')

    q = read('QUALIFICATION.json')
    need([x['id'] for x in q['rows']] == [x['id'] for x in request['rows']] == request['s3']['selected'], 'eight exact rows/order')
    rows = []
    all_u = []
    all_guards = []
    cases = []
    adverse = []
    with tempfile.TemporaryDirectory(prefix='w14-s32-review-') as td:
        tmp = Path(td)
        reader = tmp / 'reader'
        reader.mkdir()
        for name in deps['frozen_control_source_closure']:
            target = reader / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob(CONTROL, ctrl, 'ch8-s1-control/' + name))
        sys.path.insert(0, str(reader))
        runner = importlib.import_module('runner')
        campaign = importlib.import_module('s32_campaign')
        public = importlib.import_module('collect')
        evidence = importlib.import_module('s3_evidence')
        rich = importlib.import_module('rich_evidence')
        policy = importlib.import_module('s32_policy')
        materialized = tmp / 'materialized'
        upload = tmp / 'upload'
        materialized.mkdir()
        upload.mkdir()
        for name, b in members.items():
            path = materialized / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b)
        (upload / 'group-evidence.json.gz').write_bytes(gz)
        need(list(upload.iterdir()) == [upload / 'group-evidence.json.gz'], 'fresh upload-only directory')
        local_result = campaign.collect([materialized], request)
        upload_result = public.collect([upload], request)
        need(local_result == upload_result == read('PREFIX-REPLAY.json')['collector'], 'independent materialized/public-upload/author prefix equality')
        need(list(campaign.sealed(materialized)) == request['s3']['selected'], 'eight durable completion seals')
        need(not upload_result['global_stop'] and not upload_result['selected_missing_groups'], 'no global stop or missing selected')
        need(data['receipt.json']['state'] == 'SELECTED_PARTIAL' and data['receipt.json']['stop_reason'] is None, 'campaign partial continuation')
        for rank, (row, qr) in enumerate(zip(request['rows'], q['rows']), 1):
            rid = row['id']
            selector = row['selector']
            gp = 'groups/s3-' + rid + '/'
            g, co, stock, pr, bm = [data[gp + n] for n in ['receipt.json', 'compile/receipt.json', 'export.json', 'properties.json', 'binding-metadata.json']]
            life = data['workers/' + rid + '-lifecycle.json']
            sup = data['workers/' + rid + '-supervision.json']
            can = data[rid + '/receipt.json']
            ex = g['execution']
            need(evidence.provenance(g, co, request, rid, sha(request_bytes)), rid + ' all-state provenance')
            protected = evidence.protected(g, request, data['baseline.json'], sup, sha(request_bytes))
            need(not protected['observed_errors_ignored'], rid + ' protected no ignored errors')
            need(campaign.snapshots.validate_pair(data['baseline.json'], life['pre'], life['post'], life['context']), rid + ' E0/controller-pre/post source/control/tool/request')
            for label, snap in [('E0', data['baseline.json']['binaries']), ('pre', life['pre']['binaries']), ('workerBEFORE', g['tool_fingerprints_before']), ('workerAFTER', g['tool_fingerprints_after']), ('post', life['post']['binaries'])]:
                need(runner.fingerprints_match(data['baseline.json']['binaries'], snap), rid + ' binary identity ' + label)
            need(g['argv'] == runner.build_argv(STD, Path('/home/runner/work/kani/kani/tool'), [selector], row['unwind'], Path('/home/runner/work/_temp/ch8-s1-receipts') / (gp + 'export.json')), rid + ' exact singleton argv')
            need(g['native_start_verified'] and [x['selector'] for x in g['native_start_events']] == [selector] and g['unwind'] == row['unwind'] and g['effective_cfg'] == request['flags']['RUSTFLAGS'], rid + ' start cfg unwind')
            need(g['cargo_target_dir'] == str(STD / 'target/ch8-s1-cargo' / g['invocation_id']), rid + ' fresh namespace')
            need(bm['invocation_id'] == g['invocation_id'] and bm['argv'] == g['argv'] and bm['request_sha256'] == sha(request_bytes) and bm['std_sha'] == source and bm['tool_sha'] == tool, rid + ' binding metadata identity')
            for a in bm['artifacts']:
                need(sha(members[gp + a['path']]) == a['sha256'] and len(members[gp + a['path']]) == a['bytes'], rid + ' bound artifact ' + a['path'])
            need(g['timeout_seconds'] == g['group_budget_seconds'] == 600 and g['compile_limit_seconds'] == 180 and g['memory']['group_cap_kib'] == 6291456 and not g['phase_limited'], rid + ' unchanged actual caps')
            need(ex['child_shutdown_verified'] and sup['worker_exit'] == 0 and sup['containment']['verified'] and not sup['orphan_survivors_at_worker_exit'] and not sup['cutoff'] and not sup['limit_initiated'] and sup['supervisor_error'] is None, rid + ' shutdown containment continuation')
            props = pr['harnesses'][0]['properties']
            need(props == read('NATIVE-PROPERTIES.json')[rid]['properties'], rid + ' author native projection exact')
            need(stock == read('NATIVE.json')[rid]['export'], rid + ' author stock projection exact')
            need(stock['schema_version'] == '0.1.0' and stock['kani_commit'] == tool and stock['kani_commit_dirty'] is False and stock['target'] == 'x86_64-unknown-linux-gnu', rid + ' stock schema tool target')
            need(stock['harness_selection'] == {'requested_filters': [selector], 'exact': True, 'unmatched_filters': [], 'matched_count': 1}, rid + ' native exact selection')
            registrations = []
            providers = []
            for m in bm['native_metadata']:
                if m.get('state') != 'CAPTURED':
                    continue
                b = m['text'].encode() if m.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(m['text'], validate=True)
                need(sha(b) == m['sha256'] and len(b) == m['bytes'], rid + ' native metadata hash ' + m['path'])
                md = json.loads(b)
                registrations.extend(x for x in md.get('proof_harnesses', []) if x['pretty_name'] == selector)
                providers.extend(x for x in md.get('contracted_functions', []) if selector in x.get('harnesses', []))
            need(len(registrations) == 1, rid + ' unique native registration')
            registration = registrations[0]
            binding = request['source_bindings'][rid]
            need(registration['crate_name'] == 'core' and registration['original_file'] == str(STD / binding['file']), rid + ' native registration source')
            need(registration['attributes']['kind'] == ({'ProofForContract': {'target_fn': binding['target']}} if row['mode'] == 'PFC' else 'Proof'), rid + ' native Original/PFC target')
            need(registration['attributes']['stubs'] == ([{'original': 's2_swap_seam', 'replacement': 'weak_swap'}] if rid == 'sort13_weak' else []) and not registration['attributes']['verified_stubs'], rid + ' actual stub seams')
            if row['mode'] == 'PFC':
                need(len(providers) == 1, rid + ' contracted provider registered; not proof credit')
            for role in row['roles']:
                b = blob(SOURCE, source, role['file'])
                need(sha(b) == role['source_sha256'] and b.decode().splitlines()[role['line'] - 1] == role['source_line'], rid + ' source literal ' + role['description'])
                matches = [p for p in props if p['description'] == role['description']]
                if stock.get('harnesses'):
                    need(len(matches) == 1 and all(matches[0][k] == role[k] for k in ['class', 'status']) and matches[0]['file'] == str(STD / role['file']) and matches[0]['line'] == str(role['line']), rid + ' exact native role ' + role['description'])
                else:
                    need(not matches, rid + ' absent completed role remains unknown')
            guards = [p for p in props if p['class'] == 'unsupported_construct']
            u = [p for p in props if p['status'] == 'UNREACHABLE']
            bad = [p for p in props if not located(p)]
            failures = [p for p in props if p['status'] == 'FAILURE']
            covers = [p for p in props if p['class'] == 'cover']
            need(qr['unsupported_guards'] == guards and qr['U_properties'] == u and qr['missing_location'] == bad, rid + ' no omitted U guard or location record')
            if stock.get('harnesses'):
                h = stock['harnesses'][0]
                need(len(stock['harnesses']) == 1 and h['name'] == selector and h['n_properties'] == len(props) == h['checks']['total'] + h['covers']['total'], rid + ' property partitions')
                need(len({p['id'] for p in props}) == len(props), rid + ' unique native IDs')
                rebound = runner.validate_export_value(stock, row, source_binding=binding, std=STD, group_selectors=[selector])
                need(rebound['outcome'] == 'RECORDED', rid + ' native source-stage-target decoder')
                dec = rich.RegularEvidence([selector], STD)
                dec.finished = True
                dec.closed = {selector}
                dec.records = {selector: copy.deepcopy(props)}
                try:
                    dec.validate(stock)
                    actual_reader = 'ACCEPT'
                except ValueError as e:
                    actual_reader = str(e)
                need(actual_reader == ('rich metadata incomplete: file/line missing' if rid.startswith('m8_') else 'ACCEPT'), rid + ' frozen rich strict verdict')
                need(not policy.expected_observation(row, rebound, {'name': selector, 'properties': props}) and can['s3_expected_match'] is False, rid + ' strict expected match false')
                need(len(covers) == row['required_cover_count'] and {p['description'] for p in covers} == set(row['required_cover_messages']) and all(p['status'] == 'SATISFIED' and located(p) for p in covers), rid + ' exact located SAT covers')
                guard_fields = ['id', 'class', 'description', 'file', 'line', 'status']
                need(sorted((canonical({k: p[k] for k in guard_fields}) for p in guards)) ==
                     sorted((canonical({k: p[k] for k in guard_fields}) for p in h['unsupported_constructs'])) and
                     all(p['status'] == 'SUCCESS' and located(p) for p in guards), rid + ' every unsupported guard retained SUCCESS')
                need(all(p['status'] in ['SUCCESS', 'FAILURE', 'UNREACHABLE', 'SATISFIED'] for p in props), rid + ' no error unknown status')
                if rid.startswith('m8_'):
                    need(collections.Counter(p['status'] for p in props) == {'SUCCESS': 372, 'UNREACHABLE': 8, 'SATISFIED': 6} and len(props) == 386 and len(guards) == 4 and len(bad) == 1, rid + ' exact merge counts')
                    need(h['outcome'] == {'kind': 'COMPLETED', 'verdict': 'SUCCESS'} and not failures, rid + ' native SUCCESS separate producer UNKNOWN')
                    need(can['status'] == 'UNKNOWN' and g['original_exception']['message'] == 'rich metadata incomplete: file/line missing', rid + ' immutable producer metadata failure')
                    review_location(rid, selector, g, bm, stock, pr, bad[0], row, data, members, rich, cases, adverse)
                    pfc = qr['PFC']
                    decoded = subprocess.check_output(['c++filt', '-i', '-s', 'rust', registration['contract']['contracted_function_name']], text=True).strip()
                    need(decoded == pfc['demangled_symbol'] and 'bidirectional_merge::<u8,' in decoded and 'KeyLess<u8>' in decoded, rid + ' concrete actual PFC symbol')
                    links = [p for p in props if p['id'].startswith(decoded + '.')]
                    need(all(any(p['class'] == cl and p['status'] == 'SUCCESS' and registration['contract']['contracted_function_name'] in p['description'] for p in links) for cl in ['single_top_level_call', 'no_recursive_call']), rid + ' DFCC actual body links')
                    need(len(pfc['ensures']) == 1 and pfc['ensures'][0] in props and pfc['ensures'][0]['status'] == 'SUCCESS' and located(pfc['ensures'][0]), rid + ' checked ensures at source-reported assurance')
                else:
                    need(len(failures) == 1 and failures[0]['description'] == row['failure_description'] and not bad and not guards and not covers and h['outcome']['verdict'] == 'FAILURE', rid + ' intended exact negative FAIL')
                    need(can['status'] == 'OBSERVED', rid + ' producer observed negative unchanged')
                for p in u:
                    all_u.append(review_u(rid, selector, g, p, source, members[gp + 'properties.json'], q))
            else:
                need(stock['run_state'] == pr['state'] == 'INCOMPLETE' and not props and ex['termination_reason'] == 'rss_cap' and ex['original_exit_code'] == -15 and ex['signal'] == 15 and not ex['timed_out'], rid + ' censored not NOT_RUN or completed')
                need(0 < co['elapsed_upper_bound_seconds'] < ex['elapsed_seconds'] < 600 and ex['rss_peak_kib'] > 6291456, rid + ' compile complete before RSS cutoff')
                need(qr['native_property_count'] == 'UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY' and qr['U_count'] == 'UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY', rid + ' absent inventory unknown not zero')
            need(not qr['strict_expected_match'] and not qr['qualification_admitted'] and not qr['eligible_as_init_leaf_or_provider_summary'], rid + ' no qualification or init/provider admission')
            all_guards.extend({'root': rid, 'property': p} for p in guards)
            rows.append({'root': rid, 'rank': rank, 'invocation_id': g['invocation_id'], 'controller_context': life['context'], 'namespace': g['cargo_target_dir'], 'selector': selector, 'mode': row['mode'], 'unwind': row['unwind'], 'native': qr['native_verdict'], 'producer': {k: can[k] for k in ['status', 'outcome', 's3_expected_match']}, 'S1': qr['provisional_assessment'], 'scope': qr['scope_classification'], 'domain': qr['domain'], 'literal_roles': qr['literal_roles'], 'properties': len(props) if stock.get('harnesses') else 'UNKNOWN', 'U': len(u) if stock.get('harnesses') else 'UNKNOWN', 'guards': guards if stock.get('harnesses') else 'UNKNOWN', 'covers': covers if stock.get('harnesses') else 'UNKNOWN', 'protected': protected, 'cleanup': sup['containment'], 'elapsed_s': ex['elapsed_seconds'], 'rss_kib': ex['rss_peak_kib'], 'compile_upper_bound_s': co['elapsed_upper_bound_seconds'], 'native_verification_s': stock.get('harnesses', [{}])[0].get('resources', {}).get('verification_time_s', 'UNKNOWN_CENSORED_NO_COMPLETED_EXPORT'), 'next_root': request['rows'][rank]['id'] if rank < 8 else None, 'admitted': False, 'init_provider_eligible': False})
        # Exercise real frozen sealed/protected code; these are reporting service tests.
        target = materialized / 'groups/s3-m8_s32_d00_allinit/export.json'
        original = target.read_bytes()
        for name, value in [('missing_sealed_export', None), ('tampered_sealed_export', original + b' ')]:
            if value is None:
                target.unlink()
            else:
                target.write_bytes(value)
            try:
                campaign.sealed(materialized)
            except (campaign.GlobalFailure, ValueError, OSError):
                adverse.append({'test': name, 'result': 'REJECT', 'scope': 'ACTUAL_FROZEN_SEAL_READER'})
            else:
                raise AssertionError(name + ' accepted')
            target.write_bytes(original)
        bad_g = copy.deepcopy(data['groups/s3-m8_s32_d00_allinit/receipt.json'])
        bad_g['tool_fingerprints_after']['binaries']['kani_driver']['sha256'] = '0' * 64
        try:
            evidence.protected(bad_g, request, data['baseline.json'], data['workers/m8_s32_d00_allinit-supervision.json'], sha(request_bytes))
        except evidence.EvidenceError:
            adverse.append({'test': 'protected_binary_changed', 'result': 'REJECT', 'scope': 'ACTUAL_FROZEN_PROTECTED_READER'})
        else:
            raise AssertionError('changed protected binary accepted')
        need(all((materialized / name).read_bytes() == b for name, b in members.items()), 'authentic materialized bytes restored unchanged')

    need(len(rows) == len({r['invocation_id'] for r in rows}) == 8, 'eight independent native invocation identities')
    need(len(all_u) == q['U_count'] == 41 and len(all_guards) == 12, '41 individual U reviews and12 guards')
    need(len(cases) == 3 and len(adverse) == 108, 'three exact location cases and108 adverse controls')
    source_scope(source, rows)
    tool_trace(tool, ctrl)
    cost_review(data, rows)
    need(q['qualified_new_leaves'] == q['qualified_partial_provider_contexts'] == q['proof_obligations_closed'] == 0 and q['sort8_init_caller_contexts_open'] == 34 and q['independent_credit'] == 'NONE', 'no qualified leaves closed contexts or independent credit')
    write('ROW-REVIEW.json', {'rows': rows, 'native_properties_total': sum(x['properties'] for x in rows if isinstance(x['properties'], int)), 'assurance': 'S1 Profiles v4 SOURCE_REPORTED; no admission'})
    write('U-REVIEW.json', {'count': len(all_u), 'occurrences': all_u, 'assurance': 'Independent source-local conditional review of source-reported site associations; independent AST/MIR causality UNKNOWN', 'policy': request['unreachable_admission']})
    write('GUARD-REVIEW.json', {'count': len(all_guards), 'records': all_guards, 'waived': False, 'partial_inventory': 'Insertion guards UNKNOWN, not empty'})
    write('LOCATION-DECISION.json', {'recommendation': 'RECOMMEND_EXACT_CASES', 'status': 'NOT_APPLIED', 'admission': False, 'cases': cases, 'general_rule': 'PENDING_NOT_RECOMMENDED_FOR_ACTIVATION', 'shared_actual_emitter': 'UNKNOWN', 'positive_source_MIR_origin': 'UNKNOWN', 'old_f740': 'ORIGINAL_RUN_44416629057_ONLY_UNCHANGED', 'reversal_scope': 'Withdraw only these three metadata recommendations if any exact binding, status, cardinality, source-local premise or packet digest fails. No policy/history change to reverse.', 'remaining_gates': read('LOCATION-PROPOSAL.json')['remaining_gates'], 'partial_effect': 'DIAGNOSTIC_ONLY_INITIALIZATION_OPEN; init/provider eligibility false regardless of metadata recommendation'})
    write('ADVERSE-TESTS.json', {'status': 'PASS', 'controls': adverse, 'count': len(adverse), 'scope': '105 exact packet recommendation mutations plus3 actual frozen reader controls; no policy changes'})
    write('INPUTS.json', {'task': TASK, 'owner_request': 'Owner05:39 /new14', 'intake': INTAKE, 'intake_path': AUTHOR, 'terminal_inputs': {'commit': TASK, 'path': PREFIX + 'postrun-s3-2-r1-terminal/INPUTS.json', 'sha256': sha(blob(REPO, TASK, PREFIX + 'postrun-s3-2-r1-terminal/INPUTS.json'))}, 'payload_sha256': sha(gz), 'source_tool_control_trigger': deps['source_tool_control_trigger'], 'request_sha256': sha(request_bytes), 'workflow_sha256': sha(workflow), 'settings': 'high/FastOFF preserved, no subagents/model change', 'output': PREFIX + HERE.name + '/', 'restrictions': 'No code/policy/ledger/CI/native changes; review outputs only; no acquisition or raw/full archive/logs'})
    write('PROVENANCE.json', {'intake': INTAKE, 'task': TASK, 'intake_manifest_sha256': sha(blob(REPO, INTAKE, AUTHOR + 'MANIFEST.json')), 'dependency_manifest_sha256': sha(blob(REPO, INTAKE, AUTHOR + 'DEPENDENCIES.json')), 'intake_files': 35, 'intake_hashed_files': 33, 'dependency_blobs': dependency_count, 'source_files': 41, 'tool_source_files': 6, 'control_files': 84, 'compact_members': 119, 'compact_sha256': sha(gz), 'uncompressed_sha256': sha(raw), 'transport': 'Historical intake receipt and committed native metadata rechecked; no independent transport reacquisition; transport bytes not retained', 'replay': 'Fresh tempfile exact control Git readers, materialized compact and upload-only public route agree with sealed intake prefix', 'evidence_modified': False, 'native_run': False, 'proof_credit': 'NONE'})
    write('VALIDATION.json', {'status': 'PASS', 'checks_count': len(CHECKS), 'checks': CHECKS, 'adverse_count': len(adverse), 'native_or_fullValidate_rerun': False, 'author_validation': 'Committed1120 checks/102 controls read as author claims; this review uses independent checks and108 controls', 'original_intake_unchanged': True})
    write('FINDINGS.json', {'disposition': 'APPROVE_INTAKE_WITH_PRESERVED_LIMITS', 'blocking_findings': [], 'blocking_findings_count': 0, 'location_recommendation': 'RECOMMEND_EXACT_CASES', 'location_status': 'NOT_APPLIED', 'general_rule': 'PENDING', 'admission': False, 'qualification': 'Three fixed negative observations; one provisional bounded allinit PFC candidate pending separate decision; two DIAG_INIT_OPEN nonproviders; two RSS-censored insertions', 'open_limits': ['Shared actual emitter/positive source-MIR origin UNKNOWN', 'Strict expected matches0/8; U REJECT_ALL and disabled proposal unchanged', 'Both partial masks/dstinit/provider eligibility OPEN/false', 'Independent AST/MIR/B1/B2/init/generic/caller/fullN16N32 credit NONE', 'All34 sort8 initialization/caller contexts OPEN'], 'repair_required': False, 'policy_ledger_code_CI_native_changes': False})
    print(json.dumps({'status': 'PASS', 'checks': len(CHECKS), 'adverse': len(adverse), 'rows': 8, 'U': len(all_u), 'guards': len(all_guards), 'location_cases': len(cases), 'blocking_findings': 0}))


def review_u(rid, selector, group, p, source, member, qualification):
    rel = p['file'].split('/export/', 1)[1]
    line = int(p['line'])
    b = blob(SOURCE, source, rel)
    ls = b.decode().splitlines()
    site = ls[line - 1]
    premise = ''
    predicate = ''
    if rel.endswith('/sorting_model.rs') and rid in ['checker_order_corrupt', 'checker_count_corrupt', 'sort13_weak']:
        lengths = {'checker_order_corrupt': 2, 'checker_count_corrupt': 32, 'sort13_weak': 13}
        expected = {100: 'i += 1;', 106: 'let query = before.values[i];', 111: 'if before.values[j] == query { old_count += 1; }', 112: 'if values[j].value() == query { new_count += 1; }', 113: 'j += 1;', 118: 'i += 1;'}
        need(line in expected and site.strip() == expected[line], rid + ' U exact checker site ' + p['id'])
        premise = f'Entry guard91-94: before.valid and before.len=values.len={lengths[rid]}<=32, snapshot.values capacity32. Normal continuation only; early false returns retain no later obligation.'
        predicate = {100: '1<=i<L<=32 => i+1<=32', 106: '0<=i<L<=32 => before.values[i] in bounds', 111: 'j<L<=32 => before.values[j] in bounds; old_count<=j so increment<=32', 112: 'j<L=values.len<=32 => values[j] in bounds; new_count<=j so increment<=32', 113: 'j<L<=32 => j+1<=32', 118: 'i<L<=32 => i+1<=32'}[line]
    elif rel.endswith('/num/uint_macros.rs') and line == 3222:
        need(site.strip() == 'other - self' and 'if self < other' in ls[line - 2], rid + ' U abs_diff exact branch')
        premise = 'Concrete usize monomorphization; source branch self<other.'
        predicate = 'other>=self => other-self cannot underflow'
    elif rel.endswith('/fmt/mod.rs') and line == 820:
        need('s.len() << 1 | 1' in site and p['description'] == 'attempt to shift left with overflow', rid + ' U exact shift-kind')
        premise = 'x86_64 target usize width64; the check is shift-count overflow, not loss of shifted bits.'
        predicate = 'literal shift amount1<64 for every string length'
    elif rel.endswith('/ptr/const_ptr.rs') and line == 1479:
        need('align - 1' in site and '!align.is_power_of_two()' in ls[line - 5] and 'panic!' in ls[line - 4], rid + ' U exact alignment guard')
        premise = 'Normal path after is_power_of_two guard; panic and pointer validity checks remain separate.'
        predicate = 'power-of-two align implies align>=1, hence align-1 defined'
    elif rel.endswith('/ub_checks.rs') and line == 148:
        need('if size == 0' in site and 'else { isize::MAX as usize / size }' in site, rid + ' U guarded division')
        premise = 'Only else arm evaluates division; u8 size1 independently.'
        predicate = 'else(size==0) implies divisor size!=0'
    elif rel.endswith('/smallsort.rs') and rid.startswith('m8_') and line in [974, 990, 991, 992]:
        tokens = {974: 'len / 2', 990: 'len_div_2 - 1', 991: 'len - 1', 992: 'len - 1'}
        need(tokens[line] in site, rid + ' U exact merge arithmetic ' + p['id'])
        premise = 'This exact harness constructs source slice length8 before actual u8/KeyLess bidirectional_merge call; half4. Source/destination offsets and initialization intervals are per-root, with separate safety/frame gates.'
        predicate = {974: 'literal divisor2!=0', 990: 'half4-1=3>=0', 991: 'len8-1=7>=0', 992: 'len8-1=7>=0; destination writability/init is a separate obligation'}[line]
    need(bool(predicate), rid + ' U independently classified ' + p['id'])
    matches = [x for x in qualification['U_instances'] if x['root'] == rid and x['property']['id'] == p['id']]
    need(len(matches) == 1 and matches[0]['property'] == p and matches[0]['source_sha'] == source and matches[0]['source_sha256'] == sha(b) and matches[0]['source_line'] == line and matches[0]['member_sha256'] == sha(member) and matches[0]['invocation_id'] == group['invocation_id'] and matches[0]['source_local_argument'], rid + ' U author occurrence exact bindings ' + p['id'])
    return {'root': rid, 'selector': selector, 'invocation_id': group['invocation_id'], 'property': p, 'source': source, 'source_file': rel, 'source_sha256': sha(b), 'line': line, 'context': '\n'.join(f'{i+1}: {ls[i]}' for i in range(max(0, line-6), min(len(ls), line+4))), 'premises': premise, 'reviewer_predicate': predicate, 'assessment': 'SOURCE_LOCAL_CONDITIONAL_ARGUMENT_SUPPORTED', 'independent_MIR_origin': 'UNKNOWN', 'policy_admitted': False}


def review_location(rid, selector, g, bm, stock, pr, exact, row, data, members, rich, cases, adverse):
    expected = {'id': selector + '.unreachable.1', 'display_id': selector + '.unreachable.1', 'class': 'unreachable', 'status': 'SUCCESS', 'description': 'unreachable code', 'file': None, 'line': None, 'location_display': 'library/core/src/lib.rs:0:0 in function ' + selector}
    need(exact == expected, rid + ' exact null/systemSUCCESS fingerprint')
    need(not rich.location_exception(selector, exact), rid + ' frozen old exception excludes new exact case')
    stream = ('Checking harness ' + selector + '...\nRESULTS:\nCheck 1: ' + exact['display_id'] + '\n\t - Status: SUCCESS\n\t - Description: "unreachable code"\n\t - Location: ' + exact['location_display'] + '\nSUMMARY:\n').encode()
    dec = rich.RegularEvidence([selector], STD)
    dec.feed(stream)
    dec.finish()
    need(dec.error is None and dec.records == {selector: [expected]} and len(dec.missing_sites) == 1, rid + ' isolated authentic fields reproduce parser null normalization')
    gap = next(x for x in read('METADATA-GAP.json')['rows'] if x['root'] == rid)
    need(gap['all_missing_null_wrong_type_location_records'] == [expected] and gap['missing_key_count'] == gap['non_null_wrong_type_count'] == 0 and gap['present_null_count'] == 1, rid + ' independently exhaustive offending records')
    proposal = next(x for x in read('LOCATION-PROPOSAL.json')['candidates'] if x['root'] == rid)
    need(proposal['allowed_missing_location_records'] == [expected] and proposal['allowed_missing_location_cardinality'] == 1 and proposal['invocation_id'] == g['invocation_id'], rid + ' candidate exact case bindings')
    gp = 'groups/s3-' + rid + '/'
    original = {'selector': selector, 'stock': stock, 'rich': pr, 'group': g, 'binding': bm, 'compile': data[gp + 'compile/receipt.json'], 'supervision': data['workers/' + rid + '-supervision.json'], **proposal['bindings']}
    need(sha(canonical(original)) == proposal['structural_packet_fingerprint_sha256'], rid + ' complete structural packet fingerprint')
    for name, digest in proposal['member_digests'].items():
        need(sha(members[gp + name]) == digest, rid + ' candidate member pin ' + name)

    def recommend(case):
        # Immutable packet recommendation only; deliberately no future-packet generalization.
        if sha(canonical(case)) != proposal['structural_packet_fingerprint_sha256']:
            return False
        ps = case['rich']['harnesses'][0]['properties']
        return ([p for p in ps if not located(p)] == [expected] and len(ps) == 386 and
                collections.Counter(p['status'] for p in ps) == {'SUCCESS': 372, 'UNREACHABLE': 8, 'SATISFIED': 6} and
                all(located(p) for p in ps if p != expected))

    need(recommend(original), rid + ' reviewer exact packet recommendation accepts authentic case')
    mutations = ['id', 'display_id', 'class', 'failure', 'U_status', 'unknown_status', 'description', 'raw_display', 'selector', 'missing_record', 'duplicate_record', 'second_bad_location', 'role_location', 'cover_location', 'U_location', 'guard_location', 'guard_status', 'file_key', 'line_key', 'file_type', 'line_type', 'mixed_invocation', 'member', 'request', 'source', 'tool', 'cfg', 'namespace', 'schema', 'protected_binary', 'control', 'head', 'workflow', 'run', 'count']
    for mutation in mutations:
        case = copy.deepcopy(original)
        ps = case['rich']['harnesses'][0]['properties']
        p = next(x for x in ps if x['id'] == expected['id'])
        if mutation in ['id', 'display_id', 'class', 'description']:
            p[mutation] += 'CHANGED'
        elif mutation in ['failure', 'U_status', 'unknown_status']:
            p['status'] = {'failure': 'FAILURE', 'U_status': 'UNREACHABLE', 'unknown_status': 'UNKNOWN'}[mutation]
        elif mutation == 'raw_display':
            p['location_display'] += 'CHANGED'
        elif mutation == 'missing_record':
            ps.remove(p)
        elif mutation == 'duplicate_record':
            ps.append(copy.deepcopy(p))
        elif mutation == 'second_bad_location':
            next(x for x in ps if x != p)['file'] = None
        elif mutation in ['role_location', 'cover_location', 'U_location', 'guard_location', 'guard_status']:
            pred = {'role_location': lambda x: x['description'] == row['roles'][0]['description'], 'cover_location': lambda x: x['class'] == 'cover', 'U_location': lambda x: x['status'] == 'UNREACHABLE', 'guard_location': lambda x: x['class'] == 'unsupported_construct', 'guard_status': lambda x: x['class'] == 'unsupported_construct'}[mutation]
            other = next(x for x in ps if pred(x))
            other['status' if mutation == 'guard_status' else 'line'] = 'UNKNOWN' if mutation == 'guard_status' else None
        elif mutation in ['file_key', 'line_key']:
            del p[mutation.split('_')[0]]
        elif mutation in ['file_type', 'line_type']:
            p[mutation.split('_')[0]] = 0
        elif mutation == 'mixed_invocation':
            case['binding']['invocation_id'] = 'mixed'
        elif mutation == 'member':
            case['properties_member'] += '.other'
        elif mutation == 'tool':
            case['binding']['tool_sha'] = '0' * 40
        elif mutation == 'cfg':
            case['group']['effective_cfg'] = ''
        elif mutation == 'namespace':
            case['group']['cargo_target_dir'] += '/other'
        elif mutation == 'schema':
            case['stock']['schema_version'] = 'changed'
        elif mutation == 'protected_binary':
            case['group']['tool_fingerprints_after']['binaries']['kani_driver']['sha256'] = '0' * 64
        elif mutation == 'count':
            case['stock']['harnesses'][0]['n_properties'] += 1
        elif mutation == 'run':
            case['run'] += 1
        else:
            case[mutation] += 'CHANGED'
        need(not recommend(case), rid + ' reviewer exact recommendation rejects ' + mutation)
        adverse.append({'root': rid, 'test': mutation, 'result': 'REJECT', 'scope': 'EXACT_IMMUTABLE_PACKET_RECOMMENDATION_MODEL'})
    old = read('METADATA-GAP.json')['old_admission']
    old_actual = json.loads(blob(REPO, 'f74025e493a627962842e8f7bc6a2766d33dd300', PREFIX + 'admission-r2-location/ADMISSION.json'))
    old_review = json.loads(blob(REPO, 'a9fe0055aab3279e3f5bb71bde9667925da80e65', PREFIX + 'run-44416629057-review-w14/LOCATION-DECISION.json'))
    need(old['case'] == old_actual and old_actual['exact_property'] == old_review['exact_property'] and old_actual['run'] == old_review['run'] == 44416629057, rid + ' old exact decision/review verified')
    need(all(expected[k] == old_actual['exact_property'][k] for k in ['class', 'status', 'description', 'file', 'line']) and expected['id'] != old_actual['exact_property']['id'], rid + ' structural similarity but different exact identity')
    cases.append({'root': rid, 'recommendation': 'RECOMMEND_EXACT_CASES', 'status': 'NOT_APPLIED', 'exact_property': expected, 'invocation_id': g['invocation_id'], 'namespace': g['cargo_target_dir'], 'bindings': proposal['bindings'], 'pinned_parser': read('LOCATION-PROPOSAL.json')['pinned_parser'], 'schemas': proposal['schema'], 'member_digests': proposal['member_digests'], 'structural_packet_fingerprint_sha256': proposal['structural_packet_fingerprint_sha256'], 'counts': stock['harnesses'][0]['checks'], 'covers': stock['harnesses'][0]['covers'], 'allowed_bad_location_cardinality': 1, 'all_other_records_located': True, 'old_original_run_exception_transferred': False, 'actual_shared_emitter': 'UNKNOWN', 'positive_source_MIR_origin': 'UNKNOWN', 'native_verdict': 'SUCCESS', 'producer_verdict': 'UNKNOWN unchanged', 'init_provider_eligible': False, 'partial_classification': 'DIAG_INIT_OPEN' if 'partial_diag' in rid else None})


def source_scope(source, rows):
    leaf_path = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_s3_2_leaf.rs'
    leaf = blob(SOURCE, source, leaf_path).decode()
    negative = blob(SOURCE, source, 'library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs').decode()
    need('let mut v = [12u8,11,10,9,8,7,6,5,4,3,2,1,0];' in negative and '#[kani::stub(s2_swap_seam,weak_swap)]' in negative and '(_v:*mut T,_a:usize,_b:usize,_f:&mut F) {}' in negative, 'fixed descending13 ordinary weak no-op seam')
    intervals = {'m8_s32_d00_allinit': ('if i >= 8 {', [[8, 48]], 32, 0), 'm8_s32_d00_partial_diag': ('if 32 <= i && i < 40 {', [[32, 40]], 32, 0), 'm8_s40_d16_partial_diag': ('if i < 8 || i >= 32 {', [[0, 8], [32, 48]], 40, 16)}
    for r in rows:
        rid = r['root']
        if rid in intervals:
            token, initialized, src, dst = intervals[rid]
            start = leaf.index('fn ' + rid + '()')
            body = leaf[start:leaf.find('\n}', start)+2]
            need(token in body and f'let src = {src};' in body and f'let dst = {dst};' in body and 'slice::from_raw_parts(p.add(src), 8)' in body, rid + ' exact geometry initialized construction')
            d = r['domain']['domain']
            need(d['initialized_intervals'] == initialized and d['src'] == src and d['dst'] == dst and d['span'] == 8 and d['source_sorted_halves'] == [4, 4], rid + ' reported domain source match')
            if 'partial_diag' in rid:
                need(r['scope']['category'] == 'DIAGNOSTIC_ONLY_INITIALIZATION_OPEN' and not r['scope']['qualification_eligible'] and r['S1'] == 'DIAG_INIT_OPEN', rid + ' permanent partial nonprovider')
    small = blob(SOURCE, source, 'library/core/src/slice/sort/shared/smallsort.rs').decode()
    need('#[cfg_attr(kani, crate::kani::modifies(ptr::slice_from_raw_parts_mut(dst, v.len())))]' in small, 'actual stock PFC destination footprint retained')
    scope = {'source': source, 'leaf': leaf_path, 'leaf_sha256': sha(leaf.encode()), 'review': 'Full byte arrays, stateless KeyLess<u8>, only sorted source halves constrained. Fixed source/destination ranges; normal-return functional multiplicity/order and known initialized value frame. Destination initially uninitialized; stock typed output loads do not establish a mask/dstinit theorem.', 'allinit': 'Initialized outside-dst [8,48), source[32,40), dst[0,8); provisional bounded SOURCE_REPORTED actual-body PFC only.', 'left_partial': 'Only [32,40) initially initialized; outside source and destination initialization state unproved.', 'right_partial': '[0,8) and[32,48) initially initialized; source[40,48), dst[16,24); other outside initialization state unproved.', 'frame': 'Only actually initialized locations read for known-value frame/spec; stock modifies/assigns source-reported footprint is not emitted byte-state initialization evidence.', 'initialization_instrumentation': 'OFF/constanttrue, no ghost mask used; no initrole or summary credit', 'source_assurance': 'Profiles v4 SOURCE_REPORTED, no independent AST/MIR/ADT/parser-input/caller-edge proof', 'open': 'All34 sort8 init/caller contexts and generic/fullN16N32 remain OPEN; no B1/B2 promotion'}
    write('SOURCE-REVIEW.json', scope)


def tool_trace(tool, ctrl):
    specifications = [
        ('kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs', [(465, 470), (509, 517)], ['term.source_info.span', 'TerminatorKind::Unreachable', 'PropertyClass::Unreachable']),
        ('kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs', [(210, 223)], ['codegen_assert_assume', 'PropertyClass']),
        ('kani-compiler/src/codegen_cprover_gotoc/codegen/span.rs', [(40, 65), (92, 109)], ['start_line', 'start_col']),
        ('kani-driver/src/cbmc_output_parser.rs', [(261, 310)], ['SourceLocation', 'line', 'column']),
        ('kani-driver/src/cbmc_property_renderer.rs', [(274, 347)], ['Location:']),
        ('kani-driver/src/frontend/schema_utils.rs', [(485, 550), (750, 790)], ['unsupported_constructs', 'success'])]
    traces = []
    for path, ranges, tokens in specifications:
        b = blob(TOOL, tool, path)
        ls = b.decode().splitlines()
        excerpt = '\n'.join(f'{i+1}: {ls[i]}' for a, z in ranges for i in range(a-1, min(z, len(ls))))
        need(all(t in excerpt for t in tokens), 'independent stock source trace ' + path)
        traces.append({'path': path, 'tool': tool, 'sha256': sha(b), 'excerpts': excerpt})
    old_parser = blob(CONTROL, 'cb63033ffcde918f4341146e56373476b8eeb569', 'ch8-s1-control/rich_evidence.py')
    new_parser = blob(CONTROL, ctrl, 'ch8-s1-control/rich_evidence.py')
    need(old_parser == new_parser, 'old/new rich parser byte identity')
    write('TOOL-TRACE.json', {'traces': traces, 'parser_sha256': sha(new_parser), 'normalization': 'Positive-line regex excludes0; exact raw display retained, normalized file and line null. Authentic isolated-field parser replay confirms behavior only.', 'shared_actual_emitter': 'UNKNOWN', 'causality': 'A compatible MIR Unreachable emission route is visible; no retained per-record MIR/positive span binds actual cases to it. Matching text/class/suffix/display does not establish cause.'})


def cost_review(data, rows):
    cost = read('COST.json')
    need(cost['campaign_elapsed_seconds'] == data['receipt.json']['phase_elapsed_seconds'] == 1068.751379632, 'campaign elapsed exact')
    need(cost['setup']['setup_total_seconds'] == data['setup/receipt.json']['setup_total_seconds'], 'setup total scope retained')
    reviewed = []
    for r, c in zip(rows, cost['rows']):
        rid = r['root']
        need(rid == c['id'] and r['elapsed_s'] == c['execution']['elapsed_seconds'] and r['rss_kib'] == c['execution']['rss_peak_kib'] and r['compile_upper_bound_s'] == c['compile_elapsed_upper_bound_seconds'] and r['native_verification_s'] == c['native_verification_time_s'], rid + ' native/cost projection match')
        sup = data['workers/' + rid + '-supervision.json']
        need(c['supervisor_lifecycle_diagnostics']['retained_count'] == len(sup['lifecycle_events']) and c['supervisor_lifecycle_diagnostics']['omitted_count'] == sup['lifecycle_events_omitted'], rid + ' bounded lifecycle diagnostics not hidden')
        if rid.startswith('i_'):
            expect = {'i_p01_b1_16': (131.465, 6361996, 33.306), 'i_p16_b1_16': (126.13, 6330308, 31.836)}[rid]
            need((r['elapsed_s'], r['rss_kib'], r['compile_upper_bound_s']) == expect and c['trigger']['cause'] == 'LOCAL_SAMPLED_PGID_RSS_FIRST_OVER_CAP', rid + ' exact local RSS cutoff')
        reviewed.append({'root': rid, 'whole_child_elapsed_s': r['elapsed_s'], 'compile_upper_bound_s': r['compile_upper_bound_s'], 'native_verification_time_s': r['native_verification_s'], 'sampled_PGID_RSS_kib': r['rss_kib'], 'censoring': c['censoring'], 'trigger': c['trigger'], 'supervisor_lifecycle_retained': len(sup['lifecycle_events']), 'supervisor_lifecycle_omitted': sup['lifecycle_events_omitted'], 'cleanup': r['cleanup'], 'next_root': r['next_root']})
    runner = blob(CONTROL, '775574eb2f361ef90eade30330ff0d608530287f', 'ch8-s1-control/runner.py').decode().splitlines()
    excerpt = '\n'.join(runner[625:671])
    need('deadline = started + timeout' in excerpt and 'max(info["rss_peak_kib"], rss)' in excerpt and 'if rss > rss_cap_kib:' in excerpt and 'killed_for = "rss_cap"; break' in excerpt, 'runner child includes compile and first-over-cap break')
    write('COST-REVIEW.json', {'rows': reviewed, 'campaign_elapsed_s': cost['campaign_elapsed_seconds'], 'setup': cost['setup'], 'caps': cost['caps'], 'interpretation': 'Compile bound is observer time to initial export, not exclusive CPU. Child600 includes compile180; slot720/worker710/local RSS6GiB/outer12GiB+2GiB headroom distinct. Local RSS fired, no time/global cutoff. Component peaks nonsimultaneous. Sampled PGID VmRSS is not kernel/cgroup/tree peak or RSS at signal. Native resource verification time is not exclusive backend time. Symex/backend/steps/VCC UNKNOWN.', 'historical_comparison': cost['old_cutoff_reference'], 'speedup_or_full_domain_fit_claim': False})


if __name__ == '__main__':
    main()
