#!/usr/bin/env python3
"""Hosted-only origin certificate for the actual SmallSort panic macro body.

This is a log classification gate, not a verifier or a source transformation.
It cannot make a failed VeriFast run successful or grant a function summary.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ORIGINAL = REPO / 'library/core/src/slice/sort/shared/smallsort.rs'
ORIGINAL_SHA256 = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
ORIGINAL_BLOB = '40939f922bcb6fdc7ee0d30427fa861827043827'
BODY_SHA256 = '2732f3532a1d8796efc7d9b16221bdc1820d1a9e42a4e0de92d426a33a583e5f'
SIGNATURE = 'fn panic_on_ord_violation() -> ! {'
MESSAGE = 'user-provided comparison function does not correctly implement a total order'
FROM_STR = "std::fmt::Arguments::<'a>::from_str"
PANIC_MIR = 'core::panicking::panic_fmt'
PANIC_AST = 'std::panicking::panic_fmt'
TOOLCHAIN = 'nightly-2026-09-25-x86_64-unknown-linux-gnu'


class Rejected(Exception):
    pass


def need(ok, reason):
    if not ok:
        raise Rejected(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    need(spec is not None and spec.loader is not None, f'missing {filename}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MIR = load('panic_admission_mir', 'stack-address-admission.py')
AST = load('panic_admission_ast', 'stack-proof-ast-admission.py')


def one(items, description):
    need(len(items) == 1, f'expected one {description}; found {len(items)}')
    return items[0]


def extract(text, signature=SIGNATURE):
    need(text.count(signature) == 1, 'actual helper signature changed or ambiguous')
    start = text.index(signature)
    end = text.find('\n}\n', start)
    need(end >= 0, 'actual helper closing brace missing')
    return text[start:end + 2]


def strip_ghost(text):
    text = re.sub(r'(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)', '', text)
    return re.sub(r'/\*@.*?@\*/', '', text, flags=re.S)


def source_gate(source):
    original = ORIGINAL.read_bytes()
    need(sha(original) == ORIGINAL_SHA256, 'repository SmallSort source SHA changed')
    blob = hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest()
    need(blob == ORIGINAL_BLOB, 'repository SmallSort Git blob changed')
    body = extract(original.decode('utf-8'))
    need(sha(body.encode()) == BODY_SHA256, 'actual helper body SHA changed')
    checked = extract(source.decode('utf-8'), SIGNATURE[:-1])
    need(strip_ghost(checked) == body, 'verified helper runtime body changed')
    need(checked.count('panic!("' + MESSAGE + '");') == 1,
         'actual macro invocation changed')
    lines = source.decode('utf-8').splitlines()
    line = one([n for n, text in enumerate(lines, 1)
                if 'panic!("' + MESSAGE + '");' in text], 'checked panic invocation')
    need(lines[line - 1].strip() == 'panic!("' + MESSAGE + '");',
         'checked panic invocation is not the whole statement')
    return lines, line


def span(span):
    regular = MIR.path(span, 'regular')
    lo, hi = MIR.path(regular, 'lo'), MIR.path(regular, 'hi')
    path_lo = MIR.path(lo, 'file', 'name', 'real', 'localPath')
    path_hi = MIR.path(hi, 'file', 'name', 'real', 'localPath')
    need(path_lo == path_hi and isinstance(path_lo, str), 'call span crosses files')
    l1, l2 = MIR.path(lo, 'line'), MIR.path(hi, 'line')
    c1, c2 = MIR.path(lo, 'col', 'pos'), MIR.path(hi, 'col', 'pos')
    need(all(type(x) is int for x in (l1, l2, c1, c2)) and
         l1 > 0 and l2 >= l1 and c1 >= 0 and c2 >= 0,
         'invalid call span coordinates')
    return path_lo, l1, c1, l2, c2


def ast_loc(file, line, lo, end_line, hi):
    need(line == end_line, 'multi-line macro span is not admitted')
    return f'{file}({line},{lo + 1}-{hi + 1})'


def compiler_hash_gate(actual, expected):
    need(re.fullmatch(r'[0-9a-f]{64}', expected) is not None,
         'expected compiler panic.rs SHA-256 is not a lowercase digest')
    need(actual == expected, 'compiler panic.rs bytes differ from expected SHA-256')


def sysroot_gate(sysroot, spans, expected_sha=None):
    need(sysroot.name == TOOLCHAIN and sysroot.is_dir(), 'compiler sysroot version changed')
    panic_path = (sysroot / 'lib/rustlib/src/rust/library/core/src/panic.rs').resolve(strict=True)
    need(panic_path.is_file(), 'compiler panic.rs missing')
    content = panic_path.read_bytes()
    text = content.decode('utf-8')
    lines = text.splitlines()
    need(all(Path(file).resolve(strict=True) == panic_path for file, *_ in spans),
         'macro span is outside this compiler sysroot panic.rs')
    need(all(l1 == l2 == 61 and 0 <= c1 < c2 <= len(lines[60])
             for _, l1, c1, l2, c2 in spans),
         'macro span moved outside pinned panic.rs line 61')
    # The span is from the compiler's panic! macro implementation.  Its exact
    # bytes are recorded below; a toolchain update changes the admitted origin.
    need('pub macro panic_2021' in '\n'.join(lines[:61]) and
         'panic_fmt' in lines[60] and 'const_format_args!' in lines[60],
         'compiler panic macro callsite shape changed')
    need(spans[0][1:] == (61, 37, 61, 71) and
         spans[1][1:] == (61, 8, 61, 72),
         'pinned from_str/panic_fmt macro columns changed')
    actual_sha = sha(content)
    if expected_sha is not None:
        compiler_hash_gate(actual_sha, expected_sha)
    return str(panic_path), actual_sha


def normal_gate(root, source_lines, call_line, sysroot):
    bodies = MIR.path(root, 'bodies')
    need(isinstance(bodies, list), 'normal MIR bodies are not a list')
    body = one([b for b in bodies if MIR.path(b, 'defPath') ==
                'panic_on_ord_violation'], 'normal MIR panic helper')
    need(MIR.path(body, 'defKind') == {'fn': None} and
         MIR.path(body, 'inputs') == [], 'actual helper signature changed in normal MIR')
    signature_line = one([i for i, text in enumerate(source_lines, 1)
                          if text.startswith('fn panic_on_ord_violation() -> ! ')],
                         'checked helper signature line')
    need(span(MIR.path(body, 'span')) ==
         ('verified/lib.rs', signature_line, 0, call_line + 1, 1),
         'normal MIR body is not the exact checked helper')
    annotations = [MIR.path(a, 'raw') for a in MIR.path(body, 'contract', 'annotations')]
    need(annotations == ['/*@\nreq thread_token(?t);\n@*/',
                         '/*@\nens false;\n@*/',
                         '/*@\non_unwind_ens thread_token(t);\n@*/'],
         'normal/unwind helper contract changed')
    blocks = MIR.path(body, 'basicBlocks')
    need(isinstance(blocks, list) and len(blocks) == 2 and
         [MIR.path(b, 'id', 'index') for b in blocks] == [0, 1] and
         all(MIR.path(b, 'isCleanup') is False for b in blocks),
         'panic helper control flow changed')
    calls = [MIR.path(b, 'terminator', 'kind', 'call') for b in blocks]
    need([MIR.call_name(c) for c in calls] == [FROM_STR, PANIC_MIR],
         'panic macro MIR calls changed')
    need(all(MIR.path(c, 'unwindAction') == {'continue': None} for c in calls),
         'panic macro MIR unwind edge changed')
    need(MIR.path(calls[0], 'target') == {'something': {'index': 1}} and
         'target' not in calls[1], 'panic macro MIR normal edges changed')
    need(MIR.local(MIR.path(calls[0], 'destination')) == '_3' and
         MIR.local(MIR.path(calls[1], 'destination')) == '_2' and
         len(MIR.path(calls[0], 'args')) == len(MIR.path(calls[1], 'args')) == 1 and
         MIR.operand_local(MIR.path(calls[1], 'args')[0]) == '_3',
         'panic macro MIR argument/destination chain changed')
    literal = MIR.path(calls[0], 'args')[0]['constant']
    need(MIR.path(literal, 'const', 'val', 'constValue', 'slice') == MESSAGE,
         'panic literal changed in normal MIR')
    lit_span = span(MIR.path(literal, 'span'))
    need(lit_span[0] == 'verified/lib.rs' and lit_span[1] == lit_span[3] == call_line and
         source_lines[call_line - 1][lit_span[2]:lit_span[4]] == '"' + MESSAGE + '"',
         'panic literal no longer originates at actual macro argument')
    spans = [span(MIR.path(c, 'callSpan')) for c in calls]
    path, panic_sha = sysroot_gate(sysroot, spans)
    need(all(span(MIR.path(blocks[i], 'terminator', 'sourceInfo', 'span')) == spans[i]
             for i in range(2)), 'MIR terminator and call spans disagree')
    need([MIR.path(s, 'kind') for s in MIR.path(blocks[0], 'statements')] ==
         [{'storageLive': {'name': '_2'}}, {'storageLive': {'name': '_3'}}] and
         MIR.path(blocks[1], 'statements') == [],
         'panic helper MIR statements changed')
    return body, spans, path, panic_sha, lit_span


def ast_gate(tree, spans, lit_span):
    functions = [f for f in AST.nodes(tree, 'Func') if len(f.args) >= 11 and
                 f.args[4] == 'panic_on_ord_violation' and
                 isinstance(f.args[10], AST.Node) and f.args[10].name == 'Some']
    func = one(functions, 'actual proof AST panic body')
    need(func.args[5] == [] and func.args[6] == AST.Sym('false'),
         'proof AST panic signature changed')
    contract = AST.narg(func.args[8], 'Some', 1)[0]
    need(isinstance(contract, tuple) and len(contract) == 2,
         'proof AST panic contract malformed')
    pre, post = contract
    need(AST.call_name(pre) == 'thread_token' and
         len(pre.args[4]) == 1 and
         AST.narg(pre.args[4][0], 'VarPat', 2)[1] == 't',
         'panic precondition changed')
    need(isinstance(post, tuple) and len(post) == 2 and post[0] == 'outcome',
         'panic postcondition is not outcome-indexed')
    clauses = AST.narg(post[1], 'SwitchExpr', 4)[2]
    need(isinstance(clauses, list) and len(clauses) == 2,
         'panic normal/unwind post clauses changed')
    by_outcome = {AST.narg(c, 'SwitchExprClause', 4)[1]:
                  AST.narg(c, 'SwitchExprClause', 4)[3] for c in clauses}
    unwind_post = by_outcome.get('unwinding')
    need(set(by_outcome) == {'returning', 'unwinding'} and
         AST.narg(by_outcome['returning'], 'False', 1) is not None and
         AST.call_name(unwind_post) == 'thread_token' and
         len(unwind_post.args[4]) == 1 and
         AST.var(AST.narg(unwind_post.args[4][0], 'LitPat', 1)[0]) == 't',
         'panic full normal/unwind posts changed')
    body = AST.narg(func.args[10], 'Some', 1)[0]
    need(isinstance(body, tuple) and len(body) == 2 and
         isinstance(body[0], list), 'panic proof AST body malformed')
    statements = body[0]
    need(len(statements) == 8 and
         [s.name for s in statements] ==
         ['DeclStmt'] * 4 + ['LabelStmt', 'SwitchStmt', 'ExprStmt', 'ReturnStmt'],
         'panic proof AST statement path changed')
    decls = [AST.narg(s, 'DeclStmt', 2)[1] for s in statements[:4]]
    need(all(isinstance(d, list) and len(d) == 1 for d in decls) and
         [d[0][2] for d in decls] == ['$_0', '$_1', '$_2', '$_3'],
         'panic proof AST local declarations changed')
    need(AST.narg(statements[4], 'LabelStmt', 2)[1] == '0',
         'panic proof AST entry label changed')
    sw = AST.narg(statements[5], 'SwitchStmt', 3)
    from_loc = ast_loc(*spans[0])
    panic_loc = ast_loc(*spans[1])
    need(AST.loc(sw[0]) == from_loc and
         AST.call_name(sw[1]) == FROM_STR and AST.loc(sw[1].args[0]) == from_loc,
         'proof AST from_str call/span changed')
    args = AST.narg(sw[1], 'CallExpr', 6)[4]
    need(isinstance(args, list) and len(args) == 1, 'proof AST literal arity changed')
    string_lit = AST.narg(AST.narg(args[0], 'LitPat', 1)[0], 'StringLit', 2)
    need(string_lit[1] == MESSAGE and
         AST.loc(string_lit[0]) == ast_loc(*lit_span),
         'proof AST literal/source argument changed')
    clauses = sw[2]
    need(isinstance(clauses, list) and len(clauses) == 2,
         'proof AST from_str outcomes changed')
    by_name = {AST.call_name(AST.narg(c, 'SwitchStmtClause', 3)[1]):
               AST.narg(c, 'SwitchStmtClause', 3)[2] for c in clauses}
    need(set(by_name) == {'returning', 'unwinding'},
         'proof AST from_str outcome set changed')
    normal = AST.narg(one(by_name['returning'], 'from_str normal assignment'), 'ExprStmt', 1)[0]
    assignment = AST.narg(normal, 'AssignExpr', 4)
    need(AST.var(assignment[1]) == '$_3' and
         assignment[2] == AST.Sym('Mutation') and
         AST.var(assignment[3]) == '__result',
         'proof AST from_str result not assigned to panic_fmt argument')
    nested = AST.narg(one(by_name['unwinding'], 'from_str unwind return'), 'ReturnStmt', 2)
    need(AST.call_name(AST.narg(nested[1], 'Some', 1)[0]) == 'unwinding',
         'proof AST from_str unwind return suppressed')
    panic_call = AST.narg(statements[6], 'ExprStmt', 1)[0]
    need(AST.call_name(panic_call) == PANIC_AST and
         AST.loc(panic_call.args[0]) == panic_loc and
         len(panic_call.args[4]) == 1 and
         AST.var(AST.narg(panic_call.args[4][0], 'LitPat', 1)[0]) == '$_3',
         'proof AST panic_fmt call/argument/span changed')
    ret = AST.narg(statements[7], 'ReturnStmt', 2)
    need(AST.loc(ret[0]) == panic_loc and
         AST.call_name(AST.narg(ret[1], 'Some', 1)[0]) == 'unwinding',
         'proof AST panic_fmt unwind return suppressed')
    return {'normal_post': 'false', 'unwind_post': 'thread_token(t)',
            'calls': [FROM_STR, PANIC_AST], 'return': 'unwinding'}


LOG_EVENT = re.compile(r'^\s*[0-9]+(?:\.[0-9]+)?s: (.*?): (.*?)\s*$')
LOG_HEADER = re.compile(r"Verifying function '([^']+)'$")


def log_gate(log, source_lines, path, spans):
    lines = log.splitlines()
    sections = [(i, LOG_HEADER.search(line).group(1)) for i, line in enumerate(lines)
                if LOG_HEADER.search(line)]
    start = one([i for i, name in sections if name == 'panic_on_ord_violation'],
                'panic verification section')
    end = min((i for i, _ in sections if i > start), default=len(lines))
    need(start < end, 'panic verification section empty')
    signature_line = one([i for i, text in enumerate(source_lines, 1)
                          if text.startswith('fn panic_on_ord_violation() -> ! ')],
                         'checked helper signature line')
    header = re.search(rf'verified/lib\.rs\({signature_line},1-([0-9]+),2\): '
                       r"Verifying function 'panic_on_ord_violation'$", lines[start])
    need(header is not None, 'panic log header is not the actual checked helper')
    closing_line = int(header.group(1))
    need(closing_line > signature_line and closing_line <= len(source_lines) and
         source_lines[closing_line - 1] == '}',
         'panic log header closing line changed')
    events = []
    for line in lines[start + 1:end]:
        match = LOG_EVENT.fullmatch(line)
        if match:
            events.append(match.groups())
    macro_locs = [ast_loc(*item) for item in spans]
    macro_events = [(location, action) for location, action in events
                    if location.startswith(str(Path(path).parent))]
    need(macro_events == [
        (macro_locs[0], 'Executing statement'),
        (macro_locs[0], 'Verifying call'),
        (macro_locs[0], 'Executing statement'),
        (macro_locs[1], 'Executing statement'),
        (macro_locs[1], 'Verifying call'),
        (macro_locs[1], 'Executing return statement')],
         'panic macro body call/return log events changed')
    first_macro = events.index(macro_events[0])
    last_macro = events.index(macro_events[-1])
    need(first_macro < last_macro and
         all(action != 'Verifying call' for _, action in events[:first_macro]),
         'panic body log contains an unbound earlier call')
    tail = events[last_macro + 1:]
    need([action for _, action in tail if action in
          ('Freeing locals.', 'Cleaning up dummy fraction chunks and empty chunks',
           'Leak check.')] ==
         ['Freeing locals.', 'Cleaning up dummy fraction chunks and empty chunks',
          'Leak check.'] and
         not any(action in ('Verifying call', 'Executing return statement')
                 for _, action in tail),
         'panic helper unwind cleanup/leak check missing or reordered')
    need(all(location == f'verified/lib.rs({closing_line},1-2)' for location, action in tail
             if action in ('Freeing locals.', 'Cleaning up dummy fraction chunks and empty chunks',
                           'Leak check.')),
         'panic helper leak check does not belong to checked source')
    return {'body_execution_records': 3,
            'verified_macro_calls': 2,
            'unwind_return_records': 1,
            'leak_check_records': 1,
            'macro_log_events': macro_events}


def provenance_gate(provenance, source_sha, mir_sha, decoded_sha, sysroot):
    need(MIR.provenance_ok(provenance, source_sha, mir_sha, decoded_sha),
         'normal exporter provenance hashes/hosted run disagree')
    command = provenance.get('command')
    need(isinstance(command, list) and len(command) == 5 and
         Path(command[0]).name == 'vf-rust-mir-exporter' and
         command[1:] == ['verified/lib.rs', '--sysroot=' + str(sysroot),
                         '--edition', '2021'] and
         provenance.get('normal_preprocess') is True,
         'normal exporter command is not exact same-args preprocessing')


def negative_controls(decoded, tree, log, source_lines, line, sysroot, spans,
                      path, panic_sha, provenance, hashes):
    checked = []
    def reject(label, attempt):
        try:
            attempt()
        except (Rejected, MIR.AdmissionError, AST.AdmissionError,
                ValueError, KeyError, TypeError, IndexError):
            checked.append(label)
        else:
            raise Rejected(f'{label} negative control was admitted')

    def altered_mir(edit):
        mutant = copy.deepcopy(decoded)
        body = one([b for b in mutant['bodies'] if b['defPath'] ==
                    'panic_on_ord_violation'], 'mutant helper')
        edit(body)
        normal_gate(mutant, source_lines, line, sysroot)

    def call(body, index):
        return body['basicBlocks'][index]['terminator']['kind']['call']

    reject('wrong_owner', lambda: altered_mir(
        lambda b: b.__setitem__('defPath', 'other_helper')))
    reject('wrong_literal', lambda: altered_mir(
        lambda b: call(b, 0)['args'][0]['constant']['const']['val']
        ['constValue'].__setitem__('slice', 'different panic message')))
    reject('wrong_unwind_edge', lambda: altered_mir(
        lambda b: call(b, 1).__setitem__('unwindAction', {'unreachable': None})))
    reject('wrong_macro_span', lambda: altered_mir(
        lambda b: call(b, 0)['callSpan']['regular']['lo']['col']
        .__setitem__('pos', 1)))
    reject('duplicate_owner', lambda: normal_gate(
        {**decoded, 'bodies': decoded['bodies'] +
         [copy.deepcopy(one([b for b in decoded['bodies'] if b['defPath'] ==
                             'panic_on_ord_violation'], 'helper'))]},
        source_lines, line, sysroot))
    reject('wrong_source_hash', lambda: provenance_gate(
        {**provenance, 'source_sha256': '0' * 64}, *hashes, sysroot))
    reject('wrong_compiler_version', lambda: sysroot_gate(
        sysroot.with_name('nightly-wrong'), spans))
    reject('wrong_compiler_path', lambda: sysroot_gate(
        sysroot, [(str(ORIGINAL), *spans[0][1:]), spans[1]]))
    reject('wrong_compiler_source_hash', lambda: compiler_hash_gate(
        panic_sha, ('0' if panic_sha[0] != '0' else '1') + panic_sha[1:]))
    reject('missing_macro_call_log', lambda: log_gate(
        log.replace(f'{ast_loc(*spans[1])}: Verifying call',
                    f'{ast_loc(*spans[1])}: Initializing local'),
        source_lines, path, spans))
    reject('missing_unwind_return_log', lambda: log_gate(
        log.replace(f'{ast_loc(*spans[1])}: Executing return statement',
                    f'{ast_loc(*spans[1])}: Initializing local'),
        source_lines, path, spans))
    reject('initializers_only_log', lambda: log_gate(
        '\n'.join(x for x in log.splitlines()
                  if not x.startswith(str(path)) and
                  'panic.rs(' not in x), source_lines, path, spans))
    reject('ast_return_suppressed', lambda: ast_gate(
        mutate_ast_return(tree), spans,
        span_from_literal(decoded)))
    need(len(checked) == 13, 'panic negative-control suite incomplete')
    return checked


def span_from_literal(decoded):
    body = one([b for b in decoded['bodies'] if b['defPath'] ==
                'panic_on_ord_violation'], 'literal helper')
    call = body['basicBlocks'][0]['terminator']['kind']['call']
    return span(call['args'][0]['constant']['span'])


def mutate_ast_return(tree):
    mutant = copy.deepcopy(tree)
    func = one([f for f in AST.nodes(mutant, 'Func') if len(f.args) >= 11 and
                f.args[4] == 'panic_on_ord_violation' and
                isinstance(f.args[10], AST.Node) and f.args[10].name == 'Some'],
               'mutant AST helper')
    statements = AST.narg(func.args[10], 'Some', 1)[0][0]
    ret = AST.narg(statements[-1], 'ReturnStmt', 2)[1]
    AST.narg(ret, 'Some', 1)[0].args[1] = 'returning'
    return mutant


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('normal-decoded', 'normal-mir', 'proof-ast', 'source',
                   'provenance', 'compiler-sysroot', 'verifast-log', 'output'):
        parser.add_argument('--' + option, type=Path, required=True)
    parser.add_argument('--expected-compiler-panic-sha256')
    parser.add_argument('--require-final', action='store_true')
    args = parser.parse_args()
    need(os.environ.get('GITHUB_ACTIONS') == 'true' and
         os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and
         os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and
         os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10' and
         re.fullmatch(r'[0-9a-f]{40}', os.environ.get('GITHUB_SHA', '')) and
         os.environ.get('GITHUB_RUN_ID', '').isdigit(),
         'panic origin admission requires exact owned GitHub hosted run')
    need(not args.output.exists(), 'panic origin certificate already exists')
    need(not args.require_final or args.expected_compiler_panic_sha256 is not None,
         'final panic origin admission requires a pinned compiler source SHA-256')
    source = args.source.read_bytes()
    source_lines, call_line = source_gate(source)
    mir_bytes = args.normal_mir.read_bytes()
    decoded_bytes = args.normal_decoded.read_bytes()
    proof_bytes = args.proof_ast.read_bytes()
    log_bytes = args.verifast_log.read_bytes()
    provenance = json.loads(args.provenance.read_text(encoding='utf-8'))
    root = MIR.CapnpText(decoded_bytes.decode('utf-8')).parse()
    tree = AST.OcamlAstText(proof_bytes.decode('utf-8')).parse()
    sysroot = args.compiler_sysroot.resolve(strict=True)
    hashes = (sha(source), sha(mir_bytes), sha(decoded_bytes))
    provenance_gate(provenance, *hashes, sysroot)
    _, spans, panic_path, panic_sha, lit_span = normal_gate(
        root, source_lines, call_line, sysroot)
    if args.expected_compiler_panic_sha256 is not None:
        compiler_hash_gate(panic_sha, args.expected_compiler_panic_sha256)
    ast_result = ast_gate(tree, spans, lit_span)
    log = log_bytes.decode('utf-8')
    log_result = log_gate(log, source_lines, panic_path, spans)
    controls = negative_controls(root, tree, log, source_lines, call_line,
                                 sysroot, spans, panic_path, panic_sha,
                                 provenance, hashes)
    result = {'status': ('PANIC_MACRO_BODY_ORIGIN_LINKED'
                         if args.require_final else 'CALIBRATION'),
              'require_final': args.require_final,
              'function': 'panic_on_ord_violation',
              'github_sha': os.environ['GITHUB_SHA'],
              'github_run_id': os.environ['GITHUB_RUN_ID'],
              'source_sha256': hashes[0], 'normal_mir_sha256': hashes[1],
              'normal_decoded_sha256': hashes[2],
              'proof_ast_sha256': sha(proof_bytes),
              'verifast_log_sha256': sha(log_bytes),
              'original_source_sha256': ORIGINAL_SHA256,
              'original_source_git_blob': ORIGINAL_BLOB,
              'original_helper_body_sha256': BODY_SHA256,
              'compiler_panic_rs': panic_path,
              'compiler_panic_rs_sha256': panic_sha,
              'expected_compiler_panic_rs_sha256': args.expected_compiler_panic_sha256,
              'macro_spans': [ast_loc(*s) for s in spans],
              'ast': ast_result, 'log': log_result,
              'body_execution_records': log_result['body_execution_records'],
              'negative_controls': controls}
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    try:
        main()
    except (Rejected, MIR.AdmissionError, AST.AdmissionError,
            UnicodeDecodeError, OSError, ValueError, TypeError, KeyError,
            IndexError, RecursionError, AttributeError) as exc:
        print(f'PANIC_MACRO_ADMISSION_REJECTED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
