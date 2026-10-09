"""Isolated shell capture wiring test; fake stages, no compiler or verifier."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
runner=Path(__file__).with_name('run-verifast-mdnew-cfg.sh').read_text()
function=runner[runner.index('capture_case() {'):runner.index('# Run the same five source bytes')]
with tempfile.TemporaryDirectory(prefix='mdnew-capture-log-') as td:
 root=Path(td);cases=root/'cases';all_logs=root/'logs'
 for side in ('baseline','candidate'):
  run=cases/side/'forget'/'run';run.mkdir(parents=True)
  (run/'verified-ast.txt').write_text('fake AST for service wiring only')
  (run.parent/'source.rs').write_text('fake source for service wiring only')
 all_logs.mkdir()
 env='set -euo pipefail\nall='+str(all_logs)+'\ncases='+str(cases)+'\nbaseline_tool=/fake/base\ncandidate_tool=/fake/candidate\ncompiler_sysroot=/fake/sysroot\ninfra_sha=infra\nproof_sha=proof\nbase_sha=base\ncandidate_sha=candidate\n'
 fake='run_stage() { mkdir -p "$all"; printf "diagnostic:%s\\n" "$1" > "$all/$1-stderr.log"; if [[ "${FAIL_STAGE:-}" == "$1" ]]; then return 124; fi; printf "output:%s\\n" "$1" > "$4"; }\n'
 script=env+fake+function+'\ncapture_case baseline forget\ncapture_case candidate forget\n'
 subprocess.run(['bash','-c',script],check=True,capture_output=True)
 out=cases/'captures'/'forget'
 for side,status in [('baseline','baseline-capture-status.json'),('candidate','capture-status.json')]:
  record=json.loads((out/status).read_text());assert all(v['exit_status']==0 for v in record['stages'].values())
  for mode in ('normal','readonly'):
   assert (out/f'{side}-{mode}-export.log').read_text()==f'diagnostic:{side}-forget-{mode}-export\n'
   assert (out/f'{side}-{mode}-decode.log').read_text()==f'diagnostic:{side}-forget-{mode}-decode\n'
  run=cases/side/'forget'/'run'
  for stage,artifact in [('normal-export','normal-mir.bin'),('normal-decode','normal-mir.txt'),
                         ('readonly-export','readonly-mir.bin'),('readonly-decode','readonly-mir.txt'),
                         ('refinement','refinement.log')]:
   assert record['stages'][stage]['output_sha256']==hashlib.sha256((run/artifact).read_bytes()).hexdigest()
  assert record['verified_ast_sha256']==hashlib.sha256((run/'verified-ast.txt').read_bytes()).hexdigest()
  assert not (all_logs/f'{side}-forget-normal-export.log').exists()

# A failed export has no decoded stdout file. It must still publish a receipt
# with the failing status so the auditor can classify the capture as incomplete.
for side in ('baseline','candidate'):
 run=cases/side/'failed'/'run';run.mkdir(parents=True)
 (run.parent/'source.rs').write_text('fake source for service wiring only')
 (run/'verified-ast.txt').write_text('fake AST for service wiring only')
env_fail=env.replace('candidate_sha=candidate\n','candidate_sha=candidate\nFAIL_STAGE=baseline-failed-normal-export\n')
script=env_fail+fake+function+'\ncapture_case baseline failed\n'
failed_capture=subprocess.run(['bash','-c',script],capture_output=True,text=True)
assert failed_capture.returncode==0, failed_capture.stderr or failed_capture.stdout
record=json.loads((cases/'captures'/'failed'/'baseline-capture-status.json').read_text())
assert record['stages']['normal-export']['exit_status']==124
assert record['stages']['normal-decode']['exit_status']==-1
assert record['stages']['normal-decode']['output_sha256'] is None
print(json.dumps({'service_test':'separate stdout/stderr capture, all output hashes, and failed-stage receipt','sides':2,'compiler_or_verifier_execution':False,'passed':True}))
