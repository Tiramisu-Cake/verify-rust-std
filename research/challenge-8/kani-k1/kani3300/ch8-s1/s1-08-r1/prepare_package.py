#!/usr/bin/env python3
"""Rebuild S1-08 frozen metadata from pinned Git source and historical receipt.
No compiler, verifier, evidence archive reader, network or CI operations.
"""
import argparse
import difflib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
STD_BASE = '5be85699b8826e3286c0bf89efb9affefac0acb5'
STD = '99e8456d200fff1299ee5756279cddb23921dc65'
CONTROL_BASE = '9208b373c0a08a265fa0d7493a6529e331065271'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
PREFIX = 'library/core/src/slice/sort/shared/smallsort/verify/'
FILES = {'sorting_entry_smoke.rs': {'smoke': 8, 'smoke_exact_n': 8},
         'sorting_model_controls.rs': {'positive': 7}}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True)


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def line_map(old, new):
    out = {}
    for tag, a, b, c, d in difflib.SequenceMatcher(None, old.splitlines(), new.splitlines(), autojunk=False).get_opcodes():
        if tag == 'equal':
            out.update({i+1: c+i-a+1 for i in range(a,b)})
    return out


def prepare(control, std_repo):
    spec = importlib.util.spec_from_file_location('s108', control/'ch8-s1-control/s108_package.py')
    lib = importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
    h = control/'ch8-s1-control'
    import sys
    sys.path.insert(0,str(h))
    import oracle_source
    old_request = json.loads(git(control, 'show', CONTROL_BASE+':ch8-s1-control/CI-REQUEST.json'))
    request = json.loads(json.dumps(old_request))
    assert git(std_repo, 'rev-parse', 'HEAD').strip() == STD
    assert git(std_repo, 'rev-parse', 'HEAD^').strip() == STD_BASE
    assert git(control, 'rev-parse', 'HEAD').strip() == CONTROL_BASE
    assert git(control, 'rev-parse', CONTROL_BASE+'^{tree}').strip() == git(control, 'rev-parse', 'b37f6f75c5b7b77e84297cd7104f9c0868502fd4^{tree}').strip()
    source, old_source, maps = {}, {}, {}
    equivalence = {}
    for name, macros in FILES.items():
        rel = PREFIX+name
        source[rel] = git(std_repo, 'show', STD+':'+rel)
        old_source[rel] = git(std_repo, 'show', STD_BASE+':'+rel)
        equivalence[rel] = lib.equivalent(old_source[rel], source[rel], macros)
        maps[rel] = line_map(old_source[rel], source[rel])
    assert set(git(std_repo, 'diff', '--name-only', STD_BASE, STD).splitlines()) == set(source)
    def text(rel):
        return source.get(rel) or git(std_repo, 'show', STD+':'+rel)
    def moved(rel, line):
        return maps.get(rel, {}).get(line, line) if rel not in maps else maps[rel][line]
    request['schema'] = 'ch8-s1-08-r1-ready-v1'
    request['control_parent'] = CONTROL_BASE
    request['std_sha'] = STD
    request['std_tree'] = git(std_repo, 'rev-parse', STD+'^{tree}').strip()
    request['reservations'] = {'S1-08': 'NOT_RESERVED; preparation only; no dispatch/push/ledger'}
    for rel in request['changed_file_sha256']:
        request['changed_file_sha256'][rel] = lib.sha(text(rel).encode())
    for binding in request['source_bindings'].values():
        rel = binding['file']
        binding['sha256'] = lib.sha(text(rel).encode())
        for loc in binding['locations']:
            loc['line'] = moved(rel, loc['line'])
            assert text(rel).splitlines()[loc['line']-1] == loc['source']
    for row in request['rows']:
        oracle = row.get('oracle')
        if oracle and row['variant'] == 'production':
            rel = oracle['file']
            oracle['line'] = moved(rel, oracle['line'])
            oracle['source_sha256'] = lib.sha(text(rel).encode())
            assert text(rel).splitlines()[oracle['line']-1] == oracle['source_line']
            oracle['property_id'] = oracle_source.repair_id(oracle['property_id'], text(rel), row['selector'].rsplit('::',1)[-1])
    receipt_path = HERE.parent/'s1-07/run-43923266772/accept/ACCEPT.json'
    receipt = json.loads(receipt_path.read_text())
    prior = {row['id']: row for row in receipt['rows']}
    entries, supplemental = [], []
    for row in request['rows']:
        binding = request['source_bindings'][row['id']]
        rel = binding['file'];src = text(rel)
        root = row['selector'].rsplit('::',1)[-1]
        inv = re.search(r'(?m)^(smoke_exact_n|smoke|positive)!\('+re.escape(root)+r'\b', src)
        macro = inv[1] if inv else None
        sites = lib.labelled_sites(src, macro) if macro else {}
        old_entries = {e['message']: e for e in prior[row['id']].get('required_success', [])}
        new_messages = []
        for old_message in row['required_success_messages']:
            previous = old_entries[old_message]
            role = lib.ROLE_SUFFIX[old_message] if macro else old_message.removeprefix('S1_').lower()
            label = root+'::'+role if macro else old_message
            if macro:
                site = sites[role]
                source_sites = [{'line': site['line'], 'end_line': site['end_line'],
                                 'text': site['text'], 'sha256': lib.sha(site['text'].encode())}]
                invocation = {'line': src.count('\n',0,inv.start())+1,
                              'text': src[inv.start():src.index(';', inv.start())+1]}
                allowed_lines = sorted({site['line'], invocation['line']})
            else:
                source_sites = [{'line': moved(rel,n), 'text': src.splitlines()[moved(rel,n)-1],
                                 'sha256': lib.sha(src.splitlines()[moved(rel,n)-1].encode())}
                                for n in previous['source']['source_role_sites']]
                invocation = None
                allowed_lines = [s['line'] for s in source_sites]
            entry = {'row_id': row['id'], 'selector': row['selector'], 'root': root,
                     'role': role, 'legacy_message': old_message, 'expected_message': label,
                     'expected_description': label if macro else lib.PLACEHOLDER,
                     'binding_kind': 'EXACT_ROLE_LABEL' if macro else previous['binding'],
                     'cardinality': 'EXACTLY_ONE_ID_SUCCESS' if macro else
                        ('COMPLETE_SOURCE_INSTANCE_SET' if previous['binding'].endswith('_SET') else 'EXACT_SOURCE_SEMANTIC_BINDING'),
                     'applicability': {'N': row.get('N'), 'predicate': 'true_for_this_row'},
                     'source': {'commit': STD, 'file': rel, 'sha256': lib.sha(src.encode()),
                                'macro': macro, 'sites': source_sites, 'invocation': invocation,
                                'allowed_property_lines': allowed_lines},
                     'observed_s108_property_ids': None, 'observed_s108_status': 'NOT_RUN'}
            if not macro:
                # Historical IDs are preserved verbatim, never reused as future IDs.
                entry['legacy_s107'] = previous
                entry['future_binding_policy'] = 'Re-audit exact source semantics; complete helper callsite/instance set where applicable; no historical ordinal/ID reuse'
                if previous['candidate_binding_source']:
                    context = previous['candidate_binding_source']
                    entry['source']['helper_callsites'] = [moved(rel,n) for n in context['helper_callsite_lines']]
            entries.append(entry);new_messages.append(label)
        row['required_success_messages'] = new_messages
        if macro in ('smoke', 'smoke_exact_n'):
            for role in ('type_layout', 'n0_empty_unchanged', 'n1_value_unchanged'):
                site = sites[role]
                n = 0 if role.startswith('n0') else 1 if role.startswith('n1') else None
                supplemental.append({'row_id': row['id'], 'role': role, 'expected_description': root+'::'+role,
                    'required_in_127': False, 'guard': 'true' if n is None else f'n == {n}',
                    'applies': n is None or row.get('N') in (n, 'symbolic0..3'),
                    'source': {'file':rel, 'sha256':lib.sha(src.encode()), **site}})
    manifest = {'schema':'ch8-s1-08-role-map-v1','std_sha':STD,'std_tree':request['std_tree'],'tool_sha':TOOL,
                'assurance':'STATIC_SOURCE_EXPECTATIONS_ONLY; S1-08 compiler/runtime/messages NOT_RUN; no proof credit',
                'legacy_receipt':{'path':str(receipt_path.relative_to(HERE.parent.parent.parent.parent.parent.parent)),
                                  'sha256':lib.sha(receipt_path.read_bytes()),'run':43923266772},
                'required_success_bindings':entries,'supplemental_label_sites':supplemental,
                'policy':'New labels exact per selected root/role, one unique ID with SUCCESS; missing/duplicate/mismatch UNKNOWN. Existing 16 exact semantic bindings/sets retained; fresh offline audit required. IDs never inferred from ordinal.'}
    lib.validate_map(manifest,request)
    write(h/'ROLE-MAP.json', manifest)
    request['role_map'] = {'path':'ROLE-MAP.json','sha256':lib.sha((h/'ROLE-MAP.json').read_bytes()),
                           'required_success_bindings':127,'new_labels':111,'preserved_semantic_bindings':16,
                           'observed_s108_messages':'NOT_RUN','admission':'OFFLINE_ONLY'}
    # Union semantics are the same five roles in each of four N members. Labels
    # are member-specific; keep role names plus the exact member message lists.
    for union in request['replacement_unions']:
        union['required_success_roles'] = [lib.ROLE_SUFFIX[x] for x in union['required_success_messages']]
        union['required_success_messages'] = [msg for rid in union['member_row_ids'] for row in request['rows']
                                               if row['id']==rid for msg in row['required_success_messages']]
        union['qualification'] = 'All four same-pin PFC cases; each member exact root/role labels and required exported covers; no partial-union acceptance; offline admission'
    for legacy in request['legacy_symbolic_rows']:
        root = legacy['selector'].rsplit('::',1)[-1]
        legacy['required_success_messages'] = [root+'::'+lib.ROLE_SUFFIX[m] for m in legacy['required_success_messages']]
    added = ['ch8-s1-control/'+x for x in ('ROLE-MAP.json','s108_package.py','test_s108.py','oracle_source.py','test_s108r1.py','ORACLE-SOURCES.json','fixtures/s108r1-smallsort.rs.txt','fixtures/s108r1-sorting_model_controls.rs.txt')]
    request['ci_changed_paths'] = sorted(set(request['ci_changed_paths']+added))
    for rel in sorted(set(request['ci_payload_sha256']) | set(added)):
        request['ci_payload_sha256'][rel] = lib.sha((control/rel).read_bytes())
    write(h/'CI-REQUEST.json',request)
    write(HERE/'SOURCE-VALIDATION.json', {'status':'PASS','source_equivalence':equivalence,
             'complete_changed_paths':list(source),'scope':'23 assertion sites; all non-diagnostic tokens preserved',
             'reviewed_base_equals_executed_control_tree':True,'compiler_runtime':'NOT_RUN'})
    print(json.dumps({'std_sha':STD,'std_tree':request['std_tree'],'required':len(entries),
                      'role_map_sha256':request['role_map']['sha256'],
                      'request_sha256':lib.sha((h/'CI-REQUEST.json').read_bytes())}))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--control',type=Path,default=Path('/root/kani-ch8-s1-08-fix-w13'))
    p.add_argument('--std',type=Path,default=Path('/root/verify-rust-std-ch8-s1-08-w13'))
    a=p.parse_args();prepare(a.control,a.std)
