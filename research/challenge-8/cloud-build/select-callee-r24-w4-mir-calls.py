#!/usr/bin/env python3
"""Pure, conservative extractor for the R24 W4 selector-call MIR records.

This reports typed structure in captured MIR text only. It does not bind the
record to parser input, source identity, proof execution, or theorem
applicability.
"""
from __future__ import annotations

import ast
import re
from typing import Any


SCHEMA = 'select-r24-w4-mir-calls-v1'
CALLEE = 'std::hint::select_unpredictable'
EXPECTED_CALLS = 8
EXPECTED_DEF_PATH = 'sort4_stable'
MAX_TEXT_CHARS = 8_000_000
MAX_TOKENS = 3_000_000
MAX_DEPTH = 256
MAX_NODES = 1_500_000


class MirParseError(ValueError):
    pass


def _fail(message: str) -> None:
    raise MirParseError(message)


def _decode_string(token: str) -> str:
    # Python's literal parser accepts unknown escapes with a warning. Capnp's
    # text format emits explicit escapes, so reject those before decoding.
    i = 1
    end = len(token) - 1
    while i < end:
        if token[i] != '\\':
            i += 1
            continue
        i += 1
        if i >= end:
            _fail('trailing string escape')
        ch = token[i]
        if ch in '\\"\'nrtb ':
            i += 1
        elif ch == 'x' and i + 2 < end and re.fullmatch(r'[0-9A-Fa-f]{2}', token[i + 1:i + 3]):
            i += 3
        elif ch == 'u' and i + 4 < end and re.fullmatch(r'[0-9A-Fa-f]{4}', token[i + 1:i + 5]):
            i += 5
        elif ch == 'U' and i + 8 < end and re.fullmatch(r'[0-9A-Fa-f]{8}', token[i + 1:i + 9]):
            i += 9
        elif ch.isdigit() and i + 2 < end and token[i:i + 3].isdigit():
            i += 3
        else:
            _fail('unsupported string escape')
    try:
        decoded = ast.literal_eval(token)
    except (SyntaxError, ValueError) as exc:
        raise MirParseError('invalid escaped string') from exc
    if not isinstance(decoded, str):
        _fail('quoted atom is not a string')
    return decoded


def _lex(text: str) -> list[str]:
    if not isinstance(text, str):
        _fail('record must be text')
    if len(text) == 0 or len(text) > MAX_TEXT_CHARS:
        _fail('record is empty or exceeds text budget')
    tokens: list[str] = []
    i, n = 0, len(text)
    delimiters = '()[],='
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in delimiters:
            tokens.append(ch)
            i += 1
        elif ch == '"':
            start = i
            i += 1
            escaped = False
            while i < n:
                current = text[i]
                if escaped:
                    escaped = False
                elif current == '\\':
                    escaped = True
                elif current == '"':
                    i += 1
                    break
                i += 1
            else:
                _fail('unterminated quoted string')
            token = text[start:i]
            _decode_string(token)
            tokens.append(token)
        else:
            start = i
            while i < n and not text[i].isspace() and text[i] not in delimiters:
                if text[i] == '"':
                    _fail('quote embedded in bare atom')
                i += 1
            if i == start:
                _fail('invalid token')
            tokens.append(text[start:i])
        if len(tokens) > MAX_TOKENS:
            _fail('record exceeds token budget')
    return tokens


def _parse_record(text: str) -> dict[str, Any]:
    tokens = _lex(text)
    index = 0
    nodes = 0

    def value(depth: int = 0) -> Any:
        nonlocal index, nodes
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            _fail('record exceeds structural budget')
        if index >= len(tokens):
            _fail('truncated value')
        head = tokens[index]
        index += 1
        if head == '(':
            fields: dict[str, Any] = {}
            while True:
                if index >= len(tokens):
                    _fail('unterminated record')
                if tokens[index] == ')':
                    index += 1
                    return fields
                key = tokens[index]
                index += 1
                if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', key) is None:
                    _fail('invalid record field name')
                if index >= len(tokens) or tokens[index] != '=':
                    _fail('missing field assignment')
                index += 1
                if key in fields:
                    _fail('duplicate field ' + key)
                fields[key] = value(depth + 1)
                if index >= len(tokens):
                    _fail('unterminated field list')
                if tokens[index] == ',':
                    index += 1
                elif tokens[index] != ')':
                    _fail('invalid record separator')
        if head == '[':
            items: list[Any] = []
            while True:
                if index >= len(tokens):
                    _fail('unterminated list')
                if tokens[index] == ']':
                    index += 1
                    return items
                items.append(value(depth + 1))
                if index >= len(tokens):
                    _fail('unterminated list item')
                if tokens[index] == ',':
                    index += 1
                elif tokens[index] != ']':
                    _fail('invalid list separator')
        if head in (')', ']', ',', '='):
            _fail('unexpected structural token')
        if head.startswith('"'):
            return _decode_string(head)
        if head == 'true':
            return True
        if head == 'false':
            return False
        if re.fullmatch(r'-?[0-9]+', head):
            return int(head)
        return head

    result = value()
    if index != len(tokens) or not isinstance(result, dict):
        _fail('expected one complete function record')
    return result


def _variant(value: Any, key: str) -> Any:
    if not isinstance(value, dict) or len(value) != 1 or key not in value:
        _fail('unexpected ' + key + ' variant shape')
    return value[key]


def _string_variant(value: Any, key: str, expected: str | None = None) -> str:
    inner = _variant(value, key)
    if not isinstance(inner, str) or (expected is not None and inner != expected):
        _fail('unexpected ' + key + ' value')
    return inner


def _type_node(raw: Any) -> Any:
    return _variant(raw, 'kind')


def _const_ptr_t(raw: Any) -> bool:
    try:
        pointer = _type_node(raw)['rawPtr']
        if not isinstance(pointer, dict) or set(pointer) != {'ty', 'mutability'}:
            return False
        pointee = _type_node(pointer['ty'])
        return (pointee == {'param': 'T'} and
                _variant(pointer['mutability'], 'not') == 'void')
    except (KeyError, TypeError, MirParseError):
        return False


def _source_point(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != {'file', 'line', 'col'}:
        _fail('source point is not a record')
    file_record = raw['file']
    if not isinstance(file_record, dict) or set(file_record) != {'name'}:
        _fail('unexpected source file shape')
    name_record = file_record['name']
    if not isinstance(name_record, dict) or set(name_record) != {'real'}:
        _fail('unexpected source file name shape')
    real_record = name_record['real']
    if not isinstance(real_record, dict) or set(real_record) != {'localPath'}:
        _fail('unexpected source path shape')
    file = real_record['localPath']
    line = raw['line']
    pos = raw['col']['pos']
    if (not isinstance(file, str) or type(line) is not int or line < 1 or
            type(pos) is not int or pos < 0):
        _fail('invalid emitted source point')
    return {'path': file, 'line': line, 'column_pos': pos}


def _span(raw: Any) -> dict[str, Any]:
    regular = _variant(raw, 'regular')
    if not isinstance(regular, dict) or set(regular) != {'lo', 'hi'}:
        _fail('unexpected source span shape')
    return {'lo': _source_point(regular['lo']), 'hi': _source_point(regular['hi'])}


def _source_info(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != {'span'}:
        _fail('unexpected sourceInfo shape')
    return {'span': _span(raw['span'])}


def _ghost_generic_arg_list(raw: Any) -> Any:
    """Validate the optional Cap'n Proto Option(Annotation) field."""
    if not isinstance(raw, dict) or len(raw) != 1:
        _fail('ghostGenericArgList is not an Option variant')
    if 'nothing' in raw:
        if raw['nothing'] != 'void':
            _fail('ghostGenericArgList nothing payload is not void')
        return raw
    if 'something' not in raw:
        _fail('unknown ghostGenericArgList option variant')
    annotation = raw['something']
    if not isinstance(annotation, dict) or set(annotation) != {
            'raw', 'span', 'startLine', 'startCol', 'endLine', 'endCol'}:
        _fail('ghostGenericArgList annotation shape differs')
    if not isinstance(annotation['raw'], str):
        _fail('ghostGenericArgList annotation text is malformed')
    _span(annotation['span'])
    for field in ('startLine', 'startCol', 'endLine', 'endCol'):
        if type(annotation[field]) is not int or annotation[field] < 0:
            _fail('ghostGenericArgList annotation coordinate is malformed')
    return raw


def _local_name(raw: Any, *, require_mutable: bool = True) -> str:
    if not isinstance(raw, dict) or set(raw) != {
            'local', 'projection', 'localIsMutable', 'kind'}:
        _fail('operand local is not a record')
    local = raw['local']
    if not isinstance(local, dict) or set(local) != {'name'}:
        _fail('unexpected operand local shape')
    name = local['name']
    if not isinstance(name, str):
        _fail('operand local identifier is not text')
    if raw.get('projection') != []:
        _fail('operand local is projected')
    if type(raw.get('localIsMutable')) is not bool:
        _fail('operand local mutability observation missing')
    if require_mutable and raw['localIsMutable'] is not True:
        _fail('move operand local is not marked mutable')
    _variant(raw['kind'], 'other')
    return name


def _move_local(raw: Any) -> str:
    return _local_name(_variant(raw, 'move'))


def _local_index(body: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = body.get('localDecls')
    if not isinstance(rows, list) or not rows:
        _fail('missing localDecls')
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
                'mutability', 'id', 'ty', 'sourceInfo'}:
            _fail('malformed local declaration')
        name = _string_variant(row['id'], 'name')
        if name in result:
            _fail('duplicate local declaration ' + name)
        result[name] = row
    return result


def _local_type(locals_by_name: dict[str, dict[str, Any]], name: str) -> Any:
    if name not in locals_by_name:
        _fail('operand refers to undeclared local ' + name)
    return locals_by_name[name]['ty']


def _selector_call(fn: dict[str, Any]) -> bool:
    # Only a structural FnDef name counts. Other raw mentions are not calls.
    try:
        ty = _type_node(fn['constant']['const']['ty'])
        definition = ty['fnDef']
        return _string_variant(definition['id'], 'name') == CALLEE
    except (KeyError, TypeError, MirParseError):
        return False


def _call_candidates(body: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]:
    blocks = body.get('basicBlocks')
    if not isinstance(blocks, list) or not blocks:
        _fail('missing basicBlocks')
    found: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for block in blocks:
        if not isinstance(block, dict) or set(block) != {
                'id', 'statements', 'terminator', 'isCleanup'}:
            _fail('malformed basic block')
        if not isinstance(block['statements'], list) or type(block['isCleanup']) is not bool:
            _fail('malformed basic block contents')
        terminator = block.get('terminator')
        if not isinstance(terminator, dict) or set(terminator) != {'sourceInfo', 'kind'}:
            _fail('missing block terminator')
        kind = terminator.get('kind')
        if not isinstance(kind, dict) or len(kind) != 1:
            _fail('unknown terminator variant')
        call = kind.get('call')
        if call is None:
            continue
        call_fields = {'func', 'args', 'destination', 'callSpan', 'target', 'unwindAction'}
        if not isinstance(call, dict) or frozenset(call) not in {
                frozenset(call_fields), frozenset(call_fields | {'ghostGenericArgList'})}:
            _fail('malformed call terminator')
        if 'ghostGenericArgList' in call:
            _ghost_generic_arg_list(call['ghostGenericArgList'])
        func = call.get('func')
        if not isinstance(func, dict):
            _fail('call has no func record')
        if _selector_call(func):
            found.append((block, terminator, call))
    return found


def _target_string_count(value: Any) -> int:
    count = 0
    if value == CALLEE and isinstance(value, str):
        count += 1
    elif isinstance(value, dict):
        for child in value.values():
            count += _target_string_count(child)
    elif isinstance(value, list):
        for child in value:
            count += _target_string_count(child)
    return count


def _extract_one(text: str) -> dict[str, Any]:
    body = _parse_record(text)
    if body.get('defPath') != EXPECTED_DEF_PATH:
        _fail('function defPath is not the exact sort4_stable target')
    locals_by_name = _local_index(body)
    calls = _call_candidates(body)
    target_strings = _target_string_count(body)
    if target_strings != EXPECTED_CALLS or len(calls) != EXPECTED_CALLS:
        _fail('selector target/call count is not exactly eight')
    rows = []
    for ordinal, (block, terminator, call) in enumerate(calls):
        ghost_generic_arg_list = call.get('ghostGenericArgList', {'nothing': 'void'})
        ghost_generic_args = _variant(ghost_generic_arg_list, 'nothing')
        if ghost_generic_args != 'void':
            _fail('selector call has nonempty/malformed ghost generic arguments')
        fn = call['func']['constant']['const']['ty']['kind']['fnDef']
        if set(fn) != {'id', 'substs', 'lateBoundGenericParamCount'}:
            _fail('selector FnDef shape differs')
        callee = _string_variant(fn['id'], 'name', CALLEE)
        substitutions = fn['substs']
        if (not isinstance(substitutions, list) or len(substitutions) != 1 or
                not isinstance(substitutions[0], dict) or
                set(substitutions[0]) != {'kind'} or
                not isinstance(substitutions[0]['kind'], dict) or
                set(substitutions[0]['kind']) != {'type'} or
                not _const_ptr_t(substitutions[0]['kind']['type'])):
            _fail('selector substitution is not exactly *const T')
        if type(fn['lateBoundGenericParamCount']) is not int or \
                fn['lateBoundGenericParamCount'] != 0:
            _fail('selector has unexpected late-bound generic parameters')
        args = call.get('args')
        if not isinstance(args, list) or len(args) != 3:
            _fail('selector does not have exactly three operands')
        names = [_move_local(arg) for arg in args]
        bool_type = _local_type(locals_by_name, names[0])
        if _type_node(bool_type) != {'bool': 'void'}:
            _fail('selector first operand local is not bool')
        pointer_types = [_local_type(locals_by_name, name) for name in names[1:]]
        if not all(_const_ptr_t(ty) for ty in pointer_types):
            _fail('selector pointer operands are not both *const T')
        destination = call.get('destination')
        dest_name = _local_name(destination, require_mutable=False)
        dest_type = _local_type(locals_by_name, dest_name)
        if not _const_ptr_t(dest_type):
            _fail('selector destination local is not *const T')
        target = _variant(call['target'], 'something')
        if (not isinstance(target, dict) or set(target) != {'index'} or
                type(target['index']) is not int or target['index'] < 0):
            _fail('selector call has an unknown/malformed normal target')
        unwind_action = call['unwindAction']
        if (not isinstance(unwind_action, dict) or len(unwind_action) != 1 or
                next(iter(unwind_action)) not in {'continue', 'unreachable', 'terminate'}):
            _fail('selector call has an unknown/malformed unwind action')
        call_span = _span(call['callSpan'])
        terminator_source = _source_info(terminator['sourceInfo'])
        related_locals = [locals_by_name[name] for name in [*names, dest_name]]
        local_sources = []
        for local in related_locals:
            source_info = _source_info(local['sourceInfo'])
            local_sources.append({'local_id': _string_variant(local['id'], 'name'),
                                  'type': local['ty'],
                                  'source_info': source_info})
        block_id = _variant(block['id'], 'index')
        if type(block_id) is not int or block_id < 0:
            _fail('invalid basic-block index')
        rows.append({
            'ordinal': ordinal,
            'block_index': block_id,
            'def_path': body['defPath'],
            'callee': callee,
            'raw_callee': call['func'],
            'fn_def': fn,
            'ghost_generic_arg_list': ghost_generic_arg_list,
            'substitution_types': substitutions,
            'late_bound_generic_param_count': 0,
            'operand_local_ids': names,
            'operand_types': [bool_type, *pointer_types],
            'operand_records': args,
            'operand_local_sources': local_sources[:3],
            'destination_local_id': dest_name,
            'destination_type': dest_type,
            'destination_record': destination,
            'destination_local_source': local_sources[3],
            'call_span': call_span,
            'terminator_source_info': terminator_source,
            'target': call['target'],
            'unwind_action': unwind_action,
        })
    return {'def_path': body['defPath'], 'calls': rows}


def _typed_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return (row['callee'], row['substitution_types'], row['late_bound_generic_param_count'],
            row['operand_types'], row['destination_type'])


def analyze_pair(normal_text: str, readonly_text: str) -> dict[str, Any]:
    """Return typed observations, retaining UNKNOWN on every parse/shape gap."""
    base: dict[str, Any] = {
        'schema': SCHEMA,
        'scope': 'TYPED_MIR_OBSERVATION_ONLY',
        'source_parser_input_binding': 'NOT_ESTABLISHED',
        'proof_claim': False,
        'accepted': False,
        'proof_credit': 0,
        'publication_allowed': False,
        'complete': False,
        'status': 'INCOMPLETE_UNKNOWN',
        'typed_call_linkage': 'UNKNOWN',
        'typed_callee_family_observation': 'UNKNOWN',
        'source_site_mapping': 'UNKNOWN',
        'normal': None,
        'readonly': None,
        'errors': [],
    }
    try:
        normal = _extract_one(normal_text)
        readonly = _extract_one(readonly_text)
        if normal['def_path'] != readonly['def_path']:
            _fail('normal/readonly function defPath differs')
        if [_typed_signature(row) for row in normal['calls']] != \
                [_typed_signature(row) for row in readonly['calls']]:
            _fail('ordered normal/readonly typed selector signatures differ')
        if [row['call_span'] for row in normal['calls']] == \
                [row['call_span'] for row in readonly['calls']]:
            mapping = 'EQUAL_EMITTED_COORDINATES_ONLY'
        else:
            _fail('normal/readonly selector call spans differ')
        base.update({
            'complete': True,
            'status': 'COMPLETE_TYPED_MIR_OBSERVATION',
            'typed_call_linkage': 'UNKNOWN',
            'typed_callee_family_observation': 'OBSERVED_STRUCTURAL_MIR_CALLS',
            'source_site_mapping': mapping,
            'normal': normal,
            'readonly': readonly,
            'errors': [],
        })
    except (MirParseError, KeyError, TypeError, IndexError, RecursionError) as exc:
        base['errors'] = [str(exc) or type(exc).__name__]
    return base
