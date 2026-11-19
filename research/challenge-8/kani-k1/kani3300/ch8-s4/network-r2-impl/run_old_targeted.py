"""Old-profile synthetic routing regressions, not full/final Validate."""
from pathlib import Path
import json,os,subprocess,time
OUT=Path(__file__).resolve().parent;H=Path('/root/kani-ch8-s4p-2-r1-control-w13/ch8-s1-control')
code="import s4p2r2_validate as v; r=v.old_s4p2_suite(('test_s4p2.RoleTests','test_s4p2.WorkflowTests','test_s4p2.SingletonRunnerTests')); print({'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors)}); raise SystemExit(not r.wasSuccessful())"
command=['python3','-c',code];start=time.monotonic()
with (OUT/'tests/old-targeted-final.stdout').open('wb') as out,(OUT/'tests/old-targeted-final.stderr').open('wb') as err:r=subprocess.run(command,cwd=H,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=out,stderr=err,timeout=120)
record={'command':command,'exit_code':r.returncode,'seconds':time.monotonic()-start,'control_sha':subprocess.check_output(['git','-C',str(H.parent),'rev-parse','HEAD'],text=True).strip(),'scope':'Eight existing S4P2 role/workflow/singleton tests under immutable old fixture; final Validate NOT_RUN'}
(OUT/'tests/old-targeted-final.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));raise SystemExit(r.returncode)
