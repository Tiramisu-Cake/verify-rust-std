"""Read-only identity gate for the coordinator-created S4P3 trigger."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
HERE=Path(__file__).resolve().parent
EXPECTED_TREE='09938d27a127351f5c51b6c9f451602d797a1c0f'
EXPECTED_PARENT='3d3fb715271e3b195c6e0eee3557d5b0a6aad00d'
REVIEWED='65a9ea656a4b5f1e66f7b31eceffb5eefeba7541'
STD='7b31b060b90ce286e94547993f6a698c549bc5fa'
TOOL='0aac16ef62da9e9d5645782d458593e5d78143ba'
REQUEST='693e12689bfee859560d5042a36fd8b80051e9fca4082fd1a612642d7e389e30'
WORKFLOW='fc21d9f44a403b6294daaca2b25fdfcebe38d3dd7e89a927af0d289a86c177a0'
REF='uninit-ci/ch8-s4p-3-20261119'
SKIP=re.compile(r'\[(?:skip ci|ci skip|no ci|skip actions|actions skip)\]|(?im:^\s*skip-checks\s*:\s*true\s*$)',re.I)
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--head',required=True);p.add_argument('--ref',required=True);p.add_argument('--out');a=p.parse_args()
 git=lambda *args:subprocess.check_output(['git','-C',a.repo,*args])
 errors=[];info={}
 try:
  if not re.fullmatch(r'[0-9a-f]{40}',a.head):raise ValueError('full lowercase40 SHA required')
  h=git('rev-parse','--verify',a.head+'^{commit}').decode().strip()
  if h!=a.head:errors.append('head is not the exact supplied commit')
  if h==REVIEWED:errors.append('skipped reviewed candidate is not a new trigger sibling')
  if a.ref!=REF:errors.append('ref differs from this GO proposed trigger ref')
  tree=git('show','-s','--format=%T',h).decode().strip();parents=git('show','-s','--format=%P',h).decode().split()
  if tree!=EXPECTED_TREE:errors.append('tree differs from exact reviewed control')
  if parents!=[EXPECTED_PARENT]:errors.append('sole parent must be3d3f; not reviewed65a9 candidate or9e14')
  introduced=git('rev-list','--reverse',EXPECTED_PARENT+'..'+h).decode().splitlines()
  if introduced!=[h]:errors.append('exactly one commit3d3f..trigger required')
  message=git('show','-s','--format=%B',h).decode()
  if SKIP.search(message):errors.append('skip-CI directive in trigger message')
  request_bytes=git('show',h+':ch8-s1-control/CI-REQUEST.json');workflow=git('show',h+':.github/workflows/ch8-s2.yml')
  if hashlib.sha256(request_bytes).hexdigest()!=REQUEST:errors.append('request hash mismatch')
  if hashlib.sha256(workflow).hexdigest()!=WORKFLOW:errors.append('workflow hash mismatch')
  r=json.loads(request_bytes)
  if r['std_sha']!=STD or r['tool_sha']!=TOOL:errors.append('source/tool pin mismatch')
  if r['control_parent']!=EXPECTED_PARENT or r['schema']!='ch8-s4p-3-v1' or r['profile']!='ch8-s4p-3-network-fullbyte-concrete-calls-v1':errors.append('profile/schema/parent mismatch')
  for name,sha in r['ci_payload_sha256'].items():
   if hashlib.sha256(git('show',h+':'+name)).hexdigest()!=sha:errors.append('payload mismatch: '+name)
  if [x['id'] for x in r['rows']]!=['checker_order_corrupt','checker_count_corrupt','sort13_weak','s4p_cell_count_corrupt','s4p3_network_b01_n08_fullbyte','s4p3_network_b01_n09_fullbyte','s4p3_network_b01_n13_fullbyte','s4p3_network_b01_n17_fullbyte'] or not all(x['mode']=='Original' and x.get('target') is None for x in r['rows']):errors.append('selection/mode/target mismatch')
  info={'head':h,'tree':tree,'parents':parents,'range':introduced,'ref':a.ref,'request_sha256':hashlib.sha256(request_bytes).hexdigest(),'workflow_sha256':hashlib.sha256(workflow).hexdigest(),'payload_files':len(r['ci_payload_sha256']),'std_sha':r['std_sha'],'tool_sha':r['tool_sha']}
 except Exception as e:errors.append(type(e).__name__+': '+str(e))
 result={'status':'MATCH' if not errors else 'REJECT','errors':errors,**info,'remote_source_fetchability':'REQUIRES_COORDINATOR_CONNECTED_CHECK','remote_ref_absence':'REQUIRES_COORDINATOR_CONNECTED_CHECK','authorization_granted_by_this_script':False,'dispatch_push_accounting_performed':False}
 text=json.dumps(result,indent=2)+'\n'
 if a.out:Path(a.out).write_text(text)
 print(text,end='');return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())
