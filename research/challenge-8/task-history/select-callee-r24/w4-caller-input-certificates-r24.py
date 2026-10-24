#!/usr/bin/env python3
"""Static authoring of the closed W4 source-only input table; no admission."""
from __future__ import annotations
import hashlib
import json
import re

INPUTS_SHA256 = '1bc11197642bc057b6c7558777e56b6f8c04f0108d4115119193d7bb2f5ec8ea'
SCHEMA = 'select-r24-w4-source-input-universe-v1'
TRANSLATOR_SHA256 = '1276f006b5dd757a9dc9fbf87e4d9491758c24f71ba5dc409f0c08720a528a13'
BINARY_SHA256 = 'ee6758eafcae52664b33c523e34df0376fcb3253f0461713c8559406e8ce4a2a'

def rows(raw: bytes) -> list[tuple[str, str, str, str]]:
    if hashlib.sha256(raw).hexdigest() != INPUTS_SHA256:
        raise ValueError('exact source-only input universe required')
    obj = json.loads(raw)
    if (obj.get('schema') != SCHEMA or obj.get('assurance') != 'SOURCE_REPORTED' or
        obj.get('classification') != 'COMPLETE_SOURCE_ONLY_INPUT_UNIVERSE' or
        obj.get('complete') is not True or obj.get('input_universe_complete') is not True or
        type(obj.get('universe_count')) is not int or obj['universe_count'] != 37 or
        any(obj.get(key) is not False for key in ('body_proof_run', 'callee_qualification',
             'caller_body_proof_admission', 'accepted', 'publication_allowed')) or
        type(obj.get('proof_credit')) is not int or obj['proof_credit'] != 0 or
        obj.get('control_validator_outcomes') != 'UNKNOWN' or
        obj.get('typed_call_linkage') != 'UNKNOWN'):
        raise ValueError('input universe must remain data-only')
    pins = obj.get('tool_hashes')
    if (type(pins) is not dict or len(pins) != 9 or
        pins.get('bin/verifast') != BINARY_SHA256 or
        pins.get('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml') != TRANSLATOR_SHA256):
        raise ValueError('data tool identity differs')
    result = []
    entries = obj.get('rows')
    if type(entries) is not list or len(entries) != 37:
        raise ValueError('exactly37 input rows required')
    for index, row in enumerate(entries):
        if (type(row) is not dict or type(row.get('index')) is not int or row['index'] != index or
            type(row.get('variant')) is not str or
            re.fullmatch(r'[a-z0-9-]+', row['variant']) is None):
            raise ValueError('ordered closed input row differs')
        digests = []
        for field in ('source', 'unit', 'body'):
            item = row.get(field)
            if (type(item) is not dict or type(item.get('bytes')) is not int or item['bytes'] <= 0 or
                type(item.get('sha256')) is not str or
                re.fullmatch('[0-9a-f]{64}', item['sha256']) is None):
                raise ValueError('input fingerprint malformed')
            path = item.get('path')
            if type(path) is not str or (field == 'source' and not path.endswith(
                '/variants/' + row['variant'] + '/fixture/verified/lib.rs')) or (
                field == 'unit' and path != 'caller-native-unit.marshal') or (
                field == 'body' and path != 'caller-native-body-0.marshal'):
                raise ValueError('input path differs')
            digests.append(item['sha256'])
        result.append((row['variant'], *digests))
    if result[0][0] != 'positive' or len({row[0] for row in result}) != 37:
        raise ValueError('closed case names differ')
    return result

def ocaml_module(raw: bytes) -> str:
    entries = rows(raw)
    rendered = ';\n'.join('    (' + json.dumps(name) + ', (' + ', '.join(
        json.dumps(value) for value in fingerprints) + '))' for name, *fingerprints in entries)
    return '''  (* Closed source-only capture table. A matching input is NOT proof or
     callee qualification and does not activate the dormant caller route. *)
  module Sort4R24W4InputCertificates = struct
    let source_only = true
    let rows = [
''' + rendered + '''
    ]
    let find case = List.assoc_opt case rows
  end

'''
