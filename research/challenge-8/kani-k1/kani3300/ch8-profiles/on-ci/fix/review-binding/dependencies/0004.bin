# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Offline policy v2. Evidence is data; this module never runs evidence commands.

ACCEPTED is policy admission of a bounded source-reported observation, not proof
credit. Source reviews are exact-ID records, never function-name exemptions.
"""
import re


CHECK_LISTS = ('failure', 'unreachable', 'undetermined', 'error', 'unknown', 'other')
COVER_LISTS = ('satisfied', 'unsatisfiable', 'unreachable', 'undetermined',
               'error', 'unknown', 'other')
REQUIRED_ROLES = {'postcondition', 'frame', 'relation', 'required_section'}


def tokens(value):
    if not isinstance(value, str) or not re.fullmatch(
            r'\s*[A-Za-z_][A-Za-z_0-9]*(?:\s*::\s*[A-Za-z_][A-Za-z_0-9]*)*\s*', value):
        return None
    return tuple(re.split(r'\s*::\s*', value.strip()))


def finish(result):
    result['status'] = ('UNKNOWN' if result['unknown_reasons'] else
                        'PENDING' if result['pending_reasons'] else 'ACCEPTED')
    return result


def classify(row, harness, mapping, links, role_reviews, preflight_state):
    result = {'id': row['id'], 'status': 'UNKNOWN', 'unknown_reasons': [],
              'pending_reasons': [], 'unsupported': [], 'unreachable': [],
              'proof_credit': 'NONE'}
    try:
        _classify(result, row, harness, mapping, links, role_reviews, preflight_state)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        result['unknown_reasons'].append('MALFORMED_INPUT: ' + type(exc).__name__ + ': ' + str(exc))
    return finish(result)


def _classify(out, row, h, mapping, links, roles, preflight):
    unknown, pending = out['unknown_reasons'], out['pending_reasons']
    # The unchanged v1 parser owns source/tool/config/selection/mode/unwind guards.
    # INCOMPLETE_CHECK_INVENTORY is exactly the gate replaced below, not a PASS.
    if preflight not in {'INCOMPLETE_CHECK_INVENTORY', 'VALIDATED_OBSERVATION',
                         'FRAME_BINDING_REVIEW_REQUIRED'}:
        unknown.append('PREFLIGHT_' + str(preflight))
        return
    if h['name'] != row['selector'] or h['crate_name'] != 'core':
        unknown.append('EXACT_HARNESS_BINDING_MISMATCH')
    if h['outcome']['kind'] != 'COMPLETED':
        unknown.append('NOT_COMPLETED')
    checks, covers = h['checks'], h['covers']
    for bucket, names in ((checks, CHECK_LISTS), (covers, COVER_LISTS)):
        if type(bucket['total']) is not int or bucket['total'] < 0:
            raise ValueError('invalid total')
        for name in names:
            if not isinstance(bucket[name], list):
                raise ValueError('missing/wrong-type bucket ' + name)
            if name != 'other' and any(not isinstance(x, str) or not x for x in bucket[name]):
                raise ValueError('invalid property ID')
    if type(checks['success']) is not int or checks['success'] < 0:
        raise ValueError('invalid success count')
    if checks['success'] + sum(len(checks[k]) for k in CHECK_LISTS) != checks['total']:
        unknown.append('LOST_OR_INCONSISTENT_CHECKS')
    if sum(len(covers[k]) for k in COVER_LISTS) != covers['total']:
        unknown.append('LOST_OR_INCONSISTENT_COVERS')
    if type(h['n_properties']) is not int or h['n_properties'] != checks['total'] + covers['total']:
        unknown.append('INCONSISTENT_N_PROPERTIES')
    ids = [x for k in CHECK_LISTS if k != 'other' for x in checks[k]]
    cover_ids = [x for k in COVER_LISTS if k != 'other' for x in covers[k]]
    if len(ids + cover_ids) != len(set(ids + cover_ids)):
        unknown.append('DUPLICATE_OR_CROSS_BUCKET_ID')
    if any(checks[k] for k in ('undetermined', 'error', 'unknown', 'other')):
        unknown.append('INCOMPLETE_CHECK_STATUSES')
    if any(covers[k] for k in COVER_LISTS if k != 'satisfied'):
        pending.append('COVER_NOT_SATISFIED')
    failures = h['failed_properties']
    if (not isinstance(failures, list) or type(h['n_failed']) is not int or
            h['n_failed'] != len(checks['failure']) or len(failures) != h['n_failed'] or
            sorted(p['id'] for p in failures) != sorted(checks['failure'])):
        unknown.append('INCONSISTENT_FAILURE_INVENTORY')
    if any(not isinstance(p.get('description'), str) or p.get('status') != 'FAILURE'
           for p in failures):
        unknown.append('MALFORMED_NAMED_FAILURE')
    out['kani_verdict'] = h['outcome']['verdict']
    if row['expected'] == 'SUCCESS':
        if h['outcome']['verdict'] != 'SUCCESS' or checks['failure']:
            pending.append('POSITIVE_NOT_SUCCESS')
    else:
        descriptions = row['allowed_failure_descriptions']
        if any(d.startswith('<generated modifies') for d in descriptions):
            pending.append('PREDECLARED_FRAME_ORACLE_BINDING_PENDING')
        elif (h['outcome']['verdict'] != 'FAILURE' or len(failures) != len(descriptions) or
              any(sum(d in p['description'] for p in failures) != 1 for d in descriptions) or
              any(sum(d in p['description'] for d in descriptions) != 1 for p in failures)):
            pending.append('PREDECLARED_NEGATIVE_ORACLE_MISMATCH')
    unsupported = h['unsupported_constructs']
    if not isinstance(unsupported, list):
        raise ValueError('unsupported inventory missing')
    if len({u['id'] for u in unsupported}) != len(unsupported):
        unknown.append('DUPLICATE_UNSUPPORTED_ID')
    if len(unsupported) > checks['total']:
        unknown.append('INCONSISTENT_UNSUPPORTED_COUNT')
    for u in unsupported:
        record = dict(u)
        link = links.get(u['id'])
        record['assert_false_link'] = link
        if u['status'] not in {'SUCCESS', 'FAILURE', 'UNREACHABLE'}:
            unknown.append('UNSUPPORTED_STATUS_UNKNOWN:' + u['id'])
            record['decision'] = 'UNKNOWN'
        elif u['status'] != 'SUCCESS':
            pending.append('UNSUPPORTED_NOT_SUCCESS:' + u['id'])
            record['decision'] = 'BLOCK'
        elif (u['class'] != 'unsupported_construct' or
              not re.search(r'\.unsupported_construct\.[1-9][0-9]*$', u['id']) or
              link is None or link.get('semantics') != 'assert(false); assume(false)' or
              u['description'] != link.get('description') or u['line'] != link.get('line') or
              not isinstance(u['file'], str) or not u['file'].endswith('/' + link['file_suffix'])):
            unknown.append('UNSUPPORTED_EXACT_LINK_UNKNOWN:' + u['id'])
            record['decision'] = 'UNKNOWN'
        elif u['id'] in ids + cover_ids:
            unknown.append('UNSUPPORTED_STATUS_CONFLICT:' + u['id'])
            record['decision'] = 'UNKNOWN'
        else:
            record['decision'] = 'ALLOWED_UNREACHABLE_CONSTRUCT'
        out['unsupported'].append(record)
    if sum(u['status'] == 'SUCCESS' for u in unsupported) > checks['success']:
        unknown.append('UNSUPPORTED_SUCCESS_COUNT_CONFLICT')
    for pid in checks['unreachable']:
        review = roles.get(pid)
        record = {'id': pid, 'status': 'UNREACHABLE',
                  'function': pid.rsplit('.assertion.', 1)[0],
                  'property_location': None, 'role': 'UNKNOWN',
                  'target_wrapper_relation': 'UNESTABLISHED',
                  'reason': 'Export has only ID; source numbered-assertion/location binding absent.'}
        if review is not None:
            record.update(review)
            record['id'], record['status'] = pid, 'UNREACHABLE'
        if record['role'] in REQUIRED_ROLES:
            pending.append('REQUIRED_ASSERTION_UNREACHABLE:' + pid)
            record['decision'] = 'BLOCK'
        elif (record['role'] == 'defensive_branch' and record.get('property_location') and
              record.get('reason') and record.get('target_wrapper_relation') != 'UNESTABLISHED'):
            record['decision'] = 'ALLOWED_DEFENSIVE_BRANCH'
        else:
            unknown.append('UNREACHABLE_ROLE_UNKNOWN:' + pid)
            record['decision'] = 'UNKNOWN'
        out['unreachable'].append(record)
    if mapping is None:
        unknown.append('SOURCE_OBLIGATION_MAPPING_MISSING')
        return
    out['binding'] = mapping['binding']
    bind = mapping['binding']
    if bind['target_status'] != 'BOUND':
        pending.append('FULL_QUALIFIED_TARGET_BINDING_PENDING')
    if bind['wrapper_status'] not in {'BOUND', 'NOT_APPLICABLE'}:
        pending.append('EXACT_CONTRACT_WRAPPER_BINDING_PENDING')
    if row['mode'] == 'PFC':
        actual = h['attributes']['kind']['ProofForContract']['target_fn']
        if tokens(actual) is None or tokens(actual) != tokens(bind['source_target_expression']):
            unknown.append('FULL_SOURCE_ATTRIBUTE_TARGET_MISMATCH')
        if h['contract']['contracted_function_name'] != bind['export_contract_symbol']:
            unknown.append('CONTRACT_EXPORT_SYMBOL_CHANGED')
    if h['attributes']['stubs'] != []:
        unknown.append('UNDECLARED_STUBS')
    if h['attributes']['verified_stubs'] != bind['verified_stubs']:
        unknown.append('FULL_VERIFIED_STUB_BINDING_MISMATCH')
    out['cover_mapping'] = mapping['coverage']
    required = mapping['coverage']['required_ids']
    if len(required) != len(set(required)) or any(not isinstance(x, str) for x in required):
        raise ValueError('invalid required IDs')
    post_ids = mapping['coverage']['post_target_ids']
    pre_ids = mapping['coverage'].get('pre_call_only_ids', [])
    if (not set(post_ids).issubset(set(required)) or set(post_ids) & set(pre_ids) or
            not set(covers['satisfied']).issubset(set(required))):
        unknown.append('UNMAPPED_OR_INCONSISTENT_COVER_OBLIGATION')
    missing = sorted(set(required) - set(covers['satisfied']))
    out['missing_required_cover_ids'] = missing
    if missing:
        pending.append('REQUIRED_COVER_MISSING_OR_NOT_SATISFIED')
    if row['expected'] == 'SUCCESS' and not mapping['coverage']['post_target_ids']:
        pending.append('REQUIRED_POST_TARGET_COVER_ABSENT')
    if mapping['coverage'].get('missing_obligations'):
        pending.append('REQUIRED_COVER_OBLIGATION_ABSENT')


def consumers_after_leaves(rows, results):
    """Resolve dependencies after classification; a raw SUCCESS never passes."""
    by_id = {r['id']: r for r in rows}
    visiting, done = set(), set()

    def visit(rid):
        if rid in done:
            return
        out, row = results[rid], by_id[rid]
        if rid in visiting:
            out['unknown_reasons'].append('CONSUMER_DEPENDENCY_CYCLE')
            finish(out)
            return
        visiting.add(rid)
        leaf = row.get('leaf_companion')
        if row.get('profile_mode', row['mode']).startswith('Replace:'):
            if leaf not in results or leaf == rid:
                out['unknown_reasons'].append('CONSUMER_LEAF_MISSING_OR_SELF')
            else:
                visit(leaf)
                out['consumer_leaf'] = {'id': leaf, 'status': results[leaf]['status']}
                if (results[leaf]['status'] != 'ACCEPTED' or by_id[leaf]['expected'] != 'SUCCESS' or
                        by_id[leaf].get('profile') != row.get('profile')):
                    out['pending_reasons'].append('MATCHING_LEAF_NOT_ACCEPTED')
        visiting.remove(rid)
        done.add(rid)
        finish(out)

    for rid in results:
        visit(rid)
