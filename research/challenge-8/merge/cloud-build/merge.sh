#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Cloud Build entrypoint for the retained OVERNIGHT-MERGE-26.10 matrix.
set -euo pipefail

proof_root=${PROOF_ROOT:-/workspace/proof}
infra_root=${INFRA_ROOT:-/workspace/infra}
cloud_dir=${INFRA_CLOUD_DIR:-$infra_root/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/merge-work}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
overlay_tool=${MERGE_OVERLAY_TOOL:-$proof_root/research/challenge-8/merge/cloud-build/provider-overlays.py}

for path in "$proof_root" "$infra_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || {
    printf 'path outside /workspace: %s\n' "$path" >&2
    exit 2
  }
done
mkdir -p "$evidence_root"
CURRENT_STAGE=provider-identity
write_incomplete_audit() {
  local status=$?
  if (( status != 0 )) && [[ ! -f "$evidence_root/proof-audit.json" ]]; then
    python3 - "$evidence_root/proof-audit.json" "$status" "$CURRENT_STAGE" <<'FAILURE' || true
import json, pathlib, sys
path, status, stage = sys.argv[1:]
pathlib.Path(path).write_text(json.dumps({
    "schema": "smallsort-merge-cloud-diagnostic-v1",
    "lane": "merge", "accepted": False,
    "diagnostic_complete": False, "classification": "INCONCLUSIVE",
    "exit_status": int(status), "failed_stage": stage,
    "note": "setup/preflight failed before complete matrix collection",
}, sort_keys=True, indent=2) + "\n")
FAILURE
  fi
  return "$status"
}
trap write_incomplete_audit EXIT

[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || {
  printf 'explicit Cloud Build provider identity required\n' >&2
  exit 2
}
[[ -f "$cloud_dir/provider.py" && -f "$overlay_tool" ]] || {
  printf 'merge lane provider or overlay is missing\n' >&2
  exit 2
}

provider_json=$(python3 "$cloud_dir/provider.py")
CURRENT_STAGE=source-input-certificate
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "${PROOF_SHA:?PROOF_SHA is required}" ]] || {
  printf 'proof checkout HEAD differs from the explicit proof SHA\n' >&2
  exit 2
}
python3 - "$proof_root" "$infra_root" "$evidence_root/source-input-certificate.json" \
  "$PROOF_SHA" "$INFRA_SHA" <<'INPUTS'
import hashlib, json, pathlib, subprocess, sys
proof, infra, certificate = map(pathlib.Path, sys.argv[1:4])
proof_sha, infra_sha = sys.argv[4:]
record = json.loads(certificate.read_text())
if (record.get("lane") != "merge" or
    record.get("proof", {}).get("commit") != proof_sha or
    record.get("proof", {}).get("head") != proof_sha or
    record.get("infra", {}).get("commit") != infra_sha or
    record.get("infra", {}).get("head") != infra_sha):
    raise SystemExit("pinned source certificate does not match the merge lane SHAs")
recipe = record.get("recipe", {})
restored = record.get("proof", {}).get("restored_paths", [])
if [x.get("path") for x in restored] != recipe.get("proof_paths"):
    raise SystemExit("restored proof paths differ from the committed merge recipe")
for item in restored:
    path = proof / item["path"]
    if path.is_symlink() or not path.is_file():
        raise SystemExit("restored proof input is missing or a symlink: " + item["path"])
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != item.get("sha256"):
        raise SystemExit("restored proof input changed after source restore: " + item["path"])
    expected_mode = 0o755 if item.get("mode") == "100755" else 0o644
    if path.stat().st_mode & 0o777 != expected_mode:
        raise SystemExit("restored proof input mode changed: " + item["path"])
if subprocess.check_output(["git", "-C", str(proof), "rev-parse", "HEAD"], text=True).strip() != proof_sha:
    raise SystemExit("proof HEAD changed after source restore")
INPUTS

expected_source_sha=85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1
printf '%s  %s\n' "$expected_source_sha" \
  "$proof_root/library/core/src/slice/sort/shared/smallsort.rs" | sha256sum -c -

allprooflogs="$evidence_root/allprooflogs"
[[ ! -e "$allprooflogs" ]] || {
  printf 'refusing to reuse merge evidence: %s\n' "$allprooflogs" >&2
  exit 2
}
mkdir -p "$work_root" "$evidence_root" "$proof_root/research/challenge-8/cloud-build"
cp "$cloud_dir/provider.py" "$proof_root/research/challenge-8/cloud-build/provider.py"

# The adapter changes provider guards/identity and selects the saved modular
# diagnostic groups with a bounded suite time cap. It records every base and
# overlay hash plus the exact operational/guard diff before the runner starts.
CURRENT_STAGE=provider-overlay
python3 "$overlay_tool" --proof-root "$proof_root" \
  --evidence "$evidence_root/provider-overlay"

CURRENT_STAGE=cloud-static-preflight
{
  python3 - "$proof_root" "$evidence_root/provider-overlay/provider-overlay-manifest.json" <<'STATIC'
import ast, json, pathlib, sys
proof = pathlib.Path(sys.argv[1])
manifest = json.loads(pathlib.Path(sys.argv[2]).read_text())
for item in manifest.get("files", []):
    rel = item.get("path", "")
    if not rel.endswith(".py"):
        continue
    source = proof / rel
    ast.parse(source.read_bytes(), filename=rel)
    print("AST OK", rel)
STATIC
  bash -n "$proof_root/research/challenge-8/merge/overnight/run.sh"
  bash -n "$proof_root/research/challenge-8/merge/overnight/build.sh"
  printf 'bash -n OK run.sh and build.sh\n'
} > "$evidence_root/cloud-static-preflight.log" 2>&1

export PROOF_ROOT="$proof_root" INFRA_ROOT="$infra_root" INFRA_CLOUD_DIR="$cloud_dir"
export CLOUD_BUILD_ID=${CLOUD_BUILD_ID:?CLOUD_BUILD_ID is required}
export CLOUD_BUILD_PROJECT_ID=${CLOUD_BUILD_PROJECT_ID:?CLOUD_BUILD_PROJECT_ID is required}
export CLOUD_BUILD_REGION=${CLOUD_BUILD_REGION:?CLOUD_BUILD_REGION is required}
export PROOF_SHA
export SMALLSORT_PROVIDER_FILE="$proof_root/research/challenge-8/cloud-build/provider.py"
export EVIDENCE_ROOT="$evidence_root"
export RUNNER_TEMP="$work_root/runner-temp"
mkdir -p "$RUNNER_TEMP"

export DEBIAN_FRONTEND=noninteractive
CURRENT_STAGE=apt-prerequisites
timeout --signal=TERM --kill-after=10s 120s apt-get update
timeout --signal=TERM --kill-after=10s 180s apt-get install --yes --no-install-recommends sudo build-essential m4 patch unzip capnproto time \
  libgmp10 libmpfr6 libgomp1 libffi8 libncurses6 libtinfo6 zlib1g libz3-4 libgtk-3-0 libgtksourceview-4-0
CURRENT_STAGE=rustup-init-download
rustup_init="$work_root/rustup-init-1.28.2"
timeout --signal=TERM --kill-after=5s 100s curl --fail --silent --show-error --location --retry 2 --max-time 90 \
  https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init \
  --output "$rustup_init"
printf '%s  %s\n' 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c \
  "$rustup_init" | sha256sum -c -
chmod +x "$rustup_init"
export RUSTUP_HOME="$work_root/rustup" CARGO_HOME="$work_root/cargo"
export PATH="$CARGO_HOME/bin:$PATH"
timeout --signal=TERM --kill-after=10s 120s "$rustup_init" -y --no-modify-path --default-toolchain none --profile minimal
CURRENT_STAGE=pinned-rust-toolchain
timeout --signal=TERM --kill-after=10s 240s rustup toolchain install nightly-2026-09-25 --profile minimal --component rustc-dev --component rust-src
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
rustc --version --verbose > "$evidence_root/rustc-version.txt"
python3 - "$evidence_root/rustc-version.txt" <<'RUSTPIN'
import pathlib, sys
rows = dict(line.split(": ", 1) for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if ": " in line)
if rows.get("commit-hash") != "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f":
    raise SystemExit("nightly compiler commit differs from frozen pin")
if rows.get("host") != "x86_64-unknown-linux-gnu":
    raise SystemExit("nightly compiler host differs from frozen pin")
RUSTPIN

{
  printf 'provider=%s\n' "$provider_json"
  printf 'lane=overnight-merge-26.10\nproof_sha=%s\n' "$PROOF_SHA"
  printf 'source_sha256=%s\n' "$expected_source_sha"
  printf 'build_id=%s\nproject=%s\nregion=%s\n' \
    "$CLOUD_BUILD_ID" "$CLOUD_BUILD_PROJECT_ID" "$CLOUD_BUILD_REGION"
  printf 'matrix=retained-merge-suite; cloud-migration A-storage/B-stock/C-constructor lanes=NOT_SELECTED; math G2/A/B compatibility groups=INCLUDED\n'
} >> "$evidence_root/environment.txt"

python3 - "$cloud_dir/provider.py" "$evidence_root/environment.txt" <<'PIN'
import hashlib, pathlib, sys
path = pathlib.Path(sys.argv[1])
with pathlib.Path(sys.argv[2]).open('a') as out:
    out.write(f"provider_helper_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}\n")
PIN

# run.sh owns its existing pinned source build and named proof matrix. The
# bounded execution leaves Cloud Build time for evidence packaging and upload.
cd "$proof_root"
status=0
CURRENT_STAGE=retained-merge-matrix
timeout --signal=TERM --kill-after=10s 1550s \
  bash research/challenge-8/merge/overnight/run.sh merge_geometry || status=$?
printf '%s\n' "$status" > "$evidence_root/run-exit.txt"

python3 - "$evidence_root" "$status" "$PROOF_SHA" "$CLOUD_BUILD_ID" <<'AUDIT'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
status = int(sys.argv[2])
cases = root / "allprooflogs" / "cases"
cases.mkdir(parents=True, exist_ok=True)
# The retained runner puts each verifier aggregate beside its group logs. The
# Cloud evidence contract stores case aggregates below cases/ while preserving
# group and build logs/resources at the allprooflogs root for collection.
for path in sorted((root / "allprooflogs").glob("checked-*")):
    if path.is_dir():
        path.rename(cases / path.name)
expected_groups = {
    "rust-profile-smoke", "G2-compatibility", "A-compatibility", "B-compatibility",
    "native-baselines", "rust-unwind-baselines", "callback-model-diagnostics",
    "tuple2-shape-admission", "tuple2-resource-diagnostics", "callback-borrow-diagnostic",
    "prepared-hrtb-diagnostics", "hrtb-admission-certificate", "callback-cleanup-diagnostics",
    "copy-model-diagnostics", "wrapping-acceptance", "pointer-bridge-diagnostic",
    "pointer-domain-bridge", "owned-array-resource-diagnostic", "scratch-option-resource-diagnostic",
    "concrete-zst-diagnostic", "experimental-rust-regression", "tuple-layout-entry-diagnostics",
    "trace-entry-tuple-diagnostics", "usize-source-admission", "usize-primitive-diagnostics",
    "stack-address-admission-diagnostics", "stack-address-role-control-preparation",
    "stack-address-role-controls", "pointer-quartet-trace-entry-negative",
    "pointer-quartet-trace-diagnostic", "actual-source-preparation", "actual-callee-applicability",
    "bidirectional-option-stages", "bidirectional-small-source-preparation",
    "bidirectional-len23-diagnostic", "pointer-modular-trace-entry-negative",
    "pointer-modular-trace-diagnostic",
}
evidence = root / "allprooflogs"
group_status = evidence / "group-status.txt"
observed = {}
if group_status.is_file():
    for line in group_status.read_text(errors="replace").splitlines():
        parts = line.split()
        if len(parts) == 2:
            observed[parts[0]] = parts[1]
groups_complete = set(observed) == expected_groups and all(v == "0" for v in observed.values())

def raw_cases(path):
    try:
        value = json.loads((cases / path / "aggregate.json").read_text())
        return value.get("cases", {}) if isinstance(value, dict) else {"_aggregate": "MALFORMED"}
    except (OSError, ValueError):
        return {"_aggregate": "NOT_REPORTED"}

quartet_cases = raw_cases("checked-pointer-trace-quartets")
actual_merge_cases = raw_cases("checked-actual")
bidirectional_cases = raw_cases("checked-bidirectional-small")
modular_entry_cases = raw_cases("checked-pointer-modular-trace-entry-negative")
modular_trace_cases = raw_cases("checked-pointer-modular-trace")
panic_candidates = []
for path in cases.glob("**/panic-macro-origin.json"):
    try:
        certificate = json.loads(path.read_text())
    except (OSError, ValueError):
        continue
    if (certificate.get("status") == "PANIC_MACRO_BODY_ORIGIN_LINKED" and
        certificate.get("require_final") is True and
        certificate.get("expected_compiler_panic_rs_sha256") ==
            "b63eeb2d8e1fa130d3582253fd043fdcd722d16031b289c25f2437e2edda87dd" and
        certificate.get("compiler_panic_rs_sha256") ==
            "b63eeb2d8e1fa130d3582253fd043fdcd722d16031b289c25f2437e2edda87dd"):
        panic_candidates.append(str(path.relative_to(root)))
mandatory_artifacts = (
    (cases / "checked-pointer-trace-quartets/aggregate.json").is_file() and
    (cases / "checked-actual/aggregate.json").is_file() and
    (cases / "checked-bidirectional-small/aggregate.json").is_file() and
    (cases / "checked-pointer-modular-trace-entry-negative/aggregate.json").is_file() and
    (cases / "checked-pointer-modular-trace/aggregate.json").is_file() and
    (cases / "checked-stack-role-controls/aggregate.json").is_file() and
    bool(panic_candidates)
)
diagnostic_complete = status == 0 and groups_complete and mandatory_artifacts
audit = {
    "schema": "smallsort-merge-cloud-diagnostic-v1",
    "lane": "merge",
    "proof_sha": sys.argv[3],
    "execution_provider": "cloud-build",
    "execution_id": sys.argv[4],
    "accepted": False,
    "diagnostic_complete": diagnostic_complete,
    "classification": "MERGE_DIAGNOSTIC_MATRIX_COMPLETE" if diagnostic_complete else "INCONCLUSIVE",
    "theorem_statuses": {
        "whole_small_sort_challenge": "NOT_PROVEN",
        "g2_quartet_trace_cases": quartet_cases,
        "g2_modular_entry_control_cases": modular_entry_cases,
        "g2_modular_trace_cases": modular_trace_cases,
        "actual_bidirectional_len2_len3_cases": bidirectional_cases,
        "actual_merge_up_down_cases": actual_merge_cases,
    },
    "mandatory_group_statuses": observed,
    "mandatory_groups_complete": groups_complete,
    "mandatory_artifacts_complete": mandatory_artifacts,
    "final_panic_origin_certificates": panic_candidates,
    "raw_group_status_path": "allprooflogs/group-status.txt",
    "note": "Matrix collection status does not change per-case classifications or establish a whole-function theorem.",
}
(root / "proof-audit.json").write_text(json.dumps(audit, sort_keys=True, indent=2) + "\n")
AUDIT
CURRENT_STAGE=complete
exit "$status"
