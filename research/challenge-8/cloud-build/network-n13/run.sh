#!/usr/bin/env bash
set -euo pipefail

stage=${NETWORK_STAGE:?NETWORK_STAGE is required}
case "$stage" in
  preflight|exact|controls|controls-order|regressions) ;;
  *) printf 'unsupported Network N13 stage: %s\n' "$stage" >&2; exit 2 ;;
esac

infra_root=${INFRA_ROOT:-/workspace/infra}
proof_root=${PROOF_ROOT:-/workspace/proof}
work_root=${WORK_ROOT:-/workspace/smallsort-work/network-n13}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
runner_evidence="$evidence_root/network-n13"
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
  'stage_exit_status':status,'failed_stage':'cloud-setup','evidence_root':'allprooflogs'
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

setup_deadline=$((SECONDS + 120))
setup_run() {
  local remaining=$((setup_deadline - SECONDS))
  if (( remaining <= 0 )); then
    printf 'Network N13 setup exceeded its 120-second allowance\n' >&2
    return 124
  fi
  timeout --signal=TERM "${remaining}s" "$@"
}

setup_run python3 "$infra_root/research/challenge-8/cloud-build/provider.py" > "$work_root/provider.json"

export DEBIAN_FRONTEND=noninteractive
setup_run apt-get update
setup_run apt-get install --yes --no-install-recommends ca-certificates curl \
  libgmp10 libmpfr6 libgomp1 libffi8 libncurses6 libtinfo6 zlib1g libz3-4 \
  libgtk-3-0 libgtksourceview-4-0

setup_run curl -fL --connect-timeout 20 --max-time 90 -o "$archive" \
  https://github.com/verifast/verifast/releases/download/26.09/verifast-26.09-linux.tar.gz
printf '%s  %s\n' \
  da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa \
  "$archive" | setup_run sha256sum -c - | tee "$work_root/verifast-archive-sha256.txt"
setup_run tar -xzf "$archive" -C "$tool_parent"
[[ -x "$tool_home/bin/verifast" ]] || { printf 'unexpected VeriFast archive layout\n' >&2; exit 2; }
printf '%s  %s\n' \
  dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc \
  "$tool_home/bin/verifast" | setup_run sha256sum -c - | tee "$work_root/verifast-console-sha256.txt"

set +e
export LD_LIBRARY_PATH="$tool_home/bin:${LD_LIBRARY_PATH:-}"
python3 "$proof_root/research/challenge-8/network/n13/run-cloud.py" \
  --tool-home "$tool_home" --evidence "$runner_evidence" --stage "$stage" > "$runner_log" 2>&1
runner_status=$?
set -e
cat "$runner_log"

python3 - "$evidence_root" "$runner_evidence" "$work_root" "$stage" "$runner_status" <<'EVIDENCE'
import json,pathlib,shutil,sys
evidence,runner_evidence,work=map(pathlib.Path,sys.argv[1:4])
stage=sys.argv[4]
status=int(sys.argv[5])
results=runner_evidence/'results.json'
summary={}
try:
    value=json.loads(results.read_text())
    if isinstance(value,dict): summary=value
except (OSError,ValueError):
    pass
cases_dir=evidence/'allprooflogs'/'cases'
cases_dir.mkdir(parents=True,exist_ok=True)
case_rows=summary.get('cases') if isinstance(summary.get('cases'),list) else []
for row in case_rows:
    if not isinstance(row,dict) or not isinstance(row.get('name'),str): continue
    name=row['name']
    for suffix in ('.c','.log'):
        source=runner_evidence/(name+suffix)
        if source.is_file() and not source.is_symlink():
            shutil.copyfile(source,cases_dir/(name+suffix))
stage_dir=evidence/'allprooflogs'
(stage_dir/'network-n13-stage.log').write_text((work/'network-n13-runner.log').read_text(errors='replace'))
(stage_dir/'network-n13-stage-exit-code.txt').write_text(str(status)+'\n')
for name in ('provider.json','verifast-archive-sha256.txt','verifast-console-sha256.txt'):
    source=work/name
    if source.is_file(): shutil.copyfile(source,evidence/name)
complete=(status==0 and summary.get('complete') is True and isinstance(summary.get('cases'),list))
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
}
(stage_dir/'proof-audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
if not case_rows:
    (cases_dir/'runner-result.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
EVIDENCE
exit "$runner_status"
