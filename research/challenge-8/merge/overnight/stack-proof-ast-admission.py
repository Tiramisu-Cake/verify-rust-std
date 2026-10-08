#!/usr/bin/env python3
"""Hosted, fail-closed linkage of final normal-MIR roles to VeriFast proof AST.

This checks observable syntax and identity only. It grants no memory permission
and cannot replace VeriFast, refinement, leak/dead-code, or source-integrity gates.
"""

from __future__ import annotations

import argparse
import ast
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
    return call


def check_extracts(func, role_name, call_line, wanted):
    seeds = {}
    edges = {}
    for assign in nodes(func, 'AssignExpr'):
        args = narg(assign, 'AssignExpr', 4)
        if location_line(args[0]) != call_line or not isinstance(args[1], Node) or args[1].name != 'Var':
            continue
        lhs = var(args[1])
        rhs = args[3]
        if isinstance(rhs, Node) and rhs.name == 'Select':
            selector = narg(rhs, 'Select', 3)
            if isinstance(selector[1], Node) and selector[1].name == 'Var' and var(selector[1]) == role_name:
                field = selector[2]
                require(field in ('0', '1', '2') and field not in seeds,
                        'tuple result extraction field duplicate/changed')
                seeds[field] = lhs
        elif isinstance(rhs, Node) and rhs.name == 'Var':
            edges.setdefault(var(rhs), set()).add(lhs)
    require(set(seeds) == {'0', '1', '2'},
            f'{role_name} tuple result is not destructured through three fields')
    for index, target in enumerate(wanted):
        pending = [seeds[str(index)]]
        reached = set()
        while pending:
            current = pending.pop()
            if current not in reached:
                reached.add(current)
                pending.extend(edges.get(current, ()))
        require(target in reached and not (set(wanted) - {target}) & reached,
                f'{role_name} field {index} does not reach unique {target}')


def check_merge_inputs(func, call, line, expected):
    actual = narg(call, 'CallExpr', 6)[4]
    require(isinstance(actual, list) and len(actual) == 4,
            'merge call argument arity changed')
    arguments = [var(narg(item, 'LitPat', 1)[0]) for item in actual]
    require(len(set(arguments)) == 4, 'merge call arguments alias unexpectedly')
    assignments = [a for a in nodes(func, 'AssignExpr')
                   if location_line(a.args[0]) == line and
                   isinstance(a.args[1], Node) and a.args[1].name == 'Var']
    for argument, source in zip(arguments[:3], expected):
        copies = [a for a in assignments if var(a.args[1]) == argument and
                  isinstance(a.args[3], Node) and a.args[3].name == 'Var' and
                  var(a.args[3]) == source]
        only(copies, f'merge input {argument} from {source}')
    callbacks = [a for a in assignments if var(a.args[1]) == arguments[3] and
                 isinstance(a.args[3], Node) and a.args[3].name == 'AddressOf' and
                 isinstance(a.args[3].args[1], Node) and
                 a.args[3].args[1].name == 'Deref' and
                 var(a.args[3].args[1].args[1]) == 'is_less']
    only(callbacks, 'merge callback input from is_less')


def check_range_constructor(func, identifier, line):
    builds = {}
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
    return builds


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
        call = check_switch(sw, callee, names[role],
                            cert['role_details'][role]['declaration_span'])
        require(location_line(sw.args[0]) == line, f'{callee} line changed')
        check_merge_inputs(func, call, line,
                           ('left', 'right', 'dst_1') if callee == 'merge_up'
                           else ('left_rev', 'right_rev', 'dst_rev'))
    check_extracts(func, names['merge_up_result'], cert['merge_up_line'],
                   ('left', 'right', 'dst_1'))
    check_extracts(func, names['merge_down_result'], cert['merge_down_line'],
                   ('left_rev', 'right_rev', 'dst_rev'))

    range_calls = [sw for sw in switches if call_name(sw.args[1]).endswith('::into_iter')
                   and 'Range<usize>' in call_name(sw.args[1])]
    range_sw = only(range_calls, 'Range into_iter switch')
    range_call = check_switch(range_sw, call_name(range_sw.args[1]),
                              names['range_result'],
                              cert['role_details']['range_result']['declaration_span'])
    arguments = range_call.args[4]
    require(isinstance(arguments, list) and len(arguments) == 1 and
            var(narg(arguments[0], 'LitPat', 1)[0]) == names['range_input'],
            'Range into_iter argument is not range_input')
    loop_line = cert['loop_line']
    iter_moves = [a for a in nodes(func, 'AssignExpr')
                  if location_line(a.args[0]) == loop_line and
                  isinstance(a.args[1], Node) and a.args[1].name == 'Var' and
                  isinstance(a.args[3], Node) and a.args[3].name == 'Var' and
                  var(a.args[1]) == 'iter' and var(a.args[3]) == names['range_result']]
    only(iter_moves, 'Range result move to iter')
    check_range_constructor(func, names['range_input'], loop_line)

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
    require(len(checked) == 12, 'AST negative-control suite incomplete')
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
