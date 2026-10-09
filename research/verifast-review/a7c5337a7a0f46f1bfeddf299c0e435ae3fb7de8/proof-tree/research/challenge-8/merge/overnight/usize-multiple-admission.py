#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted source/alpha-renaming certificate; does not prove the std primitive."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / 'library/core/src/num/uint_macros.rs'
BLOB = '558763a41c013bcda43c4a64ec3c01e6a9f54229'
FILE_SHA = '18f5398756410bddf13b918dbb8e821a3207817497ceb89874660a7bbc80b885'
BODY_SHA = '67d3897787b9eb698ef9485939e36a378c56a63034c3d833f05f4b3d1837b56b'
SIGNATURE = 'pub const fn is_multiple_of(self, rhs: Self) -> bool'
ADAPTER_SIGNATURE = 'pub fn repo_usize_is_multiple_of(value: usize, rhs: usize) -> bool'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def body(text: str, signature: str) -> str:
    if text.count(signature) != 1:
        raise ValueError('missing or ambiguous exact function signature')
    start = text.index('{', text.index(signature) + len(signature))
    depth = 0
    for end in range(start, len(text)):
        if text[end] == '{':
            depth += 1
        elif text[end] == '}':
            depth -= 1
            if depth == 0:
                return text[start:end + 1]
    raise ValueError('unclosed exact source body')


def strip_ghost(text: str) -> str:
    text = re.sub(r'(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)', '', text)
    return re.sub(r'/\*@.*?@\*/', '', text, flags=re.S)


def normalized(text: str) -> str:
    return re.sub(r'\s+', '', text)


def validate(source: bytes, adapter: str) -> dict:
    if digest(source) != FILE_SHA:
        raise ValueError('repository source file pin mismatch')
    exact_body = body(source.decode(), SIGNATURE)
    if digest(exact_body.encode()) != BODY_SHA:
        raise ValueError('repository source body pin mismatch')
    actual_adapter = body(strip_ghost(adapter), ADAPTER_SIGNATURE)
    expected_adapter = re.sub(r'\bself\b', 'value', exact_body)
    if normalized(actual_adapter) != normalized(expected_adapter):
        raise ValueError('adapter differs beyond the declared alpha-renaming/whitespace mapping')
    return {'source_body_sha256': BODY_SHA,
            'adapter_body_sha256': digest(actual_adapter.encode()),
            'alpha_renaming': {'self': 'value', 'Self': 'usize'},
            'normalized_body_sha256': digest(normalized(expected_adapter).encode()),
            'trust': 'std primitive summary is TRUSTED; separately checked adapter body and lexical source relation'}


def main() -> None:
    if (os.environ.get('GITHUB_ACTIONS') != 'true' or
            os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted' or
            os.environ.get('GITHUB_REF') != 'refs/heads/overnight/merge-26.10'):
        raise RuntimeError('source admission requires own GitHub-hosted branch')
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError('refusing existing admission output')
    actual_blob = subprocess.check_output(
        ['git', '-C', str(ROOT), 'rev-parse', 'HEAD:library/core/src/num/uint_macros.rs'], text=True).strip()
    if actual_blob != BLOB:
        raise RuntimeError('repository Git blob mismatch')
    source = SOURCE.read_bytes()
    adapter = (HERE / 'usize-multiple-cases.rs').read_text()
    record = validate(source, adapter)
    controls = {}
    mutations = {
        'zero_answer_changed': adapter.replace('0 => value == 0,', '0 => value != 0,', 1),
        'modulo_answer_changed': adapter.replace('_ => value % rhs == 0,', '_ => value % rhs != 0,', 1),
        'divisor_changed': adapter.replace('_ => value % rhs == 0,', '_ => value % 2 == 0,', 1),
        'signature_changed': adapter.replace(ADAPTER_SIGNATURE, ADAPTER_SIGNATURE.replace('usize', 'u32', 1), 1),
        'duplicate_adapter': adapter + '\n' + strip_ghost(adapter).split('// CASE_BEGIN', 1)[0],
    }
    for name, mutation in mutations.items():
        try:
            validate(source, mutation)
        except ValueError:
            controls[name] = True
        else:
            controls[name] = False
    try:
        validate(source.replace(b'0 => self == 0,', b'0 => self != 0,', 1), adapter)
    except ValueError:
        controls['source_body_mutation'] = True
    else:
        controls['source_body_mutation'] = False
    if not all(controls.values()):
        raise RuntimeError(f'fail-closed admission control failed: {controls}')
    record.update(source_blob=BLOB, source_file_sha256=FILE_SHA,
                  fixture_sha256=digest(adapter.encode()),
                  actions_sha=os.environ['GITHUB_SHA'], classification='SOURCE_ADAPTER_CERTIFICATE',
                  fail_closed_controls=controls)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + '\n')
    print('usize source/adapter admission PASS (primitive remains explicitly trusted)')


if __name__ == '__main__':
    main()
