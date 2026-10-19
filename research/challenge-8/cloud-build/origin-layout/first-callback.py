#!/usr/bin/env python3
"""Cloud-only first actual comparator campaign. Import has no side effects.

The prefix is mechanically cut immediately before tail.read, and never stands
in for the complete actual insert_tail. Full-body final posts stay unchanged.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
PROFILE = 'experimental-merge-guard-addressability-v1'
PREFIX_NAME = b'insert_tail_first_callback_prefix'
CUT = b'        // SAFETY: after this read'

# Pure entry facts, before the callback lifetime; no resources or value equality.
SINGLETON_FACTS = b"""    //@ length_drop(1, xs);
    //@ length_take(1, drop(1, xs));
    //@ length_drop(1, drop(1, xs));
    //@ note(length(take(1, drop(1, xs))) == 1);
    //@ note(length(drop(1, drop(1, xs))) == 1);
    //@ drop_length(drop(1, drop(1, xs)));
"""

# Exact inherited suffix and owner-authorized CURRENT replacement; ghost only.
ENTRY_OWNER_REJOIN = b"""        //@ close own::<u64>(t)(head(take(1, drop(1, xs))));
        //@ close own::<u64>(t)(head(drop(1, drop(1, xs))));
        //@ close foreach(take(1, drop(1, xs)), own::<u64>(t));
        //@ close foreach(drop(1, drop(1, xs)), own::<u64>(t));
        //@ close array::<u64>(sift, 1, take(1, drop(1, xs)));
        //@ close array::<u64>(tail, 1, drop(1, drop(1, xs)));
        //@ array_join::<u64>(begin + 1);
        //@ array_join::<u64>(begin);
        //@ foreach_join(drop(1, xs), own::<u64>(t), 1);
        //@ foreach_join(xs, own::<u64>(t), 1);
"""
CURRENT_OWNER_REJOIN = b"""        //@ close own::<u64>(t)(current_sift);
        //@ close own::<u64>(t)(current_tail);
        //@ close foreach(cons(current_sift, nil), own::<u64>(t));
        //@ close foreach(cons(current_tail, nil), own::<u64>(t));
        //@ close array::<u64>(sift, 1, cons(current_sift, nil));
        //@ close array::<u64>(tail, 1, cons(current_tail, nil));
        //@ array_join::<u64>(begin + 1);
        //@ array_join::<u64>(begin);
        //@ foreach_append(cons(current_sift, nil), cons(current_tail, nil));
        //@ foreach_append(take(1, xs), append(cons(current_sift, nil), cons(current_tail, nil)));
"""


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'missing pinned module: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _one(data, old, new, label):
    if data.count(old) != 1:
        raise ValueError(f'{label}: expected one exact anchor')
    return data.replace(old, new, 1)


def _add_singleton_facts(source):
    anchor = b"    //@ let cmp_k = begin_lifetime();\n"
    return _one(source, anchor, SINGLETON_FACTS + anchor,
                'pure singleton length facts before callback lifetime')


# Fullbody only: expose the physically owned CURRENT tail from the rejoined array.
TAIL_READ_OPEN = b"""        //@ assert array::<u64>(begin, 3, ?read_current);
        //@ array_split::<u64>(begin, 2);
        //@ open array::<u64>(tail, 1, drop(2, read_current));
"""


def _open_tail_read(source):
    anchor = b'        let tmp = ManuallyDrop::new(tail.read());\n'
    return _one(source, anchor, TAIL_READ_OPEN + anchor,
                'open CURRENT tail singleton before original read')


def _commands(fragment):
    lines = fragment.splitlines()
    if any(not line.lstrip().startswith(b'//@ ') for line in lines):
        raise ValueError('recovery must contain only explicit ghost commands')
    return b' '.join(line.lstrip()[4:] for line in lines)


def _markers(old, mutation=None):
    split = b"        //@ end_lft_binding::<'cmp>();\n"
    if old.B2_COMPARE_RECOVER.count(split) != 1:
        raise ValueError('callback lifetime split changed')
    close, recover = old.B2_COMPARE_RECOVER.split(split)
    recover = _one(recover, ENTRY_OWNER_REJOIN, CURRENT_OWNER_REJOIN,
                   'CURRENT owner and physical-cell rejoin')
    for pointer, value in (('tail', 'current_tail'), ('sift', 'current_sift')):
        opened = f'        //@ open_full_borrow_content::<u64>(t, {pointer});\n'.encode()
        bound = f'        //@ assert *{pointer} |-> ?{value};\n'.encode()
        recover = _one(recover, opened, opened + bound,
                       f'bind returned CURRENT {pointer} value')
    if mutation == 'lost_reference_fraction':
        close = _one(close, b'close_frac_borrow(tail_ref_frac,',
                     b'close_frac_borrow(tail_ref_frac + 1,', 'bad reference fraction')
    if mutation == 'lost_reference_token':
        close = _one(close, b'assert [1/2]lifetime_token(cmp_k);',
                     b'assert lifetime_token(cmp_k);', 'insufficient lifetime token')
    return (b"            /*@ { first_callback_close::<'cmp>(); " +
            _commands(close) + b" } @*/\n" +
            b"            //@ first_callback_scope_end::<'cmp>();\n" +
            b"            /*@ { first_callback_recover::<'cmp>(); " +
            _commands(recover) + b' } @*/\n')


def _cut_prefix(source):
    """Exact partial source relation: keep before CUT, close unsafe/function.

    Preserve all helper/Drop code preceding insert_tail and the actual local
    wrapper after it. No original source is extracted or run on the VPS.
    """
    wrapper = b'pub unsafe fn b2_three_from_local'
    if source.count(CUT) != 1 or source.count(wrapper) != 1:
        raise ValueError('prefix cut or wrapper boundary is not unique')
    cut = source.index(CUT)
    wrapper_at = source.index(wrapper, cut)
    # Wrapper contract precedes its signature and must remain attached to it.
    suffix = source[wrapper_at:]
    wrapper_contract = source.rfind(b'/*@\nreq thread_token', cut, wrapper_at)
    if wrapper_contract >= 0:
        suffix = source[wrapper_contract:]
    result = source[:cut] + b'    }\n}\n\n' + suffix
    result = _one(result, b'unsafe fn insert_tail<',
                  b'unsafe fn ' + PREFIX_NAME + b'<', 'prefix function name')
    result = _one(result, b'insert_tail(begin, begin.add(2), is_less);',
                  PREFIX_NAME + b'(begin, begin.add(2), is_less);', 'prefix wrapper')
    if b'tail.read()' in result or b'if !is_less(&tmp' in result:
        raise ValueError('prefix includes forbidden post-cut runtime')
    return result


def prepare(evidence, *, prefix=False, mutation=None):
    old = _load('first_callback_original_preparation', HERE / 'actual-insert-tail-b2.py')
    record = old._prepare(evidence)  # Cloud-only inherited actual-source binding.
    case = evidence / 'cases' / old.CASE
    original = (case / 'original/lib.rs').read_bytes()
    verified = (case / 'verified/lib.rs').read_bytes()
    full_original = original
    verified = _add_singleton_facts(verified)
    verified = _one(verified,
                    old.B2_COMPARE_RECOVER.replace(b'        ', b'            '),
                    b'', 'remove old false recovery')
    verified = _one(verified, old.B2_COMPARE_RECOVER, b'',
                    'remove old true recovery')
    call = (b"        if !is_less/*@::<F, (&'cmp u64, &'cmp u64), 'cmp>@*/"
            b'(&*tail, &*sift) {\n')
    markers = _markers(old, mutation)
    verified = _one(verified, call, call + markers, 'first actual comparator markers')
    negative = b''
    if mutation == 'lost_current_f':
        negative = b'            //@ leak <F>.own(t, _);\n'
    elif mutation == 'lost_cell_owner':
        negative = (b'            //@ array_split::<u64>(begin, 1);\n'
                    b'            //@ leak array::<u64>(begin, 1, _);\n'
                    b'            //@ array_join::<u64>(begin); // TARGET: missing physical cell owner\n')
    if negative:
        verified = _one(verified, markers, markers + negative,
                        'explicit negative-only resource loss on false path')
    if mutation not in (None, 'lost_reference_fraction', 'lost_reference_token',
                         'lost_current_f', 'lost_cell_owner'):
        raise ValueError('unknown first-comparator mutation')
    if not prefix:
        verified = _open_tail_read(verified)
    # Strip the NEW ghost-only annotations and compare with inherited source.
    # Other original ghost commands were already checked by old._prepare.
    # Runtime comparison removes only comments and whitespace; the inherited
    # preparation already established exact actual-source extraction identities.
    def runtime(data):
        return re.sub(rb'/\*.*?\*/|//[^\n]*', b'', data, flags=re.S)
    if runtime(verified) != runtime(original):
        # Removing whole annotation lines leaves whitespace-only source lines.
        clean = lambda data: b'\n'.join(x.strip() for x in runtime(data).splitlines() if x.strip())
        if clean(verified) != clean(original):
            raise ValueError('new recovery changed runtime tokens')
    if prefix:
        original, verified = _cut_prefix(original), _cut_prefix(verified)
    if mutation is None and (b'//@ leak' in verified or b'//@ assume' in verified):
        raise ValueError('positive cannot discard or assume resources')
    if old.INSERT_CONTRACT not in verified:
        raise ValueError('full CURRENT normal/unwind final posts changed')
    (case / 'original/lib.rs').write_bytes(original)
    (case / 'verified/lib.rs').write_bytes(verified)
    record.update(schema='first-actual-callback-source-v1', profile=PROFILE,
                  original_sha256=_sha(original), verified_sha256=_sha(verified),
                  full_specialized_original_sha256=_sha(full_original),
                  prefix=prefix, mutation=mutation,
                  cut='immediately before tail.read/ManuallyDrop/guard; true path returns at cut' if prefix else None,
                  source_relation='exact pre-cut runtime segment plus closing braces and renamed function/wrapper' if prefix else 'complete actual body; ghost-only annotation replacement',
                  final_posts_sha256=_sha(old.INSERT_CONTRACT),
                  callback_marker_sha256=_sha(markers),
                  first_callback_unwind_recovery_qualified=False,
                  first_callback_unwind_status='NOT_RUN', proof_credit=False)
    record['actual_first_call_line'] = old._line(verified, call.rstrip(b'\n'))
    for key, anchor in (
        ('actual_read_line', b'let tmp = ManuallyDrop::new(tail.read());'),
        ('actual_shift_line', b'ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);'),
        ('actual_update_line', b'gap_guard.dst = sift;'),
        ('actual_late_call_line', b'if !is_less(&tmp, &*sift) {')):
        record[key] = None if prefix else old._line(verified, anchor)
    record['false_return_line'] = old._line(verified, b'            return;')
    if prefix:
        record['true_cut_line'] = verified[:verified.index(b'    }\n}\n\n', verified.index(call))].count(b'\n') + 1
    else:
        record['true_frontier_line'] = old._line(verified, b'let tmp = ManuallyDrop::new(tail.read());')
    (evidence / 'preparation.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    return case, record


def classify(case, record, execution, *, baseline_positive=False):
    stages = execution.get('stages', {})
    text = (case / 'verifast.log').read_text(errors='replace') if (case / 'verifast.log').is_file() else ''
    refinement = ''.join((case / name).read_text(errors='replace')
                         for name in ('refinement.log', 'refinement.out') if (case / name).is_file())
    errors = [line for line in text.splitlines() if re.search(r'\berror:', line, re.I)]
    exact = (_sha((case/'original/lib.rs').read_bytes()) == record['original_sha256'] and
             _sha((case/'verified/lib.rs').read_bytes()) == record['verified_sha256'] and
             execution.get('source_unchanged_at_every_stage') is True and
             execution.get('stage_receipt_gate', {}).get('admitted') is True)
    # These are necessary admission observations, never sufficient by themselves.
    hrtb = bool(re.search(r'MERGE_HRTB_CALL registered=1 .*T=u64 .*', text))
    local = 'MERGE_FIRST_CALLBACK_LOCAL_CONTINUE' in text
    official = ('QUALIFIED_FIRST_FNMUT_CONTINUE_EDGE:' in refinement and stages.get('refinement') == 0)
    first_error = errors[0] if errors else None
    admitted = exact and hrtb and local and official and stages.get('exporter') == 0 and stages.get('decode') == 0
    mutation = record['mutation']
    negative_match = False
    if mutation:
        intended = {
            'lost_reference_fraction': ('ref_initialized', 'close_frac_borrow_token', 'Cannot prove condition'),
            'lost_reference_token': ('lifetime_token',),
            'lost_current_f': ('own',),
            'lost_cell_owner': ('array',),
        }[mutation]
        source = (case/'verified/lib.rs').read_bytes()
        if mutation in ('lost_reference_fraction', 'lost_reference_token'):
            anchor = b'first_callback_close::<'
            expected_line = source[:source.index(anchor)].count(b'\n')+1
        elif mutation == 'lost_current_f':
            contract_at = source.index(b'unsafe fn ' + PREFIX_NAME)
            normal_post_at = source.index(b'    *is_less |-> ?normal_f &*& <F>.own(t, normal_f);', contract_at)
            expected_line = source[:normal_post_at].count(b'\n')+1
        else:
            anchor = b'            //@ array_join::<u64>(begin); // TARGET: missing physical cell owner'
            expected_line = source[:source.index(anchor)].count(b'\n')+1
        target_executed = bool(re.search(
            rf'verified/lib\.rs\({expected_line},\d+[^\n]*Executing statement', text))
        error_at_target = bool(first_error and f'({expected_line},' in first_error)
        # An executed target alone does not locate a later proof error. Only
        # direct source errors, or the exact close/join specification with the
        # target as the LAST executed statement before that error, qualify.
        before_error = text.split(first_error, 1)[0] if first_error else ''
        executions = re.findall(r'verified/lib\.rs\((\d+),\d+[^\n]*Executing statement', before_error)
        last_at_target = bool(executions and int(executions[-1]) == expected_line)
        canonical_spec_error = bool(first_error and (
            mutation == 'lost_reference_fraction' and
            re.search(r'lifetime_logic\.rsspec\(282,', first_error) or
            mutation == 'lost_cell_owner' and
            re.search(r'prelude_core\.rsspec\(293,', first_error)))
        negative_match = bool(baseline_positive and admitted and
                              stages.get('verifast') not in (0,125,None) and first_error and
                              (error_at_target or (canonical_spec_error and last_at_target)) and
                              any(word in first_error for word in intended))
    prefix_proved = bool(admitted and record['prefix'] and mutation is None and
                         stages.get('verifast') == 0 and not errors and 'dead code' not in text.lower())
    runtime_frontiers = {}
    for key in ('actual_first_call_line', 'actual_read_line', 'actual_shift_line',
                'actual_update_line', 'actual_late_call_line', 'false_return_line'):
        line = record.get(key)
        runtime_frontiers[key] = bool(line and re.search(
            rf'verified/lib\.rs\({line},\d+[^\n]*(?:Executing statement|Executing return statement)', text))
    result = dict(schema='first-callback-result-v1', accepted=False,
                  classification='PREFIX_CURRENT_NORMAL_UNWIND_PROVED' if prefix_proved else
                  'INTENDED_RESOURCE_NEGATIVE' if negative_match else 'INCONCLUSIVE',
                  prefix=record['prefix'], cut=record['cut'], mutation=mutation,
                  stages=stages, source_exact=exact, runtime_frontiers=runtime_frontiers,
                  hrtb_registration_observed=hrtb, local_first_continue_observed=local,
                  official_first_continue_qualified=official,
                  current_false_true_panic_proved=prefix_proved,
                  intended_negative=negative_match,
                  full_insert_tail_proved=False, b2_achieved=False,
                  first_error=first_error, proof_credit=prefix_proved,
                  next_frontier='full body diagnostic required' if prefix_proved else first_error,
                  limitations='Prefix is partial. Registration/reached-call/refiner exit0 alone give no resource credit.')
    (case/'classification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


def run(evidence, args, env, execute_case, validated_receipt):
    if not callable(execute_case):
        raise TypeError('hosted execute_case required')
    profile_path = os.environ.get('SMALLSORT_MERGE_PROFILE')
    if not profile_path or json.loads(Path(profile_path).read_text()).get('profile') != PROFILE:
        raise RuntimeError('first callback requires its new experimental profile')
    proof = _load('first_callback_hosted_proof', HERE.parents[1] / 'merge/overnight/copy-on-drop-prove.py')
    proof.require_hosted_cloud()
    consumer = _load('first_callback_receipt', HERE/'concrete-consumer.py')
    provider, proof_sha = proof.require_hosted_cloud()
    consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    evidence.mkdir(parents=True, exist_ok=False)
    results = {}
    # Full-body case runs regardless of prefix failure, retaining the next real
    # resource frontier under unmodified final posts.
    cases = [('prefix', True, None), ('full_body', False, None)] + [
        (name, True, name) for name in ('lost_reference_fraction', 'lost_reference_token',
                                      'lost_current_f', 'lost_cell_owner')]
    previous_flag = getattr(args, 'first_fnmut_continue', False)
    args.first_fnmut_continue = True
    try:
        for name, prefix, mutation in cases:
            if mutation and not results['prefix']['current_false_true_panic_proved']:
                results[name] = dict(classification='NOT_RUN_PREFIX_PREREQUISITE_FAILED',
                                     intended_negative=False, proof_credit=False)
                continue
            case, record = prepare(evidence/name, prefix=prefix, mutation=mutation)
            before = consumer._hashes(case)
            execution = execute_case(case, args, env)
            execution['stage_receipt_gate'] = consumer._stage_receipts(case, execution.get('stages', {}), before)
            execution['source_unchanged_at_every_stage'] = (before == consumer._hashes(case) and
                execution['stage_receipt_gate'].get('admitted') is True)
            results[name] = classify(case, record, execution,
                                     baseline_positive=results.get('prefix', {}).get('current_false_true_panic_proved', False))
        if results['prefix']['current_false_true_panic_proved']:
            controls = _load('first_callback_admission', HERE/'first-callback-admission-controls.py')
            results['admission_controls'] = controls.run(
                evidence/'admission-controls', args, env, execute_case,
                evidence/'prefix/cases/actual_three_current_full_posts',
                {**json.loads((evidence/'prefix/preparation.json').read_text()),
                 'full_body_case': str(evidence/'full_body/cases/actual_three_current_full_posts'),
                 'full_body_source_record': json.loads((evidence/'full_body/preparation.json').read_text())})
        else:
            results['admission_controls'] = dict(all_matched=False,
                classification='NOT_RUN_PREFIX_PREREQUISITE_FAILED', proof_credit=False)
    finally:
        args.first_fnmut_continue = previous_flag
    aggregate = dict(schema='first-callback-campaign-v1', profile=PROFILE, accepted=False,
                     results=results, b2_achieved=False,
                     prefix_current_normal_unwind_proved=results['prefix']['current_false_true_panic_proved'],
                     all_target_controls_matched=(
                         results['prefix']['current_false_true_panic_proved'] and
                         all(results[name].get('intended_negative') is True for name in
                             ('lost_reference_fraction', 'lost_reference_token', 'lost_current_f', 'lost_cell_owner')) and
                         results['admission_controls'].get('all_matched') is True),
                     classification='DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH')
    (evidence/'aggregate.json').write_text(json.dumps(aggregate, indent=2, sort_keys=True)+'\n')
    return aggregate
