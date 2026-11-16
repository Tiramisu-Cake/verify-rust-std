"""Offline PROF-ON-02 intake. Structured exports plus bounded rg excerpts, never full logs.

Reuses v2 policy, v3 role rules and v4 exact binding, without OFF admissions.
No compiler, verifier, network, publication or ledger operations.
"""
import collections
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
PROFILES = HERE.parents[3]
FIX = HERE.parents[1]
sys.path.insert(0, str(FIX))
import binding_v02 as fresh
OFF = PROFILES / 'off-ci-batch/run-43784551069'
ART = Path('/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/prof02/on')
CONTROL = Path('/root/kani-ch8-prof-on-w15')
SOURCE = '166a406e2203bae2fc9246ba00c00b944b364445'
TOOL = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
TRIGGER = '5710dd6758'
sys.path[:0] = [str(OFF / 'accept-v4'), str(OFF / 'accept-v3'), str(OFF / 'accept-v2')]
import reclassify_v4 as v4
import classifier_v3 as v3
import classifier_v2 as policy


def read(p):
    return json.loads(p.read_bytes())


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def sha(p):
    # Hashing bytes does not inspect or copy raw log contents.
    return subprocess.check_output(['sha256sum', str(p)], text=True).split()[0]


def rg(path, pattern, cap, after=0):
    p = subprocess.run(['rg', '--color', 'never', '--no-heading', '--no-line-number',
                        '-m', str(cap), '-A', str(after), pattern, str(path)],
                       capture_output=True, text=True)
    v3.require(p.returncode in (0, 1), 'RG_FAILED')
    v3.require(len(p.stdout.encode()) <= max(12000, cap * (after + 1) * 4096), 'RG_BOUND')
    return p.stdout


def select_records(path, ids):
    """Select exact property IDs with at most 12 following context lines each."""
    if not ids:
        return {}
    pattern = r'^Check [0-9]+: (?:' + '|'.join(re.escape(x) for x in sorted(ids)) + r')$'
    text = rg(path, pattern, len(ids) + 1, 12)
    out = {}
    for block in re.split(r'(?=^Check )', text, flags=re.M):
        header = re.match(r'^Check [0-9]+: ([^\n]+)', block)
        if header is None or header[1] not in ids:
            continue
        m = v3.CHECK.match(block)
        v3.require(m is not None, 'PARTIAL_SELECTED_CHECK:'+header[1])
        v3.require(m[2] not in out, 'DUPLICATE_SELECTED_PROPERTY')
        v3.require(m[4].startswith('"') and m[4].endswith('"'), 'DESCRIPTION_QUOTES')
        out[m[2]] = dict(id=m[2], status=m[3], description=m[4][1:-1],
                         file=m[5], line=int(m[6]), column=int(m[7]) if m[7] else None,
                         function=m[8], stdout_check_number=int(m[1]))
    v3.require(set(out) == ids, 'SELECTED_PROPERTY_MISSING:' + str(sorted(ids-set(out))[:3]))
    return out


def record_ids(obj):
    if isinstance(obj, dict):
        if {'id', 'status', 'description'} <= obj.keys():
            yield obj['id']
        for v in obj.values():
            yield from record_ids(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from record_ids(v)


def validate_markers(marker,row,h):
    # Five expected markers plus one sentinel: any extra match invalidates the row.
    v3.require(len(marker.splitlines())==5,'MARKER_COUNT')
    v3.require(v3.MARKER.findall(marker)==[row['selector']],'HARNESS_MARKER')
    verdict='SUCCESSFUL' if h['outcome']['verdict']=='SUCCESS' else 'FAILED'
    v3.require(re.findall(r'^VERIFICATION:- (\S+)\s*$',marker,re.M)==[verdict],'TERMINAL_VERDICT')
    v3.require(len(re.findall(r'^Verification Time: [0-9.]+s\s*$',marker,re.M))==1,'VERIFICATION_TIME')
    v3.require(len(re.findall(r'^RESULTS:\s*$',marker,re.M))==len(re.findall(r'^SUMMARY:\s*$',marker,re.M))==1,'BOUNDARIES')


def stdout_inventory(path, row, h, receipt, group, compilation):
    """All ID/status *lines* are bounded by export count; no full-log read."""
    count = h['n_properties']
    text = rg(path, r'^Check [0-9]+: |^[ \t]+- Status: ', 2 * count + 1)
    pairs = re.findall(r'^Check ([0-9]+): ([^\n]+)\n[ \t]+- Status: ([A-Z_]+)$', text, re.M)
    v3.require(len(pairs) == count and len(text.splitlines()) == 2*count, 'INVENTORY_SIZE')
    v3.require([int(p[0]) for p in pairs] == list(range(1, count+1)), 'CHECK_SEQUENCE')
    statuses = {p[1]: p[2] for p in pairs}
    v3.require(len(statuses) == count, 'DUPLICATE_CHECK_ID')
    counts = collections.Counter(statuses.values())
    expected = {'SUCCESS': h['checks']['success'], 'FAILURE': len(h['checks']['failure']),
                'UNREACHABLE': len(h['checks']['unreachable'])+len(h['covers']['unreachable']),
                'SATISFIED': len(h['covers']['satisfied']), 'UNSATISFIABLE':len(h['covers']['unsatisfiable'])}
    v3.require(dict(counts) == {k:v for k,v in expected.items() if v}, 'STATUS_COUNTS:'+row['id']+str(counts))
    for bucket, status in [('failure','FAILURE'), ('unreachable','UNREACHABLE')]:
        cover_ids=set(h['covers']['unreachable']) if bucket=='unreachable' else set()
        v3.require({p for p,s in statuses.items() if s == status} == set(h['checks'][bucket])|cover_ids, 'CHECK_BUCKET')
    v3.require({p for p,s in statuses.items() if s == 'SATISFIED'} == set(h['covers']['satisfied']), 'COVER_BUCKET')
    marker = rg(path, r'^Checking harness |^VERIFICATION:|^Verification Time:|^RESULTS:|^SUMMARY:', 6)
    validate_markers(marker,row,h)
    v3.require(receipt['id'] == row['id'] and receipt['selector'] == h['name'] == row['selector'], 'ROW_BINDING')
    v3.require(receipt['group'] == group['id'] and receipt['group_export_sha256'] == group['export_sha256'], 'GROUP_BINDING')
    v3.require(receipt['group_receipt'] == 'groups/'+group['id']+'/receipt.json', 'GROUP_RECEIPT_PATH')
    ex = group['execution']
    v3.require(group['state'] == 'OBSERVED' and all(ex[k] is False for k in
        ('stdout_truncated','stderr_truncated','output_truncated','timed_out')), 'TRUNCATED_OR_INTERRUPTED')
    v3.require(ex['signal'] is None and ex.get('termination_reason') is None, 'INTERRUPTED')
    v3.require(ex['compilation'] == compilation and compilation['state'] == 'PRE_HARNESS_COMPLETE', 'COMPILE_RECEIPT')
    order = compilation['harness_marker_order']
    v3.require(len(order) == len(set(order)) == len(group['rows']) and set(order) == set(group['rows']), 'MARKER_ORDER')
    v3.require(0 < path.stat().st_size == compilation['row_output_bytes'][row['id']]['stdout'] < receipt['stdout_cap_bytes'], 'OUTPUT_SIZE')
    return statuses, dict(state='BOUND_INVENTORY_AND_TARGETED_RECORDS', stdout_sha256=sha(path),
                          stdout_bytes=path.stat().st_size, parsed_id_status_pairs=count,
                          method='rg -m (2*n_properties+1) ID/status lines; exact-ID rg -m (selected+1) -A12',
                          receipt_sha256=sha(path.parent/'receipt.json'))


def instrumentation_role(p):
    # Concrete source-site families; never a blanket kani::mem_init exemption.
    add='attempt to add with overflow'; sub='attempt to subtract with overflow'
    mul='attempt to multiply with overflow'; rem='attempt to calculate the remainder with a divisor of zero'
    idx='index out of bounds: the length is less than or equal to the given index'
    sites={'MemoryInitializationState::get':{93:{add},95:{sub,idx}},
           'MemoryInitializationState::set':{118:{add},120:{sub,idx}},
           'MemoryInitializationState::copy_by_id':{166:{add,mul},171:{add,sub},173:{sub,rem,idx},181:{add,mul},183:{sub,rem,idx}},
           'MemoryInitializationState::get_slice':{204:{add,mul},206:{sub,rem,idx}},
           'MemoryInitializationState::set_slice':{230:{add,mul},232:{sub,rem,idx}},
           'store_argument':{479:{add},488:{sub}},'load_argument':{537:{add},539:{idx},543:{sub}}}
    columns={(93,add):46,(95,sub):29,(95,idx):22,(118,add):46,(120,sub):41,(120,idx):34,
             (166,add):46,(166,mul):60,(171,sub):59,(171,add):47,(173,sub):46,(173,rem):46,(173,idx):39,
             (181,add):46,(181,mul):58,(183,sub):41,(183,rem):41,(183,idx):34,
             (204,add):46,(204,mul):55,(206,sub):29,(206,rem):29,(206,idx):22,
             (230,add):46,(230,mul):55,(232,sub):41,(232,rem):41,(232,idx):34,
             (479,add):21,(488,sub):28,(537,add):25,(539,idx):65,(543,sub):17}
    family=p['function'].removeprefix('kani::mem_init::').split('::<')[0]
    if (p['function'].startswith('kani::mem_init::') and family in sites and
            p['file']=='library/kani_core/src/mem_init.rs' and
            p['description'] in sites[family].get(p['line'],set())
            and p['column']==columns.get((p['line'],p['description']))
            and re.fullmatch(re.escape(p['function'])+r'\.assertion\.[1-9][0-9]*',p['id'])):
        return dict(p, role='instrumentation_defensive_branch', rule='ON-mem-init-exact-sites',
                    property_location={k:p[k] for k in ('file','line','column')},
                    target_wrapper_relation='GHOST_SHADOW_STATE_BOOKKEEPING',
                    reason='Error branch of bounded shadow-byte bookkeeping/argument transfer; not an initialization predicate result or target post/frame/relation. Zero-size loops skip body; reverse copy uses guarded offsets; argument loops use their fixed layout. No failed check waived.',
                    decision='ALLOWED_INSTRUMENTATION_ONLY_UNREACHABLE')
    return None


def required_role(p, sources):
    """Recognize literal source clauses, independently of assertion ordinals."""
    source=sources.get(p['file'])
    if source is None or not 1<=p['line']<=len(source.splitlines()): return None
    line=source.splitlines()[p['line']-1].strip()
    role=None
    if line.startswith('#[kani::ensures(') and v4.compact(p['description'])==v4.compact(v4.clause(source,p['line'],'ensures')):
        role='postcondition'
    elif line.startswith('#[kani::requires(') and v4.compact(p['description'])==v4.compact(v4.clause(source,p['line'],'requires')):
        role='required_section'
    elif 'assert!' in line and ('consumer' in p['description'] or 'adapter' in p['description']):
        role='required_section'
    if role:
        return dict(p,role=role,rule='ON-literal-source-obligation',
            property_location={k:p[k] for k in ('file','line','column')},
            reason='Literal required source contract clause/assertion is unreachable; no exemption.',
            target_wrapper_relation='REQUIRED_TARGET_WRAPPER_OBLIGATION')
    return None


def decision(row, h, result, tool_failures):
    # A known tool failure is a blocker even when subsequent obligations are unknown.
    # Unknowns are retained in the receipt, never converted into admission.
    if tool_failures:
        tool_ids={p['id'] for p in tool_failures}
        non_tool=set(h['checks']['failure'])-tool_ids
        named={p['id'] for p in result.get('negative_oracle_records',[])}
        if non_tool and (row['expected']=='SUCCESS' or not non_tool<=named): return 'REJECTED'
        return 'BLOCKED_TOOL'
    if result['unknown_reasons']: return 'PENDING'
    if row['expected']=='SUCCESS' and h['checks']['failure']: return 'REJECTED'
    if row['expected']!='SUCCESS' and 'PREDECLARED_NEGATIVE_ORACLE_MISMATCH' in result['pending_reasons']:
        return 'REJECTED'
    return 'PENDING' if result['pending_reasons'] else 'ACCEPTED'


def bind_covers(mapping, records, sources, row):
    # Reuse the exact v4 cover-binding implementation without its PFC prelude.
    code = (FIX/'binding_v02.py').read_text()
    body = code[code.index('    covers = []\n'):code.index("    if row['id'] == FRAME:\n",code.index('    covers = []\n'))]
    ns = dict(fresh.__dict__)
    exec('def checked(row, old, mapping, records, sources):\n    out = {}\n'+body+'    return out\n',ns)
    return ns['checked'](row, {'cover_mapping':mapping['coverage']}, mapping, records, sources)


def fresh_unsupported_links(h, records):
    links = {}
    for u in h['unsupported_constructs']:
        p = records[u['id']]
        v3.require(u['class']=='unsupported_construct' and
                   re.search(r'\.unsupported_construct\.[1-9][0-9]*$',u['id']) and
                   p['status']==u['status'] and p['description']==u['description'] and
                   u['file'].endswith('/'+p['file']) and int(u['line'])==p['line'], 'UNSUPPORTED_EXACT_RECORD')
        links[u['id']]=dict(id=u['id'],description=u['description'],line=u['line'],file_suffix=p['file'],
            semantics='assert(false); assume(false)',tool_commit=TOOL,
            origin='PINNED_PROPERTY_CLASS_EXPORT_AND_ALL_UNSUPPORTED_GENERATORS',
            assert_then_assume='kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs:129-145,214-220,278-324',
            export_exact_id_status_class='kani-driver/src/frontend/schema_utils.rs:495-505,768-772',
            assurance='Exact same-row ID/class/status/description/site; shared generator semantics, no construct support claim')
    return links


def negative_oracles(row,h,records,sources):
    out=[]
    for failure in h['failed_properties']:
        p=records[failure['id']]
        if not any(d in failure['description'] for d in row['allowed_failure_descriptions']):continue
        v3.require(p['description'] in row['allowed_failure_descriptions'],'NEGATIVE_EXACT_DESCRIPTION')
        v3.require(p['status']=='FAILURE' and p['function']==row['selector'] and
                   re.fullmatch(re.escape(row['selector'])+r'\.assertion\.[1-9][0-9]*',p['id']) and
                   p['file']==row['source_file'],'NEGATIVE_SOURCE_FUNCTION')
        tail='\n'.join(sources[p['file']].splitlines()[p['line']-1:]).lstrip()
        v3.require(tail.startswith('kani::assert('),'NEGATIVE_SOURCE_ASSERT')
        depth=1;start=len('kani::assert(');end=None
        for index in range(start,len(tail)):
            depth+=(tail[index]=='(')-(tail[index]==')')
            if depth==0:end=index;break
        v3.require(end is not None and '"'+p['description']+'"' in tail[start:end], 'NEGATIVE_LITERAL_ORACLE')
        out.append(dict(p,oracle_binding='EXACT_PREDECLARED_DESCRIPTION_AND_PINNED_SOURCE_ASSERT_FUNCTION_SITE'))
    return out


def main():
    off = read(OFF/'accept-v4/ACCEPT.json')
    previous_on_path = PROFILES/'on-ci/run-43798838603/accept/ACCEPT.json'
    previous = {r['id']:r for r in read(previous_on_path)['rows']}
    mappings = fresh.SPEC
    rules = read(OFF/'accept-v3/ROLE-RULES.json')['rules']
    reuse = read(PROFILES/'on-ci/CLASSIFIER-REUSE.json')
    for p,digest in reuse['files'].items():
        v3.require(sha(ROOT/p)==digest,'CLASSIFIER_REUSE_HASH:'+p)
    package=read(FIX/'CI-REQUEST.json')
    v3.require(sha(FIX/'BINDING-SPEC.json')==package['binding_spec_sha256'], 'FRESH_SPEC_HASH')
    v3.require(sha(FIX/'binding_v02.py')==package['binding_adapter_sha256'], 'FRESH_ADAPTER_HASH')
    for name in ('runner.py','CI-REQUEST.json','manifest.json','kani-version.toml'):
        v3.require((HERE/'runner-input'/name).read_bytes()==git(CONTROL,'show',TRIGGER+':ch8-prof-on-control/'+name), 'EXECUTED_RUNNER_INPUT:'+name)
    spec = importlib.util.spec_from_file_location('on_runner',HERE/'runner-input/runner.py')
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    request_bytes = git(CONTROL,'show',TRIGGER+':ch8-prof-on-control/CI-REQUEST.json')
    request = runner.load_request(HERE/'runner-input/CI-REQUEST.json')
    v3.require((HERE/'runner-input/CI-REQUEST.json').read_bytes()==request_bytes,'REQUEST_CHANGED')
    v3.require(read(ART/'job-status.json')['request_sha256']==v3.digest(request_bytes)==package['lanes']['on']['request_sha256'],'REQUEST_RECEIPT_HASH')
    v3.require(request['manifest_sha256']==mappings['manifest_sha256'], 'FRESH_SPEC_MANIFEST_HASH')
    rows = request['rows']; v3.require(len(rows)==63 and {r['id'] for r in rows}==set(mappings['rows']) and set(previous)<{r['id'] for r in rows},'ROW_SET')
    sources = {p:git(ROOT,'show',SOURCE+':'+p).decode() for p in mappings['source_files_sha256']}
    for p,d in mappings['source_files_sha256'].items():
        v3.require(v3.digest(sources[p].encode())==d,'SOURCE_HASH:'+p)
    # Carry the reviewed role only across the exact unchanged source clause.
    region_path='library/core/src/slice/sort/shared/smallsort/verify/merge.rs'
    old_region=git(ROOT,'show',off['source_commit']+':'+region_path).decode().splitlines()
    new_region=sources[region_path].splitlines()
    v3.require(old_region[110]==new_region[113] and 'd >= n as isize || -d >= m as isize' in new_region[113], 'REGION_ROLE_SOURCE_DRIFT')
    region_rule=next(r for r in rules if r['id']=='region-distance-negate')
    v3.require(region_rule['lines']==[111], 'REGION_PRIOR_ROLE_DRIFT')
    region_rule['lines']=[114]
    region_rule['id']='prof02-region-distance-negate-exact-source-translation'
    tool_hashes = {}
    for p in v4.TOOL_FILES + ['kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs']:
        data = git(CONTROL,'show',TOOL+':'+p)
        v3.require(data==git(CONTROL,'show',off['tool_commit']+':'+p),'TOOL_BINDING_CHAIN_CHANGED:'+p)
        tool_hashes[p]=v3.digest(data)
    for p in ['library/kani_core/src/mem_init.rs','library/kani_core/src/lib.rs','library/kani_core/src/mem.rs',
              'kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs',
              'kani-compiler/src/codegen_cprover_gotoc/codegen/foreign_function.rs',
              'kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs',
              'kani-compiler/src/kani_middle/transform/check_uninit/mod.rs',
              'kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs',
              'kani-compiler/src/kani_middle/transform/body.rs']:
        tool_hashes[p]=v3.digest(git(CONTROL,'show',TOOL+':'+p))
    overall = read(ART/'receipt.json')
    v3.require(overall['std_sha']==SOURCE and overall['tool_sha']==TOOL,'TOP_IDENTITIES')
    exports, groups = {}, {}
    for gp in sorted((ART/'groups').iterdir()):
        e=read(gp/'export.json'); g=read(gp/'receipt.json'); c=read(gp/'compile-receipt.json')
        v3.require(sha(gp/'export.json')==g['export_sha256'],'EXPORT_HASH')
        selected=[r for r in rows if r['id'] in g['rows']]
        v3.require(g['cfg']==selected[0]['cfg'] and all(r['cfg']==g['cfg'] for r in selected),'CFG')
        argv=g['argv']
        expected_argv=runner.build_argv(Path(argv[4]).parent,Path(argv[0]).parents[1],
            [r['selector'] for r in selected],None,Path(argv[argv.index('--export-json')+1]))
        v3.require(argv==expected_argv,'EXACT_ARGV')
        v3.require(g['environment']['RUSTFLAGS']==('' if not g['cfg'] else '--cfg kani_smallsort_controls'),'CFG_ENV')
        v3.require(g['source_before']==g['source_after'] and
                   g['source_before']['std_sha']==SOURCE and g['source_before']['tool_sha']==TOOL and
                   g['source_before']['std_tree']==request['std_tree'] and
                   g['source_before']['tool_tree']==request['tool_tree'] and
                   g['source_before']['changed_file_sha256']==request['changed_file_sha256'],'GROUP_SOURCE_PINS')
        before=g['tool_fingerprints_before'];after=g['tool_fingerprints_after']
        v3.require(before['required_hashes_present'] is True and after['required_hashes_present'] is True and
                   before['binaries']==after['binaries'] and after['reported_versions']==e['tools'] and
                   after['target']==after['expected_target']==runner.TARGET,'TOOL_FINGERPRINTS')
        groups[gp.name]=dict(export_sha256=sha(gp/'export.json'),receipt_sha256=sha(gp/'receipt.json'),
                             compile_receipt_sha256=sha(gp/'compile-receipt.json'),cfg=g['cfg'])
        for i,h in enumerate(e['harnesses']):
            v3.require(h['name'] not in exports,'DUPLICATE_HARNESS')
            exports[h['name']]=(gp,h,g,c,selected,i)
    symbols = sorted({h['contract']['contracted_function_name'] for _,h,_,_,_,_ in exports.values() if h['contract']})
    names=subprocess.check_output(['c++filt','-i','-s','rust'],input='\n'.join(symbols)+'\n',text=True).splitlines()
    v3.require(len(names)==len(symbols) and all(a!=b for a,b in zip(symbols,names)),'DEMANGLE')
    demangled=dict(zip(symbols,names)); results=[]
    for row in rows:
        rid=row['id']; old=previous.get(rid); mapping=copy.deepcopy(mappings['rows'][rid])
        mode_row=dict(row,mode=row.get('profile_mode',row['mode']))
        binding=mapping['binding']
        target=binding['source_target'].get('fully_qualified')
        decl=mapping['source_function_decl_line']
        source_prefix='\n'.join(sources[row['source_file']].splitlines()[max(0,decl-15):decl]) if decl else ''
        attr=re.findall(r'#\[kani::proof_for_contract\(([^)]+)\)\]',source_prefix)
        source_expression=attr[-1] if row['mode']=='PFC' and attr else binding['source_target'].get('source_expression')
        if row['mode']=='PFC' and not decl:
            v3.require('#[kani::proof_for_contract('+str(source_expression)+')]' in sources[row['source_file']], 'MACRO_SOURCE_ATTRIBUTE_MISSING')
        v3.require(row['mode']!='PFC' or source_expression is not None,'SOURCE_ATTRIBUTE_ABSENT:'+rid)
        binding.update(harness_fully_qualified=row['source_selector'],source_file=row['source_file'],
            source_target_expression=source_expression,target_status='BOUND',
            wrapper_status='PENDING' if row['mode']=='PFC' or mode_row['mode'].startswith('Replace:') else 'NOT_APPLICABLE',
            verified_stubs=[target] if mode_row['mode'].startswith('Replace:') else [])
        gp,h,g,c,group_rows,index=exports[row['selector']]
        pre=runner.parse_export(gp/'export.json',row,group_rows=group_rows)
        receipt=read(ART/rid/'receipt.json')
        statuses,stdout=stdout_inventory(ART/rid/'stdout.log',row,h,receipt,g,c)
        selected=set(h['checks']['unreachable']+h['checks']['failure']+
                     [x for v in h['covers'].values() if isinstance(v,list) for x in v])
        selected.update(u['id'] for u in h['unsupported_constructs'])
        selected.update(p for p in statuses if p.startswith('kani::internal::write_any_slice::') and '.safety_check.' in p)
        # Fresh same-row property selection; historical property IDs never drive binding.
        if row['mode']=='PFC' or mode_row['mode'].startswith('Replace:'):
            instance=fresh.expected_instance(mode_row,mapping)
            prefixes=(instance, fresh.relative(instance))
            selected.update(pid for pid in statuses if '.assigns.' in pid or
                any(pid.startswith(prefix+'::') or pid.startswith(prefix+'.') for prefix in prefixes))
        # Missing old properties are not silently omitted: this is a binding failure.
        records=select_records(ART/rid/'stdout.log', selected)
        v3.require(all(statuses[p]==v['status'] for p,v in records.items()),'SELECTED_STATUS')
        for failure in h['failed_properties']:
            p=records[failure['id']]
            v3.require(p['status']==failure['status'] and p['description']==failure['description'] and
                       failure['file'].endswith('/'+p['file']) and int(failure['line'])==p['line'],
                       'FAILED_EXPORT_STDOUT_SITE_MISMATCH')
        links=fresh_unsupported_links(h,records)
        role_reviews={}
        for pid in h['checks']['unreachable']:
            p=records[pid]; instr=instrumentation_role(p)
            role_reviews[pid]=instr or required_role(p,sources) or v3.role(p,rules)
        # The v2 engine expects defensive_branch; retain the separate ON category in receipt.
        engine_roles=copy.deepcopy(role_reviews)
        for p in engine_roles.values():
            if p['role']=='instrumentation_defensive_branch': p['role']='defensive_branch'
        if h['contract']:
            mapping['binding']['export_contract_symbol']=h['contract']['contracted_function_name']
        result=policy.classify(row,h,mapping,links,engine_roles,pre['state'])
        result.update(expected=row['expected'],mode=row.get('profile_mode',row['mode']),profile=row.get('profile'),
                      identity=dict(source_commit=SOURCE,source_tree=request['std_tree'],tool_commit=TOOL,
                                    tool_tree=request['tool_tree'],configuration=read(gp/'export.json')['configuration'],
                                    enabled_unstable_features=read(gp/'export.json')['enabled_unstable_features'],cfg=row['cfg']),
                      checks=h['checks'],covers=h['covers'],named_failures=h['failed_properties'],
                      stdout_binding=stdout,preflight_state=pre['state'],
                      evidence=dict(export_member=str((gp/'export.json').relative_to(ART)),
                                    export_sha256=g['export_sha256'],harness_index=index),
                      unreachable=[dict(role_reviews[pid],decision=next((u['decision'] for u in result['unreachable'] if u['id']==pid),'UNKNOWN'))
                                   for pid in h['checks']['unreachable']])
        for u in result['unreachable']:
            if u['role']=='instrumentation_defensive_branch': u['decision']='ALLOWED_INSTRUMENTATION_ONLY_UNREACHABLE'
        if row['expected']!='SUCCESS':
            result['negative_oracle_records']=negative_oracles(row,h,records,sources)
        try:
            fresh_old={'binding':mapping['binding'],'cover_mapping':mapping['coverage']}
            mode_row=dict(row,mode=row.get('profile_mode',row['mode']))
            if row['mode']=='PFC' or mode_row['mode'].startswith('Replace:'):
                result['exact_instance_identity']=fresh.expected_instance(mode_row,mapping)
                bound=fresh.bind_fresh(mode_row,h,records,demangled,sources)
                result['exact_binding_v4']=bound
                result['binding']['wrapper_status']='BOUND'
                result['pending_reasons']=[p for p in result['pending_reasons'] if p not in
                    {'EXACT_CONTRACT_WRAPPER_BINDING_PENDING','PREDECLARED_FRAME_ORACLE_BINDING_PENDING'}]
            else:
                # Cover-only rows use the same fresh source/site binder's cover section.
                result['exact_binding_v4']=bind_covers(mapping,records,sources,mode_row)
            result['binding_state']='BOUND'
        except (KeyError,ValueError,TypeError) as exc:
            result['binding_state']='PENDING'
            result['fresh_binding_observations']=records
            result['pending_reasons'].append('FRESH_BINDING:'+str(exc))
        failures=h['failed_properties']
        tool_failures=[p for p in failures if (p['class']=='unsupported_construct' and
                       'memory initialization' in p['description'].lower()) or
                       p['id'] in {'kani::internal::write_any_slice::<u8>.safety_check.1','kani::internal::write_any_slice::<u64>.safety_check.1'}]
        result['tool_failures']=tool_failures
        result['tool_failure_binding']=[dict(property=records[p['id']],export_class=p['class'],
            relation=('GENERATED_KANI_UNINIT_UNSUPPORTED_CHECK_AT_STD_SITE' if p['class']=='unsupported_construct' else
                      'KANI_REPLACE_HAVOC_MODEL_CHECK; diagnostic core/lib.rs:357 is not model implementation lib.rs:716'),
            failure_property_in_algorithm_body=False,causal_trace='NOT_ESTABLISHED',
            supplemental_havoc_checks=[q for pid,q in records.items() if pid.startswith('kani::internal::write_any_slice::') and '.safety_check.' in pid])
            for p in tool_failures]
        result['non_tool_failure_ids']=[p['id'] for p in failures if p not in tool_failures]
        result['sole_failure_is_tool_instrumentation']=len(failures)==len(tool_failures)==1
        policy.finish(result)
        result['status']=decision(row,h,result,tool_failures)
        result['previous_on_comparison']=dict(
            previous_run=43798838603, status=old['status'] if old else 'NEW_ROW',
            previous_failure_ids=old['checks']['failure'] if old else [],
            current_failure_ids=h['checks']['failure'],
            unreachable_added=sorted(set(h['checks']['unreachable'])-set(old['checks']['unreachable'] if old else [])),
            unreachable_removed=sorted(set(old['checks']['unreachable'] if old else [])-set(h['checks']['unreachable'])),
            previous_covers=old['covers'] if old else None,current_covers=h['covers'],
            previous_target=(old.get('exact_instance_identity') if old else None),
            current_target=result.get('exact_instance_identity'))
        result['original_receipt']=dict(status=receipt['status'],outcome=receipt['outcome'],
            original_exit=receipt['original_exit'],signal=receipt['signal'],exit_scope=receipt['exit_scope'])
        results.append(result)
    by_id={r['id']:r for r in results}
    for row in rows:
        if not row.get('profile_mode','').startswith('Replace:'): continue
        r=by_id[row['id']];leaf=by_id[row['leaf_companion']]
        a=r.get('exact_instance_identity')
        b=leaf.get('exact_instance_identity')
        same_tuple=r['identity']==leaf['identity']
        r['consumer_leaf']=dict(id=leaf['id'],status=leaf['status'],exact_instance_match=a is not None and a==b,
                                identical_source_tool_config=same_tuple)
        if leaf['status']!='ACCEPTED' or a is None or a!=b or not same_tuple:
            r['pending_reasons'].append('MATCHING_LEAF_NOT_ACCEPTED')
            if r['status']=='ACCEPTED':r['status']='PENDING'
    counts=collections.Counter(r['status'] for r in results)
    summary=dict(rows=len(results),statuses={s:counts[s] for s in ('ACCEPTED','BLOCKED_TOOL','REJECTED','PENDING')},
        unreachable_roles=dict(collections.Counter(u['role'] for r in results for u in r['unreachable'])),
        covers=dict(collections.Counter(k for r in results for k,v in r['covers'].items() if isinstance(v,list) for _ in v)),
        tool_blocked_rows=[r['id'] for r in results if r['status']=='BLOCKED_TOOL'],
        pending_rows={r['id']:r['unknown_reasons']+r['pending_reasons'] for r in results if r['status']=='PENDING'})
    result=dict(schema='ch8-prof-on-02-intake-v1',g0_input='7d1ae3dd048e50b245817fadbcdfb4244153669c',
        source_commit=SOURCE,tool_commit=TOOL,control_trigger=git(CONTROL,'rev-parse',TRIGGER).decode().strip(),
        run=43808894294,artifact_id=14203740678,artifact_directory=str(ART),
        assurance='BOUNDED_SOURCE_REPORTED_POLICY_ADMISSION; NOT_INDEPENDENT_PROOF',proof_credit='NONE',
        prior_admissions_reused=0,source_files_sha256=mappings['source_files_sha256'],tool_sources_sha256=tool_hashes,
        request_sha256=v3.digest(request_bytes),previous_on_accept_sha256=sha(previous_on_path),
        classifier_dependencies_sha256=reuse['files'],group_identities=groups,summary=summary,rows=results)
    result['intake_sources_sha256']={str(p.relative_to(ROOT)):sha(p) for p in
        [HERE/'intake.py',HERE/'test_intake.py',FIX/'binding_v02.py',FIX/'BINDING-SPEC.json', *sorted(p for p in (HERE/'runner-input').iterdir() if p.is_file())]}
    result['artifact_binding_limitation']='Directory-to-artifact ID is coordinator-reported; no independent archive attestation.'
    (HERE/'ACCEPT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='pending_rows'},indent=2))


if __name__=='__main__':
    main()
