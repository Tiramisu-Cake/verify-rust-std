#!/usr/bin/env python3
"""Hosted, fail-closed linkage of final normal-MIR roles to VeriFast proof AST.

This checks observable syntax and identity only. It grants no memory permission
and cannot replace VeriFast, refinement, leak/dead-code, or source-integrity gates.
"""

from __future__ import annotations

import argparse
import ast
import copy
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import sys


class AdmissionError(Exception):
    pass


def require(ok: bool, why: str) -> None:
    if not ok:
        raise AdmissionError(why)


@dataclass
class Node:
    name: str
    args: list


@dataclass(frozen=True)
class Sym:
    name: str


class OcamlAstText:
    """Parse the restricted constructor/list/tuple dump, consuming every token."""

    token = re.compile(r'\s+|"(?:\\.|[^"\\])*"|-?(?:0|[1-9][0-9]*)|'
                       r'[A-Za-z_][A-Za-z_0-9]*|[\[\](),;]')

    def __init__(self, text: str):
        require(len(text) <= 32_000_000, 'proof AST text exceeds admission bound')
        self.tokens = []
        at = 0
        while at < len(text):
            match = self.token.match(text, at)
            require(match is not None, f'unknown proof AST syntax at byte {at}')
            if not match.group().isspace():
                self.tokens.append(match.group())
            at = match.end()
        require(len(self.tokens) <= 2_000_000, 'proof AST token bound exceeded')
        self.at = 0

    def peek(self):
        return self.tokens[self.at] if self.at < len(self.tokens) else None

    def take(self, wanted):
        if self.peek() == wanted:
            self.at += 1
            return True
        return False

    def expect(self, wanted):
        require(self.take(wanted), f'expected {wanted!r} at AST token {self.at}')

    def value(self, depth=0):
        require(depth < 4096, 'proof AST nesting bound exceeded')
        current = self.peek()
        require(current is not None, 'truncated proof AST')
        if self.take('['):
            items = []
            if self.take(']'):
                return items
            while True:
                items.append(self.value(depth + 1))
                if self.take(']'):
                    return items
                self.expect(';')
        if self.take('('):
            if self.take(')'):
                return ()
            first = self.value(depth + 1)
            if self.take(')'):
                return first
            self.expect(',')
            items = [first]
            while True:
                items.append(self.value(depth + 1))
                if self.take(')'):
                    return tuple(items)
                self.expect(',')
        if current.startswith('"'):
            self.at += 1
            try:
                value = ast.literal_eval(current)
            except (ValueError, SyntaxError) as exc:
                raise AdmissionError('invalid proof AST string') from exc
            require(isinstance(value, str), 'nontext proof AST string')
            return value
        if re.fullmatch(r'-?(?:0|[1-9][0-9]*)', current):
            self.at += 1
            return int(current)
        require(re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', current) is not None,
                f'unknown proof AST atom {current!r}')
        self.at += 1
        if self.take('('):
            args = []
            if self.take(')'):
                return Node(current, args)
            while True:
                args.append(self.value(depth + 1))
                if self.take(')'):
                    return Node(current, args)
                self.expect(',')
        if current in ('loc', 'big_int_of_string') and self.peek() and self.peek().startswith('"'):
            return Node(current, [self.value(depth + 1)])
        return Sym(current)

    def parse(self):
        result = self.value()
        require(self.at == len(self.tokens),
                f'trailing proof AST tokens at position {self.at}')
        return result


def walk(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, Node):
            yield item
            pending.extend(reversed(item.args))
        elif isinstance(item, (list, tuple)):
            pending.extend(reversed(item))


def nodes(value, name):
    return [node for node in walk(value) if node.name == name]


def only(items, what):
    require(len(items) == 1, f'expected one {what}, found {len(items)}')
    return items[0]


def narg(value, name, count=None):
    require(isinstance(value, Node) and value.name == name and
            (count is None or len(value.args) == count),
            f'expected {name} constructor')
    return value.args


def sym(value, name):
    require(value == Sym(name), f'expected AST symbol {name}')


def var(value):
    args = narg(value, 'Var', 2)
    require(isinstance(args[1], str), 'invalid AST variable name')
    return args[1]


def loc(value):
    args = narg(value, 'loc', 1)
    require(isinstance(args[0], str), 'invalid AST location')
    return args[0]


def location_line(value):
    match = re.fullmatch(r'verified/lib\.rs\(([1-9][0-9]*),[1-9][0-9]*(?:-[0-9]+(?:,[0-9]+)?)?\)', loc(value))
    require(match is not None, 'AST location is not in checked source')
    return int(match.group(1))


def expected_loc(span):
    lo, hi = span['lo'], span['hi']
    require(lo['file']['name']['real']['localPath'] == 'verified/lib.rs' and
            hi['file']['name']['real']['localPath'] == 'verified/lib.rs' and
            lo['line'] == hi['line'], 'invalid normal-MIR role span')
    return (f"verified/lib.rs({lo['line']},{lo['col']['pos'] + 1}-"
            f"{hi['col']['pos'] + 1})")


def call_name(value):
    args = narg(value, 'CallExpr', 6)
    require(isinstance(args[1], str), 'invalid AST callee')
    return args[1]


def expr_stmt_assign(value):
    args = narg(value, 'ExprStmt', 1)
    return narg(args[0], 'AssignExpr', 4)


def role_address(value, names):
    if not isinstance(value, Node) or value.name != 'AddressOf':
        return None
    args = narg(value, 'AddressOf', 2)
    if not isinstance(args[1], Node) or args[1].name != 'Var':
        return None
    target = var(args[1])
    return target if target in names else None


def hidden_address(value):
    if not isinstance(value, Node) or value.name != 'AddressOf':
        return None
    args = narg(value, 'AddressOf', 2)
    if not isinstance(args[1], Node) or args[1].name != 'Var':
        return None
    target = var(args[1])
    return target if re.fullmatch(r'\$_[0-9]+', target) else None


def check_type(role, ty):
    args = narg(ty, 'StructTypeExpr', 5)
    type_name = narg(args[1], 'Some', 1)[0]
    params = args[4]
    require(isinstance(params, list), 'AST struct parameters are not a list')
    if role.startswith('range_'):
        require(type_name == 'std::ops::Range' and len(params) == 1,
                f'{role} AST Range type mismatch')
        check_usize_type(params[0])
    else:
        require(type_name == 'std_tuple_3_' and len(params) == 3,
                f'{role} AST tuple type mismatch')
        for param in params:
            check_t_pointer_type(param)


def check_usize_type(value):
    kind = narg(value, 'ManifestTypeExpr', 2)[1]
    int_args = narg(kind, 'Int', 2)
    sym(int_args[0], 'Unsigned')
    sym(int_args[1], 'PtrRank')


def check_t_pointer_type(value):
    pointer = narg(value, 'PtrTypeExpr', 2)[1]
    inner = narg(pointer, 'IdentTypeExpr', 3)
    sym(inner[1], 'None')
    require(inner[2] == 'T', 'AST pointer element changed')


def check_switch(sw, name, result, span):
    args = narg(sw, 'SwitchStmt', 3)
    call = args[1]
    require(call_name(call) == name and loc(call.args[0]) == expected_loc(span),
            f'{name} call or source span changed')
    require(loc(args[0]) == expected_loc(span), f'{name} switch span changed')
    clauses = args[2]
    require(isinstance(clauses, list) and len(clauses) == 2,
            f'{name} normal/unwind cases changed')
    by_name = {}
    for clause in clauses:
        cargs = narg(clause, 'SwitchStmtClause', 3)
        label = call_name(cargs[1])
        require(label not in by_name, f'{name} duplicate call outcome')
        by_name[label] = cargs[2]
    require(set(by_name) == {'returning', 'unwinding'},
            f'{name} call outcome set changed')
    normal = only(by_name['returning'], f'{name} normal assignment')
    assignment = expr_stmt_assign(normal)
    require(var(assignment[1]) == result and
            assignment[2] == Sym('Mutation') and
            var(assignment[3]) == '__result',
            f'{name} normal destination changed')
    unwinding = only(by_name['unwinding'], f'{name} unwind return')
    returned = narg(unwinding, 'ReturnStmt', 2)[1]
    outcome = narg(returned, 'Some', 1)[0]
    require(call_name(outcome) == 'unwinding', f'{name} unwind was suppressed')
    return call, assignment[1]


def statement_list_containing(value, target):
    found = []
    def visit(item):
        if isinstance(item, list):
            if any(entry is target for entry in item):
                found.append(item)
            for entry in item:
                visit(entry)
        elif isinstance(item, tuple):
            for entry in item:
                visit(entry)
        elif isinstance(item, Node):
            for entry in item.args:
                visit(entry)
    visit(value)
    return only(found, 'linear statement list containing checked call')


def ordered_assignment(stmt):
    assignment = expr_stmt_assign(stmt)
    require(isinstance(assignment[1], Node) and assignment[1].name == 'Var',
            'checked call def-use assignment is not a local write')
    return assignment


def direct_assignment(stmt):
    if (isinstance(stmt, Node) and stmt.name == 'ExprStmt' and
            len(stmt.args) == 1 and isinstance(stmt.args[0], Node) and
            stmt.args[0].name == 'AssignExpr'):
        return narg(stmt.args[0], 'AssignExpr', 4)
    return None


def all_local_writes(func, name):
    return [a.args for a in nodes(func, 'AssignExpr')
            if len(a.args) == 4 and isinstance(a.args[1], Node) and
            a.args[1].name == 'Var' and var(a.args[1]) == name]


def check_all_role_vars(func, names, allowed):
    role_names = set(names.values())
    actual = [node for node in nodes(func, 'Var') if var(node) in role_names]
    require(len(actual) == len(allowed) and
            len({id(node) for node in actual}) == len(actual) and
            {id(node) for node in actual} == {id(node) for node in allowed} and
            len({id(node) for node in allowed}) == len(allowed),
            'hidden role has an extra/missing proof AST variable read or write')


def check_extracts(func, switch, role_name, call_line, wanted):
    statements = statement_list_containing(func, switch)
    at = next(index for index, stmt in enumerate(statements) if stmt is switch)
    require(len(statements) >= at + 10,
            'tuple result has fewer than nine immediate extraction writes')
    following = [ordered_assignment(stmt) for stmt in statements[at + 1:at + 10]]
    seeds = []
    role_uses = []
    for field, assignment in enumerate(following[:3]):
        rhs = narg(assignment[3], 'Select', 3)
        require(assignment[2] == Sym('Initialization') and
                var(rhs[1]) == role_name and rhs[2] == str(field) and
                location_line(assignment[0]) == call_line,
                f'{role_name} field {field} extraction was reordered or changed')
        seeds.append(var(assignment[1]))
        role_uses.append(rhs[1])
    require(len(set(seeds)) == 3, 'tuple result field seeds alias')
    bridges = []
    for field, target in enumerate(wanted):
        first, second = following[3 + 2 * field:5 + 2 * field]
        bridge = var(first[1])
        require(first[2] == Sym('Mutation') and
                var(first[3]) == seeds[field] and
                second[2] == Sym('Mutation') and
                var(second[1]) == target and var(second[3]) == bridge and
                location_line(first[0]) == location_line(second[0]) == call_line,
                f'{role_name} field {field} has an overwritten or wrong cursor path')
        bridges.append(bridge)
    require(len(set(seeds + bridges + list(wanted))) == 9,
            'tuple field temporary/cursor identities alias')
    for position, seed in enumerate(seeds):
        writes = all_local_writes(func, seed)
        require(len(writes) == 1 and writes[0] is following[position],
                'tuple field seed is overwritten elsewhere in the AST')
    for position, bridge in enumerate(bridges):
        writes = all_local_writes(func, bridge)
        require(len(writes) == 1 and writes[0] is following[3 + 2 * position],
                'tuple field bridge is overwritten elsewhere in the AST')
    tracked = set(seeds + bridges + list(wanted))
    for stmt in statements[at + 10:]:
        assignment = direct_assignment(stmt)
        if (assignment is not None and location_line(assignment[0]) == call_line and
                isinstance(assignment[1], Node) and assignment[1].name == 'Var'):
            require(var(assignment[1]) not in tracked,
                    'tuple field temporary/cursor has a later same-line overwrite')
    return role_uses


def check_merge_inputs(func, switch, call, line, expected):
    actual = narg(call, 'CallExpr', 6)[4]
    require(isinstance(actual, list) and len(actual) == 4,
            'merge call argument arity changed')
    arguments = [var(narg(item, 'LitPat', 1)[0]) for item in actual]
    require(len(set(arguments)) == 4, 'merge call arguments alias unexpectedly')
    statements = statement_list_containing(func, switch)
    at = next(index for index, stmt in enumerate(statements) if stmt is switch)
    require(at >= 4, 'merge call lacks four immediate argument definitions')
    assignments = [ordered_assignment(stmt) for stmt in statements[at - 4:at]]
    require(all(location_line(a[0]) == line and a[2] == Sym('Mutation')
                for a in assignments) and
            [var(a[1]) for a in assignments] == arguments,
            'merge argument definitions are reordered, overwritten or missing')
    for argument, assignment in zip(arguments, assignments):
        writes = all_local_writes(func, argument)
        require(len(writes) == 1 and writes[0] is assignment,
                'merge argument temporary is overwritten elsewhere in the AST')
    for stmt in statements[:at - 4]:
        assignment = direct_assignment(stmt)
        if (assignment is not None and location_line(assignment[0]) == line and
                isinstance(assignment[1], Node) and assignment[1].name == 'Var'):
            require(var(assignment[1]) not in arguments,
                    'merge argument temporary has an earlier same-line write')
    for assignment, source in zip(assignments[:3], expected):
        require(var(assignment[3]) == source,
                f'merge argument is not copied from {source}')
    callback = narg(assignments[3][3], 'AddressOf', 2)[1]
    require(var(narg(callback, 'Deref', 2)[1]) == 'is_less',
            'merge callback input is not borrowed from is_less')


def check_range_constructor(func, identifier, line):
    builds = {}
    role_uses = {}
    for assign in nodes(func, 'AssignExpr'):
        args = narg(assign, 'AssignExpr', 4)
        if location_line(args[0]) != line or not isinstance(args[1], Node) or args[1].name != 'Select':
            continue
        field = narg(args[1], 'Select', 3)
        if not isinstance(field[1], Node) or field[1].name != 'Var' or var(field[1]) != identifier:
            continue
        require(field[2] in ('start', 'end') and field[2] not in builds,
                'range input field construction changed')
        builds[field[2]] = args[3]
        role_uses[field[2]] = field[1]
    require(set(builds) == {'start', 'end'}, 'range input fields not constructed')
    start = narg(builds['start'], 'CastExpr', 3)
    check_usize_type(start[1])
    zero = narg(start[2], 'IntLit', 5)
    require(narg(zero[1], 'big_int_of_string', 1)[0] == '0',
            'range start no longer zero')
    endpoint = var(builds['end'])
    candidates = [a for a in nodes(func, 'AssignExpr')
                  if location_line(a.args[0]) == line and
                  isinstance(a.args[1], Node) and a.args[1].name == 'Var' and
                  isinstance(a.args[3], Node) and a.args[3].name == 'Var' and
                  var(a.args[1]) == endpoint and var(a.args[3]) == 'len_div_2']
    only(candidates, 'range endpoint copy from len_div_2')
    return [role_uses['start'], role_uses['end']]


def validate(tree, cert):
    require(isinstance(tree, list), 'proof AST root is not a list')
    funcs = [node for node in nodes(tree, 'Func')
             if len(node.args) >= 5 and node.args[4] == 'bidirectional_merge']
    func = only(funcs, 'bidirectional_merge AST function')
    roles = cert['roles']
    expected_keys = {'range_input', 'range_result', 'merge_up_result', 'merge_down_result'}
    require(set(roles) == expected_keys and
            all(type(value) is int and value > 0 for value in roles.values()) and
            len(set(roles.values())) == 4 and cert['marker_count'] == 14 and
            cert['status'] == 'final', 'final normal-MIR role certificate invalid')
    names = {role: f'$_{number}' for role, number in roles.items()}
    allowed_role_vars = []
    require(all(cert['role_details'][role]['vf_name'] == name and
                cert['role_details'][role]['raw_id'] == f'_{roles[role]}'
                for role, name in names.items()), 'role detail identity changed')
    for role, name in names.items():
        matches = []
        for decl in nodes(func, 'DeclStmt'):
            entries = narg(decl, 'DeclStmt', 2)[1]
            require(isinstance(entries, list), 'invalid AST declaration list')
            for entry in entries:
                require(isinstance(entry, tuple) and len(entry) == 5,
                        'invalid AST declaration entry')
                if entry[2] == name:
                    matches.append(entry)
        entry = only(matches, f'{role} declaration')
        typed = narg(entry[1], 'Some', 1)[0]
        check_type(role, typed)
        require(loc(typed.args[0]) == expected_loc(cert['role_details'][role]['declaration_span']),
                f'{role} AST declaration type location changed')
        sym(entry[3], 'None')

    switches = [node for node in nodes(func, 'SwitchStmt')
                if isinstance(node.args[1], Node) and node.args[1].name == 'CallExpr']
    for callee, role, line in (
        ('merge_up', 'merge_up_result', cert['merge_up_line']),
        ('merge_down', 'merge_down_result', cert['merge_down_line']),
    ):
        sw = only([item for item in switches if call_name(item.args[1]) == callee],
                  f'{callee} switch')
        call, destination = check_switch(sw, callee, names[role],
                                         cert['role_details'][role]['declaration_span'])
        allowed_role_vars.append(destination)
        require(location_line(sw.args[0]) == line, f'{callee} line changed')
        check_merge_inputs(func, sw, call, line,
                           ('left', 'right', 'dst_1') if callee == 'merge_up'
                           else ('left_rev', 'right_rev', 'dst_rev'))
        allowed_role_vars.extend(check_extracts(
            func, sw, names[role], line,
            ('left', 'right', 'dst_1') if callee == 'merge_up'
            else ('left_rev', 'right_rev', 'dst_rev')))

    range_calls = [sw for sw in switches if call_name(sw.args[1]).endswith('::into_iter')
                   and 'Range<usize>' in call_name(sw.args[1])]
    range_sw = only(range_calls, 'Range into_iter switch')
    range_call, destination = check_switch(
        range_sw, call_name(range_sw.args[1]), names['range_result'],
        cert['role_details']['range_result']['declaration_span'])
    allowed_role_vars.append(destination)
    arguments = range_call.args[4]
    require(isinstance(arguments, list) and len(arguments) == 1 and
            var(narg(arguments[0], 'LitPat', 1)[0]) == names['range_input'],
            'Range into_iter argument is not range_input')
    allowed_role_vars.append(narg(arguments[0], 'LitPat', 1)[0])
    loop_line = cert['loop_line']
    iter_moves = [a for a in nodes(func, 'AssignExpr')
                  if location_line(a.args[0]) == loop_line and
                  isinstance(a.args[1], Node) and a.args[1].name == 'Var' and
                  isinstance(a.args[3], Node) and a.args[3].name == 'Var' and
                  var(a.args[1]) == 'iter' and var(a.args[3]) == names['range_result']]
    allowed_role_vars.append(only(iter_moves, 'Range result move to iter').args[3])
    allowed_role_vars.extend(check_range_constructor(func, names['range_input'], loop_line))

    invariant_line = loop_line + 1
    invariants = [node for node in nodes(func, 'InvariantStmt')
                  if location_line(node.args[0]) == invariant_line]
    invariant = only(invariants, 'actual loop body invariant')
    require(len(invariant.args) == 2, 'loop invariant AST shape changed')
    all_addresses = [node for node in nodes(func, 'AddressOf')
                     if hidden_address(node) is not None]
    inner_addresses = [node for node in nodes(invariant, 'AddressOf')
                       if hidden_address(node) is not None]
    require(len(all_addresses) == len(inner_addresses) == 14 and
            set(map(id, all_addresses)) == set(map(id, inner_addresses)) and
            all(hidden_address(node) in set(names.values()) for node in inner_addresses) and
            all(location_line(node.args[0]) == invariant_line for node in inner_addresses),
            'hidden stack addresses escape, retarget or are missing from the invariant')
    allowed_role_vars.extend(narg(address, 'AddressOf', 2)[1]
                             for address in inner_addresses)
    require(len(allowed_role_vars) == 27,
            'hidden role proof AST whitelist has an unexpected size')
    check_all_role_vars(func, names, allowed_role_vars)
    require(not [node for node in nodes(tree, 'CallExpr')
                 if call_name(node) == 'mir_stack_addr'],
            'untranslated mir_stack_addr remains in proof AST')
    expected = Counter({(names['range_input'], 'padding'): 1,
                        (names['range_result'], 'padding'): 1,
                        (names['merge_up_result'], 'padding'): 1,
                        (names['merge_down_result'], 'padding'): 1})
    for role in ('range_input', 'range_result'):
        expected[(names[role], 'start')] = 1
        expected[(names[role], 'end')] = 1
    for role in ('merge_up_result', 'merge_down_result'):
        for field in ('0', '1', '2'):
            expected[(names[role], field)] = 1
    observed = Counter()
    for call in nodes(invariant, 'CallExpr'):
        if call_name(call) not in ('std::ops::struct_Range_padding',
                                  'struct_std_tuple_3__padding'):
            continue
        args = narg(call, 'CallExpr', 6)
        pats = args[4]
        require(isinstance(pats, list) and len(pats) == 1,
                'padding predicate argument changed')
        address = narg(pats[0], 'LitPat', 1)[0]
        role = role_address(address, set(names.values()))
        require(role is not None, 'padding predicate lost hidden address')
        require(call_name(call) == ('std::ops::struct_Range_padding'
                                    if role in (names['range_input'], names['range_result'])
                                    else 'struct_std_tuple_3__padding'),
                'padding predicate targets wrong struct')
        tparams = args[2]
        require(isinstance(tparams, list), 'padding type arguments changed')
        if role in (names['range_input'], names['range_result']):
            require(len(tparams) == 1, 'Range padding type arity changed')
            check_usize_type(tparams[0])
        else:
            require(len(tparams) == 3, 'tuple padding type arity changed')
            for tparam in tparams:
                check_t_pointer_type(tparam)
        observed[(role, 'padding')] += 1
    for point in nodes(invariant, 'PointsTo'):
        args = narg(point, 'PointsTo', 4)
        selected = args[1]
        if not isinstance(selected, Node) or selected.name != 'Select':
            continue
        selection = narg(selected, 'Select', 3)
        deref = selection[1]
        if not isinstance(deref, Node) or deref.name != 'Deref':
            continue
        address = narg(deref, 'Deref', 2)[1]
        role = role_address(address, set(names.values()))
        if role is None:
            continue
        field = selection[2]
        require(field in ('start', 'end') if role in
                (names['range_input'], names['range_result']) else field in ('0', '1', '2'),
                'hidden stack field selector changed')
        require(args[2] == ('RegularPointsTo' if role in
                (names['range_input'], names['range_result']) else 'MaybeUninit'),
                'hidden stack points-to mode changed')
        observed[(role, field)] += 1
    require(observed == expected,
            f'invariant hidden stack field/padding mismatch: expected={expected}, observed={observed}')
    return {'function': 'bidirectional_merge', 'roles': roles,
            'addresses': len(inner_addresses), 'loop_invariant_line': invariant_line,
            'checked_calls': ['Range::into_iter', 'merge_up', 'merge_down']}


def negative_controls(tree, cert):
    func = only([n for n in nodes(tree, 'Func') if len(n.args) >= 5 and
                 n.args[4] == 'bidirectional_merge'], 'negative-control function')
    invariant = only([n for n in nodes(func, 'InvariantStmt') if
                      location_line(n.args[0]) == cert['loop_line'] + 1],
                     'negative-control invariant')
    roles = cert['roles']
    checked = []

    def rejected(label, owner, index, mutant):
        previous = owner[index]
        owner[index] = mutant
        try:
            try:
                validate(tree, cert)
            except AdmissionError:
                checked.append(label)
            else:
                raise AdmissionError(f'{label} negative control was admitted')
        finally:
            owner[index] = previous

    def rejected_insert(label, owner, index, mutant, expected_reason=None):
        owner.insert(index, mutant)
        try:
            try:
                validate(tree, cert)
            except AdmissionError as exc:
                require(expected_reason is None or expected_reason in str(exc),
                        f'{label} negative control failed at wrong gate: {exc}')
                checked.append(label)
            else:
                raise AdmissionError(f'{label} negative control was admitted')
        finally:
            owner.pop(index)

    addresses = [a for a in nodes(invariant, 'AddressOf')
                 if role_address(a, {f'$_{n}' for n in roles.values()}) is not None]
    first = only(addresses[:1], 'negative-control hidden address')
    target = narg(first, 'AddressOf', 2)[1]
    rejected('wrong_hidden_address', target.args, 1, '$_999999')
    ranges = [entry for decl in nodes(func, 'DeclStmt')
              for entry in narg(decl, 'DeclStmt', 2)[1]
              if isinstance(entry, tuple) and len(entry) == 5 and
              entry[2] == f"$_{roles['range_result']}"]
    range_type = narg(only(ranges, 'negative-control Range declaration')[1],
                      'Some', 1)[0]
    rejected('wrong_declared_struct', narg(range_type, 'StructTypeExpr', 5), 1,
             Node('Some', ['std_tuple_3_']))
    up = only([sw for sw in nodes(func, 'SwitchStmt') if
               isinstance(sw.args[1], Node) and sw.args[1].name == 'CallExpr' and
               call_name(sw.args[1]) == 'merge_up'], 'negative-control merge_up')
    up_statements = statement_list_containing(func, up)
    up_at = next(i for i, stmt in enumerate(up_statements) if stmt is up)
    extra_arg_write = copy.deepcopy(up_statements[up_at - 4])
    ordered_assignment(extra_arg_write)[3].args[1] = 'right'
    rejected_insert('overwritten_call_argument_temporary',
                    up_statements, up_at, extra_arg_write)
    extra_field_write = copy.deepcopy(up_statements[up_at + 1])
    narg(ordered_assignment(extra_field_write)[3], 'Select', 3)[2] = '1'
    rejected_insert('overwritten_tuple_field_temporary',
                    up_statements, up_at + 4, extra_field_write)
    extra_cursor_write = copy.deepcopy(up_statements[up_at + 9])
    ordered_assignment(extra_cursor_write)[3].args[1] = '$_999999'
    rejected_insert('overwritten_tuple_cursor',
                    up_statements, up_at + 10, extra_cursor_write)
    extra_role_read = copy.deepcopy(up_statements[up_at - 4])
    role_read_assign = ordered_assignment(extra_role_read)
    narg(role_read_assign[1], 'Var', 2)[1] = '$_999999'
    role_read_assign[3] = Node('Var', [role_read_assign[0],
                                       f"$_{roles['merge_up_result']}"])
    role_read_assign[0] = Node('loc', ['verified/lib.rs(1,1-2)'])
    rejected_insert('extra_hidden_role_read_other_line',
                    up_statements, up_at + 10, extra_role_read,
                    expected_reason='hidden role has an extra/missing proof AST variable')
    extra_role_write = copy.deepcopy(up_statements[up_at - 4])
    role_write_assign = ordered_assignment(extra_role_write)
    narg(role_write_assign[1], 'Var', 2)[1] = f"$_{roles['merge_down_result']}"
    role_write_assign[0] = Node('loc', ['verified/lib.rs(1,1-2)'])
    nested_write = Node('BlockStmt', [role_write_assign[0], [],
                                      [extra_role_write], role_write_assign[0],
                                      Node('ref', [[]])])
    rejected_insert('extra_nested_hidden_role_write_other_line',
                    up_statements, up_at + 10, nested_write,
                    expected_reason='hidden role has an extra/missing proof AST variable')
    rejected('wrong_call_source_span', up.args, 0,
             Node('loc', ['verified/lib.rs(1,1-2)']))
    clauses = narg(up, 'SwitchStmt', 3)[2]
    returning = only([cl for cl in clauses if call_name(cl.args[1]) == 'returning'],
                     'negative-control normal clause')
    normal = only(returning.args[2], 'negative-control normal assignment')
    normal_lhs = expr_stmt_assign(normal)[1]
    rejected('wrong_normal_destination', narg(normal_lhs, 'Var', 2), 1,
             f"$_{roles['range_result']}")
    unwinding = only([cl for cl in clauses if call_name(cl.args[1]) == 'unwinding'],
                     'negative-control unwind clause')
    rejected('unwind_clause_removed', narg(unwinding.args[1], 'CallExpr', 6), 1,
             'returning')
    tuple_name = f"$_{roles['merge_up_result']}"
    tuple_fields = [p.args[1] for p in nodes(invariant, 'PointsTo')
                    if isinstance(p.args[1], Node) and p.args[1].name == 'Select' and
                    isinstance(p.args[1].args[1], Node) and
                    p.args[1].args[1].name == 'Deref' and
                    role_address(p.args[1].args[1].args[1], {tuple_name}) == tuple_name and
                    p.args[1].args[2] == '0']
    field = only(tuple_fields, 'negative-control tuple field')
    rejected('wrong_tuple_field', narg(field, 'Select', 3), 2, '1')
    call_args = narg(up.args[1], 'CallExpr', 6)[4]
    first_arg = narg(call_args[0], 'LitPat', 1)[0]
    rejected('wrong_merge_argument', narg(first_arg, 'Var', 2), 1, '$_999999')
    range_name = f"$_{roles['range_input']}"
    endpoints = [a for a in nodes(func, 'AssignExpr')
                 if location_line(a.args[0]) == cert['loop_line'] and
                 isinstance(a.args[1], Node) and a.args[1].name == 'Select' and
                 a.args[1].args[2] == 'end' and
                 var(a.args[1].args[1]) == range_name]
    endpoint = only(endpoints, 'negative-control range endpoint')
    rejected('wrong_range_endpoint', narg(endpoint.args[3], 'Var', 2), 1,
             '$_999999')
    paddings = [c for c in nodes(invariant, 'CallExpr')
                if call_name(c) == 'std::ops::struct_Range_padding']
    padding = only(paddings[:1], 'negative-control Range padding')
    padding_type = narg(padding.args[2][0], 'ManifestTypeExpr', 2)[1]
    rejected('wrong_padding_type', narg(padding_type, 'Int', 2), 0,
             Sym('Signed'))
    rejected('wrong_padding_predicate', narg(padding, 'CallExpr', 6), 1,
             'struct_std_tuple_3__padding')
    extra_loc = Node('loc', [f"verified/lib.rs({cert['loop_line'] + 1},1-2)"])
    rogue = Node('AddressOf', [extra_loc, Node('Var', [extra_loc, '$_999999'])])
    old_invariant = invariant.args[1]
    rejected('extra_unknown_hidden_address', invariant.args, 1,
             Node('Sep', [extra_loc, old_invariant, Node('Operation', [
                 extra_loc, Sym('Eq'), [rogue, Node('Var', [extra_loc, 'dst'])]])]))
    tuple_points = [p for p in nodes(invariant, 'PointsTo')
                    if isinstance(p.args[1], Node) and p.args[1].name == 'Select' and
                    isinstance(p.args[1].args[1], Node) and
                    p.args[1].args[1].name == 'Deref' and
                    role_address(p.args[1].args[1].args[1], {tuple_name}) == tuple_name]
    point = only(tuple_points[:1], 'negative-control tuple points-to')
    rejected('wrong_field_mode', narg(point, 'PointsTo', 4), 2,
             'RegularPointsTo')
    require(len(checked) == 17, 'AST negative-control suite incomplete')
    return checked


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proof-ast', type=Path, required=True)
    p.add_argument('--roles', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and
            os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and
            os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and
            os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10',
            'proof AST admission requires the owned hosted branch')
    require(not args.output.exists(), 'proof AST certificate already exists')
    role_bytes = args.roles.read_bytes()
    cert = json.loads(role_bytes)
    require(cert['github_sha'] == os.environ.get('GITHUB_SHA') and
            cert['github_run_id'] == os.environ.get('GITHUB_RUN_ID') and
            hashlib.sha256(args.source.read_bytes()).hexdigest() == cert['source_sha256'],
            'proof AST inputs do not match final normal-MIR certificate')
    proof_bytes = args.proof_ast.read_bytes()
    tree = OcamlAstText(proof_bytes.decode('utf-8')).parse()
    result = validate(tree, cert)
    result['negative_controls'] = negative_controls(tree, cert)
    result.update({'status': 'AST_LINKED',
                   'github_sha': cert['github_sha'],
                   'github_run_id': cert['github_run_id'],
                   'source_sha256': cert['source_sha256'],
                   'normal_mir_sha256': cert['normal_mir_sha256'],
                   'normal_roles_sha256': hashlib.sha256(role_bytes).hexdigest(),
                   'proof_ast_sha256': hashlib.sha256(proof_bytes).hexdigest()})
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    try:
        main()
    except (AdmissionError, UnicodeDecodeError, OSError, ValueError, SyntaxError,
            KeyError, TypeError, IndexError, RecursionError) as exc:
        print(f'STACK_PROOF_AST_ADMISSION_REJECTED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
