"""Payload-only freeze after test/Validate wiring edits. Semantic bytes unchanged."""
from pathlib import Path
import hashlib,json,subprocess
C=Path('/root/kani-ch8-s4p-2-r1-control-w13');H=C/'ch8-s1-control'
r=json.loads((H/'CI-REQUEST.json').read_text())
assert json.loads((H/'S4P2R2-INVENTORY.json').read_text())=={k:v for k,v in r.items() if k not in ('ci_changed_paths','ci_deleted_paths','ci_payload_sha256')}
subprocess.run(['git','-C',str(C),'add','.github/workflows/ch8-s2.yml','ch8-s1-control'],check=True)
def git(*args):return subprocess.check_output(['git','-C',str(C),*args],text=True).splitlines()
r['ci_changed_paths']=git('diff','--cached','--name-only',r['tool_sha'])
r['ci_deleted_paths']=git('diff','--cached','--diff-filter=D','--name-only',r['tool_sha'])
r['ci_payload_sha256']={rel:hashlib.sha256((C/rel).read_bytes()).hexdigest() for rel in r['ci_changed_paths'] if rel not in r['ci_deleted_paths'] and rel!='ch8-s1-control/CI-REQUEST.json'}
(H/'CI-REQUEST.json').write_text(json.dumps(r,indent=2)+'\n');subprocess.run(['git','-C',str(C),'add','ch8-s1-control/CI-REQUEST.json'],check=True)
print(json.dumps({'request_sha256':hashlib.sha256((H/'CI-REQUEST.json').read_bytes()).hexdigest(),'payload_files':len(r['ci_payload_sha256'])}))
