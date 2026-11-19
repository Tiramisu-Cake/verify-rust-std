#!/usr/bin/env python3
"""Bounded independent W14 review. Exact Git blobs + authorized compact JSON only.

No compilation/verifier, full validation, acquisition, policy mutation or evidence rewrite.
The hypothetical case predicate below is a test model, never an installed reader.
"""
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
ROOT = HERE.parents[5]
INTAKE = HERE.with_name('run-44416629057')
REV = 'd29ab46dbbb45d7106fa30c3ac04bb419a2ac286'
TASK = '84aac8e779dbfaeb6300d92557fd122f4dea29f1'
CTRL = 'cb63033ffcde918f4341146e56373476b8eeb569'
CONTROL = Path('/root/kani-ch8-s3-1-r2-control-w13')
SOURCE = Path('/root/verify-rust-std-ch8-s3-1-final-w13')
SOURCE_REV = '513341f41ce53833a279571401c924bdddddb6c8'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
RID = 's3_sort4_u8_same_alloc'
SEL = 'slice::sort::shared::smallsort::verify::sorting_s3_leaf::' + RID
PID = SEL + '.unreachable.1'
EXACT = dict(id=PID, display_id=PID, status='SUCCESS', description='unreachable code',
             **{'class': 'unreachable'}, file=None, line=None,
             location_display='library/core/src/lib.rs:0:0 in function ' + SEL)
CHECKS = []
TESTS = []


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def blob(repo, rev, path):
    return git(repo, 'show', rev + ':' + str(path))


def need(ok, label):
    if not ok:
        raise AssertionError(label)
    CHECKS.append(label)


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def saved(name):
    rel = INTAKE.relative_to(ROOT) / name
    b = blob(ROOT, REV, rel)
    need((INTAKE / name).read_bytes() == b, 'immutable current/committed intake: ' + name)
    return b


def main():
    paths = git(ROOT, 'ls-tree', '-r', '--name-only', REV, str(INTAKE.relative_to(ROOT))).decode().splitlines()
    need(len(paths) == 32, '32 committed original files')
    manifest = json.loads(saved('MANIFEST.json'))
    need(len(manifest['files']) == 30, '30 manifest entries')
    files = {}
    for name, expected in manifest['files'].items():
        b = saved(name)
        need(sha(b) == expected['sha256'] and len(b) == expected['bytes'], 'manifest hash/length: ' + name)
        files[name] = b
    # The hash manifest is independently compared to the JSON manifest.
    lines = saved('MANIFEST.sha256').decode().splitlines()
    need({line.split()[1]: line.split()[0] for line in lines} ==
         {n: x['sha256'] for n, x in manifest['files'].items()}, 'two manifest representations agree')
    pins = json.loads(files['INPUTS.json'])
    q = json.loads(files['QUALIFICATION.json'])
    costs = {x['id']: x for x in json.loads(files['COST.json'])['rows']}
    taskpath = ROOT / 'research/challenge-8/kani-k1/TASK-CH8-S3-R2-INTAKE-LOCATION-REVIEW-W14.md'
    need(taskpath.read_bytes() == blob(ROOT, TASK, taskpath.relative_to(ROOT)), 'exact task84aac8 bytes')
    run = json.loads(files['github-run.json'])
    need((run['id'], run['run_attempt'], run['head_sha'], run['event'], run['status'], run['conclusion']) ==
         (44416629057, 1, pins['trigger']['sha'], 'push', 'completed', 'failure'), 'saved terminal GitHub run identity')
    art = json.loads(files['github-artifacts.json'])['artifacts']
    need(len(art) == 1 and art[0]['id'] == 14482022386 and art[0]['size_in_bytes'] == 481904 and
         art[0]['digest'] == pins['artifact']['digest'] and not art[0]['expired'] and
         art[0]['workflow_run']['head_sha'] == run['head_sha'], 'saved artifact/run metadata identity')
    integ = json.loads(files['artifact-integrity.json'])
    gz = files['group-evidence.json.gz']
    need(sha(gz) == 'b9a02491bfb360eb17a13ab6f7fea78108d0371a7e8033f277674fb33213bed0', 'exact compact payload SHA256')
    raw = gzip.decompress(gz)
    need(sha(raw) == integ['uncompressed_sha256'] and len(raw) == 7006077, 'compact uncompressed identity')
    need(integ['sha256'] == '885fa419e00f4ad83d427d2d03c8c38fd51291dea0f9d04ee5c6e71030e904c0' and
         integ['bytes'] == 481904 and integ['digest_checked_before_zip_open'] and not integ['transport_saved'],
         'existing transport receipt attests digest-before-extraction; no transport reacquisition')
    packet = json.loads(raw)
    need(packet['state'] == 'PACKAGED' and packet['error'] is None, 'structured packet complete')
    members = {}
    data = {}
    for name, entry in packet['files'].items():
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts and path.suffix == '.json', 'structured member boundary: ' + name)
        b = entry['text'].encode() if entry.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(entry['text'], validate=True)
        need(len(b) == entry['bytes'] and sha(b) == entry['sha256'], 'structured member hash: ' + name)
        members[name] = b
        data[name] = json.loads(b)
    need(len(members) == 133, '133 authenticated structured members')
    identities = {}
    for label, repo, rev, tree in [
        ('source', SOURCE, SOURCE_REV, pins['source']['tree']),
        ('tool', CONTROL, TOOL, pins['tool']['tree']),
        ('control', CONTROL, CTRL, pins['control_candidate']['tree']),
        ('trigger', CONTROL, run['head_sha'], pins['trigger']['tree'])]:
        actual = git(repo, 'rev-parse', rev + '^{tree}').decode().strip()
        need(actual == tree, 'Git tree identity: ' + label)
        identities[label] = {'sha': rev, 'tree': actual, 'parents': git(repo, 'show', '-s', '--format=%P', rev).decode().strip()}
    need(identities['control']['tree'] == identities['trigger']['tree'] and
         identities['control']['parents'] == identities['trigger']['parents'] == pins['trigger']['sole_parent'], 'same-tree reviewed/executed siblings')
    dependencies = {}
    for name, rev in [('candidate', pins['candidate_g0']), ('review', pins['review_g0']), ('GO', pins['GO_g0']),
                      ('intake_task', pins['task_g0']), ('disabled_U_proposal', pins['offline_U_proposal']['g0'])]:
        dependencies[name] = {'sha': rev, 'tree': git(ROOT, 'rev-parse', rev + '^{tree}').decode().strip()}
    request_bytes = blob(CONTROL, CTRL, 'ch8-s1-control/CI-REQUEST.json')
    req = json.loads(request_bytes)
    need(sha(request_bytes) == pins['request_sha256'] and request_bytes == blob(CONTROL, run['head_sha'], 'ch8-s1-control/CI-REQUEST.json'), 'request exact executed/reviewed hash')
    wf = blob(CONTROL, CTRL, '.github/workflows/ch8-s2.yml')
    need(sha(wf) == pins['workflow_sha256'] and wf == blob(CONTROL, run['head_sha'], '.github/workflows/ch8-s2.yml'), 'workflow exact executed/reviewed hash')
    need('fetch-depth: 7' in wf.decode() and 'fetch-depth: 5' in wf.decode() and 'fetch-depth: 2' in wf.decode(), 'checkout depths7/5/2')
    for name, h in req['ci_payload_sha256'].items():
        b = blob(CONTROL, CTRL, name)
        need(sha(b) == h and b == blob(CONTROL, run['head_sha'], name), 'executed control payload: ' + name)
    sourcefiles = {}
    for key in ('changed_file_sha256', 'cfg_pfc_source_sha256', 'contract_stack_source_sha256', 'lexical_source_sha256', 'ordinary_contract_source_sha256'):
        for name, h in req[key].items():
            b = blob(SOURCE, SOURCE_REV, name)
            need(sha(b) == h, 'requested source hash: ' + name)
            sourcefiles[name] = b
    need(data['campaign-start.json']['request_data'] == req and data['receipt.json']['request_sha256'] == sha(request_bytes), 'native embedded exact request')
    need(req['unreachable_admission'] == {'mode': 'REJECT_ALL', 'proposal': 'S3-U-SITE-REVIEW-v1', 'enabled': False, 'unknown': 'REJECT', 'role_unreachable': 'REJECT'}, 'strict immutable admission policy')
    toolpaths = ['kani-driver/src/cbmc_output_parser.rs', 'kani-driver/src/cbmc_property_renderer.rs',
                 'kani-driver/src/frontend/schema_utils.rs', 'library/kani_macros/src/sysroot/contracts/check.rs',
                 'kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs']
    toolhashes = {name: sha(blob(CONTROL, TOOL, name)) for name in toolpaths}
    rows = []
    all_u = []
    with tempfile.TemporaryDirectory(prefix='w14-compact-review-') as td:
        tmp = Path(td)
        scripts = tmp / 'frozen-control'
        scripts.mkdir()
        frozen = {}
        for name in git(CONTROL, 'ls-tree', '-r', '--name-only', CTRL, 'ch8-s1-control').decode().splitlines():
            rel = Path(name).relative_to('ch8-s1-control')
            b = blob(CONTROL, CTRL, name)
            f = scripts / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(b)
            frozen[str(rel)] = sha(b)
        sys.path.insert(0, str(scripts))
        r = importlib.import_module('runner')
        campaign = importlib.import_module('s3_campaign')
        evidence = importlib.import_module('s3_evidence')
        rich = importlib.import_module('rich_evidence')
        policy = importlib.import_module('s3_policy')
        need(r.load_request() == req, 'frozen reader request loader')
        static = policy.validate_source(SOURCE, req)
        need(static['status'] == 'STATIC_PASS', 'existing bounded static source/cfg/provider/contract/lexical checks')
        local, upload = tmp / 'materialized', tmp / 'upload-only'
        local.mkdir(); upload.mkdir()
        for name, b in members.items():
            f = local / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(b)
        (upload / 'group-evidence.json.gz').write_bytes(gz)
        left = campaign.collect([local], req)
        right = campaign.collect([upload], req)
        need(left == right, 'authentic frozen upload-only/materialized collector equality')
        done = campaign.sealed(local)
        need(list(done) == req['s3']['selected'] and len(done) == 9, 'all9 completion seals in exact prefix order')
        need(left['global_stop'] is False and left['selected_missing_groups'] == [] and
             data['receipt.json']['state'] == 'SELECTED_PARTIAL' and data['receipt.json']['stop_reason'] is None,
             'durable selected partial observations; no global stop')
        write('PREFIX-AUDIT.json', {'frozen_control': CTRL, 'collector_equal': True, 'state': left['state'],
                                  'global_stop': left['global_stop'], 'selected_missing_groups': left['selected_missing_groups'],
                                  'sealed_order': list(done), 'collector_rows': [{k: x.get(k) for k in ('id', 'status', 'outcome', 'reason')} for x in left['rows']],
                                  'qualification': 'UNCHANGED; no completed observation is an admission'})
        invocations = set()
        namespaces = set()
        baseline = data['baseline.json']
        for rank, row in enumerate(req['rows'], 1):
            rid, selector = row['id'], row['selector']
            gp = 'groups/s3-' + rid + '/'
            g, co, bm = (data[gp + n] for n in ('receipt.json', 'compile/receipt.json', 'binding-metadata.json'))
            stock, properties = data[gp + 'export.json'], data[gp + 'properties.json']
            sup, life = data['workers/' + rid + '-supervision.json'], data['workers/' + rid + '-lifecycle.json']
            props = properties['harnesses'][0]['properties']
            protected = evidence.protected(g, req, baseline, sup, sha(request_bytes))
            need(evidence.provenance(g, co, req, rid, sha(request_bytes)), rid + ': compile/source/tool provenance')
            need(not protected['controller_recovery_used'] and not protected['observed_errors_ignored'], rid + ': no protected evidence recovery/suppression')
            need(campaign.snapshots.validate_pair(baseline, life['pre'], life['post'], life['context']), rid + ': E0/pre/post controller binding')
            for label, snap in [('E0', baseline['binaries']), ('pre', life['pre']['binaries']), ('worker.before', g['tool_fingerprints_before']),
                                ('worker.after', g['tool_fingerprints_after']), ('post', life['post']['binaries'])]:
                need(r.fingerprints_match(baseline['binaries'], snap), rid + ': canonical binary snapshot ' + label)
            need(g['invocation_id'] not in invocations and g['cargo_target_dir'] not in namespaces, rid + ': unique invocation and namespace')
            invocations.add(g['invocation_id']); namespaces.add(g['cargo_target_dir'])
            std = Path('/home/runner/work/kani/kani/export')
            tool = Path('/home/runner/work/kani/kani/tool')
            out = Path('/home/runner/work/_temp/ch8-s1-receipts') / gp / 'export.json'
            need(g['argv'] == r.build_argv(std, tool, [selector], row['unwind'], out), rid + ': singleton exact argv')
            need(g['cargo_target_dir'] == str(std / 'target/ch8-s1-cargo' / g['invocation_id']), rid + ': exact target namespace')
            need(g['native_start_verified'] and [x['selector'] for x in g['native_start_events']] == [selector] and
                 g['effective_cfg'] == req['flags']['RUSTFLAGS'], rid + ': native start/cfg')
            need(bm['invocation_id'] == g['invocation_id'] and bm['request_sha256'] == sha(request_bytes) and
                 bm['std_sha'] == SOURCE_REV and bm['tool_sha'] == TOOL and bm['argv'] == g['argv'], rid + ': same-invocation binding metadata')
            registrations, providers = [], []
            for m in bm['native_metadata']:
                if m.get('state') != 'CAPTURED':
                    continue
                b = m['text'].encode() if m.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(m['text'], validate=True)
                need(len(b) == m['bytes'] and sha(b) == m['sha256'], rid + ': native metadata digest ' + m['path'])
                md = json.loads(b)
                registrations += [x for x in md.get('proof_harnesses', []) if x['pretty_name'] == selector]
                providers += [x for x in md.get('contracted_functions', []) if selector in x.get('harnesses', [])]
            need(len(registrations) == 1, rid + ': unique native registration')
            registration = registrations[0]
            binding = req['source_bindings'][rid]
            need(registration['original_file'] == str(std / binding['file']) and registration['crate_name'] == 'core', rid + ': native registration source/crate')
            if row['mode'] == 'PFC':
                need(registration['attributes']['kind'] == {'ProofForContract': {'target_fn': binding['target']}} and
                     registration['attributes']['stubs'] == registration['attributes']['verified_stubs'] == [] and len(providers) == 1,
                     rid + ': native PFC target/provider; no ordinary/verified stubs')
            else:
                need(registration['attributes']['kind'] == 'Proof' and not registration['attributes']['verified_stubs'], rid + ': Original negative kind')
                expected_stubs = [{'original': 's2_swap_seam', 'replacement': 'weak_swap'}] if rid == 'sort13_weak' else []
                need(registration['attributes']['stubs'] == expected_stubs, rid + ': exact negative seam')
            hs = stock.get('harnesses', [])
            audit = {'id': rid, 'selector': selector, 'rank': rank, 'invocation_id': g['invocation_id'],
                     'namespace': g['cargo_target_dir'], 'group_state': g['state'], 'canonical': data[rid + '/receipt.json']['outcome'],
                     'original_exception': g.get('original_exception'), 'source_tool_request_protected': 'MATCH',
                     'native_registration': registration, 'providers': providers, 'role_cover_bindings': [], 'members': {n: sha(members[gp+n]) for n in ('receipt.json', 'compile/receipt.json', 'binding-metadata.json', 'export.json', 'properties.json')},
                     'unexported_binding': bm['rows'][0]['binding_gaps']}
            if not hs:
                need(props == [] and g['execution']['termination_reason'] in ('rss_cap', 'timeout'), rid + ': no completed inventory; explicit resource cap')
                audit.update(S1='NO_COMPLETED_NATIVE_RESULT', U_count=0, native=None)
                rows.append(audit)
                continue
            need(len(hs) == 1 and hs[0]['name'] == selector, rid + ': exact singleton export')
            h = hs[0]
            rebound = r.validate_export_value(stock, row, source_binding=binding, std=std, group_selectors=[selector])
            need(rebound['outcome'] == 'RECORDED', rid + ': frozen source-stage-target export reader')
            decoder = rich.RegularEvidence([selector], std)
            decoder.finished = True; decoder.closed = {selector}; decoder.records = {selector: copy.deepcopy(props)}
            try:
                decoder.validate(stock)
                need(rid != RID, rid + ': frozen full metadata validator accepted')
            except ValueError as exc:
                need(rid == RID and str(exc) == 'rich metadata incomplete: file/line missing', rid + ': frozen validator exact location rejection only')
            missing = [x for x in props if not located(x)]
            need(missing == ([EXACT] if rid == RID else []), rid + ': precise missing-site set')
            failures = [x for x in props if x['class'] != 'cover' and x['status'] == 'FAILURE']
            target_negative = row['expected'] == 'DETECTED'
            need(len(failures) == (1 if target_negative else 0), rid + ': no additional failed safety/panic/unwind checks')
            need(h['outcome'] == {'kind': 'COMPLETED', 'verdict': 'FAILURE' if target_negative else 'SUCCESS'}, rid + ': native verdict')
            for role in row['roles']:
                matches = [x for x in props if x['description'] == role['description']]
                need(len(matches) == 1 and all(x['class'] == role['class'] and x['status'] == role['status'] and
                     x['file'] == str(std / role['file']) and x['line'] == str(role['line']) for x in matches), rid + ': literal role ' + role['description'])
                b = sourcefiles[role['file']]
                need(sha(b) == role['source_sha256'] and b.decode().splitlines()[role['line']-1] == role['source_line'], rid + ': literal source site ' + role['description'])
                audit['role_cover_bindings'].append({'description': role['description'], 'source_line': role['line'], 'native': matches[0]})
            covers = [x for x in props if x['class'] == 'cover']
            need(len(covers) == row['required_cover_count'] and {x['description'] for x in covers} == set(row['required_cover_messages']) and
                 all(x['status'] == 'SATISFIED' for x in covers), rid + ': exact required covers; no extra/wrong-root covers')
            need(all(x['status'] in ('SUCCESS', 'FAILURE', 'UNREACHABLE') for x in props if x['class'] != 'cover'), rid + ': no unassessed unknown/error/undetermined check')
            unsupported = h['unsupported_constructs']
            need(all(x['status'] == 'SUCCESS' and x['id'] not in h['checks']['unreachable'] for x in unsupported), rid + ': all unsupported guards separately SUCCESS')
            strict = policy.expected_observation(row, rebound, properties['harnesses'][0])
            need(strict is False, rid + ': strict frozen expected_observation rejects')
            us = [x for x in props if x['status'] == 'UNREACHABLE']
            for prop in us:
                matches = [x for x in q['U_instances'] if x['root'] == rid and x['property']['id'] == prop['id']]
                need(len(matches) == 1, rid + ': exactly one U argument ' + prop['id'])
                u = matches[0]
                need(u['property'] == prop and u['selector'] == selector and u['invocation_id'] == g['invocation_id'] and
                     u['member'] == gp + 'properties.json' and u['member_sha256'] == sha(members[gp+'properties.json']), rid + ': exact U native/member identity ' + prop['id'])
                need(u['source_sha'] == SOURCE_REV and u['effective_cfg'] == g['effective_cfg'] and u['provider_target'] == binding['target'], rid + ': exact U provider/cfg ' + prop['id'])
                sourceb = blob(SOURCE, SOURCE_REV, u['source_file'])
                need(sha(sourceb) == u['source_sha256'] and str(u['source_line']) == prop['line'] and prop['file'] == str(std/u['source_file']), rid + ': U source hash/line ' + prop['id'])
                lines = sourceb.decode().splitlines(); lineno = u['source_line']
                context = '\n'.join(f'{n+1}: {lines[n]}' for n in range(max(0, lineno-5), min(len(lines), lineno+4)))
                need(u['source_context'] == context, rid + ': U bounded context ' + prop['id'])
                reason, loop = independent_u(rid, u)
                need(not u['proposal_argument_reused'] and u['assessment'] == 'SOURCE_LOCAL_DEFINEDNESS_ARGUMENT', rid + ': U independently assessed; proposal not reused ' + prop['id'])
                all_u.append({'root': rid, 'selector': selector, 'invocation_id': g['invocation_id'], 'property': prop,
                              'member': u['member'], 'member_sha256': u['member_sha256'], 'source_file': u['source_file'],
                              'source_line': lineno, 'source_sha': SOURCE_REV, 'source_sha256': u['source_sha256'],
                              'native_context': {'effective_cfg': g['effective_cfg'], 'provider_target': binding['target'], 'type': 'u8', 'comparator': 'KeyLess<u8>'},
                              'intake_predicate': u['predicate'], 'intake_premises': u['premises'], 'independent_reason': reason,
                              'loop_binding': loop, 'decision': 'SOUND_SOURCE_LOCAL_ARGUMENT_AT_SOURCE_REPORTED_LEVEL',
                              'independent_MIR_origin': 'UNKNOWN; not an S1 additional gate'})
            pfc = None
            if row['mode'] == 'PFC':
                contract = registration['contract']['contracted_function_name']
                decoded = subprocess.check_output(['c++filt', '-i', '-s', 'rust', contract], text=True).strip()
                need(decoded.startswith('core::slice::sort::shared::smallsort::' + binding['target'] + '::<u8, core::slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>::'), rid + ': full concrete PFC symbol')
                syschecks = [x for x in props if x['id'].startswith(decoded + '.')]
                need(all(any(x['class'] == cls and x['status'] == 'SUCCESS' and contract in x['description'] for x in syschecks)
                         for cls in ('single_top_level_call', 'no_recursive_call')), rid + ': raw contract-symbol/DFCC property links')
                basefn = 'slice::sort::shared::smallsort::' + binding['target'] + '::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>'
                ensures = [x for x in props if x['id'].startswith(basefn + '::') and x['class'] == 'assertion' and
                           x['description'].startswith('|_|')]
                need(len(ensures) == 1 and ensures[0]['status'] == 'SUCCESS' and located(ensures[0]), rid + ': source-reported checked ensures property')
                pfc = {'raw_modifies_symbol': contract, 'decoded_modifies_symbol': decoded, 'DFCC_links': syschecks,
                       'ensures': ensures[0], 'method': 'pinned stock Check actual body + source/cfg/provider/contract-stack validators',
                       'independent_MIR': 'UNKNOWN; no independent B1/B2 credit'}
            audit.update(native=h['outcome'], check_counts=dict(collections.Counter(x['status'] for x in props if x['class'] != 'cover')),
                         checks=h['checks']['total'], covers=len(covers), U_count=len(us), unsupported_constructs=unsupported,
                         strict_expected_match=strict, PFC=pfc,
                         S1='SOUND_CONDITIONAL_EXACT_LOCATION_DECISION' if rid == RID else 'SOUND_SOURCE_REPORTED_CASE_ASSESSMENT')
            rows.append(audit)
        need(len(all_u) == len(q['U_instances']) == 42, 'all42 U occurrences individually matched and assessed')
        location_tests(rich, evidence, req, data, sha(request_bytes))
        # Exercise the actual protected-evidence reader, not merely the test predicate.
        changed = copy.deepcopy(data['groups/s3-'+RID+'/receipt.json'])
        snap = changed['tool_fingerprints_after']['binaries']
        first = next(iter(snap))
        snap[first]['sha256'] = '0' * 64
        try:
            evidence.protected(changed, req, baseline, data['workers/'+RID+'-supervision.json'], sha(request_bytes))
        except evidence.EvidenceError as exc:
            need('drift' in str(exc), 'authentic frozen protected reader rejects changed binary hash')
        else:
            raise AssertionError('protected reader accepted changed hash')
    need(sum(x['U_count'] for x in rows) == 42 and sum(x.get('covers', 0) for x in rows) == 24, 'U42/cover24 aggregate independently recomputed')
    need(sum(len(x.get('unsupported_constructs', [])) for x in rows) == 16, '16 actual successful unsupported guards, arrays nonempty')
    for row in req['rows']:
        rid = row['id']; gp = 'groups/s3-' + rid + '/'
        g, co, sup = data[gp+'receipt.json'], data[gp+'compile/receipt.json'], data['workers/'+rid+'-supervision.json']
        cost = costs[rid]
        need(cost['compile_elapsed_upper_bound_seconds'] == co['elapsed_upper_bound_seconds'], rid + ': cost compile upper bound binding')
        for key, value in cost['execution'].items():
            need(g['execution'].get(key) == value, rid + ': cost execution field ' + key)
        need(sup['worker_exit'] == 0 and sup['containment']['verified'] and not sup['cutoff'] and not sup['supervisor_error'], rid + ': cleanup and serial continuation')
        hs = data[gp+'export.json'].get('harnesses', [])
        if hs:
            need(cost['native_verification_time_s'] == hs[0]['resources']['verification_time_s'], rid + ': native verification time distinct from child elapsed')
    insert, merge = costs['s3_insert_tail_u8_rel16'], costs['s3_merge8_u8_same_alloc']
    need((insert['execution']['elapsed_seconds'], insert['execution']['rss_peak_kib'], insert['compile_elapsed_upper_bound_seconds'], insert['execution']['termination_reason']) ==
         (112.349, 6326988, 34.68, 'rss_cap'), 'insert exact local sampled RSS censoring')
    need((merge['execution']['elapsed_seconds'], merge['execution']['rss_peak_kib'], merge['compile_elapsed_upper_bound_seconds'], merge['execution']['termination_reason']) ==
         (600.205, 2558128, 35.105, 'timeout'), 'merge exact whole-child timeout censoring')
    for cost in (insert, merge):
        need(cost['execution']['original_exit_code'] == -15 and cost['execution']['signal'] == 15 and cost['execution']['child_shutdown_verified'], cost['id'] + ': original signal/exit preserved')
    validation = {'status': 'PASS', 'scope': 'bounded offline integrity/static/frozen-reader replay and distinct hypothetical case model',
                  'checks_count': len(CHECKS), 'checks': CHECKS, 'negative_controls': TESTS,
                  'native_executed': False, 'full_Validate_executed': False, 'producer_reader_or_policy_modified': False,
                  'hypothetical_case': 'NOT_APPLIED; never replaces actual frozen rejection', 'proof_credit': 'NONE'}
    write('VALIDATION.json', validation)
    write('U-REVIEW.json', {'assurance': 'S1 SOURCE_REPORTED', 'occurrences': all_u, 'count': len(all_u), 'blanket_waivers': False})
    write('CASE-ASSESSMENT.json', {'rows': rows, 'six_provisional': 'SOUND, with corrected fixed sort13 fixture; no admission',
                                 'seventh': 'SOUND conditional exact location-only decision; no admission',
                                 'two_capped': 'NO_COMPLETED_RESULT', 'strict_expected_matches': 0, 'B1_B2': 'NONE'})
    write('INPUT-AUDIT.json', {'task': TASK, 'intake': REV, 'original_committed_files': len(paths), 'manifest_files': len(manifest['files']),
                             'original_intake_hashes': {n: sha(b) for n,b in files.items()}, 'structured_members': len(members),
                             'compact_sha256': sha(gz), 'uncompressed_sha256': sha(raw), 'uncompressed_bytes': len(raw),
                             'structured_member_decoded_bytes': sum(map(len, members.values())), 'identities': identities,
                             'dependencies': dependencies, 'request_sha256': sha(request_bytes), 'workflow_sha256': sha(wf),
                             'source_files_sha256': {n: sha(b) for n,b in sourcefiles.items()}, 'tool_semantics_source_sha256': toolhashes,
                             'frozen_control_sources': frozen, 'static_gate_status': static['status'],
                             'static_report_canonical_sha256': sha(json.dumps(static,sort_keys=True,separators=(',',':')).encode()),
                             'transport_digest': {'receipt_checked': True, 'reviewer_rehashed_transport': False, 'reason': 'transport not retained; reacquisition prohibited'},
                             'physical_inode_realpath_and_intermediate_bytes': 'UNKNOWN', 'intake_disposition': 'REQUEST_CHANGES localized reporting corrections; evidence integrity PASS'})
    print(json.dumps({'status': 'PASS', 'checks': len(CHECKS), 'negative_controls': len(TESTS), 'U': len(all_u), 'roots': len(rows)}))


def located(p):
    return isinstance(p.get('file'), str) and bool(p['file']) and isinstance(p.get('line'), str) and re.fullmatch('[1-9][0-9]*', p['line']) is not None


def independent_u(rid, u):
    """Reviewer decisions by exact expression/context, never by std whitelist/status."""
    name, line, p = u['source_file'], u['source_line'], u['property']
    need(p['class'] == 'assertion' and p['status'] == 'UNREACHABLE' and u['source_local_argument'] and u['predicate'] and u['premises'], rid + ': full U premise/predicate record ' + p['id'])
    if name.endswith('/sorting_model.rs'):
        need(rid in ('checker_order_corrupt', 'checker_count_corrupt', 'sort13_weak'), 'checker U actual caller')
        reason = {100: 'Order-loop entry i=1; increment only after i<L<=32, hence i+1<=32.',
                  106: 'Outer loop 0<=i<L<=32; Snapshot.values has capacity32.',
                  111: 'Inner 0<=j<L<=32 bounds Snapshot.values[j]; old_count starts0 and is at most j before its at-most-once increment.',
                  112: 'Entry L=values.len bounds values[j]; new_count starts0 and is at most j before its at-most-once increment.',
                  113: 'Inner increment requires j<L<=32, hence j+1<=32.',
                  118: 'Outer increment requires i<L<=32, hence i+1<=32.'}[line]
        return reason, {'entry': 'before.valid; L=before.len=values.len<=CAP32', 'loops': 'i/order1..L; i/count0..L; j0..L; count<=j',
                        'caller_length': {'checker_order_corrupt': 2, 'checker_count_corrupt': 32, 'sort13_weak': 13}[rid],
                        'sort13_fixture': 'fixed [12,11,...,0], ordinary weak_swap seam; NOT arbitrary bytes' if rid == 'sort13_weak' else None}
    if name.endswith('/fmt/mod.rs') and line == 820:
        return 's.len()<<1 checks shift count1, which is below 64-bit usize width. No claim that shifting preserves discarded bits.', 'no loop; exact x86_64 source-reported target'
    if name.endswith('/num/uint_macros.rs') and line in (3222, 3224):
        return ('self<other implies other-self is defined.' if line == 3222 else 'Else self>=other implies self-other is defined.'), 'branch-local; every usize operand, no range premise'
    if name.endswith('/ptr/const_ptr.rs') and line == 1479:
        return 'Normal continuation follows is_power_of_two(align); zero is not a power of two, so align>=1 and align-1 cannot underflow.', 'no loop; original panic and pointer checks remain'
    if name.endswith('/ub_checks.rs') and line == 148:
        return 'Conditional skips division when size=0; else divisor nonzero. Independently u8 size=1.', 'branch-local; allocation validity remains separate'
    if name.endswith('/smallsort.rs') and line in (782, 783):
        need(rid in ('s3_sort4_u8_separate', RID), 'sort4 U caller binding')
        return 'Concrete comparison returns bool c2. Cast of c2 or !c2 is0 or1; 2+operand<=3, no usize overflow.', 'no loop; native source-reported sort4_stable<u8,KeyLess<u8>>; each separate/same geometry retained'
    if name.endswith('/smallsort.rs') and line in (974, 990, 991, 992):
        need(rid == 's3_merge8_u8_separate', 'merge U exact native caller length binding')
        return ({974: 'Division by literal2, independent of length.', 990: 'Exact harness passes &src[1..9]: len8, half4, half-1=3.',
                 991: 'Exact harness len8 gives right_rev index len-1=7.', 992: 'Exact harness len8 gives dst_rev index len-1=7; writes/provenance remain separate.'}[line],
                'function-entry length8; before merge loop; concrete source-reported PFC context. No generic length or caller theorem')
    raise AssertionError('unreviewed U expression ' + str((rid, name, line, p['description'])))


def location_tests(rich, evidence, req, data, request_hash):
    gp = 'groups/s3-' + RID + '/'
    original = {'stock': data[gp+'export.json'], 'properties': data[gp+'properties.json'], 'group': data[gp+'receipt.json'],
                'binding': data[gp+'binding-metadata.json'], 'supervision': data['workers/'+RID+'-supervision.json'], 'selector': SEL}
    props = original['properties']['harnesses'][0]['properties']
    need([p for p in props if not located(p)] == [EXACT], 'location authentic exact singleton missing record')
    record = ('Checking harness '+SEL+'...\nRESULTS:\nCheck 1: '+PID+'\n\t - Status: SUCCESS\n\t - Description: "unreachable code"\n\t - Location: '+EXACT['location_display']+'\nSUMMARY:\n').encode()
    parser = rich.RegularEvidence([SEL], '/home/runner/work/kani/kani/export')
    parser.feed(record); parser.finish()
    need(parser.error is None and parser.records == {SEL: [EXACT]} and len(parser.missing_sites) == 1,
         'actual frozen streaming parser reconstructs zero sentinel -> present-null file/line')
    need(not rich.location_exception(SEL, EXACT), 'existing exact S1 exception excludes this harness/property')

    def hypothetical(case):
        """Independent CASE-ONLY test model. Does not modify the frozen reader."""
        try:
            if case['selector'] != SEL:
                return False
            g, bm, stock = case['group'], case['binding'], case['stock']
            if g['invocation_id'] != original['group']['invocation_id'] or bm['invocation_id'] != g['invocation_id']:
                return False
            if bm['request_sha256'] != request_hash or bm['std_sha'] != SOURCE_REV or bm['tool_sha'] != TOOL:
                return False
            evidence.protected(g, req, data['baseline.json'], case['supervision'], request_hash)
            evidence.provenance(g, data[gp+'compile/receipt.json'], req, RID, request_hash)
            if g['argv'] != original['group']['argv'] or g['cargo_target_dir'] != original['group']['cargo_target_dir'] or g['effective_cfg'] != req['flags']['RUSTFLAGS']:
                return False
            if g['native_start_events'] != original['group']['native_start_events'] or not g['native_start_verified']:
                return False
            if stock['harness_selection'] != original['stock']['harness_selection'] or stock['configuration'] != original['stock']['configuration']:
                return False
            if any(stock.get(k) != original['stock'].get(k) for k in ('kani_commit', 'kani_commit_dirty', 'target', 'enabled_unstable_features', 'run_state', 'outcome')):
                return False
            h = stock['harnesses'][0]
            if len(stock['harnesses']) != 1 or h['name'] != SEL or h['outcome'] != {'kind':'COMPLETED','verdict':'SUCCESS'} or h['n_properties'] != 363 or h['checks']['total'] != 356 or h['checks']['success'] != 351 or h['covers']['total'] != 7:
                return False
            if h['checks'] != original['stock']['harnesses'][0]['checks'] or h['covers'] != original['stock']['harnesses'][0]['covers']:
                return False
            doc = case['properties']
            if len(doc['harnesses']) != 1 or doc['harnesses'][0]['name'] != SEL:
                return False
            ps = doc['harnesses'][0]['properties']
            decoder = rich.RegularEvidence([SEL], '/home/runner/work/kani/kani/export')
            decoder.finished=True; decoder.closed={SEL}; decoder.records={SEL:copy.deepcopy(ps)}
            try:
                decoder.validate(stock)
            except ValueError as exc:
                if str(exc) != 'rich metadata incomplete: file/line missing':
                    return False
            else:
                return False  # This recommendation applies only to the authentic null-coordinate case.
            if [p for p in ps if not located(p)] != [EXACT]:
                return False
            row = next(x for x in req['rows'] if x['id']==RID)
            for role in row['roles']:
                ms = [p for p in ps if p['description']==role['description']]
                if len(ms)!=1 or ms[0]['class']!=role['class'] or ms[0]['status']!=role['status'] or ms[0]['file']!='/home/runner/work/kani/kani/export/'+role['file'] or ms[0]['line']!=str(role['line']):
                    return False
            if [p for p in ps if p['status']=='UNREACHABLE'] != [p for p in props if p['status']=='UNREACHABLE']:
                return False  # all5 U must retain their independent argument identity; status never rewritten.
            if any(p['status'] not in ('SUCCESS','UNREACHABLE','SATISFIED') for p in ps):
                return False
            if len([p for p in ps if p['class']=='cover'])!=7:
                return False
            return True
        except (ValueError, KeyError, TypeError, IndexError):
            return False

    need(hypothetical(original), 'hypothetical exact case model admits authentic observed case only')
    for field, value in [('id', PID+'.new'), ('display_id', PID+'.new'), ('class', 'assertion'), ('status', 'FAILURE'),
                         ('description', 'different'), ('location_display', EXACT['location_display']+'x'), ('file', 'library/core/src/lib.rs'), ('line','1')]:
        changed = copy.deepcopy(original)
        p = next(p for p in changed['properties']['harnesses'][0]['properties'] if p['id']==PID)
        p[field] = value
        need(not hypothetical(changed), 'hypothetical exact-case rejects changed ' + field)
        TESTS.append({'mutation': 'offending.'+field, 'expected': 'REJECT', 'observed': 'REJECT'})
    mutations = ['harness','missing-key','locationless-role','locationless-cover','locationless-failed-check', 'extra-missing-record',
                 'count-mismatch','stock-success-mismatch','wrong-invocation','wrong-request','wrong-source','wrong-tool','wrong-cfg','wrong-namespace','changed-U','changed-binary']
    for mutation in mutations:
        changed = copy.deepcopy(original); ps=changed['properties']['harnesses'][0]['properties']
        if mutation=='harness': changed['selector']+='x'
        elif mutation=='missing-key': del next(p for p in ps if p['id']==PID)['file']
        elif mutation in ('locationless-role','locationless-cover','locationless-failed-check'):
            p=next(p for p in ps if p['description']=='S3_SORT4_SAME_ACTIVE') if mutation!='locationless-cover' else next(p for p in ps if p['class']=='cover')
            p['file']=None; p['line']=None
            if mutation=='locationless-failed-check':p['status']='FAILURE'
        elif mutation=='extra-missing-record':
            p=next(p for p in ps if p['id']!=PID and p['class'] not in ('cover','assertion'));p['file']=None;p['line']=None
        elif mutation=='count-mismatch':ps.pop()
        elif mutation=='stock-success-mismatch':changed['stock']['harnesses'][0]['checks']['success']+=1
        elif mutation=='wrong-invocation':changed['binding']['invocation_id']='new'
        elif mutation=='wrong-request':changed['binding']['request_sha256']='0'*64
        elif mutation=='wrong-source':changed['binding']['std_sha']='0'*40
        elif mutation=='wrong-tool':changed['binding']['tool_sha']='0'*40
        elif mutation=='wrong-cfg':changed['group']['effective_cfg']=''
        elif mutation=='wrong-namespace':changed['group']['cargo_target_dir']+='/other'
        elif mutation=='changed-U':next(p for p in ps if p['status']=='UNREACHABLE')['description']+='x'
        elif mutation=='changed-binary':
            binaries=changed['group']['tool_fingerprints_after']['binaries'];binaries[next(iter(binaries))]['sha256']='0'*64
        need(not hypothetical(changed), 'hypothetical exact-case rejects ' + mutation)
        TESTS.append({'mutation': mutation, 'expected': 'REJECT', 'observed': 'REJECT'})
    write('LOCATION-TESTS.json', {'authentic_stream_reconstruction': 'PASS: nulls retained',
                                'frozen_reader': 'REJECT rich metadata incomplete: file/line missing',
                                'hypothetical_model': 'NOT_APPLIED; exact-case authentic ACCEPT and mutation REJECT controls',
                                'negative_controls': TESTS})


if __name__ == '__main__':
    main()
