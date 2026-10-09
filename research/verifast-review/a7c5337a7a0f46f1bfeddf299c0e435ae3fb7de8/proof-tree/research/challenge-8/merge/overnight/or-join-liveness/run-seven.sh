#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Separate Cloud-only diagnostic. It never changes the retained proof harness.
set -euo pipefail
fail() { printf 'MIR-OR-JOIN-LIVENESS run refusal: %s\n' "$*" >&2; exit 2; }
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] ||
  fail 'Cloud Build provider is required'
python3 "${SMALLSORT_PROVIDER_FILE:?provider helper is required}" >/dev/null ||
  fail 'Cloud Build provider certificate failed'

base=${1:?usage: run-seven.sh base6-home base6-build-evidence fixture schema sysroot evidence}
base_evidence=${2:?usage: run-seven.sh base6-home base6-build-evidence fixture schema sysroot evidence}
fixture=${3:?usage: run-seven.sh base6-home base6-build-evidence fixture schema sysroot evidence}
schema=${4:?usage: run-seven.sh base6-home base6-build-evidence fixture schema sysroot evidence}
sysroot=${5:?usage: run-seven.sh base6-home base6-build-evidence fixture schema sysroot evidence}
evidence=${6:?usage: run-seven.sh base6-home base6-build-evidence fixture schema sysroot evidence}
repo=$(git rev-parse --show-toplevel)
component="$repo/research/challenge-8/merge/overnight/or-join-liveness"
manifest="$component/PINNED-INPUTS.json"
pointer_prove="$repo/research/challenge-8/merge/overnight/pointer-prove.py"
baseline_fixture="$repo/research/challenge-8/merge/overnight/baseline-cases.rs"
calibration_fixture="$component/coverage-controls.rs"
work_budget=${OR_JOIN_WORK_SECONDS:-1300}
[[ "$work_budget" =~ ^[1-9][0-9]{0,3}$ ]] && (( work_budget <= 1300 )) ||
  fail 'OR_JOIN_WORK_SECONDS must be an integer in 1..1300'
work_started=$SECONDS
# Keep 10 s for a child's TERM/KILL grace and 30 s for final audit/packaging.
work_deadline=$((work_started + work_budget - 40))
remaining_work() {
  local left=$((work_deadline - SECONDS))
  if (( left > 0 )); then printf '%s\n' "$left"; else printf '0\n'; fi
}
budget_cap() {
  local requested=$1 left
  left=$(remaining_work)
  if (( left < requested )); then printf '%s\n' "$left";
  else printf '%s\n' "$requested"; fi
}
[[ "$evidence" == /workspace/* && ! -e "$evidence" ]] ||
  fail 'fresh Cloud workspace evidence path required'
mkdir -p "$evidence"
printf 'budget=%s timeout_grace=10 audit_reserve=30 started_seconds=%s\n' \
  "$work_budget" "$work_started" > "$evidence/work-budget.txt"
for name in calibrated-real-dead uncalibrated-liveness-controls actual-bounded admission-controls six-comparison; do
  printf 'NOT_RUN\n' > "$evidence/$name-exit-code.txt"
  printf 'NOT_RUN: stage has not started\n' > "$evidence/$name.log"
  printf 'NOT_RUN: stage has not started\n' > "$evidence/$name-resources.txt"
done
printf '%s\n' \
  'calibrated-real-dead NOT_RUN' \
  'uncalibrated-liveness-controls NOT_RUN' \
  'actual-bounded NOT_RUN' \
  'admission-controls NOT_RUN' \
  'six-comparison NOT_RUN' > "$evidence/group-status.txt"
CURRENT_STAGE=initialization
write_partial_audit() {
  local status=$?
  printf '%s\n' "$status" > "$evidence/seven-run-exit-code.txt"
  if [[ -f "$evidence/seven-audit.json" ]]; then return "$status"; fi
  python3 - "$evidence/seven-audit.json" "$status" "$CURRENT_STAGE" "$work_budget" <<'AUDIT'
import json,pathlib,sys
path,status,stage,budget=sys.argv[1:]
root=pathlib.Path(path).parent
mode=(root/"trial-mode.txt").read_text().strip() if (root/"trial-mode.txt").is_file() else "UNKNOWN"
names=("calibrated-real-dead","uncalibrated-liveness-controls","actual-bounded","admission-controls","six-comparison")
groups={name:(root/(name+"-exit-code.txt")).read_text().strip()
        for name in names}
pathlib.Path(path).write_text(json.dumps({
  "component":"MIR-OR-JOIN-LIVENESS","accepted":False,
  "component_gates_complete":False,"base_six_profile_accepted":False,
  "diagnostic_complete":False,"shape_controls_complete_in_this_run":False,
  "trial_mode":mode,"classification":"INCONCLUSIVE",
  "exit_status":int(status),"failed_stage":stage,
  "group_status":groups,"work_budget_seconds":int(budget),
  "same_source_six_component_comparison":{
    "classification":"NOT_RUN" if groups["six-comparison"]=="NOT_RUN" else "INCONCLUSIVE",
    "accepted":False,"proof_negative":False,
    "group_status":groups["six-comparison"],"complete":False}
},sort_keys=True,indent=2)+"\n")
AUDIT
  return "$status"
}
trap write_partial_audit EXIT
trial_mode=$(python3 - "$manifest" <<'MODE'
import json, pathlib, sys
mode=json.loads(pathlib.Path(sys.argv[1]).read_text()).get("trial_mode", "FULL_TARGET")
if mode not in ("FULL_TARGET", "SHAPE_CONTROLS_ONLY"):
    raise SystemExit("unknown seventh component trial_mode")
print(mode)
MODE
) || fail 'trial mode is not admitted'
printf '%s\n' "$trial_mode" > "$evidence/trial-mode.txt"
[[ -f "$schema" && -d "$sysroot" && -f "$fixture" ]] ||
  fail 'schema, compiler sysroot or exact fixture is missing'
[[ -f "$pointer_prove" && -f "$baseline_fixture" &&
   -f "$calibration_fixture" ]] ||
  fail 'retained proof harness or control fixture is missing'
python3 - "$manifest" "$component" <<'CHECKERS'
import hashlib, json, pathlib, sys
pin=json.loads(pathlib.Path(sys.argv[1]).read_text())
root=pathlib.Path(sys.argv[2])
for key,name in (("preflight_checker_sha256","preflight-source.py"),
                 ("audit_checker_sha256","audit-seven.py"),
                 ("control_driver_sha256","control-driver.py"),
                 ("control_exporter_sha256","control-exporter.py")):
    expected=pin.get(key)
    actual=hashlib.sha256((root/name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit("seventh component checker pin mismatch: " + name)
CHECKERS

CURRENT_STAGE=exact-source-preflight
preflight_status=0
preflight_cap=$(budget_cap 50)
(( preflight_cap >= 10 )) || fail 'work budget exhausted before source preflight'
timeout --signal=TERM --kill-after=10s "${preflight_cap}s" \
  python3 "$component/preflight-source.py" \
  --fixture "$fixture" --pointer-prove "$pointer_prove" \
  --manifest "$manifest" --output "$evidence/preflight" \
  > "$evidence/preflight.log" 2>&1 || preflight_status=$?
printf '%s\n' "$preflight_status" > "$evidence/preflight-exit-code.txt"
(( preflight_status == 0 )) || fail 'exact source extraction refused'
CURRENT_STAGE=seven-console-build
build_cap=$(budget_cap 470)
(( build_cap >= 120 )) || fail 'work budget exhausted before seventh console build'
build_status=0
/usr/bin/time -v -o "$evidence/build-wrapper-resources.txt" \
  timeout --signal=TERM --kill-after=10s "${build_cap}s" \
  bash "$component/build-seven.sh" "$base" "$base_evidence" "$evidence/build" \
  > "$evidence/build-wrapper.log" 2>&1 || build_status=$?
printf '%s\n' "$build_status" > "$evidence/build-wrapper-exit-code.txt"
(( build_status == 0 )) || fail 'seventh console build failed or timed out'
seven=$(cat "$evidence/build/seven-source-home.txt")
[[ -x "$seven/bin/verifast" ]] || fail 'seventh console is absent'
export LD_LIBRARY_PATH="$sysroot/lib:$seven/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}"

CURRENT_STAGE=exact-source-profile-admission
admission_status=0
admission_cap=$(budget_cap 40)
(( admission_cap >= 10 )) || fail 'work budget exhausted before source/profile admission'
timeout --signal=TERM --kill-after=10s "${admission_cap}s" \
  python3 "$component/admit-source.py" \
  --manifest "$manifest" \
  --source "$evidence/preflight/bidirectional_merge_len23/verified/lib.rs" \
  --baseline-translator "$evidence/build/translator.six.ml" \
  --component-patch "$component/or-join-liveness.patch" \
  --component-translator "$evidence/build/translator.seven.ml" \
  > "$evidence/source-admission.log" 2>&1 || admission_status=$?
printf '%s\n' "$admission_status" > "$evidence/source-admission-exit-code.txt"
(( admission_status == 0 )) || fail 'exact source/profile admission refused'

profile=experimental-merge-six-plus-mir-or-join-liveness-v1-unaccepted
set_group_status() {
  local name=$1 status=$2
  sed -i -E "s/^${name} NOT_RUN.*$/${name} ${status}/" "$evidence/group-status.txt"
}
run_group() {
  local name=$1 requested=$2 minimum=$3 seconds status=0
  shift 3
  CURRENT_STAGE="$name"
  seconds=$(budget_cap "$requested")
  if (( seconds < minimum )); then
    printf 'NOT_RUN: remaining work budget %s s is below required minimum %s s\n' \
      "$seconds" "$minimum" > "$evidence/$name.log"
    printf 'NOT_RUN\n' > "$evidence/$name-resources.txt"
    printf 'NOT_RUN\n' > "$evidence/$name-exit-code.txt"
    return 0
  fi
  printf '%s\n' "$seconds" > "$evidence/$name-allocated-seconds.txt"
  /usr/bin/time -v -o "$evidence/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${seconds}s" "$@" \
    > "$evidence/$name.log" 2>&1 || status=$?
  printf '%s\n' "$status" > "$evidence/$name-exit-code.txt"
  set_group_status "$name" "$status"
}

if [[ "$trial_mode" == FULL_TARGET ]]; then
CURRENT_STAGE=calibrated-real-dead
printf '%s  %s\n' adfcfd5904eb037b8cb9669f232ee34b8cb95e1f60187536d3ab4d7dddecd493 \
  "$baseline_fixture" | sha256sum -c - >/dev/null ||
  fail 'calibrated baseline fixture hash changed'
dead_cap=$(budget_cap 130)
dead_vf=$((dead_cap - 15))
if (( dead_vf > 35 )); then dead_vf=35; fi
if (( dead_vf < 1 )); then dead_vf=1; fi
run_group calibrated-real-dead 130 25 python3 "$pointer_prove" \
  --profile "$profile" \
  --scope 'existing exact unreachable real source statement dead-code negative; seventh component inactive for this function' \
  --tool-home "$seven" --compiler-sysroot "$sysroot" --schema "$schema" \
  --verifier-seconds "$dead_vf" --fixture "$baseline_fixture" \
  --cases unreachable_body_after_panic \
  --evidence "$evidence/calibrated-real-dead"

CURRENT_STAGE=uncalibrated-liveness-controls
printf '%s  %s\n' d9f2e9e11a6b72bab2aa11396038a65096d572a35fe2a5b28bbdea1de65b64e1 \
  "$calibration_fixture" | sha256sum -c - >/dev/null ||
  fail 'new liveness control fixture hash changed'
calibration_cap=$(budget_cap 240)
calibration_vf=$(( (calibration_cap - 20) / 4 ))
if (( calibration_vf > 35 )); then calibration_vf=35; fi
if (( calibration_vf < 1 )); then calibration_vf=1; fi
run_group uncalibrated-liveness-controls 240 40 python3 "$pointer_prove" \
  --profile "$profile" \
  --scope 'CALIBRATION_ONLY real return, unreachable panic, source break and continue liveness under inactive join matcher; no accepted dead oracle' \
  --tool-home "$seven" --compiler-sysroot "$sysroot" --schema "$schema" \
  --verifier-seconds "$calibration_vf" --fixture "$calibration_fixture" \
  --evidence "$evidence/uncalibrated-liveness-controls"
fi

CURRENT_STAGE=actual-bounded
if [[ "$trial_mode" == SHAPE_CONTROLS_ONLY ]]; then
  actual_requested=180
  actual_minimum=35
  actual_vf=10
  actual_scope='SHAPE_CONTROLS_ONLY short unchanged full-post fixture for fresh normal MIR/proof AST/refinement capture; verifier timeout is INCONCLUSIVE, never a theorem PASS'
else
  actual_requested=680
  actual_minimum=70
  actual_cap=$(budget_cap 680)
  actual_vf=$((actual_cap - 60))
  if (( actual_vf > 600 )); then actual_vf=600; fi
  if (( actual_vf < 1 )); then actual_vf=1; fi
  actual_scope='actual unchanged bidirectional_merge len2/3; full original posts, callee bodies, normal/unwind, stack/panic admission, refinement and dead-code gates; seventh coverage-origin component unaccepted'
fi
run_group actual-bounded "$actual_requested" "$actual_minimum" python3 "$pointer_prove" \
  --profile "$profile" \
  --scope "$actual_scope" \
  --tool-home "$seven" --compiler-sysroot "$sysroot" --schema "$schema" \
  --verifier-seconds "$actual_vf" --fixture "$fixture" \
  --cases bidirectional_merge_len23 --evidence "$evidence/actual"

# These short tests use a third diagnostic tool copy. They cannot produce a
# theorem PASS and do not modify the production six/seven tool homes.
CURRENT_STAGE=admission-controls
driver_cap=$(budget_cap 240)
driver_work=$((driver_cap - 8))
if (( driver_work < 1 )); then driver_work=1; fi
if [[ -f "$evidence/actual/cases/bidirectional_merge_len23/normal-exporter.out" &&
      -f "$evidence/actual/cases/bidirectional_merge_len23/normal-exporter-provenance.json" ]]; then
  run_group admission-controls 240 30 python3 "$component/control-driver.py" \
    --six-home "$base" --seven-home "$seven" \
    --seven-build-manifest "$evidence/build/seven-profile-manifest.json" \
    --prepared-case "$evidence/preflight/bidirectional_merge_len23" \
    --preflight "$evidence/preflight/or-join-preflight.json" \
    --normal-mir-reference "$evidence/actual/cases/bidirectional_merge_len23/normal-exporter.out" \
    --schema "$schema" --sysroot "$sysroot" \
    --work-seconds "$driver_work" --evidence "$evidence/admission-controls"
else
  printf 'NOT_RUN: exact production normal MIR evidence unavailable\n' \
    > "$evidence/admission-controls.log"
fi

if [[ "$trial_mode" == FULL_TARGET ]]; then
# Compare the same exact source and posts under the unchanged six-component
# console. A single synthetic join-location dead record is only diagnostic;
# the retained harness still reports this case INCONCLUSIVE.
CURRENT_STAGE=six-comparison
six_cap=$(budget_cap 680)
six_vf=$((six_cap - 60))
if (( six_vf > 600 )); then six_vf=600; fi
if (( six_vf < 1 )); then six_vf=1; fi
run_group six-comparison 680 70 env \
  LD_LIBRARY_PATH="$sysroot/lib:$base/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}" \
  python3 "$pointer_prove" \
  --profile 'experimental-merge-six-same-source-comparison-v1-unaccepted' \
  --scope 'exact same admitted source/posts under unchanged six-patch console; synthetic join dead record is conditional coverage diagnostic only' \
  --tool-home "$base" --compiler-sysroot "$sysroot" --schema "$schema" \
  --verifier-seconds "$six_vf" --fixture "$fixture" \
  --cases bidirectional_merge_len23 --evidence "$evidence/six-comparison"
fi

CURRENT_STAGE=seventh-diagnostic-audit
audit_cap=$((work_started + work_budget - SECONDS))
if (( audit_cap > 25 )); then audit_cap=25; fi
(( audit_cap >= 1 )) || fail 'work budget exhausted before diagnostic audit'
timeout --signal=TERM --kill-after=3s "${audit_cap}s" \
  python3 "$component/audit-seven.py" --manifest "$manifest" \
  --evidence "$evidence" --profile "$profile" \
  --fixture "$fixture" --tool-home "$seven" --six-home "$base"
