# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Fail-closed regular-output binding and explicit source-site role rules.

These are bounded source-reported observations, never independent proof credit.
No commands from evidence are executed. Historical v2 policy gates are retained.
"""
import collections
import hashlib
import json
import re


class EvidenceError(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise EvidenceError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


CHECK = re.compile(
    r'^Check ([1-9][0-9]*): ([^\n]+)\n'
    r'[ \t]+- Status: ([A-Z_]+)\n'
    r'[ \t]+- Description: (.*?)\n'
    r'[ \t]+- Location: ([^\n]+?):([0-9]+)(?::([0-9]+))? in function ([^\n]+)$', re.M | re.S)
MARKER = re.compile(r'^Checking harness (.+)\.\.\.$', re.M)


def bind_stdout(data, row, harness, receipt, group, compilation):
    """Use the pinned runner's split receipts, exact marker, bytes and inventory.

    Missing/ambiguous/truncated input invalidates the *whole row*, even if its
    export has no unreachable IDs. Group summary lines are not harness markers.
    """
    require(isinstance(data, bytes), 'STDOUT_MISSING_OR_WRONG_TYPE')
    require(receipt['id'] == row['id'] and receipt['selector'] == row['selector'] ==
            harness['name'], 'STDOUT_ROW_HARNESS_MISMATCH')
    require(receipt['group'] == group['id'] and
            receipt['group_receipt'] == 'groups/' + group['id'] + '/receipt.json',
            'STDOUT_GROUP_BINDING_MISMATCH')
    require(receipt['group_export_sha256'] == group['export_sha256'], 'STDOUT_EXPORT_SHA_MISMATCH')
    require(group['state'] == 'OBSERVED', 'STDOUT_GROUP_NOT_OBSERVED')
    execution = group['execution']
    for field in ('stdout_truncated', 'stderr_truncated', 'output_truncated', 'timed_out'):
        require(execution[field] is False, 'STDOUT_INCOMPLETE_' + field)
    require(execution.get('termination_reason') is None and execution['signal'] is None,
            'STDOUT_GROUP_INTERRUPTED')
    require(compilation == execution['compilation'] and
            compilation['state'] == 'PRE_HARNESS_COMPLETE', 'STDOUT_SPLIT_RECEIPT_MISMATCH')
    order, members = compilation['harness_marker_order'], group['rows']
    require(isinstance(order, list) and isinstance(members, list) and
            len(order) == len(set(order)) and len(members) == len(set(members)) and
            set(order) == set(members) and order.count(row['id']) == 1,
            'STDOUT_AMBIGUOUS_MARKER_ORDER')
    count, cap = compilation['row_output_bytes'][row['id']]['stdout'], receipt['stdout_cap_bytes']
    require(type(count) is int and type(cap) is int and 0 < len(data) == count < cap,
            'STDOUT_SIZE_OR_CAP_MISMATCH')
    text = data.decode('utf-8', errors='strict')
    require(MARKER.findall(text) == [row['selector']] and
            text.startswith('Checking harness ' + row['selector'] + '...\n'),
            'STDOUT_EXACT_MARKER_MISMATCH')
    require(len(re.findall(r'^RESULTS:\s*$', text, re.M)) == 1 and
            len(re.findall(r'^SUMMARY:\s*$', text, re.M)) == 1,
            'STDOUT_RESULTS_BOUNDARY_MISMATCH')
    verdict = {'SUCCESS': 'SUCCESSFUL', 'FAILURE': 'FAILED'}.get(harness['outcome']['verdict'])
    require(verdict is not None and re.findall(r'^VERIFICATION:- (\S+)\s*$', text, re.M) == [verdict]
            and len(re.findall(r'^Verification Time: [0-9.]+s\s*$', text, re.M)) == 1,
            'STDOUT_TERMINAL_VERDICT_MISMATCH')
    matches = list(CHECK.finditer(text))
    require(len(matches) == len(re.findall(r'^Check ', text, re.M)) == harness['n_properties'],
            'STDOUT_PARTIAL_CHECK_BLOCK_OR_COUNT')
    require([int(m[1]) for m in matches] == list(range(1, len(matches) + 1)),
            'STDOUT_CHECK_SEQUENCE_MISMATCH')
    results_start = text.index('RESULTS:')
    summary_start = text.index('SUMMARY:')
    require(all(results_start < m.start() < m.end() < summary_start for m in matches),
            'STDOUT_CHECK_OUTSIDE_RESULTS')
    records = {}
    for m in matches:
        require(m[2] not in records, 'STDOUT_DUPLICATE_ID:' + m[2])
        # Kani regular output uses literal surrounding quotes, not JSON string
        # escaping. Descriptions may contain raw quotes and physical newlines.
        require(m[4].startswith('"') and m[4].endswith('"') and
                not re.search(r'^Check |^Checking harness ', m[4], re.M),
                'STDOUT_INVALID_DESCRIPTION')
        desc = m[4][1:-1]
        require(bool(desc), 'STDOUT_INVALID_DESCRIPTION')
        records[m[2]] = {'id': m[2], 'status': m[3], 'description': desc,
                         'file': m[5], 'line': int(m[6]),
                         'column': int(m[7]) if m[7] else None, 'function': m[8],
                         'stdout_check_number': int(m[1]),
                         'stdout_line': text.count('\n', 0, m.start()) + 1}
    statuses = collections.Counter(r['status'] for r in records.values())
    require(set(statuses) <= {'SUCCESS', 'FAILURE', 'UNREACHABLE', 'SATISFIED'},
            'STDOUT_UNRECOGNIZED_STATUS')
    require(statuses['SUCCESS'] == harness['checks']['success'], 'STDOUT_SUCCESS_COUNT_MISMATCH')
    for bucket, status in (('failure', 'FAILURE'), ('unreachable', 'UNREACHABLE')):
        ids = harness['checks'][bucket]
        require(len(ids) == len(set(ids)) and
                set(ids) == {pid for pid, r in records.items() if r['status'] == status},
                'STDOUT_EXPORT_EXACT_ID_STATUS_MISMATCH:' + bucket)
    require(set(harness['covers']['satisfied']) ==
            {pid for pid, r in records.items() if r['status'] == 'SATISFIED'},
            'STDOUT_COVER_ID_STATUS_MISMATCH')
    return records, {'state': 'BOUND_COMPLETE', 'stdout_sha256': digest(data),
                     'stdout_bytes': count, 'stdout_cap_bytes': cap,
                     'stdout_member': row['id'] + '/stdout.log',
                     'receipt_sha256': None, 'marker_index': order.index(row['id']),
                     'parsed_properties': len(records), 'statuses': dict(statuses),
                     'split_assurance': 'PINNED_RUNNER_MARKERS_AND_RECEIPTS_SOURCE_REPORTED'}


def role(record, rules):
    """First matching explicit rule; file/function/line/description all matter.

    A helper name alone never grants an exemption. Unknown custom assertions at
    an otherwise allowed source site also fail closed.
    """
    out = dict(record)
    out.update(role='UNKNOWN', target_wrapper_relation='UNESTABLISHED',
               reason='No explicit reviewed source-site/description family matches.', rule=None)
    for rule in rules:
        if (re.fullmatch(rule['function'], record['function']) and
                re.fullmatch(rule['file'], record['file']) and
                (rule['lines'] is None or record['line'] in rule['lines']) and
                re.fullmatch(rule['property_id'], record['id']) and
                re.fullmatch(rule['description'], record['description'])):
            out.update(role=rule['role'], reason=rule['reason'], rule=rule['id'],
                       target_wrapper_relation=rule['target_wrapper_relation'])
            break
    out['property_location'] = {k: record[k] for k in ('file', 'line', 'column')}
    return out
