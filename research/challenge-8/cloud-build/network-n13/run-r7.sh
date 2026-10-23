#!/usr/bin/env bash
# Called only after the unchanged stock26.09 archive/bootstrap checks in run.sh.
set -euo pipefail
[[ "${NETWORK_STAGE:-}" == swap-size ]] || { printf 'R7 requires swap-size stage\n' >&2; exit 2; }
tool_home=${1:?stock tool home required}
runner_evidence=${2:?runner evidence required}
infra_root=${INFRA_ROOT:-/workspace/infra}
proof_root=${PROOF_ROOT:-/workspace/proof}
work_root=${WORK_ROOT:-/workspace/smallsort-work/network-n13}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
for path in "$tool_home" "$runner_evidence" "$infra_root" "$proof_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || { printf 'R7 path outside /workspace\n' >&2; exit 2; }
done
python3 "$infra_root/research/challenge-8/cloud-build/provider.py" > "$work_root/r7-provider.json"
mkdir -p "$evidence_root/allprooflogs"
ev="$evidence_root/allprooflogs"
export RUSTUP_HOME="$work_root/rustup"
export CARGO_HOME="$work_root/cargo"
export RUSTUP_TOOLCHAIN=nightly-2026-02-05
export PATH="$CARGO_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$tool_home/bin:${LD_LIBRARY_PATH:-}"
mkdir -p "$RUSTUP_HOME" "$CARGO_HOME"
set +e
timeout --signal=TERM --kill-after=2s 450s bash -ceu '
  rustup_init="$CARGO_HOME/rustup-init-1.28.2"
  curl -fL --connect-timeout 20 --max-time 90 -o "$rustup_init" \
    https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
  printf "%s  %s\n" 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c "$rustup_init" | sha256sum -c -
  chmod +x "$rustup_init"
  "$rustup_init" -y --no-modify-path --default-toolchain none --profile minimal
  rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal --no-self-update \
    --component rustc-dev --component llvm-tools-preview --component rust-src
' > "$ev/r7-compiler-setup.log" 2>&1
setup_status=$?
printf '%s\n' "$setup_status" > "$ev/r7-compiler-setup-exit-code.txt"
runner_status=2
if (( setup_status == 0 )); then
  python3 "$proof_root/research/challenge-8/network/r7/run-cloud.py" \
    --tool-home "$tool_home" --evidence "$runner_evidence" > "$ev/r7-runner.log" 2>&1
  runner_status=$?
else
  printf 'R7 proof tools NOT_RUN: compiler setup exit %s\n' "$setup_status" > "$ev/r7-runner.log"
fi
set -e
printf '%s\n' "$runner_status" > "$ev/r7-runner-exit-code.txt"
python3 - "$ev" "$runner_evidence" "$work_root" "$setup_status" "$runner_status" <<'AUDIT'
import hashlib,json,pathlib,shutil,sys
root,cases,work=map(pathlib.Path,sys.argv[1:4]);setup,runner=map(int,sys.argv[4:])
audit={'accepted':False,'classification':'INCONCLUSIVE','diagnostic_complete':False,
       'component_accepted':False,'proof_credit':False,'lane':'network-n13','stage':'swap-size',
       'compiler_setup_exit_status':setup,'stage_exit_status':runner,'evidence_root':'allprooflogs'}
try:
    raw=(cases/'proof-audit.json').read_bytes();value=json.loads(raw)
    if (setup==0 and runner==0 and isinstance(value,dict) and
        value.get('accepted') is False and value.get('proof_credit') is False and
        value.get('lane')=='network-n13' and value.get('stage')=='swap-size' and
        value.get('component_accepted') is True and value.get('diagnostic_complete') is True and
        value.get('classification')=='NETWORK_R7_COMPONENT_CHECKED'):
        audit.update(value)
        audit['runner_audit_sha256']=hashlib.sha256(raw).hexdigest()
except (OSError,ValueError):
    pass
for name in ('provider.json','verifast-archive-sha256.txt','verifast-console-sha256.txt'):
    source=work/name
    if source.is_file():shutil.copyfile(source,root.parent/name)
(root/'proof-audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
AUDIT
if (( setup_status != 0 )); then exit "$setup_status"; fi
exit "$runner_status"
