"""Freeze semantic request and hash actual complete scoped control payload."""
from pathlib import Path
import hashlib,json,re,subprocess
CONTROL=Path('/root/kani-ch8-s4p-2-r1-control-w13');HERE=CONTROL/'ch8-s1-control'
D=lambda b:hashlib.sha256(b).hexdigest()
request=json.loads((HERE/'CI-REQUEST.json').read_text())
semantic={k:v for k,v in request.items() if k not in ('ci_changed_paths','ci_deleted_paths','ci_payload_sha256')}
(HERE/'S4P2-INVENTORY.json').write_text(json.dumps(semantic,indent=2)+'\n')
path=HERE/'s4p2_policy.py';data=path.read_text()
data,n=re.subn(r"INVENTORY_SHA256='[a-f0-9]{64}'",'INVENTORY_SHA256='+repr(D((HERE/'S4P2-INVENTORY.json').read_bytes())),data)
assert n==1;path.write_text(data)
subprocess.run(['git','-C',str(CONTROL),'add','.github/workflows/ch8-s2.yml','ch8-s1-control'],check=True)
def git(*args):return subprocess.check_output(['git','-C',str(CONTROL),*args],text=True).splitlines()
request['ci_changed_paths']=git('diff','--cached','--name-only',request['tool_sha'])
request['ci_deleted_paths']=git('diff','--cached','--diff-filter=D','--name-only',request['tool_sha'])
request['ci_payload_sha256']={rel:D((CONTROL/rel).read_bytes()) for rel in request['ci_changed_paths'] if rel not in request['ci_deleted_paths'] and rel!='ch8-s1-control/CI-REQUEST.json'}
(HERE/'CI-REQUEST.json').write_text(json.dumps(request,indent=2)+'\n')
subprocess.run(['git','-C',str(CONTROL),'add','ch8-s1-control/CI-REQUEST.json'],check=True)
print(json.dumps({'request':D((HERE/'CI-REQUEST.json').read_bytes()),'payload_files':len(request['ci_payload_sha256'])}))
