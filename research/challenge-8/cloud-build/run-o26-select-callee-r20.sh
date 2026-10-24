#!/usr/bin/env bash
# R20 Select callee lane: nine-body actual select_unpredictable unit only.
# Reuses the reviewed O26 refresh tool build, provider-guard overlay, source
# preflight, capture, compare and baseline proof stages (blocker diagnostic).
# Exact R24 mode adds mutable positive proof; acceptance and proof credit remain off.
set -euo pipefail

proof_root=${PROOF_ROOT:-/workspace/proof}
infra_root=${INFRA_ROOT:-/workspace/infra}
cloud_dir=${INFRA_CLOUD_DIR:-$infra_root/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/smallsort-work}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
deadline=${SMALLSORT_DEADLINE_EPOCH:?SMALLSORT_DEADLINE_EPOCH is required}
current_sha=${PROOF_SHA:?PROOF_SHA is required}
[[ "$#" == 1 && "$1" == o26-select-callee-r20 &&
   "${LANE:-}" == o26-select-callee-r20 &&
   ( "${SORT4_R20_CALLEE_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-22-R20 ||
     "${SORT4_R20_CALLEE_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-23-R21 ) ]] || exit 2
# The R20 certificate opt-in is per proof call only, never ambient.
[[ -z "${SORT4_R20_FINAL_SELECT_REPAIR:-}" ]] || exit 2
[[ ! -v SORT4_R24_CHECKED_POINTER_OUTCOMES ]] || exit 2
while IFS= read -r route_env_key; do
  [[ "$route_env_key" != SORT4_R21_FRACTIONAL* ]] || exit 2
done < <(compgen -e)
for path in "$proof_root" "$infra_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || { printf 'path outside /workspace: %s\n' "$path" >&2; exit 2; }
done
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || exit 2
[[ -z "${GITHUB_ACTIONS:-}" ]] || { printf 'fake GitHub identity prohibited\n' >&2; exit 2; }
# The committed request is an explicit capture-only profile; absence is default off.
r24_mut_capture_only=0
r24_mut_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-CAPTURE-MODE.json"
if [[ -e "$r24_mut_mode_file" ]]; then
  [[ "$(sha256sum "$r24_mut_mode_file" | cut -d' ' -f1)" == 5ac2662dc74c166f17c01d11c7b44aa716ead91cc1ab24d6ee5fd6ad405ce624 ]] || exit 2
  python3 - "$r24_mut_mode_file" <<'MUT_MODE'
import json,os,pathlib,sys
m=json.loads(pathlib.Path(sys.argv[1]).read_text())
assert m['schema']=='select-r24-mut-capture-mode-v1'
assert m['enabled'] is True and m['source_only'] is True
assert m['proof_admission'] is False and m['publication_allowed'] is False
assert m['phase_id']==os.environ.get('SORT4_R24_SESSION_PHASE_ID')=='SORT4-ACTUAL-SELECT-2026-10-24-R24'
assert m['route_phase_id']==os.environ.get('SORT4_R20_CALLEE_PHASE_ID')=='SORT4-ACTUAL-SELECT-2026-10-23-R21'
assert m['owner']=='select-sort4' and m['independent_proof_credit']==0
MUT_MODE
  r24_mut_capture_only=1
fi
r24_mut_matrix_fingerprint_only=0
r24_mut_matrix_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-FINGERPRINT-MODE.json"
if [[ -e "$r24_mut_matrix_mode_file" ]]; then
  (( r24_mut_capture_only == 1 )) || exit 2
  [[ "$(sha256sum "$r24_mut_matrix_mode_file" | cut -d' ' -f1)" == 0f8c816ff1e588cd8f2cb066fae862ea17b07103397b5282982cb1c86cc84317 ]] || exit 2
  [[ "$(sha256sum "$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-CAPTURE-PINS.json" | cut -d' ' -f1)" == b10d8f472fd9babc5e73cb7a8da14ad691b0563975d0d6d956366165a47401d0 ]] || exit 2
  python3 - "$r24_mut_matrix_mode_file" <<'MUT_MATRIX_MODE'
import json,os,pathlib,sys
m=json.loads(pathlib.Path(sys.argv[1]).read_text())
assert m['schema']=='select-r24-mut-matrix-fingerprint-mode-v1'
assert m['enabled'] is True and m['source_only'] is True
assert m['proof_admission'] is False and m['publication_allowed'] is False
assert m['phase_id']==os.environ.get('SORT4_R24_SESSION_PHASE_ID')=='SORT4-ACTUAL-SELECT-2026-10-24-R24'
assert m['route_phase_id']==os.environ.get('SORT4_R20_CALLEE_PHASE_ID')=='SORT4-ACTUAL-SELECT-2026-10-23-R21'
assert m['owner']=='select-sort4' and type(m['independent_proof_credit']) is int and m['independent_proof_credit']==0
assert m['positive_pins_file']=='research/challenge-8/task-history/select-callee-r24/P2-MUT-CAPTURE-PINS.json'
assert m['positive_pins_sha256']=='b10d8f472fd9babc5e73cb7a8da14ad691b0563975d0d6d956366165a47401d0'
assert m['positive_evidence_build']=='b606d510-6832-483e-8168-afe8ef5fe9b4'
assert m['variant_order']==['positive','omit-selected-own','omit-unselected-own','no-retained-half','callee-false-normal','callee-owner-duplicate','callee-owner-loss','callee-thread-duplicate']
MUT_MATRIX_MODE
  r24_mut_matrix_fingerprint_only=1
fi
r24_mut_proof_enabled=0
r24_mut_proof_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-PROOF-MODE.json"
if [[ -e "$r24_mut_proof_mode_file" ]]; then
  (( r24_mut_matrix_fingerprint_only == 1 )) || exit 2
  [[ "${SORT4_R24_SESSION_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-24-R24 ]] || exit 2
  [[ "$(sha256sum "$r24_mut_proof_mode_file" | cut -d' ' -f1)" == bcbe8f080fd29cc3fc2c9282a92d6e54202c526de7d187d57ab47f822489046e ]] || exit 2
  r24_mut_proof_enabled=1
fi
r24_mut_matrix_proof_enabled=0
r24_mut_matrix_proof_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PROOF-MODE.json"
if [[ -e "$r24_mut_matrix_proof_mode_file" ]]; then
  (( r24_mut_proof_enabled == 1 )) || exit 2
  [[ "$(sha256sum "$r24_mut_matrix_proof_mode_file" | cut -d' ' -f1)" == 7870ea7c985914a1af049f685d62291bfe8d9768c0e4719c40422106d559fa94 ]] || exit 2
  [[ "$(sha256sum "$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-POSITIVE-EVIDENCE.json" | cut -d' ' -f1)" == 5b6f58485534622f66c246d37e17bd2f43cd2d2e2b020cc5c4c020d30374ee2a ]] || exit 2
  r24_mut_matrix_proof_enabled=1
fi
r24_mut_classified_proof_enabled=0
r24_mut_classified_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-CLASSIFIED-PROOF-MODE.json"
if [[ -e "$r24_mut_classified_mode_file" ]]; then
  (( r24_mut_matrix_proof_enabled == 1 )) || exit 2
  [[ "$(sha256sum "$r24_mut_classified_mode_file" | cut -d' ' -f1)" == 3e17c17a993f01e8d136effd2ec3026f11825ef30793eb5178d9fe2f787131b7 ]] || exit 2
  r24_mut_classified_proof_enabled=1
fi
r24_mut_refusal_enabled=0
r24_mut_refusal_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/P2-MUT-REFUSAL-MODE.json"
if [[ -e "$r24_mut_refusal_mode_file" ]]; then
  (( r24_mut_classified_proof_enabled == 1 )) || exit 2
  [[ "$(sha256sum "$r24_mut_refusal_mode_file" | cut -d' ' -f1)" == 63e2ae67bf6c66868fd9d79f4c21919909649e8befcb188bda22c257cead71b9 ]] || exit 2
  r24_mut_refusal_enabled=1
fi
# This separate W4 step captures the unchanged body; it never calls a verifier.
# The absent mode keeps the existing callee pipeline and its matrices unchanged.
r24_w4_capture_only=0
r24_w4_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json"
r24_w4_helper="$cloud_dir/select-callee-r24-w4-capture.py"
if [[ -e "$r24_w4_mode_file" ]]; then
  (( r24_mut_proof_enabled == 1 )) || exit 2
  [[ "${SORT4_R24_SESSION_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-24-R24 ]] || exit 2
  [[ ! -v SORT4_R21_BODY_PHASE_ID ]] || exit 2
  [[ "$(sha256sum "$r24_w4_mode_file" | cut -d' ' -f1)" == 1d251b0d1a48ec1c3310e9ae179f7a750b8608ec57c31a4da3b46ce6e12fe0a3 ]] || exit 2
  [[ "$(sha256sum "$r24_w4_helper" | cut -d' ' -f1)" == 8f3c8bddd385754aeaa4b784f3273a56e6af2f5356658c4df3d50f7c519f812d ]] || exit 2
  [[ "$(sha256sum "$proof_root/research/challenge-8/task-history/select-callee-r23/P2-INTERFACE.json" | cut -d' ' -f1)" == 656b15c1f295db2f7935f14067cf17067f04186994009715772157eb97fd2322 ]] || exit 2
  [[ "$(sha256sum "$proof_root/research/challenge-8/task-history/select-callee-r24/CONST-CALLEE-QUALIFICATION.json" | cut -d' ' -f1)" == 1d50cc12011cd8bae26f1a69fee7e43579ab3ef9bacf5708eac33875a4a00794 ]] || exit 2
  r24_w4_capture_only=1
fi
r24_w4_linkage_diagnostic=0
r24_w4_linkage_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/W4-LINKAGE-DIAGNOSTIC-MODE.json"
r24_w4_linkage_helper="$cloud_dir/select-callee-r24-w4-linkage-diagnostic.py"
if [[ -e "$r24_w4_linkage_mode_file" ]]; then
  (( r24_w4_capture_only == 1 )) || exit 2
  [[ "$(sha256sum "$r24_w4_linkage_mode_file" | cut -d' ' -f1)" == c4ef47f1c62f8777452c99a5c09317698e27413538f86d3ef003f8fc5dc494eb ]] || exit 2
  [[ "$(sha256sum "$r24_w4_linkage_helper" | cut -d' ' -f1)" == d10258f170072392a65773f609bfe8b7de6ca7625eaa5e176e710483cb7f80b0 ]] || exit 2
  [[ "$(sha256sum "$cloud_dir/select-callee-r24-w4-mir-calls.py" | cut -d' ' -f1)" == 024004290c45a4fa53e20db0f6f1e0eb7227c7eb0a433dce77b1e81407172928 ]] || exit 2
  [[ "$(sha256sum "$proof_root/research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-PINS.json" | cut -d' ' -f1)" == f81b062111436a7ab8a40e9776fdc1d1138a7861b5a6d95e018201ee93d5b6a0 ]] || exit 2
  r24_w4_linkage_diagnostic=1
fi
# Current-tool const matrix plus a checked post consequence, never a body summary.
r24_w4_const_qualification=0
r24_w4_const_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/W4-CONST-QUALIFICATION-MODE.json"
r24_w4_const_helper="$cloud_dir/select-callee-r24-w4-const-qualification.py"
if [[ -e "$r24_w4_const_mode_file" ]]; then
  (( r24_w4_linkage_diagnostic == 1 )) || exit 2
  [[ "$(sha256sum "$r24_w4_const_mode_file" | cut -d' ' -f1)" == b633c38b1d91d3e016b96dee2833d1bd9823f919526635feb67f2ac0ea920b12 ]] || exit 2
  [[ "$(sha256sum "$r24_w4_const_helper" | cut -d' ' -f1)" == 6f23bb54da4454452ea775889ad4a4386781b2857d0efcad662344fffdbb42f8 ]] || exit 2
  [[ "$(sha256sum "$cloud_dir/select-callee-r24-w4-const-consequence.py" | cut -d' ' -f1)" == bf89a183e39fddf17ea6247859775b4d0bb72febae635df67b15fccf744de420 ]] || exit 2
  [[ "$(sha256sum "$proof_root/research/challenge-8/task-history/select-callee-r24/W4-INPUTS-QUALIFICATION.json" | cut -d' ' -f1)" == 03a5e3b3afa601592a61e3f7a01c1485e674ac9f03ff8689c52c220361d75dce ]] || exit 2
  r24_w4_const_qualification=1
fi
positive_ast_args=()
target_map_args=()
if [[ -n "${SORT4_R24_SESSION_PHASE_ID:-}" ]]; then
  [[ "${SORT4_R24_SESSION_PHASE_ID}" == SORT4-ACTUAL-SELECT-2026-10-24-R24 ]] || exit 2
  positive_ast_args=(--positive-ast-inventory --checked-pointer-outcomes)
  target_map_path="$proof_root/research/challenge-8/task-history/select-callee-r24/CONTROL-TARGETS.json"
  [[ "$(sha256sum "$target_map_path" | cut -d' ' -f1)" == a6bde55bf08490352cae04fbaa61aa85f33a94890d52e8fe3147f50859e588dc ]] || exit 2
  target_map_args=(--target-map "$target_map_path")
fi
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "$current_sha" ]] || exit 2
[[ -d "$cloud_dir" ]] || exit 2
mkdir -p "$work_root" "$evidence_root"
ev="$evidence_root/allprooflogs"
[[ ! -e "$ev" ]] || { printf 'O26 refresh evidence already exists: %s\n' "$ev" >&2; exit 2; }
mkdir "$ev"
mkdir "$ev/cases"
current_stage=provider
audit_result() {
  if (( ${r24_w4_const_qualification:-0} == 1 )); then
    local const_audit_exit=0
    local const_audit_report="$ev/cases/r24-w4-const-qualification/W4-CONST-QUALIFICATION-AUDIT.json"
    local const_audit_mirror="$evidence_root/proof-audit.json"
    python3 "$r24_w4_const_helper" audit \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "${source_home:-/workspace/missing-native-tool}" \
      --native-tool-home "${w4_native_home:-/workspace/missing-w4-fingerprint-tool}" \
      --schema "${w4_native_home:-/workspace/missing-w4-fingerprint-tool}/src/rust_frontend/vf_mir/vf_mir.capnp" \
      --compiler-sysroot "${compiler_sysroot:-/workspace/missing-sysroot}" \
      --deadline-epoch "$deadline" --candidate "$current_sha" \
      --capture-mode-file "$r24_w4_mode_file" --mode-file "$r24_w4_const_mode_file" \
      --output "$const_audit_report" --runner-exit "$1" --failed-stage "$2" || const_audit_exit=$?
    if [[ ! -f "$const_audit_report" || -L "$const_audit_report" || \
          -e "$const_audit_mirror" || -L "$const_audit_mirror" ]]; then
      (( const_audit_exit != 0 )) && return "$const_audit_exit"
      return 1
    fi
    if ! python3 -c 'import json,sys; d=json.load(open(sys.argv[1], encoding="utf-8")); assert type(d) is dict and d.get("schema") == "select-r24-w4-const-qualification-v1-audit" and type(d.get("evidence_complete")) is bool and type(d.get("runner_exit")) is int and d.get("runner_exit") == int(sys.argv[2]) and d.get("failed_stage") == sys.argv[3] and d.get("accepted") is False and d.get("publication_allowed") is False and type(d.get("proof_credit")) is int and d.get("proof_credit") == 0' \
        "$const_audit_report" "$1" "$2"; then
      (( const_audit_exit != 0 )) && return "$const_audit_exit"
      return 1
    fi
    if ! cp -- "$const_audit_report" "$const_audit_mirror"; then
      (( const_audit_exit != 0 )) && return "$const_audit_exit"
      return 1
    fi
    return "$const_audit_exit"
  fi
  if (( ${r24_w4_linkage_diagnostic:-0} == 1 )); then
    local linkage_audit_exit=0
    local linkage_audit_report="$ev/cases/r24-w4-linkage-diagnostic/W4-LINKAGE-DIAGNOSTIC-AUDIT.json"
    local linkage_audit_mirror="$evidence_root/proof-audit.json"
    python3 "$r24_w4_linkage_helper" audit \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "${source_home:-/workspace/missing-native-tool}" \
      --native-tool-home "${w4_native_home:-/workspace/missing-w4-fingerprint-tool}" \
      --schema "${schema:-/workspace/missing-schema}" --compiler-sysroot "${compiler_sysroot:-/workspace/missing-sysroot}" \
      --deadline-epoch "$deadline" --candidate "$current_sha" \
      --capture-mode-file "$r24_w4_mode_file" --mode-file "$r24_w4_linkage_mode_file" \
      --output "$linkage_audit_report" --runner-exit "$1" --failed-stage "$2" || linkage_audit_exit=$?
    if [[ ! -f "$linkage_audit_report" || -L "$linkage_audit_report" || \
          -e "$linkage_audit_mirror" || -L "$linkage_audit_mirror" ]]; then
      (( linkage_audit_exit != 0 )) && return "$linkage_audit_exit"
      return 1
    fi
    if ! python3 -c 'import json,sys; d=json.load(open(sys.argv[1], encoding="utf-8")); assert type(d) is dict and d.get("schema") == "select-r24-w4-linkage-diagnostic-v1-audit" and type(d.get("evidence_complete")) is bool and type(d.get("runner_exit")) is int and d.get("runner_exit") == int(sys.argv[2]) and d.get("failed_stage") == sys.argv[3] and d.get("accepted") is False and d.get("publication_allowed") is False and type(d.get("proof_credit")) is int and d.get("proof_credit") == 0' \
        "$linkage_audit_report" "$1" "$2"; then
      (( linkage_audit_exit != 0 )) && return "$linkage_audit_exit"
      return 1
    fi
    if ! cp -- "$linkage_audit_report" "$linkage_audit_mirror"; then
      (( linkage_audit_exit != 0 )) && return "$linkage_audit_exit"
      return 1
    fi
    return "$linkage_audit_exit"
  fi
  if (( ${r24_w4_capture_only:-0} == 1 )); then
    python3 "$r24_w4_helper" audit \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "${source_home:-/workspace/missing-native-tool}" \
      --schema "${schema:-/workspace/missing-schema}" --compiler-sysroot "${compiler_sysroot:-/workspace/missing-sysroot}" \
      --deadline-epoch "$deadline" --candidate "$current_sha" --mode-file "$r24_w4_mode_file" \
      --output "$evidence_root/proof-audit.json" --runner-exit "$1" --failed-stage "$2"
    return $?
  fi
  if (( r24_mut_classified_proof_enabled == 1 )); then
    local classified_audit_exit=0 consequence_audit_exit=0 p2_composite_audit_exit=0 refusal_audit_exit=0
    python3 "$cloud_dir/select-callee-r24-mut-classified-proof.py" audit \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --classified-mode-file "$r24_mut_classified_mode_file" \
      --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file" \
      --tool-home "${source_home:-/workspace/missing-native-tool}" --candidate "$current_sha" \
      --output "$evidence_root/proof-audit.json" --runner-exit "$1" --failed-stage "$2" || classified_audit_exit=$?
    python3 "$cloud_dir/select-callee-r24-p2-entailment.py" audit \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "${source_home:-/workspace/missing-native-tool}" \
      --schema "${schema:-/workspace/missing-schema}" --compiler-sysroot "${compiler_sysroot:-}" \
      --candidate "$current_sha" --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file" \
      --output "$ev/p2-consequence-audit.json" --runner-exit "$1" --failed-stage "$2" || consequence_audit_exit=$?
    python3 - "$evidence_root/proof-audit.json" "$ev/p2-consequence-audit.json" "$classified_audit_exit" "$consequence_audit_exit" <<'P2_CONSEQUENCE_AUDIT' || p2_composite_audit_exit=$?
import json,pathlib,sys
root,extra=map(pathlib.Path,sys.argv[1:3]);codes=list(map(int,sys.argv[3:]));read_errors=[]
def read(path):
 try:
  value=json.loads(path.read_text())
  if not isinstance(value,dict):raise ValueError('audit is not an object')
  return value
 except (OSError,ValueError) as exc:
  read_errors.append(path.name+': '+str(exc));return {'evidence_complete':False}
record=read(root);consequence=read(extra)
record['p2_consequence_audit']=consequence
record['composite_audit_exits']=codes
record['composite_audit_errors']=read_errors
record['evidence_complete']=codes==[0,0] and not read_errors and record.get('evidence_complete') is True and consequence.get('evidence_complete') is True
record.update(accepted=False,publication_allowed=False,proof_credit=0,verification_accepted=False)
root.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
assert record['evidence_complete'] is True
P2_CONSEQUENCE_AUDIT
    if (( r24_mut_refusal_enabled == 1 )); then
      python3 "$cloud_dir/select-callee-r24-mut-refusal-entry.py" audit \
        --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
        --refusal-mode-file "$r24_mut_refusal_mode_file" \
        --classified-mode-file "$r24_mut_classified_mode_file" \
        --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file" \
        --tool-home "${source_home:-/workspace/missing-native-tool}" \
        --schema "${schema:-/workspace/missing-schema}" --compiler-sysroot "${compiler_sysroot:-}" \
        --candidate "$current_sha" --deadline-epoch "$deadline" \
        --output "$ev/mutable-refusal-audit.json" \
        --runner-exit "$1" --failed-stage "$2" || refusal_audit_exit=$?
      python3 - "$evidence_root/proof-audit.json" "$ev/mutable-refusal-audit.json" "$p2_composite_audit_exit" "$refusal_audit_exit" <<'MUT_REFUSAL_AUDIT'
import json,pathlib,sys
root,extra=map(pathlib.Path,sys.argv[1:3]);codes=list(map(int,sys.argv[3:]));read_errors=[]
def read(path):
 try:
  value=json.loads(path.read_text())
  if not isinstance(value,dict):raise ValueError('audit is not an object')
  return value
 except (OSError,ValueError) as exc:
  read_errors.append(path.name+': '+str(exc));return {'evidence_complete':False}
record=read(root);refusals=read(extra)
record['mutable_refusal_audit']=refusals
record['refusal_composite_audit_exits']=codes
record['refusal_composite_audit_errors']=read_errors
record['evidence_complete']=codes==[0,0] and not read_errors and record.get('evidence_complete') is True and refusals.get('evidence_complete') is True
record.update(accepted=False,publication_allowed=False,proof_credit=0,verification_accepted=False)
root.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
assert record['evidence_complete'] is True
MUT_REFUSAL_AUDIT
      return "$?"
    fi
    return "$p2_composite_audit_exit"
  fi
  if (( r24_mut_matrix_proof_enabled == 1 )); then
    python3 "$cloud_dir/select-callee-r24-mut-matrix-proof.py" audit \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file" \
      --tool-home "${source_home:-/workspace/missing-native-tool}" --candidate "$current_sha" \
      --output "$evidence_root/proof-audit.json" --runner-exit "$1" --failed-stage "$2"
    return
  fi
  if (( r24_mut_proof_enabled == 1 )); then
    python3 "$cloud_dir/select-callee-r24-mut-proof-entry.py" audit \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --proof-mode-file "$r24_mut_proof_mode_file" --output "$evidence_root/proof-audit.json" \
      --runner-exit "$1" --failed-stage "$2"
    return
  fi
  if (( r24_mut_matrix_fingerprint_only == 1 )); then
    python3 - "$ev/cases/r24-mut-matrix-fingerprint/MUT-MATRIX-FINGERPRINT.json" "$evidence_root/proof-audit.json" "$1" "$2" <<'MUT_MATRIX_AUDIT'
import json,os,pathlib,re,sys,uuid
source,output=map(pathlib.Path,sys.argv[1:3]);code=int(sys.argv[3]);failed=sys.argv[4]
summary=None;error=None
try:
 summary=json.loads(source.read_text())
except (OSError,ValueError) as exc:
 error=str(exc)
try:
 native=str(uuid.UUID(os.environ.get('CLOUD_BUILD_ID','')))
except (ValueError,TypeError,AttributeError):
 native=None
variants=['positive','omit-selected-own','omit-unselected-own','no-retained-half','callee-false-normal','callee-owner-duplicate','callee-owner-loss','callee-thread-duplicate']
provider=summary.get('provider_record') if isinstance(summary,dict) else None
rows=summary.get('rows') if isinstance(summary,dict) else None
location=summary.get('location_control') if isinstance(summary,dict) else None
base='3bf0bf792c8135bf964f19b3aaadef38b8ca5ee9ec95107029ad99d28a807aaa'
row_ok=isinstance(rows,dict) and set(rows)==set(variants)
if row_ok:
 hashes=[]
 for variant in variants:
  row=rows[variant]
  ok=(isinstance(row,dict) and row.get('complete') is True and row.get('status')=='COMPLETE_SOURCE_REPORTED_FINGERPRINT'
   and row.get('variant')==variant and row.get('native_build_id')==native and row.get('source_unchanged') is True
   and row.get('ghost_strip_identity') is True and row.get('original_sha256')==base
   and isinstance(row.get('verified_sha256'),str) and re.fullmatch('[0-9a-f]{64}',row['verified_sha256']) is not None)
  row_ok=row_ok and ok
  if ok:hashes.append(row['verified_sha256'])
 row_ok=row_ok and len(set(hashes))==8 and rows['positive'].get('verified_sha256')=='74b20681c4c34cdc9ecd0fbb7fb3d44c51941e5d9640ede5705c5d6b6fa25165'
complete=(code==0 and isinstance(summary,dict) and summary.get('schema')=='select-r24-mut-matrix-fingerprint-v1'
 and summary.get('complete') is True and summary.get('variant_order')==variants and row_ok
 and isinstance(location,dict) and location.get('complete') is True and location.get('reproduces_positive_pins') is True
 and location.get('native_build_id')==native and summary.get('native_build_id')==native
 and all(summary.get(key) is False for key in ['body_proof_run','typed_admission','semantic_rule_enabled','accepted','publication_allowed'])
 and type(summary.get('proof_credit')) is int and summary.get('proof_credit')==0
 and native is not None and native==os.environ.get('CLOUD_BUILD_ID') and isinstance(provider,dict)
 and provider.get('provider')=='cloud-build' and provider.get('build_id')==native and provider.get('project')=='smallsort-ci'
 and provider.get('region')=='global' and provider.get('os')=='ubuntu-22.04' and provider.get('arch')=='x86_64'
 and summary.get('r24_session_phase_id')==os.environ.get('SORT4_R24_SESSION_PHASE_ID')=='SORT4-ACTUAL-SELECT-2026-10-24-R24')
record={'schema':'select-r24-mut-matrix-fingerprint-audit-v1','scope':'SOURCE_MIR_MATRIX_FINGERPRINT_ONLY_NO_PROOF_ADMISSION',
 'runner_exit':code,'failed_stage':failed,'evidence_complete':complete,'fingerprint_summary':summary,
 'fingerprint_summary_error':error,'body_proof_run':False,'typed_admission':False,'verification_accepted':False,
 'accepted':False,'proof_credit':False,'publication_allowed':False}
output.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
MUT_MATRIX_AUDIT
    return
  fi
  if (( r24_mut_capture_only == 1 )); then
    python3 - "$ev/cases/r24-mut-capture/MUT-CAPTURE-SUMMARY.json" "$evidence_root/proof-audit.json" "$1" "$2" <<'MUT_AUDIT'
import json,os,pathlib,sys,uuid
source,output=map(pathlib.Path,sys.argv[1:3]); code=int(sys.argv[3]); failed=sys.argv[4]
summary=None; error=None
try:
 summary=json.loads(source.read_text())
except (OSError,ValueError) as exc:
 error=str(exc)
provider=summary.get('provider_record') if isinstance(summary,dict) else None
try:
 native_build_id=str(uuid.UUID(os.environ.get('CLOUD_BUILD_ID','')))
except (ValueError,TypeError,AttributeError):
 native_build_id=None
complete=(code==0 and isinstance(summary,dict) and summary.get('schema')=='select-r24-mut-capture-summary-v1'
 and summary.get('complete') is True and summary.get('body_proof_run') is False
 and summary.get('typed_admission') is False and summary.get('semantic_rule_enabled') is False
 and summary.get('publication_allowed') is False and summary.get('accepted') is False
 and type(summary.get('proof_credit')) is int and summary.get('proof_credit')==0 and isinstance(provider,dict)
 and native_build_id is not None and native_build_id==os.environ.get('CLOUD_BUILD_ID')
 and provider.get('provider')=='cloud-build' and provider.get('build_id')==native_build_id
 and provider.get('project')=='smallsort-ci' and provider.get('region')=='global'
 and provider.get('os')=='ubuntu-22.04' and provider.get('arch')=='x86_64'
 and summary.get('r24_session_phase_id')==os.environ.get('SORT4_R24_SESSION_PHASE_ID')=='SORT4-ACTUAL-SELECT-2026-10-24-R24')
record={'schema':'select-r24-mut-capture-audit-v1','scope':'SOURCE_MIR_CAPTURE_ONLY_NO_PROOF_ADMISSION',
 'runner_exit':code,'failed_stage':failed,'evidence_complete':complete,'capture_summary':summary,
 'capture_summary_error':error,'body_proof_run':False,'typed_admission':False,
 'verification_accepted':False,'accepted':False,'proof_credit':False,'publication_allowed':False}
output.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
MUT_AUDIT
    return
  fi
  python3 "$cloud_dir/select-callee-r21-proof-audit.py" --evidence "$ev" \
    --output "$evidence_root/proof-audit.json" \
    --runner-exit "$1" --failed-stage "$2"
}
trap 'status=$?; if [[ ! -f "$evidence_root/proof-audit.json" ]]; then audit_result "$status" "$current_stage" || true; fi' EXIT

CLOUD_BUILD_ID=${CLOUD_BUILD_ID:?} \
CLOUD_BUILD_PROJECT_ID=${CLOUD_BUILD_PROJECT_ID:?} \
CLOUD_BUILD_REGION=${CLOUD_BUILD_REGION:?} \
  python3 "$cloud_dir/provider.py" > "$ev/provider.json"

remaining() {
  local seconds=$((deadline - $(date +%s)))
  (( seconds > 0 )) || { printf 'deadline elapsed\n' >&2; exit 124; }
  printf '%s' "$seconds"
}
stage() {
  local name=$1; shift
  current_stage=$name
  local budget code=0
  budget=$(remaining)
  /usr/bin/time -v -o "$ev/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${budget}s" "$@" \
    > "$ev/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$ev/$name-exit-code.txt"
  cat "$ev/$name.log"
  (( code == 0 )) || return "$code"
}

# Source-only stages first: a missing closure file fails before the tool build.
stage provider-overlays python3 "$cloud_dir/o26-refresh-recipe.py" overlay \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev"
stage source-preflight python3 "$cloud_dir/o26-refresh-recipe.py" preflight \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev"


export RUSTUP_HOME="$work_root/rustup"
export CARGO_HOME="$work_root/cargo"
export PATH="$CARGO_HOME/bin:$PATH"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
export TMPDIR="$work_root/tmp"
mkdir -p "$RUSTUP_HOME" "$CARGO_HOME" "$TMPDIR"
task_temp="$work_root/o26-refresh"
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.10-linux.tar.gz"
stock_home="$task_temp/verifast-26.10"
source_home="$task_temp/source"
schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"
manifest="$proof_root/research/challenge-8/overnight-linkage/O26-PROFILE-MANIFEST.json"

python3 - "$manifest" "$proof_root" "$ev" <<'INPUTS'
import hashlib,json,pathlib,sys
m=pathlib.Path(sys.argv[1]); proof,ev=map(pathlib.Path,sys.argv[2:])
data=json.loads(m.read_text()); h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert data['proof_sha']=='c19e4c50470d32199178d5229a2819554fc6b2f1'
assert len(data['patches_in_application_order'])==20
assert data['kernel_modified'] is False
assert data['status']=='EXPERIMENTAL_O26_MAIN20_NOT_HELPER_ACCEPTANCE'
for i,row in enumerate(data['patches_in_application_order'],1):
 assert row['component']==i
 path=proof/'research/challenge-8'/row['path']
 assert h(path)==row['sha256'],f'patch pin mismatch {row["path"]}'
(ev/'frozen-profile.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
INPUTS

stage package-index apt-get update
stage packages-install apt-get install --yes --no-install-recommends \
  build-essential m4 patch unzip capnproto ripgrep time libgmp10 libmpfr6 \
  libgomp1 libffi8 libncurses6 libtinfo6 zlib1g libz3-4 libgtk-3-0 libgtksourceview-4-0
stage download curl -fL --retry 2 -o "$stock_archive" \
  https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd \
  "$stock_archive" | sha256sum -c - > "$ev/archive-sha256.log"
stage extract tar -xzf "$stock_archive" -C "$task_temp"
stage source-checkout git clone --depth 1 --branch 26.10 \
  https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
[[ "$(sha256sum "$schema" | cut -d' ' -f1)" == f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 ]] || exit 2
rustup_init="$work_root/rustup-init-1.28.2"
stage rustup-init-download curl -fL --retry 2 -o "$rustup_init" \
  https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
printf '%s  %s\n' 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c \
  "$rustup_init" | sha256sum -c - > "$ev/rustup-init-sha256.log"
chmod +x "$rustup_init"
stage rustup-init "$rustup_init" -y --no-modify-path --default-toolchain none --profile minimal
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal \
  --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
rustc --version --verbose > "$ev/compiler-version.txt"
rg -q '^commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f$' "$ev/compiler-version.txt"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:${LD_LIBRARY_PATH:-}"

mapfile -t patch_rows < <(python3 - "$manifest" <<'PATCHES'
import json,sys
for row in json.load(open(sys.argv[1]))['patches_in_application_order']:
 print(f"{row['component']} {row['path']} {row['sha256']}")
PATCHES
)
for row in "${patch_rows[@]}"; do
  read -r number relative expected <<< "$row"
  patch="$proof_root/research/challenge-8/$relative"
  [[ "$(sha256sum "$patch" | cut -d' ' -f1)" == "$expected" ]] || exit 2
  stage "patch-$number-check" git -C "$source_home" apply --check "$patch"
  stage "patch-$number-apply" git -C "$source_home" apply "$patch"
done
git -C "$source_home" diff --name-only > "$ev/modified-files.txt"
python3 - "$manifest" "$ev/modified-files.txt" <<'NAMES'
import json,pathlib,sys
m=json.load(open(sys.argv[1])); actual=pathlib.Path(sys.argv[2]).read_text().splitlines()
assert actual==sorted(m['production_modified_files']),(actual,m['production_modified_files'])
NAMES
git -C "$source_home" diff > "$ev/applied.patch"
[[ "$(sha256sum "$ev/applied.patch" | cut -d' ' -f1)" == 6c4c5a7708af3bdec585abd308d37383a7de522a1aaecf2c01e1f94181324c25 ]] || exit 2
cp "$ev/applied.patch" "$ev/frozen20-applied.patch"
profile="$proof_root/research/challenge-8/overnight-assume-actual/O26-REFRESH-PROFILE.json"
python3 - "$profile" "$proof_root" "$ev" <<'REFRESH'
import hashlib,json,pathlib,sys
m=json.load(open(sys.argv[1]));root=pathlib.Path(sys.argv[2]);ev=pathlib.Path(sys.argv[3])
assert m['classification']=='EXPERIMENTAL_O26_REFRESH_17_20'
assert m['historical20_applied_diff_sha256']=='6c4c5a7708af3bdec585abd308d37383a7de522a1aaecf2c01e1f94181324c25'
assert len(m['refresh_patches'])==2
for row in m['refresh_patches']:
 path=root/'research/challenge-8'/row['path']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
(ev/'refresh-profile.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
REFRESH
mapfile -t refresh_rows < <(python3 - "$profile" <<'PATCHES'
import json,sys
for row in json.load(open(sys.argv[1]))['refresh_patches']:
 print(f"{row['component']} {row['path']} {row['sha256']}")
PATCHES
)
for row in "${refresh_rows[@]}"; do
  read -r number relative expected <<< "$row"
  patch="$proof_root/research/challenge-8/$relative"
  [[ "$(sha256sum "$patch" | cut -d' ' -f1)" == "$expected" ]] || exit 2
  stage "refresh-$number-check" git -C "$source_home" apply --check "$patch"
  stage "refresh-$number-apply" git -C "$source_home" apply "$patch"
done
git -C "$source_home" diff --name-only > "$ev/refreshed-modified-files.txt"
cmp "$ev/modified-files.txt" "$ev/refreshed-modified-files.txt"
git -C "$source_home" diff > "$ev/refreshed-applied.patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a ]] || exit 2
# R21 opt-in certificate refresh for the branch-selected final-select repair;
# without SORT4_R20_FINAL_SELECT_REPAIR=1 the translator keeps the O26 pins.
branch_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r21-final-select-branch-selected-26.10.patch"
[[ "$(sha256sum "$branch_patch" | cut -d' ' -f1)" == 78079210a5548fee87e200996920bfb012bcb0cd17b0b574eb926806a46e7ab6 ]] || exit 2
stage branch-refresh-check git -C "$source_home" apply --check "$branch_patch"
stage branch-refresh-apply git -C "$source_home" apply "$branch_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 606235c66c76412d2fdcef5f30436c342771ad5a087b343f618cfb7c8a2344d2 ]] || exit 2
fractional_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r23-fractional-forget-26.10.patch"
current_stage=fractional-patch-identity
[[ "$(sha256sum "$fractional_patch" | cut -d' ' -f1)" == f954fb593665b71b2042d9e1476fbc0d1b8de124861fb8f48aed4be8d791d084 ]] || exit 2
stage fractional-refresh-check git -C "$source_home" apply --check "$fractional_patch"
stage fractional-refresh-apply git -C "$source_home" apply "$fractional_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 2d6f1950bd95b655560c767c54af8facfecde724f29a72c4218b65b6c6438c19 ]] || exit 2
# R23 exact fractional MIR coordinates, after full source/unit/body admission.
layout_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r23-fractional-mir-layout-26.10.patch"
current_stage=fractional-layout-identity
[[ "$(sha256sum "$layout_patch" | cut -d' ' -f1)" == 68810eb486d494cb49e158a13eab55b19464fad1b724bd9025cf5960b6c5bc17 ]] || exit 2
stage fractional-layout-check git -C "$source_home" apply --check "$layout_patch"
stage fractional-layout-apply git -C "$source_home" apply "$layout_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == cadaa80ab55e6fb3f53ccfcae1ab05dc953a2cb69a17616654d49dad6350478f ]] || exit 2
# UNBUILT next-window candidate: align erased ghost-call AST successors.
ghost_cfg_patch="$proof_root/research/challenge-8/task-history/select-callee-r23/ghost-cleanup-successor-fractional.patch"
current_stage=ghost-cfg-identity
[[ "$(sha256sum "$ghost_cfg_patch" | cut -d' ' -f1)" == 03f91fb5fe7cb25deabe5d6d7ab4e224e5559823b0c88b75a3c717dba088567d ]] || exit 2
stage ghost-cfg-check git -C "$source_home" apply --check "$ghost_cfg_patch"
stage ghost-cfg-apply git -C "$source_home" apply "$ghost_cfg_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44 ]] || exit 2
# R22 parser-only fix: a one-element coefficient before `<T>.pred(..)` in an
# assertion is parsed as CoefAsn instead of a `<` comparison on a list.
parser_patch="$proof_root/research/challenge-8/overnight-assume-actual/verifast-r22-coef-typepred-parser-26.10.patch"
current_stage=parser-patch-identity
[[ "$(sha256sum "$parser_patch" | cut -d' ' -f1)" == dfdaff604314ecf0e27c44320811096f05a8bd8833910c59321fdec33de7b0e5 ]] || exit 2
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/rust_parser.ml" | cut -d' ' -f1)" == 7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2 ]] || exit 2
stage parser-refresh-check git -C "$source_home" apply --check "$parser_patch"
stage parser-refresh-apply git -C "$source_home" apply "$parser_patch"
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/rust_parser.ml" | cut -d' ' -f1)" == 6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246 ]] || exit 2
[[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44 ]] || exit 2


# R24 dump-only utility support; verifier/translator semantics remain unchanged.
if (( ${#positive_ast_args[@]} > 0 )); then
  ast_serializer_patch="$proof_root/research/challenge-8/cloud-build/sort4-caller-entry-native/merge-fractions-ast-dump-r15.patch"
  ast_serializer_manifest="$proof_root/research/challenge-8/cloud-build/sort4-caller-entry-native/MERGE-FRACTIONS-AST-DUMP-R15-MANIFEST.json"
  current_stage=ast-serializer-identity
  [[ "$(sha256sum "$ast_serializer_patch" | cut -d' ' -f1)" == f08f1c391aa62e6cbeb0ad80e73958b1b6dcfd38f40b3d7d87802d12c4a534ba ]] || exit 2
  [[ "$(sha256sum "$ast_serializer_manifest" | cut -d' ' -f1)" == c529a3a45dc78a3f6f914d55f4e2e6cca29b7383f69827db1e20904d2db4b43b ]] || exit 2
  [[ "$(sha256sum "$source_home/src/frontend/ocaml_expr_of_ast.ml" | cut -d' ' -f1)" == 898203bf8fe5802478fdfd41456b49ad07f1e6fedf0535c3d303d4ec2081c9ff ]] || exit 2
  stage ast-serializer-check git -C "$source_home" apply --check "$ast_serializer_patch"
  stage ast-serializer-apply git -C "$source_home" apply "$ast_serializer_patch"
  [[ "$(sha256sum "$source_home/src/frontend/ocaml_expr_of_ast.ml" | cut -d' ' -f1)" == f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94 ]] || exit 2
  git -C "$source_home" diff --name-only > "$ev/r24-final-tool-modified-files.txt"
  python3 - "$manifest" "$ev/r24-final-tool-modified-files.txt" <<'R24_SCOPE'
import json,pathlib,sys
m=json.load(open(sys.argv[1]))
expected=sorted(m['production_modified_files']+['src/frontend/ocaml_expr_of_ast.ml'])
actual=pathlib.Path(sys.argv[2]).read_text().splitlines()
assert actual==expected,(actual,expected)
R24_SCOPE
fi


# R24 exact checked pointer outcomes; enabled only around ordinary proof calls.
if (( ${#positive_ast_args[@]} > 0 )); then
  checked_outcomes_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/checked-pointer-outcomes-r24.patch"
  current_stage=checked-outcomes-identity
  [[ "$(sha256sum "$checked_outcomes_patch" | cut -d' ' -f1)" == 81c5e18b5f754298aae94940a98a8fa3495b9d73b179d2697493b1c704070ddc ]] || exit 2
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44 ]] || exit 2
  stage checked-outcomes-check git -C "$source_home" apply --check "$checked_outcomes_patch"
  stage checked-outcomes-apply git -C "$source_home" apply "$checked_outcomes_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 6a710d26c41d69accd17aeb637e719ce7eabc321990d465a6d956ca0d0d7d93c ]] || exit 2
  checked_outcomes_scope_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/checked-pointer-outcomes-scope-r24.patch"
  current_stage=checked-outcomes-scope-identity
  [[ "$(sha256sum "$checked_outcomes_scope_patch" | cut -d' ' -f1)" == 3f342a74bd855cc4dd4e8e639fbd6d96790d14c76e718fed1b475e673a275563 ]] || exit 2
  stage checked-outcomes-scope-check git -C "$source_home" apply --check "$checked_outcomes_scope_patch"
  stage checked-outcomes-scope-apply git -C "$source_home" apply "$checked_outcomes_scope_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == e3c99165c2e5fc8ef5700dbaa3885c81310d26868e5e5ca61ecb019c4205d5db ]] || exit 2
  checked_outcomes_nine_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/checked-pointer-outcomes-nine-gate-r24.patch"
  current_stage=checked-outcomes-nine-gate-identity
  [[ "$(sha256sum "$checked_outcomes_nine_patch" | cut -d' ' -f1)" == 90ad23d24b3806690887e396cb2ec4b10e25ae53df8115cba00649aa26889a3a ]] || exit 2
  stage checked-outcomes-nine-gate-check git -C "$source_home" apply --check "$checked_outcomes_nine_patch"
  stage checked-outcomes-nine-gate-apply git -C "$source_home" apply "$checked_outcomes_nine_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e ]] || exit 2
  git -C "$source_home" diff --name-only > "$ev/r24-checked-outcomes-modified-files.txt"
  cmp "$ev/r24-final-tool-modified-files.txt" "$ev/r24-checked-outcomes-modified-files.txt"
fi


# Separate mutable family is compiled only for its exact committed mode.
if (( r24_mut_proof_enabled == 1 )); then
  mut_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/mutable-certificates-r24.patch"
  [[ "$(sha256sum "$mut_patch" | cut -d' ' -f1)" == e1b5b8aa78e905884565e16318e29559050e2fba41366a60d61ebdbe1aeb9099 ]] || exit 2
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e ]] || exit 2
  stage mutable-certificates-check git -C "$source_home" apply --check "$mut_patch"
  stage mutable-certificates-apply git -C "$source_home" apply "$mut_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == eca440a605ab3900c39d9e58328b487104a1b33f75d90323036f6beab09aa162 ]] || exit 2
  git -C "$source_home" diff --name-only > "$ev/r24-mut-tool-modified-files.txt"
  cmp "$ev/r24-final-tool-modified-files.txt" "$ev/r24-mut-tool-modified-files.txt"
  mut_a1_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/mutable-a1-primitives-r24.patch"
  [[ "$(sha256sum "$mut_a1_patch" | cut -d' ' -f1)" == e81f3a4c64df13432cbcdb9287a7247bd1e87884a6a35c901eefd0d7e0efbc4d ]] || exit 2
  stage mutable-a1-primitives-check git -C "$source_home" apply --check "$mut_a1_patch"
  stage mutable-a1-primitives-apply git -C "$source_home" apply "$mut_a1_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 11d4a092b3d91570307779cfc1e5b46ff37525343a62abb162109bfedbc22d0f ]] || exit 2
  git -C "$source_home" diff --name-only > "$ev/r24-mut-a1-modified-files.txt"
  cmp "$ev/r24-final-tool-modified-files.txt" "$ev/r24-mut-a1-modified-files.txt"
  mut_successor_patch="$proof_root/research/challenge-8/task-history/select-callee-r24/mutable-checked-successors-r24.patch"
  [[ "$(sha256sum "$mut_successor_patch" | cut -d' ' -f1)" == 07eed4b28d098812bb5e263297bac08c7dc372bc707be95f3d2b01c5832275a1 ]] || exit 2
  stage mutable-successors-check git -C "$source_home" apply --check "$mut_successor_patch"
  stage mutable-successors-apply git -C "$source_home" apply "$mut_successor_patch"
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007 ]] || exit 2
  git -C "$source_home" diff --name-only > "$ev/r24-mut-successor-modified-files.txt"
  cmp "$ev/r24-final-tool-modified-files.txt" "$ev/r24-mut-successor-modified-files.txt"
fi

deps_archive="$task_temp/vfdeps-adf88dc-linux.txz"
stage deps-download curl -fL --retry 2 -o "$deps_archive" \
  https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 \
  "$deps_archive" | sha256sum -c - > "$ev/deps-sha256.log"
stage deps-extract tar -xjf "$deps_archive" -C "$work_root"
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home" ]] || exit 2
for prefix in /vfdeps-adf88dc /tmp/vfdeps-adf88dc; do
  if [[ ! -e "$prefix" ]]; then ln -s "$deps_home" "$prefix"
  elif [[ "$(readlink -f "$prefix")" != "$deps_home" ]]; then exit 2; fi
done
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$source_home/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
stage decoder-install cargo install --locked --git \
  https://github.com/btj/capnpc-ocaml-decoder \
  --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
stage console-build make -C "$source_home/src" ../bin/verifast \
  WITHOUT_LABLGTK=yes VERBOSE=yes
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then
  mkdir -p "$source_home/lib"
  cp -an "$stock_home/lib/." "$source_home/lib/"
fi
for binary in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do
  cmp "$stock_home/bin/$binary" "$source_home/bin/$binary"
done
python3 - "$manifest" "$source_home" "$ev/profile-hashes.json" "$r24_mut_proof_enabled" <<'HASHES'
import hashlib,json,os,pathlib,sys
m=json.load(open(sys.argv[1])); root=pathlib.Path(sys.argv[2]); out=pathlib.Path(sys.argv[3])
rows={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in m['hosted_profile_hashes']}
for path in rows:
 if path=='src/rust_frontend/vf_mir_translator/rust_parser.ml':
  if rows[path]!='6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246':
   raise SystemExit(f'R22 parser pin differs: {path}')
 elif path not in ('bin/verifast','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml') and rows[path]!=m['hosted_profile_hashes'][path]:
  raise SystemExit(f'frozen O26 tool/spec pin differs: {path}')
if os.environ.get('SORT4_R24_SESSION_PHASE_ID') == 'SORT4-ACTUAL-SELECT-2026-10-24-R24':
 expected_translator='8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007' if sys.argv[4]=='1' else 'c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e'
 if rows['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml']!=expected_translator:
  raise SystemExit('R24 checked outcomes translator pin differs')
 path='src/frontend/ocaml_expr_of_ast.ml'
 rows[path]=hashlib.sha256((root/path).read_bytes()).hexdigest()
 if rows[path]!='f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94':
  raise SystemExit('R24 AST serializer pin differs')
out.write_text(json.dumps({'actual':rows,'historical':m['hosted_profile_hashes'],
 'console_byte_identical':rows['bin/verifast']==m['hosted_profile_hashes']['bin/verifast']},indent=2)+'\n')
HASHES
ldd "$source_home/bin/verifast" > "$ev/console-ldd.txt"
! rg -q 'not found' "$ev/console-ldd.txt"

if (( r24_w4_linkage_diagnostic == 1 )); then
  # Keep the frozen capture tool intact. Only this copied tool gains a
  # diagnostic probe which unconditionally refuses before proof admission.
  w4_native_home="$work_root/r24-w4-native-fingerprint-tool"
  w4_native_patch="$proof_root/research/challenge-8/cloud-build/sort4-caller-entry-native/w4-native-fingerprint-r24.patch"
  current_stage=r24-w4-native-copy-identity
  [[ ! -e "$w4_native_home" && ! -L "$w4_native_home" ]] || exit 2
  [[ "$(sha256sum "$w4_native_patch" | cut -d' ' -f1)" == e720c48a5daf9e402ceb0dfddb0b5fcbc9405bedd0f9cf7eff061e5a672dcd90 ]] || exit 2
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007 ]] || exit 2
  stage r24-w4-native-copy cp -a "$source_home" "$w4_native_home"
  stage r24-w4-native-patch-check git -C "$w4_native_home" apply --check "$w4_native_patch"
  stage r24-w4-native-patch-apply git -C "$w4_native_home" apply "$w4_native_patch"
  [[ "$(sha256sum "$w4_native_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 5170c56386f092d55a42251594eb4b080073f58828cbe1dcf44053b5bdc99942 ]] || exit 2
  [[ "$(sha256sum "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" | cut -d' ' -f1)" == 8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007 ]] || exit 2
  stage r24-w4-native-console-build make -C "$w4_native_home/src" ../bin/verifast \
    WITHOUT_LABLGTK=yes VERBOSE=yes
  if (( ${r24_w4_const_qualification:-0} == 1 )); then
    stage r24-w4-const-qualification python3 "$r24_w4_const_helper" run \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "$source_home" --native-tool-home "$w4_native_home" \
      --schema "$w4_native_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
      --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline" --candidate "$current_sha" \
      --capture-mode-file "$r24_w4_mode_file" --mode-file "$r24_w4_const_mode_file"
    current_stage=r24-w4-const-qualification-audit
    audit_result 0 complete
    exit 0
  fi
  stage r24-w4-linkage-diagnostic python3 "$r24_w4_linkage_helper" run \
    --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
    --tool-home "$source_home" --native-tool-home "$w4_native_home" \
    --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
    --deadline-epoch "$deadline" --candidate "$current_sha" \
    --capture-mode-file "$r24_w4_mode_file" --mode-file "$r24_w4_linkage_mode_file"
  current_stage=r24-w4-linkage-diagnostic-audit
  audit_result 0 complete
  exit 0
fi

if (( r24_w4_capture_only == 1 )); then
  stage r24-w4-capture python3 "$r24_w4_helper" run \
    --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
    --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
    --deadline-epoch "$deadline" --candidate "$current_sha" --mode-file "$r24_w4_mode_file"
  current_stage=r24-w4-capture-audit
  audit_result 0 complete
  exit 0
fi

run_const_regression() {
mkdir -p "$ev/cases/candidate"
stage candidate-capture python3 "$proof_root/research/challenge-8/overnight-assume-actual/capture.py" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$ev/cases/candidate/capture" \
  --deadline-epoch "$deadline" --fingerprint
stage candidate-source-compare python3 "$cloud_dir/o26-refresh-recipe.py" compare \
  --evidence "$ev"
# Baseline reproduction of the recorded blocker; its verifier exit is data.
stage candidate-proof python3 "$cloud_dir/o26-refresh-recipe.py" proof \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline"
# Fresh R23 fingerprint pins bind the unchanged reviewed R22b release ghosts.
stage r21-fractional-proof python3 "$cloud_dir/select-callee-r21-fractional-proof-entry.py" "${positive_ast_args[@]}" "${target_map_args[@]}" \
  --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
  --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --deadline-epoch "$deadline" \
  --pins-json "$proof_root/research/challenge-8/task-history/select-callee-r23/FRACTIONAL-FINGERPRINT-INPUT.json"

}

# Same-tool const matrix first, then exact mutable positive. No publication.
if (( r24_mut_proof_enabled == 1 )); then
  run_const_regression
  stage const-regression-audit python3 "$cloud_dir/select-callee-r21-proof-audit.py" \
    --evidence "$ev" --output "$ev/const-regression-audit.json" \
    --runner-exit 0 --failed-stage complete
  python3 - "$ev/const-regression-audit.json" <<'CONST_REGRESSION'
import json,sys
assert json.load(open(sys.argv[1]))['evidence_complete'] is True
CONST_REGRESSION
  if (( r24_mut_classified_proof_enabled == 1 )); then
    stage r24-mut-classified-proof python3 "$cloud_dir/select-callee-r24-mut-classified-proof.py" run \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
      --deadline-epoch "$deadline" --candidate "$current_sha" \
      --classified-mode-file "$r24_mut_classified_mode_file" \
      --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file" \
      --mode-file "$r24_mut_mode_file" \
      --mode-sha256 5ac2662dc74c166f17c01d11c7b44aa716ead91cc1ab24d6ee5fd6ad405ce624 \
      --matrix-mode-file "$r24_mut_matrix_mode_file" \
      --matrix-mode-sha256 0f8c816ff1e588cd8f2cb066fae862ea17b07103397b5282982cb1c86cc84317
  elif (( r24_mut_matrix_proof_enabled == 1 )); then
    stage r24-mut-matrix-proof python3 "$cloud_dir/select-callee-r24-mut-matrix-proof.py" run \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
      --deadline-epoch "$deadline" --candidate "$current_sha" \
      --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file" \
      --mode-file "$r24_mut_mode_file" \
      --mode-sha256 5ac2662dc74c166f17c01d11c7b44aa716ead91cc1ab24d6ee5fd6ad405ce624 \
      --matrix-mode-file "$r24_mut_matrix_mode_file" \
      --matrix-mode-sha256 0f8c816ff1e588cd8f2cb066fae862ea17b07103397b5282982cb1c86cc84317
  else
  stage r24-mut-proof python3 "$cloud_dir/select-callee-r24-mut-proof-entry.py" run \
    --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
    --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
    --deadline-epoch "$deadline" --candidate "$current_sha" \
    --proof-mode-file "$r24_mut_proof_mode_file" \
    --mode-file "$r24_mut_mode_file" \
    --mode-sha256 5ac2662dc74c166f17c01d11c7b44aa716ead91cc1ab24d6ee5fd6ad405ce624 \
    --matrix-mode-file "$r24_mut_matrix_mode_file" \
    --matrix-mode-sha256 0f8c816ff1e588cd8f2cb066fae862ea17b07103397b5282982cb1c86cc84317
  fi
  if (( r24_mut_classified_proof_enabled == 1 )); then
    stage r24-p2-consequence python3 "$cloud_dir/select-callee-r24-p2-entailment.py" run \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
      --deadline-epoch "$deadline" --candidate "$current_sha" \
      --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file"
  fi
  if (( r24_mut_refusal_enabled == 1 )); then
    stage r24-mut-refusals python3 "$cloud_dir/select-callee-r24-mut-refusal-entry.py" run \
      --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
      --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
      --deadline-epoch "$deadline" --candidate "$current_sha" \
      --refusal-mode-file "$r24_mut_refusal_mode_file" \
      --classified-mode-file "$r24_mut_classified_mode_file" \
      --matrix-proof-mode-file "$r24_mut_matrix_proof_mode_file"
  fi
  current_stage=r24-mut-proof-audit
  audit_result 0 complete
  exit 0
fi

# Full mutable fingerprint exits before every proof callback.
if (( r24_mut_matrix_fingerprint_only == 1 )); then
  stage r24-mut-matrix-fingerprint python3 "$cloud_dir/select-callee-r24-mut-matrix-fingerprint.py" \
    --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
    --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
    --deadline-epoch "$deadline" --mode-file "$r24_mut_mode_file" \
    --mode-sha256 5ac2662dc74c166f17c01d11c7b44aa716ead91cc1ab24d6ee5fd6ad405ce624 \
    --matrix-mode-file "$r24_mut_matrix_mode_file" \
    --matrix-mode-sha256 0f8c816ff1e588cd8f2cb066fae862ea17b07103397b5282982cb1c86cc84317
  current_stage=r24-mut-matrix-fingerprint-audit
  audit_result 0 complete
  exit 0
fi

# Capture-only exits before every const proof and matrix callback.
if (( r24_mut_capture_only == 1 )); then
  stage r24-mut-source-capture python3 "$cloud_dir/select-callee-r24-mut-capture.py" \
    --repo "$proof_root" --cloud-dir "$cloud_dir" --evidence "$ev" \
    --tool-home "$source_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
    --deadline-epoch "$deadline" --mode-file "$r24_mut_mode_file" \
    --mode-sha256 5ac2662dc74c166f17c01d11c7b44aa716ead91cc1ab24d6ee5fd6ad405ce624
  current_stage=r24-mut-capture-audit
  audit_result 0 complete
  exit 0
fi

run_const_regression

current_stage=audit
audit_result 0 complete
