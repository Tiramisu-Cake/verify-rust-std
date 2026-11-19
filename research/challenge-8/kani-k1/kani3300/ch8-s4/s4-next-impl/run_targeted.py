"""Small synthetic Python regression suites only; never final Validate/native/CI."""
from pathlib import Path
import hashlib,json,os,subprocess,time
OUT=Path(__file__).resolve().parent;H=Path('/root/kani-ch8-s4-next-control-w15/ch8-s1-control')
command=['python3','-m','unittest','-v','test_s4p3_domain','test_s4p3.RoleTests','test_s4p3.CampaignTests','test_s4p3.WorkflowTests','test_s4p3.SingletonRunnerTests']
start=time.monotonic()
with (OUT/'tests/targeted-final.stdout').open('wb') as stdout,(OUT/'tests/targeted-final.stderr').open('wb') as stderr:
    result=subprocess.run(command,cwd=H,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=stdout,stderr=stderr,timeout=180)
record={'command':command,'cwd':str(H),'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start,'control_sha':subprocess.check_output(['git','-C',str(H.parent),'rev-parse','HEAD'],text=True).strip(),'control_tree':subprocess.check_output(['git','-C',str(H.parent),'rev-parse','HEAD^{tree}'],text=True).strip(),'final_validate':'NOT_RUN','native_CI':'NOT_RUN','request_sha256':hashlib.sha256((H/'CI-REQUEST.json').read_bytes()).hexdigest()}
(OUT/'tests/targeted-final.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record));raise SystemExit(result.returncode)
