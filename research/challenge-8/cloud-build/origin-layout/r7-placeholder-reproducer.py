#!/usr/bin/env python3
"""Small static source-coordinate reduction; no actual compiler/preparer/proof.

272 and 305 are exact decoded R7 Build2 source starts. Other coordinates below
are synthetic to distinguish preservation from silently omitting placeholders.
"""
from collections import Counter

old_start, explicit_start, cut = 272, 305, 1001
required = {old_start, explicit_start, cut}
before = [(explicit_start, 'block-start'), (cut, 'no-op')]
after = [(old_start, 'no-op'), (explicit_start, 'block-start'), (cut, 'no-op')]

def admitted(rows):
    counts = Counter(line for line, _ in rows)
    return (all(counts[line] == 1 for line in required) and
            [line for line, kind in rows if kind == 'block-start'] == [explicit_start])

assert required - {line for line, _ in before} == {old_start}
assert not admitted(before)
assert admitted(after)
assert not admitted(after + [(explicit_start, 'no-op')])
assert not admitted([row for row in after if row[0] != cut])
assert not admitted([(old_start, 'block-start'), (explicit_start, 'no-op'), (cut, 'no-op')])
print('Static coordinate reduction: old start missing before; preserved unique dispatch after; missing/duplicate/wrong binding start rejected. Not actual parser/proof evidence.')
