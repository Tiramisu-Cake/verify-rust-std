"""Fresh OFF accept-v4 intake. No historical admissions or full raw-log reads."""
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
FIX = HERE.parents[1]
PROFILES = FIX.parents[1]
OFF = PROFILES / 'off-ci-batch/run-43784551069'
ART = Path('/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/prof02/off')
CONTROL = Path('/root/kani-ch8-prof02-w11')
TRIGGER = '5710dd67580bb62749a8b25c4c4f685780dfc2c8'
SOURCE = '166a406e2203bae2fc9246ba00c00b944b364445'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
sys.path[:0] = [str(FIX), str(OFF/'accept-v4'), str(OFF/'accept-v3'), str(OFF/'accept-v2')]
import binding_v02 as binding
import classifier_v3 as v3
import classifier_v2 as policy
import reclassify_v4 as v4


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value

helpers = module('previous_on_helpers', PROFILES/'on-ci/run-43798838603/accept/intake.py')
helpers.TOOL = TOOL
read, git, sha = helpers.read, helpers.git, helpers.sha


def mapping_for(row, h, sources):
    mapping = copy.deepcopy(binding.SPEC['rows'][row['id']])
    mode = row['profile_mode']
    target = mapping['binding']['source_target']
    expr = target.get('source_expression')
    if row['id'] == 'profile_merge4_contract_u8_len4':
        expr = 'profiles::merge4_profile'
    if row['mode'] == 'PFC':
        v3.require(expr is not None, 'SOURCE_TARGET_EXPRESSION_ABSENT')
        v3.require('#[kani::proof_for_contract('+expr+')]' in sources[row['source_file']],
                   'SOURCE_PROOF_ATTRIBUTE_ABSENT')
    stubs = [target['fully_qualified']] if mode.startswith('Replace:') else []
    mapping['binding'].update(target_status='BOUND', source_target_expression=expr,
        export_contract_symbol=(h['contract'] or {}).get('contracted_function_name'),
        harness_fully_qualified='core::'+row['selector'], source_file=row['source_file'],
        verified_stubs=stubs, wrapper_status='PENDING' if row['mode']=='PFC' or stubs else 'NOT_APPLICABLE',
        assurance='FRESH_PINNED_SOURCE_SPEC_AND_EXACT_ATTRIBUTE_BINDING')
    return mapping


def checked_preflight(runner, path, row, group_rows):
    original = runner.parse_export(path,row,group_rows=group_rows)
    # Legacy terminal-name predicate rejects qualified source expressions before
    # config/unwind checks. Re-run remaining mature guards; policy separately
    # enforces the complete predeclared source expression, never terminal names.
    checked_row = dict(row)
    checked_row.pop('profile_mode',None)
    checked = runner.parse_export(path,checked_row,group_rows=group_rows)
    v3.require(original['state'] in {'SOURCE_STAGE_TARGET_MISMATCH','INCOMPLETE_CHECK_INVENTORY','VALIDATED_OBSERVATION','FRAME_BINDING_REVIEW_REQUIRED'}, 'ORIGINAL_PREFLIGHT:'+original['state'])
    v3.require(checked['state'] in {'INCOMPLETE_CHECK_INVENTORY','VALIDATED_OBSERVATION','FRAME_BINDING_REVIEW_REQUIRED'}, 'CHECKED_PREFLIGHT:'+checked['state'])
    return original, checked


def select(path, ids):
    # Keep each raw-log query bounded to twenty exact IDs and A12 context.
    result = {}
    ids = sorted(ids)
    for start in range(0,len(ids),20):
        result.update(helpers.select_records(path,set(ids[start:start+20])))
    return result


def fresh_roles(rules,sources):
    rules=copy.deepcopy(rules)
    rule=next(r for r in rules if r['id']=='region-distance-negate')
    path=binding.DIR+'/verify/merge.rs'
    old=git(ROOT,'show','9fa2f7f97760584f38738909625c064006d8a936:'+path).decode()
    def section(text):
        start=text.index('pub(crate) fn regions_are_disjoint<T>')
        return text[start:text.index('\n}',start)+2]
    v3.require(section(old)==section(sources[path]),'REGION_HELPER_CHANGED')
    v3.require(old.splitlines()[110]==sources[path].splitlines()[113] and
               sources[path].splitlines()[113].strip()=='d >= n as isize || -d >= m as isize',
               'REGION_NEGATION_SITE_CHANGED')
    rule['lines']=[114]
    rule['id']='prof02-region-distance-negate-unchanged-source'
    return rules


def bind_negative(row,h,records,sources):
    if row['id']==binding.FRAME:return []  # dedicated semantic frame binder
    out=[]
    for pid in h['checks']['failure']:
        p=records[pid]
        v3.require(p['function']==row['selector'] and p['file']==row['source_file'] and
                   re.fullmatch(re.escape(row['selector'])+r'\.assertion\.[1-9][0-9]*',pid),
                   'NEGATIVE_HARNESS_SITE_MISMATCH')
        v3.require(p['description'] in row['allowed_failure_descriptions'],'NEGATIVE_EXACT_ORACLE_MISMATCH')
        lines=sources[p['file']].splitlines()
        tail='\n'.join(lines[p['line']-1:])
        v3.require(tail.lstrip().startswith('kani::assert('),'NEGATIVE_NOT_NAMED_SOURCE_ASSERT')
        statement=tail[:tail.index(');')+2]
        v3.require('"'+p['description']+'"' in statement,'NEGATIVE_SOURCE_CLAUSE_MISMATCH')
        out.append(dict(property=p,source_statement=statement,predeclared_description=p['description'],
                        relation='EXACT_SAME_HARNESS_SOURCE_ASSERTION_AND_PREDECLARED_ORACLE'))
    return out


def bind_covers(row,mapping,records,sources):
    mapping=copy.deepcopy(mapping)
    corrections=[]
    if row['id']=='rejects_always_true':
        predicted=copy.deepcopy(mapping['covers'])
        for c in mapping['covers']:
            p=records[c['id']]
            found=[d for d in predicted if '"'+p['description']+'"' in d['source_expression']]
            v3.require(len(found)==1,'NEGATIVE_COVER_LITERAL_AMBIGUOUS')
            d=found[0]
            v3.require(p['line']==d['source_line'] and p['function']==row['selector'] and
                       sources[d['source_file']].splitlines()[d['source_line']-1].strip()==d['source_expression'],
                       'NEGATIVE_COVER_EXACT_SOURCE_MISMATCH')
            corrections.append(dict(id=c['id'],predicted_line=c['source_line'],observed_line=p['line'],description=p['description']))
            c.update(d,id=p['id'])
    # The reviewed v4 cover binder has no contract-specific prelude.
    code = (FIX/'binding_v02.py').read_text()
    body = code[code.index('    covers = []\n'):code.index("    if row['id'] == FRAME:\n",code.index('    covers = []\n'))]
    ns = dict(binding.__dict__)
    exec('def checked(row, old, mapping, records, sources):\n    out = {}\n'+body+'    return out\n',ns)
    out=ns['checked'](row,{'cover_mapping':mapping['coverage']},mapping,records,sources)
    out['cover_prediction_corrections']=corrections
    return out


def consumers_after_leaves(rows,results):
    by_id={r['id']:r for r in results}
    for row in rows:
        if not row['profile_mode'].startswith('Replace:'):continue
        r,leaf=by_id[row['id']],by_id[row['leaf_companion']]
        instance=r.get('exact_instance_identity')
        exact=instance is not None and instance==leaf.get('exact_instance_identity')
        r['consumer_leaf']=dict(id=leaf['id'],status=leaf['status'],exact_instance_match=exact,
            source_tool_config_tuple_match=r['evidence']['export_sha256']==leaf['evidence']['export_sha256'],lane='off',run=43808894294)
        if leaf['status']!='ACCEPTED' or not exact or not r['consumer_leaf']['source_tool_config_tuple_match']:
            r['pending_reasons'].append('MATCHING_LEAF_NOT_ACCEPTED')
            if r['status']=='ACCEPTED':r['status']='PENDING'


def main():
    runner_path = CONTROL/'ch8-prof-on-control/off/runner.py'
    request_path = runner_path.parent/'CI-REQUEST.json'
    dependencies = [FIX/'BINDING-SPEC.json', FIX/'binding_v02.py',
        PROFILES/'on-ci/run-43798838603/accept/intake.py',
        OFF/'accept-v4/reclassify_v4.py', OFF/'accept-v3/classifier_v3.py',
        OFF/'accept-v2/classifier_v2.py', OFF/'accept-v3/ROLE-RULES.json']
    handoff = read(FIX/'CI-REQUEST.json')
    for path,digest in read(PROFILES/'on-ci/CLASSIFIER-REUSE.json')['files'].items():
        v3.require(sha(ROOT/path)==digest,'CLASSIFIER_REUSE_HASH:'+path)
    v3.require(sha(FIX/'BINDING-SPEC.json')==handoff['binding_spec_sha256'] and
               sha(FIX/'binding_v02.py')==handoff['binding_adapter_sha256'],'BINDING_COMPONENT_HASH')
    for p in [runner_path,request_path,request_path.parent/'manifest.json']:
        v3.require(p.read_bytes()==git(CONTROL,'show',TRIGGER+':'+str(p.relative_to(CONTROL))),'CONTROL_FILE_CHANGED:'+p.name)
    runner = module('off_runner',runner_path)
    request_bytes = request_path.read_bytes()
    request = runner.load_request(request_path)
    v3.require(sha(request_path)==handoff['lanes']['off']['request_sha256']==read(ART/'job-status.json')['request_sha256'],'REQUEST_PIN')
    rows=request['rows']
    v3.require(len(rows)==63 and {r['id'] for r in rows}==set(binding.SPEC['rows']),'ROW_SET')
    v3.require(request['manifest_sha256']==binding.SPEC['manifest_sha256'],'MANIFEST_PIN')
    sources={p:git(ROOT,'show',SOURCE+':'+p).decode() for p in binding.SPEC['source_files_sha256']}
    for p,d in binding.SPEC['source_files_sha256'].items():
        v3.require(v3.digest(sources[p].encode())==d,'SOURCE_HASH:'+p)
    v3.require(git(ROOT,'rev-parse',SOURCE+'^{tree}').decode().strip()==binding.SPEC['source_tree']==request['std_tree'],'SOURCE_TREE')
    previous=read(OFF/'accept-v4/ACCEPT.json')
    old_by_id={r['id']:r for r in previous['rows']}
    v3.require(set(old_by_id)=={r['id'] for r in rows}-{'profile_merge4_contract_u8_len4'},'PREVIOUS_ROW_SET')
    tool_hashes={}
    for p in v4.TOOL_FILES+['kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs',
                          'kani-compiler/src/codegen_cprover_gotoc/codegen/foreign_function.rs',
                          'kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs']:
        data=git(CONTROL,'show',TOOL+':'+p)
        v3.require(data==git(CONTROL,'show',TRIGGER+':'+p),'TOOL_CHAIN_CHANGED:'+p)
        tool_hashes[p]=v3.digest(data)
    overall=read(ART/'receipt.json')
    v3.require(all(overall[k]==request[k] for k in ('std_sha','std_tree','tool_sha','tool_tree')) and overall['stop_reason'] is None,'TOP_IDENTITIES')
    exports,groups={},{}
    for gp in sorted((ART/'groups').iterdir()):
        e,g,c=read(gp/'export.json'),read(gp/'receipt.json'),read(gp/'compile-receipt.json')
        v3.require(sha(gp/'export.json')==g['export_sha256'],'EXPORT_HASH')
        selected=[r for r in rows if r['id'] in g['rows']]
        v3.require(g['cfg']==selected[0]['cfg'] and all(r['cfg']==g['cfg'] for r in selected),'CFG')
        argv=g['argv']
        expected=runner.build_argv(Path(argv[4]).parent,Path(argv[0]).parents[1],
            [r['selector'] for r in selected],None,Path(argv[argv.index('--export-json')+1]))
        v3.require(argv==expected,'EXACT_ARGV')
        v3.require(g['environment']['RUSTFLAGS']==('' if not g['cfg'] else '--cfg kani_smallsort_controls'),'CFG_ENV')
        v3.require(g['source_before']==g['source_after'] and all(g['source_before'][k]==request[k] for k in ('std_sha','std_tree','tool_sha','tool_tree','changed_file_sha256')),'GROUP_SOURCE_PINS')
        before,after=g['tool_fingerprints_before'],g['tool_fingerprints_after']
        v3.require(before['required_hashes_present'] is True and after['required_hashes_present'] is True and before['binaries']==after['binaries'] and after['reported_versions']==e['tools'] and after['target']==after['expected_target']==runner.TARGET,'TOOL_FINGERPRINTS')
        groups[gp.name]=dict(export_sha256=sha(gp/'export.json'),receipt_sha256=sha(gp/'receipt.json'),compile_receipt_sha256=sha(gp/'compile-receipt.json'),cfg=g['cfg'],argv=argv,environment=g['environment'],tool_fingerprints=after,execution={k:v for k,v in g['execution'].items() if k!='compilation'})
        for i,h in enumerate(e['harnesses']):
            v3.require(h['name'] not in exports,'DUPLICATE_HARNESS')
            exports[h['name']]=(gp,h,g,c,selected,i)
    v3.require(set(exports)=={r['selector'] for r in rows},'EXPORT_ROW_SET')
    symbols=sorted({h['contract']['contracted_function_name'] for _,h,_,_,_,_ in exports.values() if h['contract']})
    names=subprocess.check_output(['c++filt','-i','-s','rust'],input='\n'.join(symbols)+'\n',text=True).splitlines()
    v3.require(len(names)==len(symbols) and all(a!=b for a,b in zip(symbols,names)),'DEMANGLE')
    demangled=dict(zip(symbols,names))
    rules=fresh_roles(read(OFF/'accept-v3/ROLE-RULES.json')['rules'],sources)
    results=[]
    for row in rows:
        rid=row['id'];gp,h,g,c,group_rows,index=exports[row['selector']]
        original,pre=checked_preflight(runner,gp/'export.json',row,group_rows)
        mapping=mapping_for(row,h,sources)
        receipt=read(ART/rid/'receipt.json')
        statuses,stdout=helpers.stdout_inventory(ART/rid/'stdout.log',row,h,receipt,g,c)
        selected=set(h['checks']['unreachable']+h['checks']['failure']+[x for v in h['covers'].values() if isinstance(v,list) for x in v])
        selected.update(u['id'] for u in h['unsupported_constructs'])
        selected.update(p for p in statuses if re.search(r'\.(assertion|assigns|single_top_level_call|no_recursive_call|no_alloc_dealloc_in_requires|no_alloc_dealloc_in_ensures)\.[1-9][0-9]*$',p))
        records=select(ART/rid/'stdout.log',selected)
        v3.require(all(statuses[p]==v['status'] for p,v in records.items()),'SELECTED_STATUS')
        for failed in h['failed_properties']:
            p=records[failed['id']]
            v3.require(p['status']==failed['status'] and p['description']==failed['description'] and
                       failed['file'].endswith('/'+p['file']) and int(failed['line'])==p['line'],
                       'FAILURE_EXPORT_STDOUT_RECORD_MISMATCH')
        links=helpers.fresh_unsupported_links(h,records)
        roles={pid:helpers.required_role(records[pid],sources) or v3.role(records[pid],rules) for pid in h['checks']['unreachable']}
        result=policy.classify(row,h,mapping,links,roles,pre['state'])
        result.update(expected=row['expected'],mode=row['profile_mode'],profile=row['profile'],
            checks=h['checks'],covers=h['covers'],named_failures=h['failed_properties'],
            stdout_binding=stdout,preflight_original=original,preflight_state=pre['state'],
            original_receipt=dict(status=receipt['status'],outcome=receipt['outcome'],original_exit=receipt['original_exit'],signal=receipt['signal'],export_observation_state=receipt['export']['state']),
            evidence=dict(export_member=str((gp/'export.json').relative_to(ART)),export_sha256=g['export_sha256'],harness_index=index))
        if row['expected']!='SUCCESS':
            result['negative_oracle_records']=[records[p] for p in h['checks']['failure']]
        try:
            mode_row=dict(row,mode=row['profile_mode'])
            if row['expected']!='SUCCESS':
                result['negative_oracle_binding']=bind_negative(row,h,records,sources)
            if row['mode']=='PFC' or row['profile_mode'].startswith('Replace:'):
                bound=binding.bind_fresh(mode_row,h,records,demangled,sources)
                result['exact_instance_identity']=bound['expected_instance_fully_qualified']
                result['binding']['wrapper_status']='BOUND'
                result['pending_reasons']=[p for p in result['pending_reasons'] if p not in {'EXACT_CONTRACT_WRAPPER_BINDING_PENDING','PREDECLARED_FRAME_ORACLE_BINDING_PENDING'}]
            else:
                bound=bind_covers(mode_row,mapping,records,sources)
            result['exact_binding_v4']=bound
            result['binding_state']='BOUND'
        except (KeyError,ValueError,TypeError) as exc:
            result['binding_state']='PENDING'
            result['pending_reasons'].append('FRESH_BINDING:'+str(exc))
        result['status']=helpers.decision(row,h,result,[])
        old=old_by_id.get(rid)
        result['previous_off_comparison']=dict(previous_status=old['status'] if old else None,
            previous_kani_verdict=old.get('kani_verdict') if old else None,
            new_row=old is None,
            old_leaf_companion='merge_contract_u8_n2_to4' if rid=='profile_merge_consumer_u8_len4' else row.get('leaf_companion'),
            fresh_leaf_companion=row.get('leaf_companion'),
            checks_before=old['checks'] if old else None, checks_after=h['checks'],
            unsupported_before=old['unsupported'] if old else None,unsupported_after=h['unsupported_constructs'],
            named_failures_before=old['named_failures'] if old else None,named_failures_after=h['failed_properties'],
            covers_before=old['covers'] if old else None,covers_after=h['covers'])
        results.append(result)
    consumers_after_leaves(rows,results)
    counts=collections.Counter(r['status'] for r in results)
    summary=dict(rows=len(results),statuses={s:counts[s] for s in ('ACCEPTED','BLOCKED_TOOL','REJECTED','PENDING')},
        positive_statuses=dict(collections.Counter(r['status'] for r in results if r['expected']=='SUCCESS')),
        negative_statuses=dict(collections.Counter(r['status'] for r in results if r['expected']!='SUCCESS')),
        covers=dict(collections.Counter(k for r in results for k,v in r['covers'].items() if isinstance(v,list) for _ in v)),
        unreachable_roles=dict(collections.Counter(u['role'] for r in results for u in r['unreachable'])),
        unsupported_statuses=dict(collections.Counter(u['status'] for r in results for u in r['unsupported'])),
        pending_rows={r['id']:r['unknown_reasons']+r['pending_reasons'] for r in results if r['status']=='PENDING'})
    out=dict(schema='prof02-off-fresh-accept-v4-v1',g0_input=git(ROOT,'rev-parse','7d1ae3dd04').decode().strip(),
        run=43808894294,lane='off',worker='worker11',artifact_id=14204858070,artifact_directory=str(ART),
        source_commit=SOURCE,source_tree=request['std_tree'],tool_commit=TOOL,tool_tree=request['tool_tree'],control_trigger=TRIGGER,
        assurance='BOUNDED_SOURCE_REPORTED_POLICY_ADMISSION; NOT_INDEPENDENT_PROOF',proof_credit='NONE',prior_admissions_reused=0,
        request_sha256=v3.digest(request_bytes),manifest_sha256=request['manifest_sha256'],
        source_files_sha256=binding.SPEC['source_files_sha256'],tool_sources_sha256=tool_hashes,
        classifier_dependencies_sha256={str(p.relative_to(ROOT)):sha(p) for p in dependencies},
        previous_off_accept_sha256=sha(OFF/'accept-v4/ACCEPT.json'),group_identities=groups,
        demangler=dict(command=['c++filt','-i','-s','rust'],executable_sha256=sha(Path('/usr/bin/c++filt')),symbols=demangled),
        fresh_role_rules=rules,intake_sha256=sha(HERE/'intake.py'),summary=summary,rows=results)
    (HERE/'ACCEPT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
