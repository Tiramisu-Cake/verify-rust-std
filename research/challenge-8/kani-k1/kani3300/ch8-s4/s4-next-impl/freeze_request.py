"""Recompute static dependency maps and seal request/payload; no native action."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,time
OUT=Path(__file__).resolve().parent;C=Path('/root/kani-ch8-s4-next-control-w15');H=C/'ch8-s1-control';S=Path('/root/verify-rust-std-ch8-s4-next-w15')
D=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
sys.path.insert(0,str(H));import s4p3_cfg_pfc as cfg,s4p3_ordinary_contracts as ordinary,s4p3_contract_stacks as stacks,s4p3_lexical_bindings as lexical
r=json.loads((H/'CI-REQUEST.json').read_text());start=time.monotonic()
for key in ('cfg_pfc_source_sha256','ordinary_contract_source_sha256','contract_stack_source_sha256','lexical_source_sha256'):r.pop(key,None)
for name,module,key in [('ordinary',ordinary,'ordinary_contract_source_sha256'),('cfg_pfc',cfg,'cfg_pfc_source_sha256'),('contract_stacks',stacks,'contract_stack_source_sha256'),('lexical',lexical,'lexical_source_sha256')]:
    report=module.check(S,r);r[key]=report['source_files_sha256'];put(OUT/('MAP-'+name.upper()+'.json'),report);print(name+' STATIC_PASS',flush=True)
# The snapshot includes every static gate dependency, not just selected roots.
snapshot={rel:(S/rel).read_text() for rel in sorted(set(r['changed_file_sha256']).union(*(set(r[k]) for k in ('cfg_pfc_source_sha256','ordinary_contract_source_sha256','contract_stack_source_sha256','lexical_source_sha256'))))}
put(H/'S4P3-SOURCE.json',snapshot)
semantic={k:v for k,v in r.items() if k not in ('ci_changed_paths','ci_deleted_paths','ci_payload_sha256')}
put(H/'S4P3-INVENTORY.json',semantic)
p=H/'s4p3_policy.py';s,n=re.subn(r"INVENTORY_SHA256='[a-f0-9]{64}'",'INVENTORY_SHA256='+repr(D((H/'S4P3-INVENTORY.json').read_bytes())),p.read_text());assert n==1;p.write_text(s)
subprocess.run(['git','-C',str(C),'add','.github/workflows/ch8-s2.yml','ch8-s1-control'],check=True)
def git(*args):return subprocess.check_output(['git','-C',str(C),*args],text=True).splitlines()
r['ci_changed_paths']=git('diff','--cached','--name-only',r['tool_sha'])
r['ci_deleted_paths']=git('diff','--cached','--diff-filter=D','--name-only',r['tool_sha'])
r['ci_payload_sha256']={rel:D((C/rel).read_bytes()) for rel in r['ci_changed_paths'] if rel not in r['ci_deleted_paths'] and rel!='ch8-s1-control/CI-REQUEST.json'}
put(H/'CI-REQUEST.json',r);subprocess.run(['git','-C',str(C),'add','ch8-s1-control/CI-REQUEST.json'],check=True)
print(json.dumps({'status':'FROZEN','seconds':time.monotonic()-start,'request_sha256':D((H/'CI-REQUEST.json').read_bytes()),'payload_files':len(r['ci_payload_sha256'])}),flush=True)
