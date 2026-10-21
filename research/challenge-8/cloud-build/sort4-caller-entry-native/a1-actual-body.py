"""R15 full actual sort4 proof attempt, with separate checked copy components.

Imports are inert. Construction/export/verification are Cloud-only. No result
from this experimental runner is an admitted callee summary or formal credit.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time

HERE = Path('research/challenge-8/cloud-build/sort4-caller-entry-native')
AUTH = 'SORT4-ACTUAL-BODY-2026-10-21-R15'
PROFILE = HERE / 'A1-ACTUAL-BODY-R15-PROFILE-2026-10-21.json'
SOURCE = 'library/core/src/slice/sort/shared/smallsort.rs'
SOURCE_SHA = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
COUNTS = {b'is_less(': 5, b'hint::select_unpredictable(': 8,
          b'ptr::copy_nonoverlapping(': 4}


def need(ok, why):
    if not ok:
        raise RuntimeError('R15-ACTUAL-BODY: ' + why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_load(path, expected, name):
    need(path.is_file() and sha(path.read_bytes()) == expected, 'dependency pin ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'module spec')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    need(sha(path.read_bytes()) == expected, 'dependency changed during import')
    return module


def snapshot(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.tmp')
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


# These are complete target posts, not presumed facts. A failing proof cannot
# yield a resource receipt. Source remains the only T ownership sequence.
CONTRACT = b'''/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    v_base[..4] |-> ?source_before &*& foreach(source_before, own::<T>(t)) &*&
    array_::<T>(dst, 4, ?destination_before) &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    v_base[..4] |-> ?source_after &*& foreach(source_after, own::<T>(t)) &*&
    dst[..4] |-> ?destination_after &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
/*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    v_base[..4] |-> ?source_after &*& foreach(source_after, own::<T>(t)) &*&
    array_::<T>(dst, 4, destination_before) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
'''


def construct_actual(source, ghost, capture):
    """Called only after Cloud guard; exact complete source body is mandatory."""
    need(sha(source) == SOURCE_SHA, 'pinned std source bytes')
    lines = source.splitlines(keepends=True)
    original_body = b''.join(lines[605:652])
    need(original_body.startswith(capture.FUNCTION_HEADER + b'{\n') and
         original_body.endswith(b'    }\n}\n'), 'full actual signature/body604..652')
    need(all(original_body.count(k) == v for k, v in COUNTS.items()), 'complete body source calls')
    # Reuse only reviewed checked-lemma/proof-annotation text; never reuse the
    # historical diagnostic's truncated runtime or positive-size precondition.
    helpers = capture.MEMORY_PRE_INTERIOR_LEMMA + capture.BORROW_PREFIX_SPLIT_LEMMA
    prefix = b'#![feature(const_trait_impl)]\n#![allow(internal_features)]\nuse std::{hint, ptr};\n'
    body = original_body.replace(capture.FUNCTION_HEADER + b'{',
                                capture.FUNCTION_HEADER + CONTRACT + b'{', 1)
    body = body.replace(b'    unsafe {\n', capture.BORROW_PREFIX_LIFETIME_SCOPE, 1)
    first = b'        let c1 = is_less(&*v_base.add(1), &*v_base);'
    need(body.count(first) == 1, 'first actual callback anchor')
    body = body.replace(first, capture.BORROW_PREFIX_FIRST_CALL, 1)
    for name in (b'c2', b'c3', b'c4', b'c5'):
        body = body.replace(b'let ' + name + b' = is_less(',
            b'let ' + name + b" = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(", 1)
    generated = prefix + helpers + body
    original = ghost.strip_ghost(generated)
    need(original == ghost.strip_ghost(prefix) + original_body,
         'ghost strip must preserve entire exact runtime body')
    lo = generated[:generated.index(b'pub unsafe fn sort4_stable')].count(b'\n') + 1
    hi = len(generated.splitlines())
    generated_lines = generated.splitlines()
    prerequisites = []
    for name in ('interior_pointer_limits', 'split_four_owned_cells'):
        starts = [i for i, line in enumerate(generated_lines, 1) if line.startswith(b'lem ' + name.encode() + b'<')]
        need(len(starts) == 1, 'one checked lemma prerequisite')
        start = starts[0]
        end = next(i for i in range(start + 1, len(generated_lines) + 1) if generated_lines[i - 1] == b'@*/') - 1
        prerequisites.append({'name': name, 'focus_line': start, 'end_line': end})
    return generated, original, {'name': 'sort4_stable', 'focus_line': lo,
        'end_line': hi, 'std_source_sha256': SOURCE_SHA,
        'std_span': [606, 652], 'required_lemmas': prerequisites, 'std_body_sha256': sha(original_body),
        'runtime_body_byteequal': True, 'runtime_call_counts': {
            k.decode(): v for k, v in COUNTS.items()},
        'domain': 'generic T/F; separating initialized source4 ownership and writable optional destination4; caller transfer/ZST qualification open',
        'normal': 'current source4 with sole T own sequence; initialized dest4 shadows; current F/thread/typeinterp',
        'unwind': 'current source4 with sole T own sequence; unchanged optional dest4; current F/thread/typeinterp',
        'sortedness': False, 'stability': False,
        'proof_credit': False, 'summary_eligible': False}


def component_cases(source, ghost, expected_count=4):
    prefix = source.split(b'// CASE_BEGIN', 1)[0]
    cases = []
    for m in re.finditer(rb'// CASE_BEGIN ([^\n]+)\n(.*?)// CASE_END \1\n', source, re.S):
        name = m[1].decode()
        verified = prefix + m[2]
        header = re.search(rb'unsafe fn ([A-Za-z_0-9]+)<T>', verified)
        need(header is not None, 'copy component function header')
        focus = verified[:header.start()].count(b'\n') + 1
        cases.append((name, verified, ghost.strip_ghost(verified), {
            'name': header[1].decode(), 'focus_line': focus,
            'end_line': len(verified.splitlines()), 'summary_eligible': False,
            'proof_credit': False, 'required_lemmas': lemma_metadata(prefix)}))
    need(len(cases) == expected_count and len({c[0] for c in cases}) == expected_count, 'exact copy resource case inventory')
    return cases


def lemma_metadata(source):
    """Exact intervals of pinned ghost lemmas, including nested proof cases."""
    lines = source.splitlines()
    result = []
    for i, line in enumerate(lines):
        match = re.match(rb'lem ([A-Za-z_0-9]+)(?:<|\()', line)
        if not match:
            continue
        begin = next((j for j in range(i + 1, len(lines)) if lines[j] == b'{'), None)
        need(begin is not None, 'ghost lemma body opening')
        balance = 0
        end = None
        for j in range(begin, len(lines)):
            # This pinned fixture grammar has no block comments/strings with
            # braces in proof bodies. AST interval equality is checked later.
            proof_line = lines[j].split(b'//', 1)[0]
            balance += proof_line.count(b'{') - proof_line.count(b'}')
            need(balance >= 0, 'ghost lemma brace balance')
            if balance == 0:
                end = j
                break
        need(end is not None, 'ghost lemma body closing')
        result.append({'name': match[1].decode(), 'focus_line': i + 1,
                       'end_line': end + 1})
    return result


def selector_cases(source, ghost):
    rows = lemma_metadata(source)
    need([r['name'] for r in rows] == [
        'selector_permutation', 'selector_wrong_minimum_post_negative'],
        'exact pure selector positive/negative inventory')
    common = {'mir_target': 'r15_selector_permutation_type_anchor',
              'summary_eligible': False, 'proof_credit': False,
              'scope': 'arbitrary Boolean indices only; actual pointer/source binding open'}
    original = ghost.strip_ghost(source)
    return [
        ('selector-permutation-positive', source, original, {**common, **rows[0]}),
        ('selector-wrong-minimum-negative', source, original,
         {**common, **rows[1], 'required_lemmas': [rows[0]]}),
    ]


def recovery_four_cases(source, ghost):
    rows = lemma_metadata(source)
    need([r['name'] for r in rows] == ['join_four_owned_cells',
        'recover_four_sources', 'recover_four_missing_fourth_end_token_negative'],
        'exact generic four-owner recovery inventory')
    original = ghost.strip_ghost(source)
    cases = []
    for i, row in enumerate(rows):
        name = ('generic-four-' + row['name'] + ('-negative' if i == 2 else '-positive'))
        cases.append((name, source, original, {**row,
            'mir_target': 'r15_recover_four_sources_type_anchor',
            'required_lemmas': rows[:i],
            'scope': 'checked debt recovery only; actual callback establishment open',
            'summary_eligible': False, 'proof_credit': False}))
    return cases


def recovery_cases(source, ghost):
    original = ghost.strip_ghost(source)
    helpers = lemma_metadata(source)
    need([x['name'] for x in helpers] == ['recover_pair', 'join_four_owned_cells'],
         'exact checked pair recovery/join helper inventory')
    cases = []
    for helper in helpers:
        cases.append((helper['name'] + '-positive', source, original,
            {**helper, 'mir_target': 'r15_recover_pair_type_anchor',
             'summary_eligible': False, 'proof_credit': False}))
    name = 'recover_pair_missing_reserved_half'
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines, 1) if line.startswith(b'pub unsafe fn ' + name.encode() + b'<'))
    end = next(i for i in range(start + 1, len(lines) + 1) if lines[i - 1] == b'}')
    cases.append(('recover-pair-missing-half-negative', source, original,
        {'name': name, 'focus_line': start, 'end_line': end,
         'required_lemmas': [helpers[0]], 'summary_eligible': False,
         'proof_credit': False}))
    return cases


def select_body(ast_text, gates, metadata):
    rows = gates.functions(ast_text)
    matches = [r for r in rows if r['name'] == metadata['name']]
    need(len(matches) == 1 and matches[0]['kind'] == 'definition', 'one actual named AST body')
    row = matches[0]
    start = gates._source_span(row['fields'][0])
    body, = gates.node(row['fields'][10], 'Some', 1)
    _, close = gates.node(body, 'tuple', 2)
    end = gates._source_span(close)
    need(start[0][0] == end[0][0] == 'verified/lib.rs' and
         start[0][1] == metadata['focus_line'] and
         end[0][1] == metadata['end_line'], 'exact AST source body interval')
    selected = []
    for candidate in rows:
        if candidate['kind'] != 'definition':
            continue
        begin = gates._source_span(candidate['fields'][0])
        content, = gates.node(candidate['fields'][10], 'Some', 1)
        _, closing = gates.node(content, 'tuple', 2)
        finish = gates._source_span(closing)
        if begin[0][0] == finish[0][0] == 'verified/lib.rs' and begin[0][1] <= metadata['focus_line'] <= finish[0][1]:
            selected.append(candidate)
    need(len(selected) == 1 and selected[0] is row, 'one unambiguous focused body interval')
    return {'classification': 'SOURCE_BOUND_FULL_BODY_INTERVAL',
            'name': row['name'], 'start': start, 'close': end,
            'body_count_from_intervals': len(selected), 'body_ast_sha256': gates.digest(row['fields'][10]),
            'proof_credit': False}


def classify(stage, log, *, selection, paired, immutable, negative=None, expected_name="sort4_stable"):
    result = {'status': 'INCONCLUSIVE', 'passed': False, 'proof_credit': False,
              'summary_eligible': False}
    if not isinstance(stage, dict) or stage.get('classification') != 'TERMINAL' or type(stage.get('exit')) is not int:
        return {**result, 'reason': 'missing terminal integer stage'}
    if not isinstance(log, bytes) or sha(log) != stage.get('log_sha256'):
        return {**result, 'reason': 'missing/mismatched log identity'}
    errors = [s for s in log.decode('utf-8', errors='replace').splitlines()
              if ': error:' in s or 'Parse error' in s or s.startswith(('error:', 'error[', 'Fatal error:')) or s.endswith(': dead code')]
    result.update(observed_exit=stage['exit'], diagnostics=errors)
    if not paired or not immutable or not isinstance(selection, dict) or selection.get('classification') != 'SOURCE_BOUND_FULL_BODY_INTERVAL' or selection.get('name') != expected_name or selection.get('body_count_from_intervals') != 1:
        return {**result, 'reason': 'source pair/MIR/refinement/body/tool identity gate absent'}
    if negative is None:
        passed = stage['exit'] == 0 and not errors
        return {**result, 'status': 'SOURCE_REPORTED_BODY_CHECKED_UNQUALIFIED' if passed else 'BODY_PROOF_FAILED',
                'passed': passed}
    # Until actual location/predicate is inspected, resource controls are raw
    # observations. A setup or different rejection must never become a PASS.
    return {**result, 'status': 'RESOURCE_CONTROL_OBSERVED_UNCLASSIFIED',
            'expected_control': negative}


def run_case(a, c4, tool, env, root, case, gates, grammar, identity, *, paired_required=True):
    name, verified, original, meta = case
    env = dict(env)
    if meta.get('actual_c1_recovery') is True:
        need(meta.get('generated_source_sha256') == sha(verified) and
             type(meta.get('first_comparator_line')) is int and
             meta['first_comparator_line'] > 0, 'exact c1 source metadata')
        env.update(SORT4_ACTUAL_BODY_C1_RECOVERY='1', SORT4_STRICT_LFT_CUT='1',
            SORT4_ACTUAL_BODY_SOURCE_SHA256=sha(verified),
            SORT4_ACTUAL_BODY_FIRST_CALL_LINE=str(meta['first_comparator_line']),
            SORT4_A1_AUTHORIZATION_PHASE_ID=AUTH,
            SORT4_A1_PHASE_ID='SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17')
    control = meta.get('frontend_control')
    if control is not None:
        need(meta.get('actual_c1_recovery') is True and control in
             ('wrong-source-sha', 'wrong-first-call-line', 'opt-in-off'), 'fixed c1 frontend control')
        if control == 'wrong-source-sha':
            env['SORT4_ACTUAL_BODY_SOURCE_SHA256'] = '0' * 64
        elif control == 'wrong-first-call-line':
            env['SORT4_ACTUAL_BODY_FIRST_CALL_LINE'] = str(meta['first_comparator_line'] + 1)
        else:
            env['SORT4_ACTUAL_BODY_C1_RECOVERY'] = '0'
    unit = root / name
    fixture = unit / 'fixture'
    for directory, raw in (('verified', verified), ('original', original)):
        p = fixture / directory / 'lib.rs'
        p.parent.mkdir(parents=True)
        p.write_bytes(raw)
    stage_root = unit / 'stage'
    stage_root.mkdir()
    pair = {'verified/lib.rs': sha(verified), 'original/lib.rs': sha(original)}
    row = {'status': 'INCONCLUSIVE', 'metadata': meta, 'source_pair_sha256': pair,
           'proof_credit': False, 'summary_eligible': False, 'passed': False}
    snapshot(unit / 'body-result.json', row)
    try:
        stages, support = c4.source_support(a, tool, fixture, stage_root, env, target=meta.get('mir_target', meta['name']))
        row.update(stages=stages, source_support=support)
        if support.get('paired_support_passed') is not True:
            row.update(status='SOURCE_PAIR_PREREQUISITE_FAILED', reason='dependent verifier explicitly NOT_RUN')
            return row
        row['checked_lemma_prerequisites'] = {}
        for helper in meta.get('required_lemmas', []):
            helper_root = stage_root / ('checked-' + helper['name'])
            helper_root.mkdir()
            helper_ast = helper_root / 'proof-ast.ml'
            helper_stage = c4.stage(a, helper_root, 'lemma-verification',
                [str(tool / 'bin/verifast'), '-focus', f"verified/lib.rs:{helper['focus_line']}",
                 '-dump_ast_with_locs', str(helper_ast), '-rustc_args', '--edition 2021',
                 '-verbose', '6', 'verified/lib.rs'], env, 120, cwd=fixture)
            helper_log = helper_root / 'lemma-verification.log'
            selection = select_body(helper_ast.read_text(), gates, helper) if helper_ast.is_file() else None
            lemma_row = classify(helper_stage, helper_log.read_bytes() if helper_log.is_file() else None,
                selection=selection, paired=True, expected_name=helper['name'],
                immutable=pair == {key: sha((fixture / key).read_bytes()) for key in pair} and
                    grammar._tool_hashes(tool) == identity['tool_hashes'])
            lemma_row.update(verification=helper_stage, body_selection=selection,
                ast_sha256=sha(helper_ast.read_bytes()) if helper_ast.is_file() else None,
                source_pair_sha256=pair)
            row['checked_lemma_prerequisites'][helper['name']] = lemma_row
            snapshot(unit / 'body-result.json', row)
            if not lemma_row['passed']:
                row.update(status='CHECKED_LEMMA_PREREQUISITE_FAILED',
                    reason='actual body explicitly NOT_RUN; unchecked lemma summaries forbidden')
                return row
        ast_path = stage_root / 'proof-ast.ml'
        stage = c4.stage(a, stage_root, 'body-verification', [str(tool / 'bin/verifast'),
            '-focus', f"verified/lib.rs:{meta['focus_line']}", '-dump_ast_with_locs', str(ast_path),
            '-rustc_args', '--edition 2021', '-verbose', '6', 'verified/lib.rs'], env, 180, cwd=fixture)
        row['verification'] = stage
        log_path = stage_root / 'body-verification.log'
        log = log_path.read_bytes() if log_path.is_file() else None
        row['ast_sha256'] = sha(ast_path.read_bytes()) if ast_path.is_file() else None
        selection = None
        if ast_path.is_file():
            try:
                selection = select_body(ast_path.read_text(), gates, meta)
                row['body_selection'] = selection
            except Exception as exc:
                row['body_selection_error'] = f'{type(exc).__name__}: {exc}'
        same_pair = pair == {key: sha((fixture / key).read_bytes()) for key in pair}
        same_tool = grammar._tool_hashes(tool) == identity['tool_hashes']
        row.update(source_pair_immutable=same_pair, tool_immutable=same_tool)
        row.update(classify(stage, log, selection=selection, paired=True,
            immutable=same_pair and same_tool,
            negative=name if name.endswith('negative') else None, expected_name=meta['name']))
    except Exception as exc:
        row.update(error=f'{type(exc).__name__}: {exc}')
    finally:
        snapshot(unit / 'body-result.json', row)
    return row


def run(a, *, c4, audit, driver, manifest, ghost):
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         os.environ.get('SORT4_A1_AUTHORIZATION_PHASE_ID') == AUTH and
         bool(os.environ.get('CLOUD_BUILD_ID')) and not os.environ.get('GITHUB_ACTIONS'), 'authorized Cloud provider')
    for key in ('proof_root', 'work_root', 'evidence', 'cloud_dir', 'production_source'):
        need(str(Path(getattr(a, key)).resolve()).startswith('/workspace/'), key + ' Cloud root')
    root = Path(a.proof_root)
    profile_path = root / PROFILE
    need(sha(profile_path.read_bytes()) == os.environ.get('SORT4_A1_PROFILE_SHA256'), 'exact profile bytes')
    profile = json.loads(profile_path.read_text())
    need(profile.get('authorization_phase_id') == AUTH and profile.get('execution_mode') == 'actual-sort4-body-v1', 'mode/authorization')
    need(int(a.deadline_epoch) > int(time.time()) + 30, 'shared deadline')
    result = {'schema': 'a1-actual-sort4-body-v1', 'classification': 'R15_ACTUAL_BODY_ATTEMPT',
              'build_id': os.environ['CLOUD_BUILD_ID'], 'profile_sha256': os.environ['SORT4_A1_PROFILE_SHA256'],
              'proof_sha': os.environ.get('PROOF_SHA'), 'infra_sha': os.environ.get('INFRA_SHA'),
              'body_target': {'status': 'UNKNOWN'}, 'copy_components': {},
              'proof_credit': False, 'accepted': False, 'verification_accepted': False,
              'profile_accepted': False, 'matrix_complete': False, 'admission_record_created': False,
              'actual_body_obligations_closed': 0, 'evidence_complete': False}
    report = Path(a.evidence) / 'diagnostic-audit.json'
    def checkpoint(*args):
        snapshot(report, result)
    checkpoint()
    try:
        def load(name, pin=None):
            return pinned_load(root / HERE / name,
                pin or profile['a1_helper_sha256'][name], 'r15_' + name.replace('-', '_').replace('.', '_'))
        tool_mod = load('a1-tool.py')
        runner = pinned_load(root / HERE / 'a1-runner.py', profile['a1_source_runner_sha256'], 'r15_pinned_core')
        helpers = runner.load_pinned_helpers(root, profile)
        tool, receipt = tool_mod.reconstruct(a, c4, audit, driver, manifest, profile)
        result.update(tool_receipt=receipt, tool_reconstructed=True)
        checkpoint()
        grammar = load('a1-ghost-grammar.py', profile['a1_ghost_grammar_sha256'])
        probe = load('a1-reference-own-probe.py', profile['reference_own_probe_sha256'])
        result['reference_own_probe'] = probe.run(a, c4, tool, receipt, profile,
            helpers['a1-fixtures.py'], ghost, helpers['a1-ast-gates.py'],
            runner.select_checked_cleanup_helper_lemma, grammar, checkpoint)
        checkpoint()
        if result['reference_own_probe'].get('passed') is not True:
            result['body_target'] = {'status': 'NOT_RUN', 'reason': 'seven resource controls failed prerequisite'}
            return result
        identity = grammar._profile_guard(a, profile, receipt, tool)
        env = c4.clean_env(a, tool)
        need(not any(k.startswith(('SORT4_A1_', 'O26_WITH_')) for k in env), 'actual body cannot consume A1 summaries')
        capture_path = root / 'research/challenge-8/overnight-sort4/capture.py'
        capture = pinned_load(capture_path, profile['actual_body_dependencies_sha256']['capture.py'], 'r15_source_annotations')
        for rel, digest in profile['std_source_sha256'].items():
            need(sha((root / rel).read_bytes()) == digest, 'pinned std source identity ' + rel)
        source = (root / SOURCE).read_bytes()
        target_root = Path(a.evidence) / 'a1-actual-body'
        target_root.mkdir()
        if profile.get('body_action') in ('checked-dependencies-after-S1', 'checked-generic-four-recovery-after-S4'):
            generic_four = profile.get('body_action') == 'checked-generic-four-recovery-after-S4'
            result['body_target'] = {'status': 'NOT_RUN', 'proof_credit': False,
                'reason': ('S4 strict lifetime entry outer-type inference boundary unchanged; verify generic base4 recovery needed for c2-c5 independently'
                    if generic_four else 'S1 full-body unwind resource boundary unchanged; verify required checked dependencies before a new body candidate'),
                'prior_observation_build_id': ('980fbc61-2d4c-43f3-9cac-c68db0b34c63'
                    if generic_four else '909fb226-b3c0-49f7-a882-2b634624ec3a')}
            result['checked_dependencies'] = {}
            filenames = (('a1-actual-recover-four.rs',) if generic_four else
                         ('a1-actual-four-copy.rs', 'a1-actual-recover-pair.rs'))
            for filename in filenames:
                path = root / HERE / filename
                need(sha(path.read_bytes()) == profile['actual_body_dependencies_sha256'][filename],
                     'checked dependency source pin ' + filename)
                cases = (recovery_four_cases(path.read_bytes(), ghost) if generic_four else
                         component_cases(path.read_bytes(), ghost, 2) if 'four-copy' in filename else
                         recovery_cases(path.read_bytes(), ghost))
                for case in cases:
                    if int(a.deadline_epoch) - int(time.time()) < 100:
                        row = {'status': 'NOT_RUN', 'reason': 'shared deadline reserve', 'proof_credit': False}
                    else:
                        row = run_case(a, c4, tool, env, target_root, case,
                            helpers['a1-ast-gates.py'], grammar, identity)
                    result['checked_dependencies'][case[0]] = row
                    checkpoint()
            result['observation_complete'] = all(
                isinstance(row.get('verification'), dict) and
                row['verification'].get('classification') == 'TERMINAL' and
                type(row['verification'].get('exit')) is int
                for row in result['checked_dependencies'].values())
            return result
        need(profile.get('body_action') in (None, 'full-body', 'full-body-c1-recovery'), 'unknown body action')
        if profile.get('body_action') == 'full-body-c1-recovery':
            constructor = load('a1-actual-body-c1.py', profile['actual_body_dependencies_sha256']['a1-actual-body-c1.py'])
            recovery = root / HERE / 'a1-actual-recover-pair.rs'
            need(sha(recovery.read_bytes()) == profile['actual_body_dependencies_sha256']['a1-actual-recover-pair.rs'],
                 'exact recovery source')
            verified, original, meta = constructor.construct(source, ghost, capture, recovery.read_bytes(),
                construct_actual, lemma_metadata)
        else:
            verified, original, meta = construct_actual(source, ghost, capture)
        result['body_target'] = run_case(a, c4, tool, env, target_root,
            ('actual-sort4', verified, original, meta), helpers['a1-ast-gates.py'], grammar, identity)
        checkpoint()
        if profile.get('body_action') == 'full-body-c1-recovery':
            result['c1_controls'] = {}
            cases = constructor.resource_controls(verified, ghost, meta, lemma_metadata)
            for variant in ('wrong-source-sha', 'wrong-first-call-line', 'opt-in-off'):
                cases.append(('c1-' + variant + '-negative', verified, original,
                    {**meta, 'required_lemmas': [], 'frontend_control': variant}))
            for case in cases:
                if int(a.deadline_epoch) - int(time.time()) < 100:
                    row = {'status': 'NOT_RUN', 'reason': 'shared deadline reserve', 'proof_credit': False}
                else:
                    row = run_case(a, c4, tool, env, target_root, case,
                        helpers['a1-ast-gates.py'], grammar, identity)
                result['c1_controls'][case[0]] = row
                checkpoint()
        copy_name = ('a1-actual-four-copy.rs' if profile.get('body_action') == 'full-body-c1-recovery' else 'a1-actual-copy-lemma.rs')
        lemma = root / HERE / copy_name
        need(sha(lemma.read_bytes()) == profile['actual_body_dependencies_sha256'][copy_name], 'copy component source')
        # Independent ownership/representation components remain useful after a
        # body annotation/front-end refusal; they do not stand in for its proof.
        for case in component_cases(lemma.read_bytes(), ghost, 2 if copy_name == 'a1-actual-four-copy.rs' else 4):
            if int(a.deadline_epoch) - int(time.time()) < 100:
                result['copy_components'][case[0]] = {'status': 'NOT_RUN', 'reason': 'shared deadline reserve'}
            else:
                result['copy_components'][case[0]] = run_case(a, c4, tool, env, target_root,
                    case, helpers['a1-ast-gates.py'], grammar, identity)
            checkpoint()
        if 'a1-actual-selector-permutation.rs' in profile['actual_body_dependencies_sha256']:
            path = root / HERE / 'a1-actual-selector-permutation.rs'
            need(sha(path.read_bytes()) == profile['actual_body_dependencies_sha256'][path.name],
                 'exact pure selector dependency source')
            result['selector_components'] = {}
            for case in selector_cases(path.read_bytes(), ghost):
                if int(a.deadline_epoch) - int(time.time()) < 100:
                    row = {'status': 'NOT_RUN', 'reason': 'shared deadline reserve', 'proof_credit': False}
                else:
                    row = run_case(a, c4, tool, env, target_root, case,
                        helpers['a1-ast-gates.py'], grammar, identity)
                result['selector_components'][case[0]] = row
                checkpoint()
        result['observation_complete'] = all(
            isinstance(row, dict) and isinstance(row.get('verification'), dict) and
            row['verification'].get('classification') == 'TERMINAL' and
            type(row['verification'].get('exit')) is int
            for row in [result['body_target'], *result['copy_components'].values(),
                        *result.get('c1_controls', {}).values(),
                        *result.get('selector_components', {}).values()])
        # Full resource/receipt/controls/matrix qualification is still open.
        result['evidence_complete'] = False
    except Exception as exc:
        result['run_error'] = f'{type(exc).__name__}: {exc}'
    finally:
        checkpoint()
    return result
