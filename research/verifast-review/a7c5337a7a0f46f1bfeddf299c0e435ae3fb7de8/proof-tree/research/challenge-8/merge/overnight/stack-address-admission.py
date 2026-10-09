#!/usr/bin/env python3
"""Hosted-only certificate for actual bidirectional_merge hidden MIR locals.

Input must be a *normal-preprocess* exporter capture with the same Rust args as
VeriFast.  The older preprocess-readonly decode.out is deliberately rejected.
This script only checks identity and dataflow roles; it grants no permissions.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys


class AdmissionError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CapnpText:
    """Full-consumption parser for capnp decode's record/list/scalar notation."""

    def __init__(self, source: str):
        self.source = source
        self.at = 0

    def whitespace(self) -> None:
        while self.at < len(self.source) and self.source[self.at].isspace():
            self.at += 1

    def take(self, character: str) -> bool:
        self.whitespace()
        if self.source.startswith(character, self.at):
            self.at += len(character)
            return True
        return False

    def atom(self) -> str:
        self.whitespace()
        start = self.at
        while self.at < len(self.source) and self.source[self.at] not in ' \r\n\t,()[]=":':
            self.at += 1
        require(self.at > start, f"invalid decoded MIR token at byte {start}")
        value = self.source[start:self.at]
        require(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*|-?(?:0|[1-9][0-9]*)", value)
                is not None, f"unknown decoded MIR atom {value!r}")
        return value

    def string(self) -> str:
        self.whitespace()
        start = self.at
        require(self.take('"'), "expected decoded MIR string")
        escaped = False
        while self.at < len(self.source):
            ch = self.source[self.at]
            self.at += 1
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                try:
                    value = ast.literal_eval(self.source[start:self.at])
                except (SyntaxError, ValueError) as exc:
                    raise AdmissionError(f"invalid decoded MIR string at {start}: {exc}") from exc
                require(isinstance(value, str), "decoded MIR string is not text")
                return value
        raise AdmissionError(f"unterminated decoded MIR string at byte {start}")

    def value(self):
        self.whitespace()
        require(self.at < len(self.source), "truncated decoded MIR")
        if self.take('('):
            result = {}
            if self.take(')'):
                return result
            while True:
                key = self.atom()
                require(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", key) is not None,
                        "invalid decoded MIR field")
                require(self.take('='), "expected '=' in decoded MIR record")
                require(key not in result, f"duplicate decoded MIR field {key}")
                result[key] = self.value()
                if self.take(')'):
                    return result
                require(self.take(','), "expected ',' in decoded MIR record")
        if self.take('['):
            result = []
            if self.take(']'):
                return result
            while True:
                result.append(self.value())
                if self.take(']'):
                    return result
                require(self.take(','), "expected ',' in decoded MIR list")
        if self.source[self.at] == '"':
            return self.string()
        atom = self.atom()
        if atom == 'void':
            return None
        if atom == 'true':
            return True
        if atom == 'false':
            return False
        if re.fullmatch(r"-?(?:0|[1-9][0-9]*)", atom):
            return int(atom)
        raise AdmissionError(f"unknown decoded MIR scalar {atom!r}")

    def parse(self):
        result = self.value()
        self.whitespace()
        require(self.at == len(self.source),
                f"trailing decoded MIR text at byte {self.at}")
        return result


def path(item, *keys):
    for key in keys:
        require(isinstance(item, dict) and key in item,
                f"missing decoded MIR field {key}")
        item = item[key]
    return item


def local(place) -> str:
    result = path(place, 'local', 'name')
    require(isinstance(result, str) and re.fullmatch(r'_[0-9]+', result) is not None,
            'invalid MIR local reference')
    require(path(place, 'projection') == [], 'unexpected projected MIR local')
    return result


def span_text(span, lines: list[str]) -> tuple[str, int]:
    regular = path(span, 'regular')
    lo, hi = path(regular, 'lo'), path(regular, 'hi')
    filename = path(lo, 'file', 'name', 'real', 'localPath')
    require(filename == 'verified/lib.rs' and
            path(hi, 'file', 'name', 'real', 'localPath') == filename,
            'MIR span does not name the checked source')
    line = path(lo, 'line')
    require(isinstance(line, int) and 1 <= line <= len(lines) and
            path(hi, 'line') == line, 'MIR call span is not on one source line')
    begin = path(lo, 'col', 'pos')
    end = path(hi, 'col', 'pos')
    require(isinstance(begin, int) and isinstance(end, int) and
            0 <= begin < end <= len(lines[line - 1]), 'invalid MIR source column')
    return lines[line - 1][begin:end], line


def call_name(call) -> str:
    name = path(call, 'func', 'constant', 'const', 'val', 'ty', 'kind',
                'fnDef', 'id', 'name')
    require(isinstance(name, str), 'non-name MIR callee')
    return name


def operand_local(operand) -> str:
    require(isinstance(operand, dict) and len(operand) == 1,
            'unexpected MIR operand shape')
    kind, place = next(iter(operand.items()))
    require(kind in ('copy', 'move'), 'expected MIR local operand')
    return local(place)


def assignment(statement):
    kind = path(statement, 'kind')
    return kind.get('assign') if isinstance(kind, dict) else None


def type_is_range(ty) -> bool:
    try:
        adt = path(ty, 'kind', 'adt')
        args = path(adt, 'substs')
        return (path(adt, 'id', 'name') == 'std::ops::Range' and
                isinstance(args, list) and len(args) == 1 and
                path(args[0], 'kind', 'type', 'kind', 'uInt') == {'uSize': None})
    except AdmissionError:
        return False


def type_is_tuple3(ty) -> bool:
    try:
        members = path(ty, 'kind', 'tuple')
        return (isinstance(members, list) and len(members) == 3 and
                all(path(member, 'kind', 'rawPtr', 'ty', 'kind', 'param') == 'T'
                    for member in members) and
                [path(member, 'kind', 'rawPtr', 'mutability')
                 for member in members] ==
                [{'not': None}, {'not': None}, {'mut': None}])
    except AdmissionError:
        return False


def vdi_map(body) -> dict[str, list[str]]:
    names: dict[str, list[str]] = {}
    for entry in path(body, 'varDebugInfo'):
        value = path(entry, 'value')
        if 'place' in value and path(value, 'place', 'projection') == []:
            name = path(entry, 'name', 'name')
            names.setdefault(name, []).append(local(value['place']))
    return names


def checked_call(body, lines, requested, source_text):
    found = []
    for block in path(body, 'basicBlocks'):
        kind = path(block, 'terminator', 'kind')
        if 'call' not in kind:
            continue
        call = kind['call']
        name = call_name(call)
        if name == requested:
            snippet, line = span_text(path(call, 'callSpan'), lines)
            require(snippet == source_text,
                    f"{requested} call span has unexpected source text {snippet!r}")
            require(path(call, 'unwindAction') == {'continue': None},
                    f"{requested} no longer has continue-unwind")
            found.append((block, call, line))
    require(len(found) == 1, f"expected one {requested} call, found {len(found)}")
    return found[0]


def target_block(blocks, call):
    index = path(call, 'target', 'something', 'index')
    found = [block for block in blocks if path(block, 'id', 'index') == index]
    require(len(found) == 1, 'normal call destination block is ambiguous')
    return found[0]


def use_source(assign):
    rhs = path(assign, 'rhsRvalue')
    if 'use' not in rhs:
        return None
    operand = rhs['use']
    if not isinstance(operand, dict) or len(operand) != 1:
        return None
    kind, place = next(iter(operand.items()))
    if kind not in ('copy', 'move'):
        return None
    return kind, place


def named_cursor(names, name, input_count):
    candidates = [identifier for identifier in names.get(name, [])
                  if int(identifier[1:]) > input_count]
    require(len(candidates) == 1,
            f'expected one nonparameter source cursor {name}, found {candidates}')
    return candidates[0]


def referenced_locals(value):
    if isinstance(value, dict):
        if isinstance(value.get('local'), dict) and 'name' in value['local']:
            yield value['local']['name']
        for nested in value.values():
            yield from referenced_locals(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from referenced_locals(nested)


def mir_places(value):
    """Enumerate every decoded MIR Place, preserving object identity."""
    if isinstance(value, dict):
        if isinstance(value.get('local'), dict) and 'name' in value['local']:
            yield value
        for nested in value.values():
            yield from mir_places(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from mir_places(nested)


def check_all_role_places(blocks, roles, allowed):
    actual = [place for place in mir_places(blocks)
              if path(place, 'local', 'name') in roles.values()]
    require(len(actual) == len(allowed) and
            {id(place) for place in actual} == set(allowed) and
            len({id(place) for place in actual}) == len(actual),
            'hidden role has an extra/missing MIR place read or write')


def all_assignment_writes(blocks, identifier):
    return [(block, stmt) for block in blocks
            for stmt in path(block, 'statements')
            if (a := assignment(stmt)) is not None and
            path(a, 'lhsPlace', 'local', 'name') == identifier]


def check_call_inputs(block, call, blocks, names, expected, input_count):
    """Bind actual MIR operands to their last definitions in the call block."""
    args = path(call, 'args')
    require(len(args) == 4, 'merge call argument arity changed')
    temps = []
    for operand in args:
        require(isinstance(operand, dict) and set(operand) == {'move'},
                'merge call argument is not a moved temporary')
        temps.append(local(operand['move']))
    require(len(set(temps)) == 4, 'merge call argument temporaries alias')
    statements = path(block, 'statements')
    for index, (temp, source_name) in enumerate(zip(temps, (*expected, 'is_less'))):
        writes = [(position, a) for position, stmt in enumerate(statements)
                  if (a := assignment(stmt)) is not None and
                  path(a, 'lhsPlace', 'local', 'name') == temp]
        require(len(writes) == 1 and
                path(writes[0][1], 'lhsPlace', 'projection') == [],
                f'merge argument {index} has an extra/missing/intervening write')
        require(len(all_assignment_writes(blocks, temp)) == 1,
                f'merge argument {index} is written in another MIR block')
        lives = [position for position, stmt in enumerate(statements)
                 if path(stmt, 'kind').get('storageLive') == {'name': temp}]
        deaths = [stmt for stmt in statements
                  if path(stmt, 'kind').get('storageDead') == {'name': temp}]
        require(len(lives) == 1 and lives[0] < writes[0][0] and not deaths,
                f'merge argument {index} storage lifetime changed before call')
        rhs = path(writes[0][1], 'rhsRvalue')
        if index < 3:
            source = named_cursor(names, source_name, input_count)
            require(set(rhs) == {'use'} and
                    set(rhs['use']) == {'copy'} and
                    local(rhs['use']['copy']) == source,
                    f'merge argument {index} is not the current {source_name} cursor')
        else:
            callback = path(names, 'is_less')
            require(len(callback) == 1 and int(callback[0][1:]) <= input_count and
                    set(rhs) == {'ref'}, 'merge callback argument shape changed')
            borrowed = rhs['ref']
            require(path(borrowed, 'borKind') == {'mut': None} and
                    path(borrowed, 'place', 'local', 'name') == callback[0] and
                    path(borrowed, 'place', 'projection') == [{'deref': None}] and
                    path(borrowed, 'placeTy', 'kind', 'param') == 'F',
                    'merge callback no longer borrows source is_less')
        # The fresh argument temporary is never consumed in an earlier RHS.
        require(not any(temp in referenced_locals(path(a, 'rhsRvalue'))
                        for a in (assignment(stmt) for stmt in statements)
                        if a is not None),
                f'merge argument {index} is used before the call')


def tuple_roles(target, blocks, tuple_id, names, expected, call_line, lines,
                input_count):
    statements = path(target, 'statements')
    extracts = {}
    extracted_places = []
    for position, stmt in enumerate(statements):
        assign = assignment(stmt)
        if assign is None:
            continue
        source = use_source(assign)
        if source is None:
            continue
        _, place = source
        if path(place, 'local', 'name') != tuple_id:
            continue
        projection = path(place, 'projection')
        require(len(projection) == 1 and 'field' in projection[0],
                'unexpected tuple result projection')
        field = path(projection[0], 'field', 'index')
        require(field in (0, 1, 2) and field not in extracts,
                'duplicate or invalid tuple result field')
        span, line = span_text(path(stmt, 'sourceInfo', 'span'), lines)
        require(line == call_line and expected[field] in span,
                'tuple extraction has wrong source binding')
        extracts[field] = (position, local(path(assign, 'lhsPlace')))
        extracted_places.append(place)
    require(set(extracts) == {0, 1, 2}, 'missing tuple result field extraction')
    require(extracts[0][0] < extracts[1][0] < extracts[2][0],
            'tuple fields are extracted out of order')
    writes = [(position, a) for position, stmt in enumerate(statements)
              if (a := assignment(stmt)) is not None]
    extract_positions = {position for position, _ in extracts.values()}
    require(all((tuple_id not in referenced_locals(path(a, 'rhsRvalue')) or
                 position in extract_positions) and
                path(a, 'lhsPlace', 'local', 'name') != tuple_id
                for position, a in writes),
            'tuple result has an unexpected target-block read/write')
    for field, wanted_name in enumerate(expected):
        start, seed = extracts[field]
        bridges = [(position, local(path(a, 'lhsPlace')))
                   for position, a in writes if position > start and
                   (u := use_source(a)) is not None and
                   path(u[1], 'projection') == [] and local(u[1]) == seed]
        require(len(bridges) == 1 and bridges[0][0] > extracts[2][0],
                f'tuple field {field} bridge is ambiguous or reordered')
        middle, bridge = bridges[0]
        target_id = named_cursor(names, wanted_name, input_count)
        cursor_writes = [(position, a) for position, a in writes
                         if path(a, 'lhsPlace', 'local', 'name') == target_id]
        require(len(cursor_writes) == 1 and cursor_writes[0][0] > middle and
                (u := use_source(cursor_writes[0][1])) is not None and
                path(u[1], 'projection') == [] and local(u[1]) == bridge,
                f'tuple field {field} does not update only {wanted_name}')
        for identifier in (seed, bridge):
            require(sum(path(a, 'lhsPlace', 'local', 'name') == identifier
                        for _, a in writes) == 1,
                    f'tuple field {field} intermediate is overwritten')
            require(len(all_assignment_writes(blocks, identifier)) == 1,
                    f'tuple field {field} intermediate is written in another MIR block')
            require(sum(identifier in referenced_locals(path(a, 'rhsRvalue'))
                        for _, a in writes) == 1,
                    f'tuple field {field} intermediate has an extra read')
        require(start < middle < cursor_writes[0][0],
                f'tuple field {field} updates are reordered')
    return extracted_places


def inspect(decoded, source_text: str):
    lines = source_text.splitlines()
    bodies = path(decoded, 'bodies')
    found = [body for body in bodies if path(body, 'defPath') == 'bidirectional_merge']
    require(len(found) == 1, 'expected one actual bidirectional_merge body')
    body = found[0]
    require(path(body, 'defKind') == {'fn': None} and len(path(body, 'inputs')) == 3,
            'bidirectional_merge body shape changed')
    declarations = path(body, 'localDecls')
    for index, decl in enumerate(declarations):
        require(path(decl, 'id', 'name') == f'_{index}',
                'MIR local declaration index/name mismatch')
    names = vdi_map(body)
    aliased = {
        path(entry, 'value', 'place', 'local', 'name')
        for entry in path(body, 'varDebugInfo')
        if 'place' in path(entry, 'value')
    }

    blocks = path(body, 'basicBlocks')
    into = []
    for block in blocks:
        kind = path(block, 'terminator', 'kind')
        if 'call' in kind:
            call = kind['call']
            name = call_name(call)
            if name == 'std::iter::IntoIterator::into_iter':
                snippet, line = span_text(path(call, 'callSpan'), lines)
                require(snippet == '0..len_div_2', 'range call no longer belongs to the for loop')
                require(path(call, 'unwindAction') == {'continue': None},
                        'range conversion unwind changed')
                into.append((block, call, line))
    require(len(into) == 1, 'expected one range into_iter call')
    _, range_call, loop_line = into[0]
    require(len(path(range_call, 'args')) == 1, 'range into_iter arity changed')
    range_input = operand_local(path(range_call, 'args')[0])
    range_result = local(path(range_call, 'destination'))
    up_block, up_call, up_line = checked_call(
        body, lines, 'merge_up', 'merge_up(left, right, dst, is_less)')
    down_block, down_call, down_line = checked_call(
        body, lines, 'merge_down',
        'merge_down(left_rev, right_rev, dst_rev, is_less)')
    require('merge_up(left, right, dst, is_less)' in lines[up_line - 1] and
            'merge_down(left_rev, right_rev, dst_rev, is_less)' in lines[down_line - 1],
            'actual merge call source text changed')
    require(loop_line < up_line < down_line, 'range and merge calls reordered')
    up_result = local(path(up_call, 'destination'))
    down_result = local(path(down_call, 'destination'))
    check_call_inputs(up_block, up_call, blocks, names,
                      ('left', 'right', 'dst'), len(path(body, 'inputs')))
    check_call_inputs(down_block, down_call, blocks, names,
                      ('left_rev', 'right_rev', 'dst_rev'), len(path(body, 'inputs')))
    roles = {'range_result': range_result, 'range_input': range_input,
             'merge_up_result': up_result, 'merge_down_result': down_result}
    require(len(set(roles.values())) == 4, 'hidden stack roles alias each other')
    for role, identifier in roles.items():
        index = int(identifier[1:])
        require(index > len(path(body, 'inputs')) and index < len(declarations),
                f'{role} targets return/parameter/missing local')
        require(identifier not in aliased, f'{role} has a VDI/source alias')
        ty = path(declarations[index], 'ty')
        require(type_is_range(ty) if role.startswith('range_') else type_is_tuple3(ty),
                f'{role} has wrong raw MIR type')
    role_details = {
        role: {
            'raw_id': identifier,
            'vf_name': '$' + identifier,
            'raw_type': ('std::ops::Range<usize>' if role.startswith('range_')
                         else '(*const T,*const T,*mut T)'),
            'declaration_span': path(declarations[int(identifier[1:])],
                                     'sourceInfo', 'span', 'regular'),
        }
        for role, identifier in roles.items()
    }

    # The range input must be the loop's concrete 0..len_div_2 aggregate.
    range_builds = []
    for block in blocks:
        for stmt in path(block, 'statements'):
            assign = assignment(stmt)
            if assign is None or path(assign, 'lhsPlace', 'projection') != []:
                continue
            if local(path(assign, 'lhsPlace')) != range_input:
                continue
            agg = path(assign, 'rhsRvalue').get('aggregate')
            if agg is not None:
                range_builds.append((stmt, agg))
    require(len(range_builds) == 1, 'range input has no unique aggregate construction')
    stmt, agg = range_builds[0]
    require(path(agg, 'aggregateKind', 'adt', 'adtId', 'name') == 'std::ops::Range' and
            [path(field, 'name') for field in path(agg, 'aggregateKind', 'adt', 'fields')]
            == ['start', 'end'] and len(path(agg, 'operands')) == 2,
            'range aggregate fields changed')
    _, build_line = span_text(path(stmt, 'sourceInfo', 'span'), lines)
    require(build_line == loop_line, 'range aggregate is not at loop site')
    iter_ids = names.get('iter', [])
    require(len(iter_ids) == 1, 'source iterator VDI is missing/ambiguous')
    iter_target = target_block(blocks, range_call)
    iter_moves = [(a, u[1]) for s in path(iter_target, 'statements')
                  if (a := assignment(s)) is not None and
                  path(a, 'lhsPlace', 'projection') == [] and
                  local(path(a, 'lhsPlace')) == iter_ids[0] and
                  (u := use_source(a)) is not None and u[0] == 'move' and
                  path(u[1], 'projection') == [] and local(u[1]) == range_result]
    require(len(iter_moves) == 1,
            'range result is not uniquely moved to source iterator')

    allowed_role_places = [id(path(stmt, 'kind', 'assign', 'lhsPlace')),
                           id(path(range_call, 'args')[0][
                               next(iter(path(range_call, 'args')[0]))]),
                           id(path(range_call, 'destination')),
                           id(iter_moves[0][1])]

    for block, call, result, expected, call_line in (
        (up_block, up_call, up_result, ('left', 'right', 'dst'), up_line),
        (down_block, down_call, down_result,
         ('left_rev', 'right_rev', 'dst_rev'), down_line),
    ):
        target = target_block(blocks, call)
        allowed_role_places.append(id(path(call, 'destination')))
        allowed_role_places.extend(id(place) for place in
                                   tuple_roles(target, blocks, result, names,
                                               expected, call_line, lines,
                                               len(path(body, 'inputs'))))
    require(len(allowed_role_places) == 12 and
            len(set(allowed_role_places)) == len(allowed_role_places),
            'hidden role place whitelist is ambiguous')
    check_all_role_places(blocks, roles, allowed_role_places)

    # All marker uses must be in the one body invariant. In discovery there
    # are no uses; after injection there are exactly 3+3+4+4 field/padding uses.
    marker_lines = [(i + 1, line) for i, line in enumerate(lines)
                    if 'mir_stack_addr' in line]
    if marker_lines:
        require(len(marker_lines) == 1 and
                marker_lines[0][1].lstrip().startswith('//@ inv ') and
                marker_lines[0][0] == loop_line + 1,
                'stack markers occur outside the loop-body invariant')
        values = re.findall(r'mir_stack_addr\(([0-9]+)\)', marker_lines[0][1])
        require(len(values) == marker_lines[0][1].count('mir_stack_addr'),
                'malformed stack marker spelling')
        expected = {range_result[1:]: 3, range_input[1:]: 3,
                    up_result[1:]: 4, down_result[1:]: 4}
        observed = {identifier: values.count(identifier)
                    for identifier in sorted(set(values) | set(expected))}
        require(all(values.count(identifier) == count
                    for identifier, count in expected.items()) and
                len(values) == 14,
                f'stack marker IDs/counts mismatch: expected={expected}, observed={observed}')
    return {
        'roles': {role: int(identifier[1:]) for role, identifier in roles.items()},
        'role_details': role_details,
        'loop_line': loop_line,
        'merge_up_line': up_line,
        'merge_down_line': down_line,
        'marker_count': sum(line.count('mir_stack_addr') for _, line in marker_lines),
        'status': 'final' if marker_lines else 'discovery',
    }


def negative_controls(decoded, source: str, certificate: dict) -> list[str]:
    """Reject targeted, in-memory mutants at this certificate's own gates."""
    checked = []

    def body_of(tree):
        matches = [body for body in path(tree, 'bodies')
                   if path(body, 'defPath') == 'bidirectional_merge']
        require(len(matches) == 1, 'negative-control body setup failed')
        return matches[0]

    def call_of(body, name):
        calls = [path(block, 'terminator', 'kind', 'call')
                 for block in path(body, 'basicBlocks')
                 if 'call' in path(block, 'terminator', 'kind') and
                 call_name(path(block, 'terminator', 'kind', 'call')) == name]
        require(len(calls) == 1, f'negative-control {name} setup failed')
        return calls[0]

    def rejected(label, mutate, changed_source=None, expected_reason=None):
        tree = copy.deepcopy(decoded)
        mutate(tree)
        try:
            inspect(tree, source if changed_source is None else changed_source)
        except AdmissionError as exc:
            require(expected_reason is None or expected_reason in str(exc),
                    f'negative control {label} failed at wrong gate: {exc}')
            checked.append(label)
            return
        raise AdmissionError(f'negative control {label} was unexpectedly admitted')

    ids = certificate['roles']

    def swapped_destination(tree):
        up = call_of(body_of(tree), 'merge_up')
        path(up, 'destination', 'local')['name'] = f"_{ids['range_result']}"
    rejected('range_tuple_destination_swap', swapped_destination)

    def wrong_type(tree):
        decls = path(body_of(tree), 'localDecls')
        decls[ids['merge_up_result']]['ty'] = copy.deepcopy(
            decls[ids['range_result']]['ty'])
    rejected('tuple_type_changed_to_range', wrong_type)

    def vdi_alias(tree):
        path(body_of(tree), 'varDebugInfo').append({
            'name': {'name': 'hidden_alias_mutant'},
            'value': {'place': {
                'local': {'name': f"_{ids['merge_up_result']}"},
                'projection': []}}})
    rejected('hidden_local_vdi_alias', vdi_alias)

    def wrong_field(tree):
        body = body_of(tree)
        up = call_of(body, 'merge_up')
        target = target_block(path(body, 'basicBlocks'), up)
        for stmt in path(target, 'statements'):
            assign = assignment(stmt)
            if assign is None:
                continue
            operand = use_source(assign)
            if operand is None:
                continue
            place = operand[1]
            if (path(place, 'local', 'name') == f"_{ids['merge_up_result']}" and
                    path(place, 'projection') and
                    path(place, 'projection')[0].get('field', {}).get('index') == 0):
                path(place, 'projection')[0]['field']['index'] = 1
                return
        raise AdmissionError('wrong-field negative-control setup failed')
    rejected('tuple_field_target_changed', wrong_field)

    def wrong_unwind(tree):
        call_of(body_of(tree), 'merge_down')['unwindAction'] = {'unreachable': None}
    rejected('callback_unwind_changed', wrong_unwind)

    def wrong_call_operand(tree):
        body = body_of(tree)
        up = call_of(body, 'merge_up')
        up['args'][0]['move']['local']['name'] = named_cursor(
            vdi_map(body), 'dst', len(path(body, 'inputs')))
    rejected('wrong_actual_mir_call_operand', wrong_call_operand)

    def overwritten_call_temp(tree):
        body = body_of(tree)
        block = next(block for block in path(body, 'basicBlocks')
                     if 'call' in path(block, 'terminator', 'kind') and
                     call_name(path(block, 'terminator', 'kind', 'call')) == 'merge_up')
        temp = operand_local(path(block, 'terminator', 'kind', 'call', 'args')[0])
        original = next(stmt for stmt in path(block, 'statements')
                        if (a := assignment(stmt)) is not None and
                        local(path(a, 'lhsPlace')) == temp)
        extra = copy.deepcopy(original)
        extra['kind']['assign']['rhsRvalue']['use']['copy']['local']['name'] = \
            named_cursor(vdi_map(body), 'right', len(path(body, 'inputs')))
        path(block, 'statements').append(extra)
    rejected('overwritten_actual_mir_argument', overwritten_call_temp)

    def overwritten_field_temp(tree):
        body = body_of(tree)
        up = call_of(body, 'merge_up')
        target = target_block(path(body, 'basicBlocks'), up)
        tuple_id = local(path(up, 'destination'))
        original = next(stmt for stmt in path(target, 'statements')
                        if (a := assignment(stmt)) is not None and
                        (u := use_source(a)) is not None and
                        path(u[1], 'local', 'name') == tuple_id and
                        path(u[1], 'projection') and
                        path(u[1], 'projection')[0].get('field', {}).get('index') == 0)
        path(target, 'statements').append(copy.deepcopy(original))
    rejected('overwritten_tuple_field_temporary', overwritten_field_temp)

    def overwritten_cursor(tree):
        body = body_of(tree)
        up = call_of(body, 'merge_up')
        target = target_block(path(body, 'basicBlocks'), up)
        cursor = named_cursor(vdi_map(body), 'left', len(path(body, 'inputs')))
        original = next(stmt for stmt in path(target, 'statements')
                        if (a := assignment(stmt)) is not None and
                        local(path(a, 'lhsPlace')) == cursor)
        path(target, 'statements').append(copy.deepcopy(original))
    rejected('overwritten_tuple_cursor', overwritten_cursor)

    def extra_hidden_role_read(tree):
        body = body_of(tree)
        blocks = path(body, 'basicBlocks')
        into = call_of(body, 'std::iter::IntoIterator::into_iter')
        target = target_block(blocks, into)
        result = f"_{ids['range_result']}"
        original = next(stmt for stmt in path(target, 'statements')
                        if (a := assignment(stmt)) is not None and
                        (u := use_source(a)) is not None and
                        u[0] == 'move' and
                        path(u[1], 'local', 'name') == result and
                        path(u[1], 'projection') == [])
        extra = copy.deepcopy(original)
        extra['kind']['assign']['rhsRvalue']['use'] = {
            'copy': extra['kind']['assign']['rhsRvalue']['use'].pop('move')}
        path(target, 'statements').append(extra)
    rejected('extra_hidden_role_read_in_other_statement', extra_hidden_role_read,
             expected_reason='hidden role has an extra/missing MIR place')

    def extra_hidden_role_write(tree):
        body = body_of(tree)
        blocks = path(body, 'basicBlocks')
        block = next(block for block in blocks
                     if 'call' in path(block, 'terminator', 'kind') and
                     call_name(path(block, 'terminator', 'kind', 'call')) == 'merge_up')
        original = next(stmt for stmt in path(block, 'statements')
                        if (a := assignment(stmt)) is not None and
                        (u := use_source(a)) is not None and u[0] == 'copy')
        extra = copy.deepcopy(original)
        path(extra, 'kind', 'assign', 'lhsPlace', 'local')['name'] = \
            f"_{ids['range_input']}"
        path(block, 'statements').append(extra)
    rejected('extra_hidden_role_write_in_other_block', extra_hidden_role_write,
             expected_reason='hidden role has an extra/missing MIR place')

    def extra_nested_hidden_role_read(tree):
        body = body_of(tree)
        blocks = path(body, 'basicBlocks')
        result = f"_{ids['range_result']}"
        for block in blocks:
            for stmt in path(block, 'statements'):
                a = assignment(stmt)
                if (a is None or
                        path(a, 'lhsPlace', 'local', 'name') != f"_{ids['range_input']}" or
                        path(a, 'lhsPlace', 'projection') != []):
                    continue
                aggregate = path(a, 'rhsRvalue').get('aggregate')
                if aggregate is None:
                    continue
                operand = path(aggregate, 'operands')[0]
                operand.clear()
                operand['copy'] = {'local': {'name': result}, 'projection': []}
                return
        raise AdmissionError('nested hidden-role read negative-control setup failed')
    rejected('extra_nested_hidden_role_read', extra_nested_hidden_role_read,
             expected_reason='hidden role has an extra/missing MIR place')

    if certificate['status'] == 'final':
        require('mir_stack_addr(' in source, 'final marker negative-control setup failed')
        malformed = source.replace('mir_stack_addr(', 'mir_stack_addr(x', 1)
    else:
        malformed = source + '\n//@ inv mir_stack_addr(x);\n'
    rejected('malformed_marker', lambda tree: None, malformed)
    require(len(checked) == 13, 'negative-control suite is incomplete')
    return checked


def provenance_ok(provenance: dict, source_sha: str, mir_sha: str,
                  decoded_sha: str) -> bool:
    return (provenance.get('normal_preprocess') is True and
            provenance.get('mir_sha256') == mir_sha and
            provenance.get('decoded_sha256') == decoded_sha and
            provenance.get('source_sha256') == source_sha and
            provenance.get('github_sha') == os.environ.get('GITHUB_SHA') and
            provenance.get('github_run_id') == os.environ.get('GITHUB_RUN_ID') and
            provenance.get('source_unchanged') is True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decoded-normal', type=Path, required=True)
    parser.add_argument('--mir', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--provenance', type=Path, required=True)
    parser.add_argument('--expected-source-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--require-final', action='store_true')
    args = parser.parse_args()
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and
            os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and
            os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and
            os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10',
            'stack address admission requires the owned hosted research branch')
    require(not args.output.exists(), 'stack address certificate output already exists')
    require(re.fullmatch(r'[0-9a-f]{64}', args.expected_source_sha256) is not None,
            'invalid expected source SHA-256')
    source_bytes = args.source.read_bytes()
    source_sha = digest(source_bytes)
    require(source_sha == args.expected_source_sha256, 'verified source SHA-256 changed')
    source = source_bytes.decode('utf-8')
    decoded_bytes = args.decoded_normal.read_bytes()
    mir_sha = digest(args.mir.read_bytes())
    provenance = json.loads(args.provenance.read_text())
    decoded_sha = digest(decoded_bytes)
    require(provenance_ok(provenance, source_sha, mir_sha, decoded_sha),
            'normal exporter provenance or input hashes do not match')
    forged = dict(provenance)
    forged['mir_sha256'] = ('0' if mir_sha[0] != '0' else '1') + mir_sha[1:]
    require(not provenance_ok(forged, source_sha, mir_sha, decoded_sha),
            'wrong-hash provenance negative control was unexpectedly admitted')
    forged_source = dict(provenance)
    forged_source['source_sha256'] = ('0' if source_sha[0] != '0' else '1') + source_sha[1:]
    require(not provenance_ok(forged_source, source_sha, mir_sha, decoded_sha),
            'wrong-source-hash provenance negative control was unexpectedly admitted')
    forged_decode = dict(provenance)
    forged_decode['decoded_sha256'] = ('0' if decoded_sha[0] != '0' else '1') + decoded_sha[1:]
    require(not provenance_ok(forged_decode, source_sha, mir_sha, decoded_sha),
            'wrong-decoded-hash provenance negative control was unexpectedly admitted')
    command = provenance.get('command')
    require(isinstance(command, list) and all(isinstance(s, str) for s in command),
            'normal exporter command missing')
    executables = [i for i, arg in enumerate(command)
                   if Path(arg).name == 'vf-rust-mir-exporter']
    require(len(executables) == 1, 'normal exporter executable is ambiguous')
    export_args = command[executables[0] + 1:]
    require(len(export_args) == 4 and export_args[0] == 'verified/lib.rs' and
            export_args[1].startswith('--sysroot=') and
            export_args[2:] == ['--edition', '2021'] and
            not any('preprocess-readonly' in arg or 'no-preprocess' in arg
                    for arg in command),
            'exporter args differ from VeriFast normal preprocessing')
    decoded = CapnpText(decoded_bytes.decode('utf-8')).parse()
    certificate = inspect(decoded, source)
    certificate['negative_controls'] = negative_controls(decoded, source, certificate) + [
        'wrong_provenance_mir_hash', 'wrong_provenance_source_hash',
        'wrong_provenance_decoded_hash']
    if args.require_final:
        require(certificate['status'] == 'final',
                'discovery certificate cannot admit a final proof')
    certificate.update({'source_sha256': source_sha,
                        'normal_mir_sha256': mir_sha,
                        'normal_decoded_sha256': decoded_sha,
                        'github_sha': os.environ.get('GITHUB_SHA', ''),
                        'github_run_id': os.environ.get('GITHUB_RUN_ID', '')})
    require(re.fullmatch(r'[0-9a-f]{40}', certificate['github_sha']) is not None,
            'exact GitHub commit SHA is missing')
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(certificate, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    try:
        main()
    except (AdmissionError, UnicodeDecodeError, OSError, ValueError, SyntaxError,
            KeyError, TypeError, IndexError, RecursionError) as exc:
        print(f'STACK_ADDRESS_ADMISSION_REJECTED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
