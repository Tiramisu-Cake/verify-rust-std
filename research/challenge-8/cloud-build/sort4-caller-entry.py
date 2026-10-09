#!/usr/bin/env python3
"""Cloud-only native mutable-slice caller prefix / c1 entry entailment diagnostic."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p: Path, x): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(x, indent=2, sort_keys=True)+'\n')
def need(b, why):
    if not b: raise RuntimeError(why)
def load_module(p, name):
    spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m

def mir_basic_blocks(record):
    """Read top-level basic block slices from a complete captured Cap'n Proto record."""
    marker='basicBlocks = ['
    at=record.find(marker)
    if at<0 or record.find(marker,at+len(marker))>=0:return None
    open_at=at+len(marker)-1
    close_at=matching_bracket(record,open_at)
    if close_at is None:return None
    tail=record[open_at+1:close_at]
    starts=list(re.finditer(r'(?m)^\s*\( id = \(index = (\d+)\),',tail))
    if not starts:return None
    blocks=[]
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else len(tail)
        blocks.append((int(m.group(1)),tail[m.start():end]))
    if [n for n,_ in blocks]!=list(range(len(blocks))):return None
    return blocks

def matching_bracket(text, opening):
    if opening<0 or opening>=len(text) or text[opening]!='[':return None
    depth=0; quoted=False; escaped=False
    for i in range(opening,len(text)):
        ch=text[i]
        if quoted:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':quoted=False
        elif ch=='"':quoted=True
        elif ch=='[':depth+=1
        elif ch==']':
            depth-=1
            if depth==0:return i
    return None

def mir_ghost_statement(record, line, marker_text):
    """Find a MIR ghostStmts raw item spanning a source marker line."""
    fields=list(re.finditer(r'(?m)^\s*ghostStmts = \[',record))
    if len(fields)!=1 or not isinstance(line,int):return None
    opening=record.find('[',fields[0].start())
    closing=matching_bracket(record,opening)
    if closing is None:return None
    section=record[opening+1:closing]
    starts=list(re.finditer(r'(?m)^\s*\( raw = "',section))
    matches=[]
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else len(section)
        item=section[m.start():end]
        start_match=re.search(r'\bstartLine = (\d+),',item)
        end_match=re.search(r'\bendLine = (\d+),',item)
        if not start_match or not end_match:continue
        lo,hi=int(start_match.group(1)),int(end_match.group(1))
        if lo<=line<=hi and marker_text in item:
            matches.append({'index':i,'start_line':lo,'end_line':hi})
    return matches if matches else None

def mir_line_blocks(blocks, line):
    if blocks is None or not isinstance(line,int):return None
    hits=[]
    for block_id,block in blocks:
        if re.search(r'\bline = '+str(line)+r',',block):hits.append(block_id)
    return hits or None

def executed_line(log, line):
    if not isinstance(line,int):return False
    return re.search(r'^\s*\d+(?:\.\d+)?s: verified/lib\.rs\('+str(line)+r',[^\n]*\): Executing statement\s*$',log,re.M) is not None

def source_line(lines, line):
    return lines[line-1] if isinstance(line,int) and 1<=line<=len(lines) else None

NATIVE_ENTRY_CERT_CLASS = 'SOURCE_LINKED_STANDALONE_NATIVE_ENTRY_RESOURCE_DIAGNOSTIC_NOT_CALLER_PROOF'
NATIVE_ENTRY_OPERATIONS = (
    ('len', b'let len = v.len();'),
    ('v_base', b'let v_base = v.as_mut_ptr();'),
    ('len_div_2', b'let len_div_2 = len / 2;'),
    ('unsafe', b'unsafe {'),
    ('scratch_base', b'let scratch_base = scratch.as_mut_ptr() as *mut T;'),
)

def native_entry_source_operations(actual, verified, cert):
    """Bind five operation spans to exact original caller bytes and lemma lines."""
    source_cert=cert.get('source_certificate',{})
    source_mapping=cert.get('source_mapped_condition_bytes',{})
    operation_map=source_mapping.get('operation_map') if isinstance(source_mapping,dict) else None
    if not isinstance(source_cert,dict) or not isinstance(operation_map,dict):
        return {'status':'NOT_CONFIRMED','reason':'native source certificate or operation map absent'}
    actual_payload=actual[:-1] if actual.endswith(b'\n') else actual
    caller_start=source_cert.get('caller_byte_start')
    rows={};absolute_offsets=[];relative_offsets=[];proof_lines=[]
    for name,expected in NATIVE_ENTRY_OPERATIONS:
        item=operation_map.get(name)
        if not isinstance(item,dict):
            rows[name]={'status':'NOT_CONFIRMED','reason':'operation entry absent'}
            continue
        absolute=item.get('source_byte_start')
        relative=item.get('caller_relative_byte_start')
        statement=item.get('exact_statement_bytes')
        if isinstance(statement,str):statement=statement.encode()
        lemma_line=item.get('verified_source_line')
        lemma_offset=item.get('lemma_byte_start')
        digest=item.get('statement_sha256')
        span_ok=(type(absolute) is int and type(relative) is int and
                 type(caller_start) is int and absolute-caller_start==relative and
                 relative>=0 and isinstance(statement,bytes) and statement.strip()==expected and
                 actual_payload[relative:relative+len(statement)]==statement)
        line_in_caller=(actual_payload.count(b'\n',0,relative)+1
                        if type(relative) is int and relative>=0 else None)
        line_in_source=(source_cert.get('caller_start_line',1)+line_in_caller-1
                        if type(line_in_caller) is int and type(source_cert.get('caller_start_line',1)) is int else None)
        declared_line=item.get('source_line')
        line_ok=(type(declared_line) is int and declared_line==line_in_caller)
        hash_ok=isinstance(digest,str) and digest==hashlib.sha256(statement).hexdigest() if isinstance(statement,bytes) else False
        lemma_ok=type(lemma_line) is int and lemma_line>=1
        verified_span_ok=(type(lemma_offset) is int and lemma_offset>=0 and isinstance(statement,bytes) and
                          verified[lemma_offset:lemma_offset+len(statement)]==statement and
                          verified.count(statement)==1 and
                          verified[:lemma_offset].count(b'\n')+1==lemma_line)
        rows[name]={
            'status':'PASS' if span_ok and line_ok and hash_ok and lemma_ok and verified_span_ok else 'NOT_CONFIRMED',
            'source_byte_start':absolute,'caller_relative_byte_start':relative,
            'source_line':declared_line,'derived_caller_line':line_in_caller,
            'derived_small_sort_line':line_in_source,
            'verified_source_line':lemma_line,'exact_expected_bytes':span_ok,
            'statement_sha256_matches':hash_ok,'source_line_matches_offset':line_ok,
            'lemma_byte_start':lemma_offset,'verified_source_span_exact':verified_span_ok,
        }
        if type(absolute) is int:absolute_offsets.append(absolute)
        if type(relative) is int:relative_offsets.append(relative)
        if lemma_ok:proof_lines.append(lemma_line)
    exact_caller=(hashlib.sha256(actual_payload).hexdigest()==source_cert.get('full_original_caller_sha256'))
    order_ok=(len(absolute_offsets)==len(NATIVE_ENTRY_OPERATIONS) and absolute_offsets==sorted(absolute_offsets) and
              len(set(absolute_offsets))==len(absolute_offsets) and
              len(relative_offsets)==len(NATIVE_ENTRY_OPERATIONS) and relative_offsets==sorted(relative_offsets) and
              len(proof_lines)==len(NATIVE_ENTRY_OPERATIONS) and proof_lines==sorted(proof_lines) and
              len(set(proof_lines))==len(proof_lines))
    all_ok=all(rows.get(name,{}).get('status')=='PASS' for name,_ in NATIVE_ENTRY_OPERATIONS)
    return {'status':'PASS' if exact_caller and order_ok and all_ok else 'NOT_CONFIRMED',
            'actual_caller_sha256':hashlib.sha256(actual_payload).hexdigest(),
            'actual_caller_sha_matches_certificate':exact_caller,
            'source_order_matches_native_entry':order_ok,'operations':rows}

def native_entry_mapping(fixture, cert, normal_record, readonly_record, log, entry):
    """Bind standalone native lemma operations, complete MIR, ghost boundary and trace."""
    verified=(fixture/'verified/lib.rs').read_bytes()
    source_lines=verified.decode(errors='replace').splitlines()
    actual_path=fixture/'actual-caller.rs'
    actual=actual_path.read_bytes() if actual_path.is_file() else b''
    source_cert=cert.get('source_certificate',{})
    contract=cert.get('native_entry_contract')
    source_mapping=cert.get('source_mapped_condition_bytes',{})
    signature=source_cert.get('native_entry_signature') if isinstance(source_cert,dict) else None
    signature_bytes=signature.encode() if isinstance(signature,str) else b''
    contract_ok=(isinstance(contract,dict) and
                 contract.get('signature_is_exact_actual_caller_signature') is True and
                 contract.get('full_native_precondition_from_generated_mutable_reference_contract') is True and
                 contract.get('automatic_native_normal_post_checked') is True and
                 contract.get('automatic_native_unwind_post_checked') is True and
                 contract.get('automatic_native_leak_check_required') is True and
                 contract.get('all_lengths_admitted') is True and
                 contract.get('all_scratch_lengths_admitted') is True and
                 contract.get('zst_admitted') is True and
                 contract.get('no_runtime_guard_or_caller_cfg_projection') is True)
    bridge_scope=cert.get('bridge_diagnostic_subdomain')
    type_interp=cert.get('type_interp_disposition')
    bridge_scope_ok=(cert.get('case')!='bridge-positive' or
        (isinstance(bridge_scope,dict) and
         bridge_scope.get('guard')=='ghost condition size_of<T>() > 0 && scratch_len >= 4' and
         bridge_scope.get('caller_scratch_success_implies_lower_bound_claim') is False and
         'no caller CFG' in bridge_scope.get('scope_note','') and
         isinstance(type_interp,dict) and
         type_interp.get('bridge-positive')=='stock produce_type_interp::<T/F>() in the real diagnostic function, followed by explicit stock leak type_interp::<T/F>(); trusted logical production, not native heap derivation'))
    identity=(cert.get('classification')==NATIVE_ENTRY_CERT_CLASS and
              isinstance(source_cert,dict) and
              source_cert.get('native_entry_signature_exact') is True and
              source_cert.get('native_entry_is_separate_resource_lemma') is True and
              bool(signature_bytes) and
              source_cert.get('caller_signature_sha256')==hashlib.sha256(signature_bytes).hexdigest() and
              actual.startswith(signature_bytes) and verified.count(signature_bytes)==1 and
              isinstance(source_mapping,dict) and
              source_mapping.get('source_runtime_identity_claim') is False and
              source_mapping.get('caller_cfg_projection_claim') is False and
              source_mapping.get('ghost_boundary_is_artificial') is True and
              contract_ok and bridge_scope_ok)
    operations=native_entry_source_operations(actual,verified,cert)
    operation_map=source_mapping.get('operation_map',{}) if isinstance(source_mapping,dict) else {}
    modes={};trace_hits={}
    for name,_ in NATIVE_ENTRY_OPERATIONS:
        row=operation_map.get(name,{}) if isinstance(operation_map,dict) else {}
        line=row.get('verified_source_line') if isinstance(row,dict) else None
        source_text=source_line(source_lines,line)
        needle=NATIVE_ENTRY_OPERATIONS[[x[0] for x in NATIVE_ENTRY_OPERATIONS].index(name)][1].decode()
        source_ok=isinstance(source_text,str) and source_text.strip()==needle
        trace_hits[name]=True if name=='unsafe' else executed_line(log,line)
        for mode,record in (('normal',normal_record),('readonly',readonly_record)):
            blocks=mir_basic_blocks(record)
            line_blocks=(None if name=='unsafe' else mir_line_blocks(blocks,line))
            modes.setdefault(mode,{'complete_basic_block_inventory':len(blocks) if blocks is not None else None,
                                   'full_function_record_sha256':hashlib.sha256(record.encode()).hexdigest() if record else None,
                                   'source_line_to_basic_blocks':{},'status':'PASS'})
            if name!='unsafe':modes[mode]['source_line_to_basic_blocks'][name]=line_blocks
            if blocks is None or (name!='unsafe' and not line_blocks) or not source_ok:modes[mode]['status']='NOT_CONFIRMED'
    marker=source_mapping.get('ghost_boundary_marker') if isinstance(source_mapping,dict) else None
    marker_lines=[i+1 for i,line in enumerate(source_lines) if isinstance(marker,str) and marker in line]
    boundary_line=marker_lines[0] if len(marker_lines)==1 else None
    boundary_text=source_line(source_lines,boundary_line)
    boundary_ghost={};trace_hits['native_entry_ghost_boundary']=executed_line(log,boundary_line)
    boundary_source_exact=(isinstance(marker,str) and
                           boundary_text is not None and
                           boundary_text.strip()==f'assert len >= 8; // {marker}')
    for mode,record in (('normal',normal_record),('readonly',readonly_record)):
        blocks=mir_basic_blocks(record)
        ghost=mir_ghost_statement(record,boundary_line,marker) if boundary_line else None
        block_hits=mir_line_blocks(blocks,boundary_line) if boundary_line else None
        unique_cover=(isinstance(ghost,list) and len(ghost)==1 and
                      ghost[0].get('start_line',boundary_line+1)<=boundary_line<=
                      ghost[0].get('end_line',boundary_line-1))
        boundary_ghost[mode]={'status':'PASS' if blocks is not None and unique_cover and boundary_source_exact else 'NOT_CONFIRMED',
                              'complete_basic_block_inventory':len(blocks) if blocks is not None else None,
                              'source_line_to_basic_blocks':block_hits,'mir_ghost_statement':ghost,
                              'ghost_span_uniquely_covers_marker_line':unique_cover,
                              'source_marker_line_exact':boundary_source_exact,
                              'full_function_record_sha256':hashlib.sha256(record.encode()).hexdigest() if record else None}
    boundary_ok=(isinstance(source_mapping,dict) and source_mapping.get('ghost_boundary_is_artificial') is True and boundary_line is not None and
                 boundary_source_exact and
                 all(row['status']=='PASS' for row in boundary_ghost.values()))
    trace_ok=all(trace_hits.values())
    mir_ok=all(row['status']=='PASS' for row in modes.values())
    return {
        'status':'PASS' if identity and operations['status']=='PASS' and boundary_ok and mir_ok and trace_ok else 'NOT_CONFIRMED',
        'lemma_identity_and_separate_resource_scope':identity,
        'bridge_diagnostic_subdomain':bridge_scope if cert.get('case')=='bridge-positive' else None,
        'type_interp_disposition':type_interp if cert.get('case')=='bridge-positive' else None,
        'source_operations':operations,
        'mir':modes,
        'artificial_ghost_boundary':{'status':'PASS' if boundary_ok else 'NOT_CONFIRMED',
             'marker':marker,'line':boundary_line,'source_text':boundary_text,
             'normal_and_readonly':boundary_ghost,'control_flow_projection_proved':False},
        'proof_execution_trace':{'status':'PASS' if trace_ok else 'NOT_CONFIRMED',
             'statement_hits':trace_hits,'evidence_kind':'native lemma verifier execution trace; no caller CFG projection claimed'},
        'proof_entry_log_offset':entry,
    }

def native_post_ast_evidence(path, cert):
    """Capture compiler-generated returning/unwinding post AST for the exact entry."""
    if not path.is_file():
        return {'status':'NOT_CONFIRMED','reason':'pre-verification proof AST is absent'}
    data=path.read_bytes(); ast=data.decode(errors='replace')
    function='small_sort_general_with_scratch'
    hits=list(re.finditer(r'\bFunc \(loc [^\n]*"'+re.escape(function)+r'", \[',ast))
    if len(hits)!=1:
        return {'status':'NOT_CONFIRMED','reason':'native entry AST declaration absent or ambiguous',
                'sha256':hashlib.sha256(data).hexdigest(),'matching_declarations':len(hits)}
    start=hits[0].start()
    nxt=re.search(r'(?m)^\s+Func \(',ast[hits[0].end():])
    end=hits[0].end()+nxt.start() if nxt else len(ast)
    record=ast[start:end]
    contract=cert.get('native_entry_contract',{})
    contract_ok=(isinstance(contract,dict) and
        contract.get('automatic_native_normal_post_checked') is True and
        contract.get('automatic_native_unwind_post_checked') is True and
        contract.get('automatic_native_leak_check_required') is True and
        contract.get('all_lengths_admitted') is True and
        contract.get('all_scratch_lengths_admitted') is True and
        contract.get('zst_admitted') is True and
        contract.get('no_runtime_guard_or_caller_cfg_projection') is True and
        contract.get('native_post_source')=='stock generated contract for the exact signature; not hand-written or strengthened')
    normal='SwitchExprClause' in record and '"returning"' in record
    unwind='SwitchExprClause' in record and '"unwinding"' in record
    outcome='"fn_outcome"' in record and '"outcome"' in record
    passed=contract_ok and normal and unwind and outcome
    return {'status':'PASS' if passed else 'NOT_CONFIRMED',
            'proof_ast_sha256':hashlib.sha256(data).hexdigest(),
            'native_entry_ast_sha256':hashlib.sha256(record.encode()).hexdigest(),
            'matching_declarations':1,'automatic_contract_certificate_matches':contract_ok,
            'fn_outcome_switch_present':outcome,'normal_return_post_present':normal,
            'unwind_post_present':unwind,
            'unwind_semantics_scope':'automatic unwinding post arm captured; this lemma executes no caller callback and claims no callback panic-path behavior',
            'proof_verifier_must_still_pass_entire_entry':True}

def native_expected_negative(case, cert, verified, log, entries, errors, verifier_exit):
    """Accept only the marker-pinned single first obligation for a native negative."""
    expected=cert.get('expected_negative_first_error')
    # Typed missing-producer controls deliberately remain uncredited until a
    # fresh Cloud log pins the exact callee predicate and source location.
    supported={'range-negative','duplicate-negative','source-post-negative'}
    if (case not in supported or not isinstance(expected,dict) or
        verifier_exit!=1 or len(entries)!=1 or len(errors)!=1):
        return False
    marker=expected.get('marker')
    obligation=expected.get('obligation')
    source_lines=verified.decode(errors='replace').splitlines()
    marker_lines=[i+1 for i,line in enumerate(source_lines) if isinstance(marker,str) and marker in line]
    if len(marker_lines)!=1 or not isinstance(obligation,str) or not obligation:
        return False
    line=marker_lines[0]
    if not executed_line(log,line):
        return False
    if case=='range-negative':
        # The failed VC is in the stock array_split contract, not at the
        # source callsite. Attribute it only through the exact executed call
        # and VeriFast's matching "Verifying call" note at that marker line.
        call_note=(re.search(r'verified/lib\.rs\('+str(line)+r',[^\n]*\): note: Verifying call\n'+
                              re.escape(str(line)+' |')+r'[^\n]*array_split::<T>\(v_base, 9\); // RANGE_AUTHORITY_CONTROL',log) is not None)
        first_error_is_stock_split_bound=(
            re.search(r'(?:^|/)prelude_core\.rsspec\(261,\d+-\d+\): error: Cannot prove condition\. \(Cannot prove 9 <= ptr_len\(v\)\.\)$',errors[0]) is not None)
        source_guard=(line>=5 and 'if (len == 8)' in source_lines[line-3] and
                      'if (len >= 8)' in source_lines[line-5])
        semantic=('array_split::<T>(v_base, 9)' in source_lines[line-1] and
                  'RANGE_AUTHORITY_CONTROL' in source_lines[line-1] and
                  call_note and first_error_is_stock_split_bound and source_guard)
    elif case=='duplicate-negative':
        loc=re.match(r'verified/lib\.rs\((\d+),',errors[0])
        semantic=('DUPLICATE_AUTHORITY_CONTROL' in source_lines[line-1] and
                  loc is not None and int(loc.group(1))==line and
                  'No matching heap chunks: array<T>' in errors[0])
    else:
        loc=re.match(r'verified/lib\.rs\((\d+),',errors[0])
        semantic=('SOURCE_CURRENT_VALUE_POST_CONTROL' in source_lines[line-1] and
                  loc is not None and int(loc.group(1))==line and
                  'less_after != less_before' in source_lines[line-1] and
                  ('Cannot prove condition' in errors[0] or 'Cannot prove' in errors[0]))
    return semantic and obligation in {
        'array_split at 9 with len==8',
        'duplicate whole-array array authority',
        'false current-value post after identity lemma',
    }

def positive_full_vf0(case, *, controls_passed, support_gates_passed,
                      source_mir_trace_passed, verifier_exit, proof_entries,
                      caller_log, errors, full_vf0_log, full_native_contract):
    """Require all evidence gates before assigning positive native resource credit."""
    return (case in {'source-frame-positive','source-typed-frame-positive','bridge-positive','prefix-native','native-scratch-frame'} and
            controls_passed is True and support_gates_passed is True and
            source_mir_trace_passed is True and verifier_exit==0 and
            len(proof_entries)==1 and 'Leak check.' in caller_log and not errors and
            full_vf0_log is True and full_native_contract is True)

def native_case_targets_reached(case, cert, caller_log, source_lines=None):
    """Require each positive case's named resource assertions to execute."""
    targets=cert.get('targeted_ghost_statement_lines',{})
    line_lists=cert.get('targeted_ghost_statement_line_lists',{})
    if not isinstance(targets,dict) or not isinstance(line_lists,dict):return False
    if case=='prefix-native':return True
    if case=='source-frame-positive':
        required=[targets.get('source_subset_four')]
    elif case=='source-typed-frame-positive':
        required=[targets.get('source_subset_four'),
                  targets.get('produce_type_interp_T'),targets.get('produce_type_interp_F'),
                  targets.get('source_typed_identity_call'),
                  targets.get('leak_type_interp_T'),targets.get('leak_type_interp_F')]
    elif case=='bridge-positive':
        identity_line=native_identity_call_target(cert, source_lines)
        required=[targets.get('positive_size_guard'),targets.get('bridge_scratch_guard'),identity_line]
    elif case=='native-scratch-frame':
        required=[targets.get('native_scratch_array')]
        required.extend(line_lists.get('native_scratch_owners',[]))
    else:
        return True
    return bool(required) and all(type(line) is int and executed_line(caller_log,line) for line in required)

def native_identity_call_target(cert, source_lines):
    """Resolve only agreeing bridge identity aliases and its exact source call."""
    targets=cert.get('targeted_ghost_statement_lines',{})
    line_lists=cert.get('targeted_ghost_statement_line_lists',{})
    if not isinstance(targets,dict) or not isinstance(line_lists,dict):return None
    candidates=[]
    for key in ('identity_lemma_call','positive_identity_lemma'):
        if key in targets:
            value=targets[key]
            if type(value) is not int:return None
            candidates.append(value)
    if 'identity_lemma_call' in line_lists:
        values=line_lists['identity_lemma_call']
        if not isinstance(values,list) or len(values)!=1 or type(values[0]) is not int:return None
        candidates.extend(values)
    if not candidates or len(set(candidates))!=1:return None
    line=candidates[0]
    if source_lines is not None:
        text=source_line(source_lines,line)
        if not isinstance(text,str) or not re.search(r'\bc1_entry_identity::<T,\s*F>\(v_base,\s*scratch_base,\s*is_less\s+as\s+\*mut\s+F\);',text):
            return None
    return line

def legacy_dead_code_vf1(errors):
    """Keep the VF1 strict dead-code refusal distinct from proof obligations."""
    return any(re.search(r'\): dead code$',line) for line in errors)

def resource_evidence(root):
    p=root/'verification-resources.txt'
    if not p.is_file():return {'status':'NOT_CONFIRMED','path':str(p)}
    data=p.read_bytes(); text=data.decode(errors='replace')
    fields={}
    for label,pattern in (
        ('elapsed_wall_seconds',r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([^\n]+)'),
        ('maximum_resident_set_kb',r'Maximum resident set size \(kbytes\): (\d+)'),
        ('user_seconds',r'User time \(seconds\): ([^\n]+)'),
        ('system_seconds',r'System time \(seconds\): ([^\n]+)'),
    ):
        m=re.search(pattern,text); fields[label]=m.group(1).strip() if m else None
    return {'status':'CAPTURED','path':str(p),'sha256':hashlib.sha256(data).hexdigest(),**fields}

def caller_mapping(root, fixture, cert, normal_record, readonly_record, log, entry):
    """Bind selected source lines to complete MIR blocks and trace locations.

    The last edge is a verifier execution-trace location, not a complete proof
    AST dump. Missing or ambiguous mappings stay NOT_CONFIRMED.
    """
    targets=cert.get('targeted_ghost_statement_lines',{})
    if not isinstance(targets,dict):targets={}
    filter_line=targets.get('scratch_success_path_filter')
    original_line=targets.get('original_scratch_len_plus_16_check')
    boundary_line=targets.get('first_sort4_callsite_boundary')
    source=(fixture/'verified/lib.rs').read_text(errors='replace').splitlines()
    actual_path=fixture/'actual-caller.rs'
    actual=actual_path.read_text(errors='replace').splitlines() if actual_path.is_file() else []
    caller_cert=cert.get('source_certificate',{})
    if not isinstance(caller_cert,dict):caller_cert={}
    actual_bytes=actual_path.read_bytes() if actual_path.is_file() else b''
    actual_sha=hashlib.sha256(actual_bytes[:-1]).hexdigest() if actual_bytes.endswith(b'\n') else None
    actual_file_sha=hashlib.sha256(actual_bytes).hexdigest() if actual_bytes else None
    source_cert=cert.get('source_mapped_condition_bytes',{})
    if not isinstance(source_cert,dict):source_cert={}
    expected=source_cert.get('scratch_success_filter_condition')
    expected=expected.strip() if isinstance(expected,str) else None
    filter_text=source_line(source,filter_line)
    original_text=source_line(source,original_line)
    boundary_text=source_line(source,boundary_line)
    line_targets_ok=all(type(line) is int for line in (filter_line,original_line,boundary_line))
    source_ok=(expected is not None and line_targets_ok and filter_line<original_line and
               filter_text is not None and original_text is not None and
               filter_text.strip()==expected and original_text.strip()==expected and
               source_line(source,filter_line+1) is not None and source_line(source,filter_line+1).strip()=='return;' and
               'FIRST_SORT4_CALLSITE_BOUNDARY' in (boundary_text or '') and
               caller_cert.get('caller_runtime_source_exact') is True and
               actual_sha==caller_cert.get('full_original_caller_sha256') and
               sum(1 for line in actual if line.strip()==expected)==1 and
               source_cert.get('scratch_success_filter_matches_original_condition') is True and
               source_cert.get('original_abort_check_retained_verbatim') is True)
    pointer_lines={}
    for name,needle in (('v_as_mut_ptr','let v_base = v.as_mut_ptr();'),
                        ('scratch_as_mut_ptr','let scratch_base = scratch.as_mut_ptr() as *mut T;')):
        hits=[i+1 for i,text in enumerate(source) if needle in text]
        pointer_lines[name]=hits[0] if len(hits)==1 else None
    abort_hits=[i+1 for i,text in enumerate(source) if 'intrinsics::abort();' in text]
    abort_line=abort_hits[0] if len(abort_hits)==1 else None
    source_ok=bool(source_ok and isinstance(original_line,int) and abort_line==original_line+1 and
                   source_line(source,abort_line)=='        intrinsics::abort();')
    order_ok=(source_ok and pointer_lines['v_as_mut_ptr'] is not None and
              pointer_lines['scratch_as_mut_ptr'] is not None and
              original_line<pointer_lines['v_as_mut_ptr']<pointer_lines['scratch_as_mut_ptr'])
    modes={}
    for mode,record in (('normal',normal_record),('readonly',readonly_record)):
        blocks=mir_basic_blocks(record)
        mapped={
            'scratch_success_path_filter':mir_line_blocks(blocks,filter_line),
            'original_scratch_len_plus_16_check':mir_line_blocks(blocks,original_line),
            'v_as_mut_ptr':mir_line_blocks(blocks,pointer_lines['v_as_mut_ptr']),
            'scratch_as_mut_ptr':mir_line_blocks(blocks,pointer_lines['scratch_as_mut_ptr']),
            'original_abort_statement':mir_line_blocks(blocks,abort_line),
        }
        boundary_ghost=mir_ghost_statement(record,boundary_line,'FIRST_SORT4_CALLSITE_BOUNDARY')
        abort_target_blocks=[block_id for block_id,block in (blocks or [])
                             if 'name = "std::intrinsics::abort"' in block]
        abort_target_linked=bool(abort_target_blocks and mapped['original_abort_statement'] and
                                 set(abort_target_blocks).intersection(mapped['original_abort_statement']))
        mir_complete=blocks is not None and all(mapped[k] for k in (
            'scratch_success_path_filter','original_scratch_len_plus_16_check',
            'v_as_mut_ptr','scratch_as_mut_ptr')) and boundary_ghost is not None
        modes[mode]={
            'status':'PASS' if source_ok and order_ok and mir_complete and abort_target_linked else 'NOT_CONFIRMED',
            'full_function_record_sha256':hashlib.sha256(record.encode()).hexdigest() if record else None,
            'complete_basic_block_inventory':len(blocks) if blocks is not None else None,
            'source_line_to_basic_blocks':mapped,
            'callsite_boundary_mir_ghost_statement':boundary_ghost,
            'abort_target_blocks':abort_target_blocks,
            'abort_target_linked_to_original_abort_span':abort_target_linked,
            'source_ordered_lines_all_present_in_mir':bool(order_ok and mir_complete),
            'control_flow_precedence_proved':False,
        }
    trace={
        'scratch_success_path_filter':executed_line(log,filter_line),
        'original_scratch_len_plus_16_check':executed_line(log,original_line),
        'first_sort4_callsite_boundary':executed_line(log,boundary_line),
        'original_abort_statement_executed':executed_line(log,abort_line),
    }
    trace_ok=all(trace[k] for k in ('scratch_success_path_filter',
                                    'original_scratch_len_plus_16_check',
                                    'first_sort4_callsite_boundary')) and not trace['original_abort_statement_executed']
    return {
        'status':'PASS' if source_ok and order_ok and all(m['status']=='PASS' for m in modes.values()) and trace_ok else 'NOT_CONFIRMED',
        'source':{
            'status':'PASS' if source_ok and order_ok else 'NOT_CONFIRMED',
            'scratch_filter_line':filter_line,'scratch_filter_text':filter_text,
            'original_check_line':original_line,'original_check_text':original_text,
            'condition_text_equal':bool(source_ok),'boundary_marker_line':boundary_line,
            'boundary_marker_text':boundary_text,'pointer_operation_lines':pointer_lines,
            'actual_caller_sha256':actual_sha,
            'actual_caller_sha_matches_certificate':actual_sha==caller_cert.get('full_original_caller_sha256'),
            'actual_caller_file_sha256':actual_file_sha,
            'saved_file_trailing_newline_excluded_from_payload_hash':True,
            'source_order_places_guards_before_pointer_operations':bool(order_ok),
            'original_abort_line':abort_line,
        },
        'mir':modes,
        'proof_execution_trace':{
            'status':'PASS' if trace_ok else 'NOT_CONFIRMED',
            'statement_hits':trace,
            'evidence_kind':'verifier execution trace locations; no complete proof AST dump claimed',
        },
        'proof_entry_log_offset':entry,
        'verification_resources':resource_evidence(fixture),
    }

def snapshot(a):
    root=a.production_source
    paths=['src/verifast.ml','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml','src/rust_frontend/vf_mir_translator/rust_parser.ml','src/rust_frontend/vf_mir/vf_mir.capnp','bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker']
    return {'critical':{p:sha(root/p) for p in paths},'effective_rsspec':{str(p.relative_to(root)):sha(p) for p in sorted((root/'bin/rust').rglob('*.rsspec'))},'base_commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'production_applied_patch_sha256':sha(a.production_applied_patch),'proof_sha':os.environ['PROOF_SHA'],'infra_sha':os.environ['INFRA_SHA'],'new_semantic_patch':True,'semantic_variant':'exact_slice_as_mut_ptr_value_projection_candidate','c1_overlay_active':False,'profile_accepted':False}

def stage(a, root, name, argv, env, cap, stdin=None, stdout=None):
    seconds=min(cap,a.deadline_epoch-int(time.time())-15)
    status={'name':name,'state':'RUNNING','argv':argv,'started_epoch':int(time.time()),'proof_verdict':None}
    write(root/(name+'-stage.json'),status); write(a.evidence/'stage-progress.json',{'case':root.name,**status})
    if seconds<=0:
        status.update(state='NOT_RUN',exit=None,reason='deadline/evidence reserve'); write(root/(name+'-stage.json'),status); return status
    output=root/(stdout or name+'.log'); errors=root/(name+'-stderr.log') if stdout else output
    with output.open('wb') as out:
        err=errors.open('wb') if errors!=output else subprocess.STDOUT
        inp=(root/stdin).open('rb') if stdin else open(os.devnull,'rb')
        try:
            code=subprocess.run(['/usr/bin/time','-v','-o',str(root/(name+'-resources.txt')),'timeout','--signal=TERM','--kill-after=10s',str(seconds)+'s',*argv],cwd=root,env=env,stdin=inp,stdout=out,stderr=err,check=False).returncode
        finally:
            inp.close()
            if errors!=output: err.close()
    status.update(state='TERMINAL',exit=code,finished_epoch=int(time.time()),stdout=output.name,stderr=errors.name,stdout_sha256=sha(output),stderr_sha256=sha(errors))
    (root/(name+'-exit-code.txt')).write_text(str(code)+'\n');write(root/(name+'-stage.json'),status);write(a.evidence/'stage-progress.json',{'case':root.name,**status})
    if stdout is None: print(output.read_text(errors='replace'),flush=True)
    return status

def run_case(a, prep, capture, parser, case, env):
    root=a.evidence/'cases'/case
    root.mkdir(parents=True)
    result={'case':case,'classification':'NOT_RUN_PREPARE','accepted':False,'bridge_premises_derived':False}
    write(root/'case-result.json',result)
    try:
        fixture=root/'fixture'; cert=prep.prepare(a.proof_root,fixture,case)
        native_mode=cert.get('classification')==NATIVE_ENTRY_CERT_CLASS
        write(root/'source-certificate.json',cert)
        before={name:sha(fixture/name) for name in ('original/lib.rs','verified/lib.rs')}
        write(root/'raw-input-pins.json',{'proof_sha':os.environ['PROOF_SHA'],'source_hashes':before,'source_linked_native_entry_resource_lemma':native_mode,'source_linked_fragment_only':not native_mode,'caller_full_body_proved':False,'sort4_summary_used':False})
        exporter=str(a.production_source/'bin/vf-rust-mir-exporter'); vf=str(a.production_source/'bin/verifast'); refiner=str(a.production_source/'bin/refinement-checker'); schema=a.production_source/'src/rust_frontend/vf_mir/vf_mir.capnp'
        rows={}; records={}
        for mode in ('normal','readonly'):
            argv=[exporter,'verified/lib.rs','--sysroot='+str(a.compiler_sysroot),'--edition','2021']
            if mode=='readonly': argv.append('--vf-rust-mir-exporter:preprocess-readonly')
            rows[mode+'-export']=stage(a,fixture,mode+'-export',argv,env,100,stdout=mode+'-mir.bin')
            if rows[mode+'-export']['exit']==0:
                rows[mode+'-decode']=stage(a,fixture,mode+'-decode',['capnp','decode',str(schema),'VfMir'],env,60,stdin=mode+'-mir.bin',stdout=mode+'-mir.txt')
                if rows[mode+'-decode']['exit']==0:
                    defpath,record=capture.complete_function_record((fixture/(mode+'-mir.txt')).read_text(),'small_sort_general_with_scratch')
                    records[mode]=record
                    (root/(mode+'-full-prefix-mir.txt')).write_text(record)
                    write(root/(mode+'-graph.json'),{'def_path':defpath,'full_record_sha256':sha(root/(mode+'-full-prefix-mir.txt')),'full_record_bytes':len(record.encode()),'complete_fields':['inputs','localDecls','basicBlocks'],'source_linked_native_entry_resource_lemma':native_mode,'source_linked_prefix_only':not native_mode,'actual_full_caller':False,'caller_cfg_projection':False if native_mode else None,'no_comparator_or_copy':not ('FnMut::call_mut' in record or 'copy_nonoverlapping' in record),'call_targets':re.findall(r'fnDef = \(\s*id = \(\s*name = "([^"]+)"',record)})
        rows['refinement']=stage(a,fixture,'refinement',[refiner,'--rustc-args','--edition 2021','original/lib.rs','verified/lib.rs'],env,120)
        gates=all(rows.get(name,{}).get('exit')==0 for name in ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')) and all(sha(fixture/n)==h for n,h in before.items())
        write(root/'admission-gates.json',{'gates_passed':gates,'source_pair_immutable':all(sha(fixture/n)==h for n,h in before.items()),'fragment_only':True,'all_support_exits':{n:r.get('exit') for n,r in rows.items()},'skipped_prerequisites':False})
        # Diagnostic verifier invocation is an independent admission probe if support failed.
        # It cannot receive resource proof credit unless every gate passed.
        rows['proof-ast-diagnostic']=stage(a,fixture,'proof-ast-diagnostic',[vf,'-dump_ast_with_locs','proof-ast.ml','-rustc_args','--edition 2021','verified/lib.rs'],env,90)
        ast_path=fixture/'proof-ast.ml'
        ast_record={'classification':'CAPTURED_PRE_VERIFICATION_AST' if ast_path.is_file() else 'NOT_CONFIRMED','sha256':sha(ast_path) if ast_path.is_file() else None,'stage_exit':rows['proof-ast-diagnostic'].get('exit'),'proof_verdict':None,'source_pair_pins':before,'emission_does_not_replace_mandatory_verification':True}
        native_mode=cert.get('classification')==NATIVE_ENTRY_CERT_CLASS
        native_post=(native_post_ast_evidence(ast_path,cert) if native_mode else {'status':'NOT_REQUIRED_FOR_LEGACY_MAPPING_REPLAY'})
        ast_record['native_entry_automatic_post_ast']=native_post
        write(root/'proof-ast-capture.json',ast_record)
        rows['verification']=stage(a,fixture,'verification',[vf,'-rustc_args','--edition 2021','-verbose','2','verified/lib.rs'],env,240)
        log=(fixture/'verification.log').read_text(errors='replace') if (fixture/'verification.log').exists() else ''
        errors=[line for line in log.splitlines() if ': error:' in line or line.startswith('Fatal error:') or re.search(r'\): dead code$',line)]
        entries=parser.proof_entries(log,'small_sort_general_with_scratch')
        helpers=parser.proof_entries(log,'c1_entry_identity')
        caller_ok=len(entries)==1
        typed_case=case.startswith('source-typed-')
        helper_name=('c1_source_typed_identity' if typed_case else
                     'c1_source_identity' if case in ('source-frame-positive','source-post-negative') else 'c1_entry_identity')
        helper_entries=parser.proof_entries(log,helper_name)
        helper_required=(native_mode and (typed_case or case in ('source-frame-positive','source-post-negative','bridge-positive'))) or (not native_mode and case=='bridge-positive')
        helper_ok=(not helper_required) or (len(helper_entries)==1 and caller_ok and helper_entries[0]<entries[0] and 'Leak check.' in log[helper_entries[0]:entries[0]] and ': error:' not in log[helper_entries[0]:entries[0]])
        targets=cert.get('targeted_ghost_statement_lines',{})
        identity_line=targets.get('positive_identity_lemma') if isinstance(targets,dict) else None
        source_lines=(fixture/'verified/lib.rs').read_text(errors='replace').splitlines()
        identity_call_line=(native_identity_call_target(cert,source_lines)
                            if native_mode and case=='bridge-positive' else
                            targets.get('identity_lemma_call') if isinstance(targets,dict) else None)
        source_identity_line=targets.get('source_identity_lemma') if isinstance(targets,dict) else None
        native_identity_line=(targets.get('source_typed_identity_call') if typed_case else
                              source_identity_line if case in ('source-frame-positive','source-post-negative') else identity_call_line)
        if native_mode and (typed_case or case in ('source-frame-positive','source-post-negative','bridge-positive')):
            identity_reached=(caller_ok and native_identity_line is not None and
                executed_line(log[entries[0]:],native_identity_line))
        else:
            identity_reached=(not (case=='bridge-positive' and not native_mode)) or (caller_ok and identity_line is not None and re.search(r'^\s*\d+\.\d+s: verified/lib\.rs\('+str(identity_line)+r',[^\n]*\): Executing ',log[entries[0]:],re.M) is not None)
        subset_line=targets.get('source_subset_four') if isinstance(targets,dict) else None
        subset_reached=(case not in ('source-frame-positive','source-typed-frame-positive','source-typed-missing-T-negative','source-typed-missing-F-negative')) or (caller_ok and subset_line is not None and re.search(r'^\s*\d+\.\d+s: verified/lib\.rs\('+str(subset_line)+r',[^\n]*\): Executing ',log[entries[0]:],re.M) is not None)
        caller_log=log[entries[0]:] if caller_ok else ''
        mapping=(native_entry_mapping(fixture,cert,records.get('normal',''),records.get('readonly',''),caller_log,entries[0] if caller_ok else None)
                 if native_mode else caller_mapping(root,fixture,cert,records.get('normal',''),records.get('readonly',''),caller_log,entries[0] if caller_ok else None))
        mapping_passed=mapping['status']=='PASS'
        representation_gates=gates
        gates=gates and mapping_passed and (native_post.get('status')=='PASS' if native_mode else True)
        write(root/'admission-gates.json',{
            'gates_passed':gates,
            'source_pair_immutable':all(sha(fixture/n)==h for n,h in before.items()),
            'fragment_only':True,
            'all_support_exits':{n:r.get('exit') for n,r in rows.items()},
            'source_mir_proof_mapping_status':mapping['status'],
            'source_mir_proof_mapping':mapping,
            'skipped_prerequisites':False,
        })
        leak_seen=caller_ok and 'Leak check.' in caller_log
        full_vf0=(rows['verification'].get('exit')==0 and not errors and
                  re.search(r'0 errors found \(\d+ statements verified\)',log) is not None)
        if native_mode:
            case_targets=native_case_targets_reached(case,cert,caller_log,source_lines)
            native_full_vf0=positive_full_vf0(case,
                controls_passed=getattr(a,'candidate_controls_passed',False),
                support_gates_passed=gates,source_mir_trace_passed=mapping_passed,
                verifier_exit=rows['verification'].get('exit'),proof_entries=entries,
                caller_log=caller_log,errors=errors,full_vf0_log=full_vf0,
                full_native_contract=native_post.get('status')=='PASS')
            complete=native_full_vf0 and caller_ok and helper_ok and identity_reached and subset_reached and case_targets
        else:
            case_targets=None
            complete=(getattr(a,'candidate_controls_passed',False) and gates and caller_ok and helper_ok and identity_reached and subset_reached and leak_seen and full_vf0)
        intended=False
        if native_mode:
            intended=(getattr(a,'candidate_controls_passed',False) and gates and caller_ok and
                native_expected_negative(case,cert,(fixture/'verified/lib.rs').read_bytes(),caller_log,entries,errors,rows['verification'].get('exit')))
        if gates and caller_ok and len(errors)==1 and rows['verification'].get('exit')==1 and entries[0]<log.index(errors[0]):
            if not native_mode and case=='range-negative': intended=('Cannot prove condition' in errors[0] and 'array_split' in log[entries[0]:] and 'len + 1' in log[log.index(errors[0]):])
            if not native_mode and case=='duplicate-negative': intended=('No matching heap chunks: array<T>' in errors[0] and 'DUPLICATE_AUTHORITY_CONTROL' in log[log.index(errors[0]):])
        first=errors[0] if errors else next((line for line in log.splitlines() if line.startswith('error[') or line.startswith('error:')),None)
        first_location=re.match(r'verified/lib\.rs\((\d+),',first or '')
        prefix_blocker=(not native_mode and representation_gates and caller_ok and first_location is not None and int(first_location.group(1)) < cert['targeted_ghost_statement_lines']['source_sort8_condition'])
        observed={name:[n for n in numbers if caller_ok and re.search(r'^\s*\d+\.\d+s: verified/lib\.rs\('+str(n)+r',[^\n]*\): Executing ',log[entries[0]:],re.M)] for name,numbers in cert.get('targeted_ghost_statement_line_lists',{}).items()}
        size_status=('C1_PREMISE_CONDITIONAL_ONLY; NOT_DERIVED_FROM_FULL_ACTUAL_BRANCH' if case=='bridge-positive' else 'NOT_REQUIRED_FOR_SOURCE_F_THREAD_SUBSET' if case in ('source-frame-positive','source-typed-frame-positive','source-typed-missing-T-negative','source-typed-missing-F-negative') else 'NOT_APPLICABLE_TO_CASE')
        native_class=('NATIVE_ENTRY_FULL_VF0_CONDITIONAL_MODEL' if complete and case in ('prefix-native','native-scratch-frame') else 'NATIVE_SOURCE_FRAME_AND_RETURN_FULL_VF0' if complete and case=='source-frame-positive' else 'NATIVE_TYPED_SOURCE_FRAME_AND_RETURN_FULL_VF0' if complete and case=='source-typed-frame-positive' else 'NATIVE_BRIDGE_AND_RETURN_FULL_VF0' if complete and case=='bridge-positive' else 'NATIVE_SOURCE_POST_NEGATIVE_AT_CERTIFIED_POST' if case=='source-post-negative' and intended else 'INTENDED_RESOURCE_CONTROL' if intended else 'NATIVE_ENTRY_OR_POST_ADMISSION_BLOCKER')
        legacy_class=('NATIVE_PREFIX_FULL_VF0_CONDITIONAL_MODEL' if complete and case=='prefix-native' else 'C1_ENTRY_ENTAILMENT_AND_NATIVE_FRAME_RETURN_CONDITIONAL' if complete and case=='bridge-positive' else 'SOURCE4_CURRENT_OWNERS_F_THREAD_AND_NATIVE_FRAME_RETURN_CONDITIONAL' if complete and case=='source-frame-positive' else 'INTENDED_RESOURCE_CONTROL' if intended else 'NATIVE_ENTRY_OR_PREFIX_ADMISSION_BLOCKER' if not gates or not caller_ok else 'FIRST_BRIDGE_RESOURCE_OR_CONTRACT_BLOCKER' if case=='bridge-positive' else 'INCONCLUSIVE_WRONG_FIRST_OBLIGATION')
        result.update(classification=native_class if native_mode else legacy_class,support_gates_passed=gates,verifier_exit=rows['verification'].get('exit'),first_error=first,proof_entries=len(entries),identity_helper_verified_before_caller=helper_ok,native_prefix_complete=complete if case=='prefix-native' else False,bridge_premises_derived=complete and case=='bridge-positive',bridge_actual_caller_applicability='NOT_PROVED',native_case_resource_targets_reached=case_targets,positive_size_condition=size_status,full_actual_caller_proved=False,actual_sort4_run=False,intended_resource_negative=intended,leak_seen=leak_seen,full_log_sha256=sha(fixture/'verification.log'),source_hashes=before,stages={n:r.get('exit') for n,r in rows.items()})
        result.update(identity_call_reached=identity_reached if case=='bridge-positive' else None,observed_target_statement_lines=observed,representation_and_fragment_refinement_passed=all(rows.get(n,{}).get('exit')==0 for n in ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')) and all(sha(fixture/n)==h for n,h in before.items()),proof_ast_capture=ast_record,source_mir_proof_mapping=mapping,caller_mapping_gate_passed=mapping_passed,first_prefix_proof_obligation=prefix_blocker)
        result['source_frame_subset_derived']=complete and case=='source-frame-positive'
        result['typed_source_frame_subset_derived']=complete and case=='source-typed-frame-positive'
        result['source_subset_assertion_reached']=subset_reached if case=='source-frame-positive' else None
        if case.startswith('source-typed-'):
            result['typed_source_control']={
                'classification':'TYPED_NATIVE_SOURCE_RESOURCE_DIAGNOSTIC_NOT_CALLER_PROOF',
                'positive_full_vf0':complete if case=='source-typed-frame-positive' else False,
                'missing_type_interp_negative_credit':'INCONCLUSIVE_UNTIL_FRESH_EXACT_FIRST_ERROR_REVIEW' if case!='source-typed-frame-positive' else 'NOT_APPLICABLE',
                'helper_entry_before_native_entry':bool(helper_required and helper_ok and caller_ok and helper_entries[0]<entries[0]) if helper_entries else False,
                'helper_reached':identity_reached,
                'expected_missing_obligation':'type_interp<T>' if case=='source-typed-missing-T-negative' else 'type_interp<F>' if case=='source-typed-missing-F-negative' else None,
                'source_typed_identity_helper':'c1_source_typed_identity',
                'type_chunks_claimed_from_native_heap':False,
                'actual_caller_or_sort4_applicability':False,
            }
            if case in ('source-typed-missing-T-negative','source-typed-missing-F-negative'):
                result['classification']='TYPED_SOURCE_MISSING_PRODUCER_CONTROL_UNREVIEWED'
        if prefix_blocker and case in ('prefix-native','source-frame-positive','bridge-positive'):result['classification']='NATIVE_PREFIX_PROOF_OBLIGATION_BLOCKER'
        if legacy_dead_code_vf1(errors):result['classification']='STRICT_DEAD_CODE_REJECTION_AFTER_SELECTED_PATH_FILTER'
        need(all(sha(fixture/n)==h for n,h in before.items()),'source pair changed')
    except Exception as exc:
        result.update(classification='SETUP_OR_COLLECTOR_ERROR_NOT_PROOF_VERDICT',collector_error=str(exc))
        write(root/'collector-error.json',{'reason':str(exc),'raw_preserved':True,'proof_verdict':None})
    write(root/'case-result.json',result)
    return result

def main():
    p=argparse.ArgumentParser()
    for name in ('production-source','production-applied-patch','stock-home','compiler-sysroot','evidence','proof-root','work-root','cloud-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--deadline-epoch',type=int,required=True);a=p.parse_args()
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER')=='cloud-build' and not os.environ.get('GITHUB_ACTIONS') and os.environ.get('LANE')=='o26-sort4-caller-entry','Cloud-only exact lane')
    need(all(str(getattr(a,n)).startswith('/workspace/') for n in ('production_source','evidence','proof_root','work_root','cloud_dir')),'workspace isolation')
    a.evidence.mkdir(parents=True,exist_ok=False)
    before=snapshot(a);write(a.evidence/'tool-snapshot.json',before)
    for rel in ('prelude_core.rsspec','prelude_core_core.rsspec','aliasing.rsspec','list.rsspec','std/lib.rsspec'):
        target=a.evidence/'model'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((a.production_source/'bin/rust'/rel).read_bytes())
    (a.evidence/'model/vf_mir_translator.ml').write_bytes((a.production_source/'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml').read_bytes())
    env=os.environ.copy();deps=a.work_root/'vfdeps-adf88dc';env['PATH']=str(a.production_source/'bin')+':'+str(deps/'bin')+':'+env.get('PATH','');env['LD_LIBRARY_PATH']=str(a.compiler_sysroot/'lib')+':'+str(a.production_source/'bin')+':'+str(deps/'lib');env['CAPNP_INC_DIR']=str(deps/'include');env['RUSTUP_TOOLCHAIN']='nightly-2026-09-25'
    controls=load_module(a.cloud_dir/'slice-projection-controls.py','slice_projection_controls')
    control_result=controls.run_controls(a,env)
    a.candidate_controls_passed=control_result.get('all_intended') is True
    prep=load_module(a.proof_root/'research/challenge-8/caller-entry/prepare.py','caller_prepare');capture=load_module(a.proof_root/'research/challenge-8/overnight-sort4/capture.py','caller_mir_static');parser=load_module(a.cloud_dir/'strict-cut-false-posts-audit.py','caller_proof_parser')
    rows={}
    for case in prep.CASES:
        rows[case]=run_case(a,prep,capture,parser,case,env)
        write(a.evidence/'case-results-so-far.json',rows)
    need(snapshot(a)==before,'production tool changed during bridge')
    result={'classification':'NATIVE_ENTRY_RESOURCE_DIAGNOSTIC_COMPLETE','accepted':False,'slice_projection_controls':control_result,'candidate_controls_passed':a.candidate_controls_passed,'diagnostic_complete':all('verifier_exit' in r for r in rows.values()),'source_frame_subset_derived':rows['source-frame-positive']['source_frame_subset_derived'],'typed_source_frame_subset_derived':rows['source-typed-frame-positive']['typed_source_frame_subset_derived'],'typed_missing_producer_controls_unreviewed':{name:rows[name].get('typed_source_control',{}).get('missing_type_interp_negative_credit') for name in ('source-typed-missing-T-negative','source-typed-missing-F-negative')},'bridge_premises_derived':rows['bridge-positive']['bridge_premises_derived'],'full_actual_caller_proved':False,'actual_sort4_proved':False,'c1_branch_proof_new':'NOT_RUN','c1_positive_size_premise_is_conditional':True,'source_frame_positive_size_premise_required':False,'positive_size_status_by_case':{name:row.get('positive_size_condition','NOT_CONFIRMED') for name,row in rows.items()},'cases':rows,'profile_status':'EXPERIMENTAL_O26_NATIVE_ENTRY_NOT_ACCEPTED','source_linkage':'Exact native signature and read-only source operation bytes, complete normal/readonly lemma MIR, artificial ghost boundary, proof trace; no caller CFG projection','proof_sha':os.environ['PROOF_SHA'],'tool_snapshot_sha256':sha(a.evidence/'tool-snapshot.json')}
    write(a.evidence/'diagnostic-audit.json',result);print(json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__': main()
