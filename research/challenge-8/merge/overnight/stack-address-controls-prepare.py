#!/usr/bin/env python3
"""Hosted two-pass normal-MIR ID admission for isolated stack-address controls.

This prepares diagnostic fixture text and certificates. It does not verify a
function or grant a permission. The ordinary hosted pointer-prove runner must
subsequently classify each final frontend rejection at its exact location.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / 'stack-address-control-templates.rs'
ADMISSION = HERE / 'stack-address-admission.py'
CASE = re.compile(rb'(?m)^// CASE_BEGIN ([a-z0-9_]+)\r?\n(.*?)^// CASE_END \1\r?\n', re.S)
NAMES = ('stack_address_named_range', 'stack_address_named_tuple',
         'stack_address_hidden_scalar')
PLACEHOLDER = b'999999'


class PrepareError(Exception):
    pass


def need(ok, message):
    if not ok:
        raise PrepareError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_decoder():
    spec = importlib.util.spec_from_file_location('stack_address_admission', ADMISSION)
    need(spec is not None and spec.loader is not None, 'normal-MIR parser unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def raw_name(place):
    need(isinstance(place, dict) and place.get('projection') == [],
         'candidate MIR place is projected')
    name = place['local']['name']
    need(isinstance(name, str) and re.fullmatch(r'_[0-9]+', name) is not None,
         'candidate MIR local name malformed')
    return name


def usize(ty):
    return ty == {'kind': {'uInt': {'uSize': None}}}


def tuple3_usize(ty):
    kinds = ty.get('kind', {}).get('tuple') if isinstance(ty, dict) else None
    return isinstance(kinds, list) and len(kinds) == 3 and all(usize(t) for t in kinds)


def identity(body, identifier):
    decls = body['localDecls']
    index = int(identifier[1:])
    need(index < len(decls) and decls[index]['id']['name'] == identifier,
         'candidate raw ID/declaration index mismatch')
    need(index > len(body['inputs']), 'candidate is return place or parameter')
    need(sum(d['id']['name'] == identifier for d in decls) == 1,
         'candidate raw declaration is duplicated')
    return decls[index]


def alias_map(body):
    aliases = {}
    for entry in body['varDebugInfo']:
        value = entry['value']
        if 'place' in value and value['place']['projection'] == []:
            aliases.setdefault(raw_name(value['place']), []).append(entry['name']['name'])
    return aliases


def candidate(decoded, source: bytes, name: str, common):
    tree = common.CapnpText(decoded.decode('utf-8')).parse()
    bodies = tree['bodies']
    matches = [b for b in bodies if b['defPath'] == name]
    need(len(matches) == 1, f'{name}: expected one decoded function body')
    body = matches[0]
    need(body['defKind'] == {'fn': None} and len(body['inputs']) == 1,
         f'{name}: function kind/parameter count changed')
    aliases = alias_map(body)
    lines = source.decode('utf-8').splitlines()
    target_lines = [(i + 1, line) for i, line in enumerate(lines)
                    if line.lstrip().startswith('//@ assert mir_stack_addr(')]
    need(len(target_lines) == 1 and target_lines[0][1].count('mir_stack_addr(') == 2,
         f'{name}: exactly two markers on one ghost assertion required')
    need('// TARGET' in target_lines[0][1], f'{name}: target line missing')

    if name in ('stack_address_named_range', 'stack_address_named_tuple'):
        source_name = ('named_range' if name.endswith('_range') else 'named_tuple')
        ids = [identifier for identifier, labels in aliases.items()
               if labels.count(source_name) == 1]
        need(len(ids) == 1, f'{name}: named source VDI local is ambiguous')
        identifier = ids[0]
        need(aliases[identifier] == [source_name],
             f'{name}: named local has extra VDI aliases')
        decl = identity(body, identifier)
        ty = decl['ty']
        need((common.type_is_range(ty) if name.endswith('_range')
              else tuple3_usize(ty)), f'{name}: named local has wrong struct type')
        location = decl['sourceInfo']['span']['regular']
        _, line = common.span_text(decl['sourceInfo']['span'], lines)
        expected_line = ('let named_range = 0..n;' if name.endswith('_range')
                         else 'let named_tuple = (n, n, n);')
        need(lines[line - 1].strip() == expected_line and line < target_lines[0][0],
             f'{name}: VDI local has wrong source construct')
        role = 'source_named_struct'
    else:
        need(name == 'stack_address_hidden_scalar', 'unknown scalar control')
        additions = []
        for block in body['basicBlocks']:
            for stmt_index, stmt in enumerate(block['statements']):
                assign = stmt['kind'].get('assign')
                if assign is None:
                    continue
                op = assign['rhsRvalue'].get('binaryOp')
                if op is None or op.get('operator') != {'add': None}:
                    continue
                left = op['operandl']
                right = op['operandr']
                need('copy' in left or 'move' in left,
                     f'{name}: addition left operand is not a local')
                left_place = left.get('copy', left.get('move'))
                left_id = raw_name(left_place)
                if left_id != '_1':
                    # Normal MIR materializes `n` in a hidden scalar before
                    # Add. Admit only its unique same-block earlier copy of
                    # the parameter; do not guess its compiler-generated ID.
                    definitions = [(i, s) for i, s in enumerate(block['statements'])
                                   if s['kind'].get('assign') is not None and
                                   raw_name(s['kind']['assign']['lhsPlace']) == left_id]
                    need(len(definitions) == 1 and definitions[0][0] < stmt_index,
                         f'{name}: Add input lacks a unique preceding definition')
                    need(sum(1 for b in body['basicBlocks'] for s in b['statements']
                             if s['kind'].get('assign') is not None and
                             raw_name(s['kind']['assign']['lhsPlace']) == left_id) == 1,
                         f'{name}: parameter-copy temporary is reassigned')
                    copied = definitions[0][1]
                    use = copied['kind']['assign']['rhsRvalue'].get('use', {})
                    need(set(use) == {'copy'} and raw_name(use['copy']) == '_1' and
                         usize(identity(body, left_id)['ty']) and left_id not in aliases,
                         f'{name}: Add input is not a hidden copy of the parameter')
                    copied_span, copied_line = common.span_text(copied['sourceInfo']['span'], lines)
                    add_span, add_line = common.span_text(stmt['sourceInfo']['span'], lines)
                    need(copied_span == 'n' and copied_line == add_line and add_span == 'n + 1',
                         f'{name}: parameter-copy/Add source correspondence changed')
                constant = right.get('constant', {}).get('const', {}).get('val', {})
                integer = constant.get('constValue', {}).get('scalar', {}).get('int', {})
                need(integer.get('data') == {'h': 0, 'l': 1} and integer.get('size') == 8,
                     f'{name}: addition no longer uses usize literal one')
                identifier = raw_name(assign['lhsPlace'])
                decl = identity(body, identifier)
                need(usize(decl['ty']) and identifier not in aliases,
                     f'{name}: addition destination is not a hidden usize scalar')
                span, line = common.span_text(stmt['sourceInfo']['span'], lines)
                need(span == 'n + 1' and line < target_lines[0][0],
                     f'{name}: addition source span changed')
                additions.append((identifier, decl))
        need(len(additions) == 1,
             f'{name}: hidden usize Add destination is ambiguous ({len(additions)})')
        identifier, decl = additions[0]
        location = decl['sourceInfo']['span']['regular']
        role = 'hidden_usize_add_destination'
    need(identifier not in ('_0', '_1'), f'{name}: forbidden candidate ID')
    return {'case': name, 'role': role, 'raw_id': identifier,
            'id': int(identifier[1:]), 'raw_type': decl['ty'],
            'vdi_names': aliases.get(identifier, []),
            'declaration_span': location, 'target_line': target_lines[0][0]}


def capture(case_dir: Path, stage: str, source: bytes, args, deadline: float, common):
    case_dir.mkdir(parents=True, exist_ok=False)
    verified = case_dir / 'verified/lib.rs'
    verified.parent.mkdir()
    verified.write_bytes(source)
    command = [str(args.tool_home / 'bin/vf-rust-mir-exporter'),
               'verified/lib.rs', f'--sysroot={args.compiler_sysroot}',
               '--edition', '2021']

    def run(label, cmd, stdin=None):
        remaining = deadline - time.monotonic()
        need(remaining > 0, 'two-pass preparation exceeded total hosted deadline')
        result = subprocess.run(cmd, cwd=case_dir, input=stdin, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=min(args.stage_seconds, remaining), check=False)
        (case_dir / f'{label}.out').write_bytes(result.stdout)
        (case_dir / f'{label}.log').write_bytes(result.stderr)
        need(result.returncode == 0, f'{stage}: {label} exited {result.returncode}')
        need(verified.read_bytes() == source, f'{stage}: exporter changed source on disk')
        return result.stdout

    mir = run('normal-exporter', command)
    decoded = run('normal-decode', ['capnp', 'decode', str(args.schema), 'VfMir'], mir)
    result = {'normal_preprocess': True, 'command': command,
              'source_sha256': sha(source), 'source_unchanged': True,
              'mir_sha256': sha(mir), 'decoded_sha256': sha(decoded)}
    (case_dir / 'normal-exporter-provenance.json').write_text(
        json.dumps(result, indent=2, sort_keys=True) + '\n')
    return decoded, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-home', type=Path, required=True)
    parser.add_argument('--compiler-sysroot', required=True)
    parser.add_argument('--schema', type=Path, required=True)
    parser.add_argument('--fixture', type=Path, default=TEMPLATE)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--stage-seconds', type=int, default=20)
    parser.add_argument('--total-seconds', type=int, default=60)
    args = parser.parse_args()
    args.tool_home = args.tool_home.resolve()
    args.schema = args.schema.resolve()
    args.fixture = args.fixture.resolve()
    args.output_dir = args.output_dir.resolve()
    need(os.environ.get('GITHUB_ACTIONS') == 'true' and
         os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and
         os.environ.get('RUNNER_OS') == 'Linux' and
         os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and
         os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10' and
         re.fullmatch(r'[0-9a-f]{40}', os.environ.get('GITHUB_SHA', '')) and
         os.environ.get('GITHUB_RUN_ID'), 'requires owned GitHub-hosted run')
    need(1 <= args.stage_seconds <= 20 and 1 <= args.total_seconds <= 60,
         'hosted preparation limits exceed 20/60 seconds')
    need(args.tool_home.joinpath('bin/vf-rust-mir-exporter').is_file() and
         args.schema.is_file(), 'pinned exporter or schema missing')
    need(not args.output_dir.exists(), 'control preparation output already exists')
    raw = args.fixture.read_bytes()
    matches = list(CASE.finditer(raw))
    need(tuple(m.group(1).decode('ascii') for m in matches) == NAMES,
         'control template cases/order changed')
    prefix = raw[:matches[0].start()]
    need(b'mir_stack_addr' not in prefix and
         raw[matches[-1].end():].strip() == b'',
         'control template has unexpected shared or trailing body')
    for match in matches:
        body = match.group(2)
        need(body.count(PLACEHOLDER) == 3 and
             # Two ghost expressions and one ordinary oracle-message quote.
             body.count(b'mir_stack_addr(999999)') == 3 and
             body.count(b'// TARGET') == 1 and
             body.count(b'// EXPECT_REJECTION ') == 1,
             'control template marker/oracle count changed')
    common = load_decoder()
    args.output_dir.mkdir(parents=True)
    deadline = time.monotonic() + args.total_seconds
    final_chunks = [prefix]
    certificates = []
    for match in matches:
        name = match.group(1).decode('ascii')
        body = match.group(2)
        discovery = prefix + body
        case_dir = args.output_dir / name
        decoded, first_prov = capture(case_dir / 'discovery', 'discovery',
                                      discovery, args, deadline, common)
        first = candidate(decoded, discovery, name, common)
        final_body = body.replace(PLACEHOLDER, str(first['id']).encode('ascii'))
        final_source = prefix + final_body
        final_decoded, final_prov = capture(case_dir / 'final', 'final',
                                            final_source, args, deadline, common)
        final = candidate(final_decoded, final_source, name, common)
        for key in ('case', 'role', 'raw_id', 'id', 'raw_type', 'vdi_names',
                    'declaration_span', 'target_line'):
            need(first[key] == final[key], f'{name}: final normal-MIR role drifted at {key}')
        need(final_source.count(b'mir_stack_addr(' + str(final['id']).encode() + b')') == 3 and
             b'mir_stack_addr(999999)' not in final_source,
             f'{name}: final marker ID does not match normal MIR')
        certificate = {'case': name, 'github_sha': os.environ['GITHUB_SHA'],
                       'github_run_id': os.environ['GITHUB_RUN_ID'],
                       'discovery': first, 'final': final,
                       'discovery_provenance': first_prov,
                       'final_provenance': final_prov,
                       'status': 'ROLE_STABLE_NOT_YET_VERIFIED'}
        (case_dir / 'role-certificate.json').write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + '\n')
        certificates.append(certificate)
        final_chunks.extend((b'// CASE_BEGIN ' + name.encode() + b'\n', final_body,
                             b'// CASE_END ' + name.encode() + b'\n'))
    prepared = b''.join(final_chunks)
    # The runner's CASE extraction must reproduce each already re-exported
    # final `verified/lib.rs` byte-for-byte.
    prepared_cases = list(CASE.finditer(prepared))
    need(len(prepared_cases) == len(NAMES), 'prepared fixture extraction changed')
    for match, cert in zip(prepared_cases, certificates):
        expected = (args.output_dir / cert['case'] / 'final/verified/lib.rs').read_bytes()
        need(prepared[:prepared_cases[0].start()] + match.group(2) == expected,
             f"{cert['case']}: runner extraction differs from final normal MIR")
    (args.output_dir / 'stack-address-control-cases.rs').write_bytes(prepared)
    (args.output_dir / 'admission.json').write_text(json.dumps({
        'status': 'ROLE_STABLE_NOT_YET_VERIFIED',
        'github_sha': os.environ['GITHUB_SHA'],
        'github_run_id': os.environ['GITHUB_RUN_ID'],
        'fixture_sha256': sha(prepared),
        'cases': {item['case']: item['final'] for item in certificates},
    }, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    try:
        main()
    except (PrepareError, OSError, ValueError, KeyError, TypeError, IndexError,
            UnicodeDecodeError, subprocess.TimeoutExpired) as exc:
        print(f'STACK_ADDRESS_CONTROL_PREPARATION_REJECTED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
