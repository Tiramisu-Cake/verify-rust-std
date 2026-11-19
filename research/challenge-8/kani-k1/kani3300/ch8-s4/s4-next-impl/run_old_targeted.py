"""Retained S4P2 routing and all network-r2 synthetic regressions; not final Validate."""
from pathlib import Path
import json,os,subprocess,time
OUT=Path(__file__).resolve().parent;H=Path('/root/kani-ch8-s4-next-control-w15/ch8-s1-control')
code="import s4p2r2_validate as r2,s4p3_validate as v; a=r2.old_s4p2_suite(('test_s4p2.RoleTests','test_s4p2.WorkflowTests','test_s4p2.SingletonRunnerTests')); b=v.old_s4p2r2_suite(); print({'tests':a.testsRun+b.testsRun,'failures':len(a.failures)+len(b.failures),'errors':len(a.errors)+len(b.errors)}); raise SystemExit(not (a.wasSuccessful() and b.wasSuccessful()))"
command=['python3','-c',code];start=time.monotonic()
with (OUT/'tests/old-targeted-final.stdout').open('wb') as out,(OUT/'tests/old-targeted-final.stderr').open('wb') as err:
    result=subprocess.run(command,cwd=H,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=out,stderr=err,timeout=180)
git=lambda arg:subprocess.check_output(['git','-C',str(H.parent),'rev-parse',arg],text=True).strip()
record={'command':command,'exit_code':result.returncode,'seconds':time.monotonic()-start,'control_sha':git('HEAD'),'control_tree':git('HEAD^{tree}'),'request_sha256':__import__('hashlib').sha256((H/'CI-REQUEST.json').read_bytes()).hexdigest(),'scope':'Eight S4P2 routing + all22 network-r2 tests with immutable fixtures; final Validate NOT_RUN'}
(OUT/'tests/old-targeted-final.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));raise SystemExit(result.returncode)
