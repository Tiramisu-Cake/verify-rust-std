#!/usr/bin/env python3
"""Read-only pins and bounded descriptor parsing model; no test driver/native tool."""
import hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[6]
SOURCE=Path('/root/cbmc-pr9487-slop-readonly-20261119')
TASK='98784e2ade6135d3177b0ad14c9ab88777ab6aa2'
BASE='research/challenge-8/kani-k1/kani3300/wave0/open-pr-slop-next-inputs-20261119/'
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def blob(repo,rev,path):return git(repo,'show',rev+':'+path)
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,v):(HERE/name).write_text(json.dumps(v,indent=2)+'\n')
def parsed(text):
    # Exact descriptor under review has no // comments or multiline matching.
    data=[x for x in text.splitlines() if not x.startswith('//')]
    level,main,options,grep_options,*patterns=data
    required=[];forbidden=[];section=1
    for pattern in patterns:
        if pattern=='--':section-=1
        elif section==1:required.append(pattern)
        elif section==0:forbidden.append(pattern)
    return {'level':level,'main':main,'options':options,'grep_options':grep_options,'required':required,'forbidden':forbidden}
def accepts(desc,output):
    lines=output.splitlines()
    return all(any(re.search(p,line) for line in lines) for p in desc['required']) and not any(any(re.search(p,line) for line in lines) for p in desc['forbidden'])
def main():
    refs={};raw=blob(REPO,TASK,BASE+'pr-9487/INPUTS.json');pins=json.loads(raw)
    for name in ['ROOT-DECISION.md','STYLE-UPSTREAM-RULES.snapshot.md','pr-9487/INPUTS.json','pr-9487/CONNECTED-PR.json','pr-9487/CONNECTED-MERGEBASE.json','pr-9487/PR-BODY.snapshot.md','pr-9487/SOURCE.patch']:
        b=blob(REPO,TASK,BASE+name);refs[BASE+name]={'sha256':sha(b),'bytes':len(b)}
    assert git(SOURCE,'rev-parse','HEAD').decode().strip()==pins['head']
    assert git(SOURCE,'rev-parse','HEAD^{tree}').decode().strip()==pins['head_tree']
    assert not git(SOURCE,'status','--porcelain')
    subprocess.run(['git','-C',str(SOURCE),'merge-base','--is-ancestor',pins['merge_base'],pins['head']],check=True)
    base_local=subprocess.run(['git','-C',str(SOURCE),'cat-file','-e',pins['base_snapshot']+'^{commit}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    assert not base_local
    changed=git(SOURCE,'diff','--name-only',pins['merge_base'],pins['head']).decode().splitlines()
    assert set(changed)==set(pins['changed_files'])
    checked=[]
    for name,expected in pins['changed_files'].items():
        b=blob(SOURCE,pins['head'],name)
        assert len(b)==expected['bytes'] and sha(b)==expected['sha256']
        assert git(SOURCE,'rev-parse',pins['head']+':'+name).decode().strip()==expected['git_blob']
        assert (SOURCE/name).read_bytes()==b
        checked.append({'path':name,**expected})
    diff=git(SOURCE,'diff','--full-index',pins['merge_base'],pins['head'])
    assert sha(diff)==pins['diff_sha256'] and diff==blob(REPO,TASK,BASE+'pr-9487/SOURCE.patch')
    assert sha(blob(REPO,TASK,BASE+'pr-9487/PR-BODY.snapshot.md'))==pins['PR_body_sha256']
    src=(SOURCE/'src/util/simplify_utils.cpp').read_text()
    old=blob(SOURCE,pins['merge_base'],'src/util/simplify_utils.cpp').decode()
    assert old.replace('CHECK_RETURN(el_size_opt.has_value() && *el_size_opt > bitst{0});','CHECK_RETURN(el_size_opt.has_value() && *el_size_opt >= bitst{0});',1)==src
    desc=(SOURCE/'regression/cbmc/byte_extract_empty_struct_array/test.desc').read_text()
    original=parsed(desc);ls=desc.splitlines();ls.insert(3,'');fixed=parsed('\n'.join(ls)+'\n')
    driver=(SOURCE/'regression/test.pl').read_text()
    assert 'my ($level_and_tags, $input, $options, $grep_options, @results) = load(' in driver
    assert 'if($grep_options eq "activate-multi-line-match")' in driver
    assert original['grep_options']=='^EXIT=0$' and '^EXIT=0$' not in original['required']
    assert fixed['grep_options']=='' and fixed['required']==['^EXIT=0$','^SIGNAL=0$','^VERIFICATION SUCCESSFUL$']
    cases=[]
    samples=[('success','VERIFICATION SUCCESSFUL\nEXIT=0\nSIGNAL=0\n',True,True),('nonzero_exit_after_success','VERIFICATION SUCCESSFUL\nEXIT=7\nSIGNAL=0\n',True,False),('signal','VERIFICATION SUCCESSFUL\nEXIT=0\nSIGNAL=15\n',False,False),('invariant_even_with_success','VERIFICATION SUCCESSFUL\nInvariant check failed\nEXIT=0\nSIGNAL=0\n',False,False),('original_abort_shape','Invariant check failed\nEXIT=134\nSIGNAL=0\n',False,False),('failed_verification','VERIFICATION FAILED\nEXIT=10\nSIGNAL=0\n',False,False),('ignored_construct','warning: ignoring construct\nVERIFICATION SUCCESSFUL\nEXIT=0\nSIGNAL=0\n',False,False)]
    for name,text,want_old,want_fixed in samples:
        a,b=accepts(original,text),accepts(fixed,text)
        assert (a,b)==(want_old,want_fixed)
        cases.append({'name':name,'synthetic_output':text,'current_accepts':a,'blank_line_fix_accepts':b})
    context_paths=['AGENTS.md','LICENSE','CODING_STANDARD.md','.github/pull_request_template.md','src/util/pointer_offset_size.cpp','src/util/endianness_map.cpp','src/ansi-c/c_typecheck_type.cpp','src/ansi-c/padding.cpp','regression/test.pl','regression/CMakeLists.txt','regression/cbmc/CMakeLists.txt','regression/cbmc/Makefile','regression/cbmc/empty_compound_type4/main.c','regression/cbmc/empty_compound_type4/test.desc','unit/util/lower_byte_operators.cpp','unit/CMakeLists.txt','unit/Makefile']
    context={name:{'sha256':sha(blob(SOURCE,pins['head'],name)),'bytes':len(blob(SOURCE,pins['head'],name))} for name in context_paths}
    write('INPUTS.json',{'task_commit':TASK,'authority':'Root explicitly issued PR9487 offline recommendation review to same currentW14 after completed S4P2 intake; no new/reset/subagents/model/Fast changes','pinned_inputs':pins,'source_policy':'READ_ONLY; exact local diff uses connected-confirmed107a, current upstream57 unavailable locally','output':str(HERE.relative_to(REPO))})
    write('PROVENANCE.json',{'task_commit':TASK,'input_references':refs,'source_head':pins['head'],'source_tree':pins['head_tree'],'connected_current_base':pins['base_snapshot'],'merge_base':pins['merge_base'],'current_base_local_object':base_local,'head_local_parent':git(SOURCE,'show','-s','--format=%P',pins['head']).decode().strip(),'changed_files_checked':checked,'diff_sha256':sha(diff),'context_files':context,'connected_metadata_assurance':'Exact root-pinned snapshots; no fresh live PR/CI request, no current-base source-equivalence claim','source_worktree_clean':True,'subagents':0,'native_tools_or_test_driver_executed':False,'external_writes':False,'ledger_or_model_changes':False})
    write('STATIC-CHECK.json',{'status':'PASS','pin_and_blob_validation':'4 exact published blobs, head/tree/mergebase, exact diff and PR body digest MATCH; read-only source clean','production_edit':'Exactly one >0 to >=0 guard change; remaining production file identical to merge base','descriptor_model_scope':'Bounded Python transcription of the inspected test.pl four-field header and line-regex matching for this exact descriptor; no Perl driver or CBMC execution; no general replacement parser','current_descriptor':original,'recommended_descriptor':fixed,'synthetic_cases':cases,'native_old_failure_new_pass':'NOT_RUN; old CHECK_RETURN failure path established by source, original release repro/CI claims remain author-reported','full_source_coverage_or_native_success_claim':False})
    print(json.dumps({'static':'PASS','published_blobs':len(checked),'descriptor_cases':len(cases),'finding':'EXIT pattern consumed as fourth header field; blank-line fix restores it','native':'NOT_RUN'}))
if __name__=='__main__':main()
