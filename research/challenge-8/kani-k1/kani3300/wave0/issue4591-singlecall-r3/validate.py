#!/usr/bin/env python3
"""Offline pins, source shape, source oracles, mutation and publication-gate checks.

No Rust toolchain or verifier is invoked. Reports source predictions separately
from native evidence. The call model has the bounded scope in tests/callshape.py.
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
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D / 'tests'))
from callshape import attr_args, functions, guard_model, local_calls, mask, trace

P = json.loads((D / 'SOURCE-PINS.json').read_text())
K = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(P['source_worktree'])
B, C, M = [P[k]['sha'] for k in ('published_failed_base', 'candidate', 'main')]
checks, shapes = [], []


def check(name, condition, detail=None):
    checks.append({'name': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})


def git(*args):
    return subprocess.check_output(['git', '-C', str(K), *args], text=True).strip()


def source(ref, path):
    return subprocess.check_output(['git', '-C', str(K), 'show', ref + ':' + path], text=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def norm(text):
    return re.sub(r'\s+', '', mask(text))


def arithmetic_body(fn, x):
    """Evaluate only identity or x+literal fixture bodies, with u8 overflow."""
    body = norm(fn['body'])
    match = re.fullmatch(r'x(?:\+(\d+))?', body)
    if not match:
        raise ValueError('outside bounded arithmetic fixture grammar')
    result = x + int(match[1] or 0)
    return result, result > 255


def post_holds(fn, x, result):
    posts = attr_args(fn, 'ensures')
    if len(posts) != 1:
        raise ValueError('one fixture postcondition required')
    rhs = re.fullmatch(r'\|result\|\s*\*result\s*==\s*(x(?:\s*\+\s*\d+)?|\d+)', posts[0])
    if not rhs:
        raise ValueError('outside bounded postcondition grammar')
    text = rhs[1].replace(' ', '')
    expected = x + int(text.split('+')[1]) if '+' in text else x if text == 'x' else int(text)
    return result == expected


for key in ('published_failed_base', 'candidate', 'main'):
    obj = P[key]
    check(key + ' object/tree/parent',
          git('show', '-s', '--format=%T', obj['sha']) == obj['tree'] and
          git('show', '-s', '--format=%P', obj['sha']) == obj['parent'])
check('source HEAD and clean isolated worktree', git('rev-parse', 'HEAD') == C and
      not git('status', '--porcelain'))
check('repair scope exactly two fixtures', git('diff', '--name-only', B, C).splitlines() ==
      P['repair_changed_paths'])
check('source parent is exact published6f', P['candidate']['parent'] == B)
check('author and local skip candidate', git('show', '-s', '--format=%an <%ae>', C) ==
      'Tiramisu-Cake <igkharin@gmail.com>' and '[skip ci]' in git('show', '-s', '--format=%B', C))
for path in P['source_paths']:
    check('compiler byte invariant ' + path, source(B, path) == source(C, path))
for path, identities in P['protected_git_trees'].items():
    check('protected tree ' + path, len(set(identities.values())) == 1 and
          all(git('rev-parse', ref + ':' + path) == value for ref, value in identities.items()))
for path, info in {**P['protected_files'], **P['all_workflows']}.items():
    check('protected bytes ' + path, digest(source(C, path).encode()) == info['sha256'] and
          source(M, path) == source(C, path))
for path, sha in P['patches'].items():
    check('patch seal ' + path, digest((D / path).read_bytes()) == sha)
replay = json.loads((D / 'PATCH-REPLAY.json').read_text())
check('three recorded isolated-index replays', len(replay['replays']) == 3 and
      all(r['result_tree'] == P['candidate']['tree'] and
          all(c['exit'] == 0 for c in r['commands']) for r in replay['replays']))

pos = 'tests/kani/FunctionContracts/ordinary_stub.rs'
neg = 'tests/expected/function-contract/ordinary_stub_fail.rs'
cases = [(pos, 'replacement_contract_target', 'contracted_replacement'),
         (neg, 'replacement_provider_postcondition', 'discriminating_replacement')]
for path, harness, provider in cases:
    old, new = source(B, path), source(C, path)
    defective, repaired = trace(old, harness), trace(new, harness)
    shapes.append({'path': path, 'baseline': defective, 'repair': repaired})
    check(harness + ' frozen6f exact target reached but two effective checks',
          defective['exact_target_reachable'] and defective['effective_check_calls'] == 2 and
          not defective['single_call_shape'])
    check(harness + ' frozen6f second sequential guard fails in bounded model',
          guard_model(defective['effective_check_calls']) == [True, False])
    check(harness + ' repair exact target and one checked call',
          repaired['single_call_shape'] and guard_model(repaired['effective_check_calls']) == [True])
    check(harness + ' provider Assert inside selected caller',
          [(e['requested'], e['effective'], e['mode']) for e in repaired['events']] ==
          [('replacement_caller', 'replacement_caller', 'Check'), ('f', provider, 'Assert')])
    defs = functions(new)
    check(harness + ' selected caller actually returns ordinary f result',
          norm(defs['replacement_caller']['body']) == 'f(x)')
    check(harness + ' straight line single meaningful call',
          local_calls(defs[harness]['body'], defs) == ['replacement_caller'] and
          not re.search(r'\b(if|match|while|loop|for|return|assume)\b', mask(defs[harness]['body'])))
    # Mutations restore the real failed baseline, remove the selected call,
    # duplicate it, or select the provider while retaining only the copied call.
    check(harness + ' mutation old arrangement rejected', not trace(old, harness)['single_call_shape'])
    duplicate = new.replace(defs[harness]['body'], defs[harness]['body'] * 2, 1)
    check(harness + ' mutation second selected call rejected', not trace(duplicate, harness)['single_call_shape'])
    removed = new.replace(defs[harness]['body'], '\n', 1)
    check(harness + ' mutation missing selected call rejected', not trace(removed, harness)['single_call_shape'])
    direct = new.replace(defs[harness]['body'], '\n    f(1);\n', 1)
    check(harness + ' mutation alias alone fails exact-target reachability',
          not trace(direct, harness)['exact_target_reachable'])
    provider_selected = old.replace(functions(old)[harness]['body'], '\n    f(1);\n', 1)
    alias = trace(provider_selected, harness)
    check(harness + ' mutation just remove direct0 keeps count1 but loses exact FnDef',
          alias['effective_check_calls'] == 1 and not alias['exact_target_reachable'])

pd, nd = functions(source(C, pos)), functions(source(C, neg))
check('positive provider and caller contracts retain arithmetic domain',
      attr_args(pd['contracted_replacement'], 'requires') == ['x < 16'] and
      attr_args(pd['replacement_caller'], 'requires') == ['x < 16'] and
      attr_args(pd['contracted_replacement'], 'ensures') == ['|result| *result == x + 3'] and
      attr_args(pd['replacement_caller'], 'ensures') == ['|result| *result == x + 3'] and
      norm(pd['contracted_replacement']['body']) == 'x+3')
check('positive arithmetic oracle all admitted u8 inputs',
      all(not arithmetic_body(pd['contracted_replacement'], x)[1] and
          post_holds(pd['contracted_replacement'], x, arithmetic_body(pd['contracted_replacement'], x)[0]) and
          post_holds(pd['replacement_caller'], x, arithmetic_body(pd['contracted_replacement'], x)[0])
          for x in range(16)))
check('negative provider identity and unique postcondition',
      norm(nd['discriminating_replacement']['body']) == 'x' and
      not attr_args(nd['discriminating_replacement'], 'requires') and
      attr_args(nd['discriminating_replacement'], 'ensures') == ['|result| *result == 0'])
check('negative caller postcondition admits actual result and no masking requires',
      not attr_args(nd['replacement_caller'], 'requires') and
      attr_args(nd['replacement_caller'], 'ensures') == ['|result| *result == x'] and
      norm(nd['replacement_provider_postcondition']['body']) == 'replacement_caller(1);')
negative_input = int(re.fullmatch(r'replacement_caller\((\d+)\);',
                                norm(nd['replacement_provider_postcondition']['body']))[1])
negative_result, overflow = arithmetic_body(nd['discriminating_replacement'], negative_input)
check('negative oracle source input yields provider failure and caller post passes',
      not overflow and not post_holds(nd['discriminating_replacement'], negative_input, negative_result) and
      post_holds(nd['replacement_caller'], negative_input, negative_result))
check('negative old direct0 passes before second-call guard',
      post_holds(nd['discriminating_replacement'], 0, arithmetic_body(nd['discriminating_replacement'], 0)[0]))
mutated_provider = copy.deepcopy(nd['discriminating_replacement'])
mutated_provider['attrs'] = ['#[kani::ensures(|result| *result == x)]']
check('mutation provider postcondition weakened to identity loses intended negative',
      post_holds(mutated_provider, negative_input, negative_result))
original_mode = trace(source(C, neg).replace('-Z stubbing', '-Z stubbing --no-assert-contracts'),
                      'replacement_provider_postcondition')
check('mutation Original provider loses provider assertion while caller post still passes',
      original_mode['events'][-1]['mode'] == 'Original' and
      post_holds(nd['replacement_caller'], negative_input, negative_result))

oracle = json.loads((D / 'REGRESSION-ORACLE.json').read_text())
old_harnesses, new_harnesses, changes = set(), set(), []
for path in P['test_paths']:
    if path.endswith('.expected'):
        check('golden byte invariant ' + path, source(B, path) == source(C, path))
        continue
    old, new = functions(source(B, path)), functions(source(C, path))
    for name, fn in old.items():
        if any('kani::proof' in a for a in fn['attrs']):
            old_harnesses.add((path, name))
    for name, fn in new.items():
        if any('kani::proof' in a for a in fn['attrs']):
            new_harnesses.add((path, name))
        if name in old and old[name]['source'] != fn['source']:
            changes.append((path, name))
    check('function inventory retained ' + path, set(old) <= set(new))
check('all declared harnesses retained', old_harnesses == new_harnesses)
check('only failing/unrun PFC harnesses changed', set(changes) == {(p, h) for p, h, _ in cases})
check('all oracle rows bind declared harnesses', {(r['path'], r['harness']) for r in oracle['harnesses']} ==
      new_harnesses and all(r['native_repair'] == 'NOT_RUN' for r in oracle['harnesses']))
for r in oracle['harnesses']:
    fn = functions(source(C, r['path']))[r['harness']]
    check('oracle attrs ' + r['harness'] + ' in ' + r['path'], fn['attrs'] == r['attributes'])
audit = json.loads((D / 'PFC-AUDIT.json').read_text())['all_affected_PFC']
check('every PFC harness audited with one exact direct source call',
      {(a['path'], a['harness']) for a in audit} ==
      {(r['path'], r['harness']) for r in oracle['harnesses']
       if any('proof_for_contract(' in a for a in r['attributes'])} and
      all(a['exact_direct_target_count'] == 1 for a in audit))
expected = source(C, neg.replace('.rs', '.expected'))
negative_rows = [r for r in oracle['harnesses'] if r['path'] == neg]
failures = [r['harness'] for r in negative_rows if r['expected_fixed'] == 'VERIFICATION_FAILURE']
check('negative golden binds named semantic failures and declared harness total',
      all('Verification failed for - ' + name in expected for name in failures) and
      f'Complete - {len(negative_rows)-len(failures)} successfully verified harnesses, '
      f'{len(failures)} failures, {len(negative_rows)} total.' in expected and
      '- Description: "|result| *result == 0"' in expected)
issue = 'tests/expected/function-contract/ordinary_stub_issue_4591.rs'
check('issue4591 caller overflow retained verbatim from6f', source(C, issue) == source(B, issue) and
      'abs_val(x) + 1' in source(C, issue) and 'kani::assume(r >= 0)' in source(C, issue))
check('issue4591 i32MAX caller counterexample oracle', (2**31 - 1) + 1 > 2**31 - 1)

# Bind the bounded model to the actual unchanged guard and mode source snippets.
guard = json.loads((D / 'inputs/CBMC-GUARD-SOURCE.json').read_text())
guard_text = '\n'.join(line['text'] for line in guard['lines'])
check('CBMC guard source binds assertion and persistent completed flag',
      'make_assertion(not_exprt(check_completed), sl)' in guard_text and
      'check_completed, true_exprt()' in guard_text and
      'check_started, false_exprt()' in guard_text and
      'Only a single top-level call to function ' in guard_text)
attrs = source(C, 'kani-compiler/src/kani_middle/attributes.rs')
check('exact reachability guard retained from main969f',
      attrs == source(M, 'kani-compiler/src/kani_middle/attributes.rs') and
      '!reachable_functions.contains(&def.def_id())' in attrs)
contracts = source(C, 'kani-compiler/src/kani_middle/transform/contracts.rs')
check('contract body-source selector and mode precedence retained',
      'self.check_fn == Some(*def) || self.replace_fns.contains(def)' in contracts and
      'body_source' in contracts and 'else if self.replace_fns.contains(&fn_def)' in contracts and
      'else if self.assert_contracts' in contracts)

# Gate tests supply metadata only. They create no final commit and grant no authority.
spec = importlib.util.spec_from_file_location('push_gate', D / 'check_push_head.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
head = 'a' * 40
commits = [{'sha': B, 'message': 'Support ordinary stubs of contracted functions'},
           {'sha': head, 'message': 'Exercise ordinary replacements through single-call PFC callers'}]
good = [P, head, P['candidate']['tree'], [B], commits]
check('metadata-only future gate valid shape', not gate.check_metadata(*good))
for label, i, value in [('candidate pushed', 1, C), ('tree drift', 2, P['published_failed_base']['tree']),
                         ('oldmain parent', 3, [M]), ('merge parent', 3, [B, M]),
                         ('missing full range', 4, commits[1:]), ('extra ancestor', 4, commits + [commits[-1]]),
                         ('skip in final', 4, [commits[0], dict(commits[1], message='repair [skip ci]')]),
                         ('skip in ancestor', 4, [dict(commits[0], message='base [skip ci]'), commits[1]]),
                         ('candidate in range', 4, [commits[0], {'sha': C, 'message': '[skip ci]'}, commits[1]])]:
    args = copy.deepcopy(good)
    args[i] = value
    check('metadata gate rejects ' + label, bool(gate.check_metadata(*args)))

native = json.loads((D / 'native/CONNECTED-METADATA.json').read_text())['runs']
jobs = [job for run in native for job in run['jobs']]
check('connected native accounts all12 jobs and correct failed head',
      len(jobs) == 12 and len({j['id'] for j in jobs}) == 12 and
      all(r['selected_fields']['head_sha'] == B and r['selected_fields']['run_attempt'] == 1 for r in native))
check('native failures and cancellations retained',
      [j['name'] for j in jobs if j['conclusion'] == 'failure'] == ['regression (ubuntu-24.04)'] and
      len([j for j in jobs if j['conclusion'] == 'cancelled']) == 4)
ci = json.loads((D / 'CI-REQUEST.json').read_text())
check('CI authority stays blocked by same11 and exhausted item1',
      not ci['authorization']['dispatch'] and not ci['authorization']['push'] and
      ci['accounting_reference']['item1'] == '31/31 EXHAUSTED' and
      ci['accounting_reference']['extra_grant'] == 'NOT_GRANTED')
check('request derives complete push workflows and matrix',
      set(ci['native_jobs']) == {'kani.yml', 'format-check.yml', 'deny.yml'} and
      len(ci['native_jobs']['kani.yml']['regression']['strategy']['matrix']['os']) == 5 and
      sum(len(v) for v in ci['native_jobs'].values()) + 4 == ci['native_instances'] == 12)
failed = [c for c in checks if c['status'] == 'FAIL']
report = {'status': 'FAIL' if failed else 'PASS', 'checks': checks, 'callshapes': shapes,
          'source_candidate': C, 'source_tree': P['candidate']['tree'],
          'compiler_typecheck_MIR_expansion_verifier_native_repair': 'NOT_RUN',
          'limitations': ['bounded lexical source model; no Rust name/type resolution or path analysis',
                          'Python arithmetic oracle; no Kani/CBMC proof',
                          'metadata gate mocks are not an actual final-head receipt or CI authorization']}
print(json.dumps(report, indent=2))
sys.exit(bool(failed))
