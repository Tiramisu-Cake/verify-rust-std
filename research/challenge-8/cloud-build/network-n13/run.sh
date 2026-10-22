#!/usr/bin/env bash
set -euo pipefail

stage=${NETWORK_STAGE:?NETWORK_STAGE is required}
case "$stage" in
  preflight|exact|controls|controls-order|regressions|regressions-n13|regressions-n9) ;;
  *) printf 'unsupported Network N13 stage: %s\n' "$stage" >&2; exit 2 ;;
esac

infra_root=${INFRA_ROOT:-/workspace/infra}
proof_root=${PROOF_ROOT:-/workspace/proof}
work_root=${WORK_ROOT:-/workspace/smallsort-work/network-n13}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
runner_evidence="$evidence_root/allprooflogs/cases"
profile="$infra_root/research/challenge-8/cloud-build/network-n13/N13-EXECUTION-PROFILE-20261023-N3.json"
tool_parent="$work_root/tool"
archive="$work_root/verifast-26.09-linux.tar.gz"
tool_home="$tool_parent/verifast-26.09"
runner_log="$work_root/network-n13-runner.log"

for path in "$infra_root" "$proof_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || { printf 'path outside /workspace: %s\n' "$path" >&2; exit 2; }
done
[[ -f "$profile" ]] || { printf 'missing pinned N13 execution profile\n' >&2; exit 2; }
mkdir -p "$(dirname "$work_root")"
if [[ -e "$work_root" && -n "$(find "$work_root" -mindepth 1 -print -quit)" ]]; then
  printf 'Network N13 work directory is not empty\n' >&2; exit 2
fi
mkdir -p "$tool_parent"

record_failure() {
  local status=$?
  if (( status != 0 )); then
    mkdir -p "$evidence_root/allprooflogs/cases"
    if [[ ! -f "$evidence_root/allprooflogs/proof-audit.json" ]]; then
      python3 - "$evidence_root/allprooflogs" "$stage" "$status" <<'FAILURE'
import json,pathlib,sys
root=pathlib.Path(sys.argv[1]); stage=sys.argv[2]; status=int(sys.argv[3])
(root/'proof-audit.json').write_text(json.dumps({
  'accepted':False,'classification':'INCONCLUSIVE','diagnostic_complete':False,
  'proof_credit':False,'lane':'network-n13','stage':stage,
  'stage_exit_status':status,'failed_stage':'cloud-setup','evidence_root':'allprooflogs',
  'archive_layout':{
    'schema':'network-n13-direct-case-artifacts-v1',
    'runner_evidence':'allprooflogs/cases',
    'results_path':'allprooflogs/cases/results.json',
    'case_artifact_root':'allprooflogs/cases',
    'case_files_copied':False,'results_sha256':None,
    'mapped_case_count':0,'unmapped_case_rows':0,'cases':[]
  }
},indent=2,sort_keys=True)+'\n')
(root/'network-n13-stage.log').write_text('Network N13 Cloud setup or runner failed before a complete stage result.\n')
(root/'network-n13-stage-exit-code.txt').write_text(str(status)+'\n')
(root/'cases/runner-not-started.txt').write_text('The pinned runner did not produce a complete case matrix.\n')
FAILURE
    fi
  fi
  return "$status"
}
trap record_failure EXIT

bootstrap_record="$evidence_root/network-n13-bootstrap.json"
bootstrap_deadline=${NETWORK_SETUP_DEADLINE_EPOCH:-}
bootstrap_runner_state=NOT_REACHED
write_bootstrap_record() {
  local state=$1 operation=$2 status=$3 runner_exit_code=${4:-null}
  mkdir -p "$(dirname "$bootstrap_record")"
  printf '{"schema":"network-n13-bootstrap-v1","stage":"%s","state":"%s","operation":"%s","exit_code":%s,"setup_deadline_epoch":%s,"runner_state":"%s","runner_exit_code":%s}\n' \
    "$stage" "$state" "$operation" "$status" \
    "${bootstrap_deadline:-null}" "$bootstrap_runner_state" "$runner_exit_code" > "$bootstrap_record"
}
if [[ ! "$bootstrap_deadline" =~ ^[0-9]+$ ]]; then
  write_bootstrap_record FAILED missing-setup-deadline 2
  printf 'Network N13 bootstrap deadline from Cloud config is missing or invalid\n' >&2
  exit 2
fi
setup_run() {
  local operation=$1 remaining status
  shift
  remaining=$((bootstrap_deadline - $(date +%s)))
  if (( remaining <= 0 )); then
    write_bootstrap_record FAILED "$operation" 124
    printf 'Network N13 shared bootstrap deadline expired before %s\n' "$operation" >&2
    return 124
  fi
  write_bootstrap_record RUNNING "$operation" null
  if timeout --signal=TERM --kill-after=2s "${remaining}s" "$@"; then status=0; else status=$?; fi
  if (( status == 0 )); then
    write_bootstrap_record SUCCEEDED "$operation" 0
  else
    write_bootstrap_record FAILED "$operation" "$status"
  fi
  return "$status"
}

setup_run provider-identity python3 "$infra_root/research/challenge-8/cloud-build/provider.py" > "$work_root/provider.json"

export DEBIAN_FRONTEND=noninteractive
apt_options=(-o Acquire::http::Timeout=25 -o Acquire::https::Timeout=25 -o Acquire::Retries=1)
setup_run runtime-apt-update apt-get "${apt_options[@]}" update
setup_run runtime-apt-install apt-get "${apt_options[@]}" install --yes --no-install-recommends ca-certificates curl \
  libgmp10 libmpfr6 libgomp1 libffi8 libncurses6 libtinfo6 zlib1g libz3-4 \
  libgtk-3-0 libgtksourceview-4-0

setup_run tool-download curl -fL --connect-timeout 20 --max-time 90 -o "$archive" \
  https://github.com/verifast/verifast/releases/download/26.09/verifast-26.09-linux.tar.gz
printf '%s  %s\n' \
  da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa \
  "$archive" | setup_run tool-archive-check sha256sum -c - | tee "$work_root/verifast-archive-sha256.txt"
setup_run tool-extract tar -xzf "$archive" -C "$tool_parent"
[[ -x "$tool_home/bin/verifast" ]] || { printf 'unexpected VeriFast archive layout\n' >&2; exit 2; }
printf '%s  %s\n' \
  dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc \
  "$tool_home/bin/verifast" | setup_run tool-console-check sha256sum -c - | tee "$work_root/verifast-console-sha256.txt"

set +e
export LD_LIBRARY_PATH="$tool_home/bin:${LD_LIBRARY_PATH:-}"
bootstrap_runner_state=RUNNING
write_bootstrap_record SUCCEEDED runner-start 0
python3 "$proof_root/research/challenge-8/network/n13/run-cloud.py" \
  --tool-home "$tool_home" --evidence "$runner_evidence" --stage "$stage" > "$runner_log" 2>&1
runner_status=$?
bootstrap_runner_state=REACHED
write_bootstrap_record SUCCEEDED runner-finished 0 "$runner_status"
set -e
cat "$runner_log"

python3 - "$evidence_root" "$runner_evidence" "$work_root" "$stage" "$runner_status" <<'EVIDENCE'
import hashlib,json,pathlib,shutil,sys

evidence,runner_evidence,work=map(pathlib.Path,sys.argv[1:4])
stage=sys.argv[4]
status=int(sys.argv[5])
results_path=runner_evidence/'results.json'
results_bytes=None
summary={}
try:
    results_bytes=results_path.read_bytes()
    value=json.loads(results_bytes)
    if isinstance(value,dict): summary=value
except (OSError,ValueError):
    pass
cases_dir=evidence/'allprooflogs'/'cases'
cases_dir.mkdir(parents=True,exist_ok=True)
case_value=summary.get('cases')
case_rows=case_value if isinstance(case_value,list) else []
case_artifacts=[]
unmapped_rows=0
for row in case_rows:
    if not isinstance(row,dict) or not isinstance(row.get('name'),str):
        unmapped_rows+=1
        continue
    name=row['name']
    if not name or any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in name):
        unmapped_rows+=1
        continue
    result=row.get('result') if isinstance(row.get('result'),dict) else {}
    source=cases_dir/(name+'.c')
    log=cases_dir/(name+'.log')
    case_artifacts.append({
        'case':name,
        'state':row.get('state') if isinstance(row.get('state'),str) else None,
        'exit':result.get('exit') if type(result.get('exit')) is int else row.get('exit') if type(row.get('exit')) is int else None,
        'source_path':'allprooflogs/cases/'+name+'.c',
        'source_present':source.is_file() and not source.is_symlink(),
        'source_sha256':result.get('source_sha256') if isinstance(result.get('source_sha256'),str) else row.get('generated_sha256') if isinstance(row.get('generated_sha256'),str) else None,
        'log_path':'allprooflogs/cases/'+name+'.log',
        'log_present':log.is_file() and not log.is_symlink(),
        'log_sha256':result.get('log_sha256') if isinstance(result.get('log_sha256'),str) else None,
    })
stage_dir=evidence/'allprooflogs'
stage_dir.mkdir(parents=True,exist_ok=True)
(stage_dir/'network-n13-stage.log').write_text((work/'network-n13-runner.log').read_text(errors='replace'))
(stage_dir/'network-n13-stage-exit-code.txt').write_text(str(status)+'\n')
for name in ('provider.json','verifast-archive-sha256.txt','verifast-console-sha256.txt'):
    source=work/name
    if source.is_file(): shutil.copyfile(source,evidence/name)
identities_complete=all(
    item['source_present'] and item['log_present'] and
    isinstance(item['source_sha256'],str) and len(item['source_sha256'])==64 and
    isinstance(item['log_sha256'],str) and len(item['log_sha256'])==64
    for item in case_artifacts)
complete=(status==0 and summary.get('complete') is True and isinstance(case_value,list) and
          bool(case_rows) and unmapped_rows==0 and len(case_artifacts)==len(case_rows) and
          identities_complete)
audit={
  'accepted':False,
  'classification':'NETWORK_N13_STAGE_COMPLETE' if complete else 'INCONCLUSIVE',
  'diagnostic_complete':complete,
  'proof_credit':False,
  'lane':'network-n13',
  'stage':stage,
  'stage_exit_status':status,
  'case_count':len(case_rows),
  'evidence_root':'allprooflogs',
  'archive_layout':{
    'schema':'network-n13-direct-case-artifacts-v1',
    'runner_evidence':'allprooflogs/cases',
    'results_path':'allprooflogs/cases/results.json',
    'case_artifact_root':'allprooflogs/cases',
    'case_files_copied':False,
    'results_sha256':hashlib.sha256(results_bytes).hexdigest() if results_bytes is not None else None,
    'mapped_case_count':len(case_artifacts),
    'unmapped_case_rows':unmapped_rows,
    'cases':case_artifacts,
  },
}
(stage_dir/'proof-audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
EVIDENCE
exit "$runner_status"
