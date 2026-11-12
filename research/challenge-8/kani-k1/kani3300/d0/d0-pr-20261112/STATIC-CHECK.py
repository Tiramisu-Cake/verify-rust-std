#!/usr/bin/env python3
"""Source-only audit of field/variant preservation; executes no Rust tools."""
import re
import sys
from pathlib import Path

repo = Path(sys.argv[1])


def braced(text, start):
    opening = text.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[opening + 1:end - 1]


def entries(text):
    result, start, depth = [], 0, 0
    for pos, char in enumerate(text):
        if char in '{([<':
            depth += 1
        elif char in '})]>' and not (char == '>' and pos > 0 and text[pos - 1] == '='):
            depth -= 1
        elif char == ',' and depth == 0:
            if text[start:pos].strip():
                result.append(text[start:pos].strip())
            start = pos + 1
    if text[start:].strip():
        result.append(text[start:].strip())
    return result


def fields(text, declaration):
    return [item.split(':', 1)[0].removeprefix('pub ').strip() if declaration else item.strip()
            for item in entries(text)]


for rel, names in (
    ('kani-compiler/src/kani_middle/transform/body.rs',
     ('MutableBody', 'InsertPosition', 'SourceInstruction')),
    ('kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs',
     ('MemoryInitOp', 'InitRelevantInstruction')),
):
    source = re.sub(r'//[^\n]*', '', (repo / rel).read_text())
    assert 'derive(serde::Serialize)' not in source
    for name in names:
        match = re.search(r'pub (struct|enum) ' + name + r'\s*\{', source)
        declaration = braced(source, match.start())
        kind = match.group(1)
        invocation = source.index('::serialize_' + kind + '!(' + name)
        assert source[invocation - 100:invocation].rstrip().endswith('crate::kani_middle::d0_diagnostics')
        if kind == 'struct':
            expected = fields(declaration, True)
            observed = fields(braced(source, invocation), False)
            assert expected == observed, (name, expected, observed)
            print(name + ': all ' + str(len(expected)) + ' fields, original order')
        else:
            expected, observed = [], []
            for index, item in enumerate(entries(declaration)):
                variant = item.split('{', 1)[0].strip()
                expected.append((index, variant, fields(braced(item, 0), True) if '{' in item else []))
            for item in entries(braced(source, invocation)):
                index, tail = item.split('=>', 1)
                variant = tail.split('{', 1)[0].strip()
                observed.append((int(index), variant, fields(braced(tail, 0), False) if '{' in tail else []))
            assert expected == observed, (name, expected, observed)
            print(name + ': all ' + str(len(expected)) + ' variants, original indices/fields/order')
print('PASS: five field-only implementations retain the former derive data shape')
