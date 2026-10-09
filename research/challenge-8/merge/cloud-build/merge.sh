#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Cloud Build entrypoint for the retained OVERNIGHT-MERGE-26.10 matrix.
set -euo pipefail
lane_started=$SECONDS
lane_work_budget_seconds=1600

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

selection_file="$proof_root/research/challenge-8/merge/cloud-build/selection.json"
selection_tool="$proof_root/research/challenge-8/merge/cloud-build/selection.py"
audit_tool="$proof_root/research/challenge-8/merge/cloud-build/merge-audit.py"
selection_resolved="$evidence_root/selection-resolved.json"
CURRENT_STAGE=group-selection-validation
python3 "$selection_tool" validate --selection "$selection_file" \
  --output "$selection_resolved"
selection_sha=$(python3 - "$selection_resolved" <<'SELECTION'
import json,pathlib,sys
print(json.loads(pathlib.Path(sys.argv[1]).read_text())["selection_sha256"])
SELECTION
)
group_not_run_template="$evidence_root/group-not-run-template.txt"
python3 - "$selection_resolved" "$group_not_run_template" <<'NOTRUN'
import json,pathlib,sys
selection=json.loads(pathlib.Path(sys.argv[1]).read_text())
pathlib.Path(sys.argv[2]).write_text("".join(f"{name} NOT_RUN\n" for name in selection["not_run_groups"]))
NOTRUN

drop_groups_selected=0
for candidate in actual-copy-on-drop-resource-diagnostic actual-copy-on-drop-stock-diagnostic; do
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$candidate"; then
    drop_groups_selected=$((drop_groups_selected + 1))
  else
    selection_status=$?
    if [[ "$selection_status" -ne 1 ]]; then
      printf 'drop selection validation failed for %s\n' "$candidate" >&2
      exit 2
    fi
  fi
done

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

# The adapter changes provider guards/identity, retains modular diagnostics,
# and enforces the committed group selection. It records every base and
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
paths = [item.get("path", "") for item in manifest.get("files", [])]
paths.extend([
    "research/challenge-8/merge/cloud-build/callback-destination-frame.py",
    "research/challenge-8/merge/cloud-build/selection.py",
    "research/challenge-8/merge/cloud-build/merge-audit.py",
  "research/challenge-8/merge/overnight/copy-on-drop-prepare.py",
  "research/challenge-8/merge/overnight/copy-on-drop-prove.py",
])
for rel in paths:
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
export MERGE_SELECTION_TOOL="$selection_tool"
export MERGE_SELECTION_FILE="$selection_file"
export MERGE_SELECTION_SHA256="$selection_sha"
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
  printf 'selection_sha256=%s\nselection_file=%s\n' "$selection_sha" "$selection_file"
  printf 'runtime_probe_selected=%s; classification=not-a-VeriFast-theorem-or-caller-counterexample\n' \
    "$(python3 -c 'import json,sys; print(str(json.load(open(sys.argv[1]))["runtime_probe"]).lower())' "$selection_resolved")"
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
matrix_timeout=1300
if (( drop_groups_selected > 0 )); then
  elapsed=$((SECONDS - lane_started))
  matrix_budget=$((lane_work_budget_seconds - elapsed - 300 * drop_groups_selected - 140))
  (( matrix_budget > 0 )) || matrix_budget=1
  matrix_timeout=900
  (( matrix_budget < matrix_timeout )) && matrix_timeout=$matrix_budget
fi
printf 'lane_work_budget_seconds=%s\nselected_drop_groups=%s\nretained_matrix_timeout_seconds=%s\n' \
  "$lane_work_budget_seconds" "$drop_groups_selected" "$matrix_timeout" \
  > "$evidence_root/drop-lane-budget.txt"
timeout --signal=TERM --kill-after=10s "${matrix_timeout}s" \
  bash research/challenge-8/merge/overnight/run.sh merge_geometry || status=$?
printf '%s\n' "$status" > "$evidence_root/matrix-exit.txt"
[[ ! -e "$allprooflogs/group-not-run.txt" ]] || {
  printf 'runner unexpectedly created group-not-run.txt\n' >&2
  status=1
}
mv "$group_not_run_template" "$allprooflogs/group-not-run.txt"

# The direct Drop diagnostic uses the retained stock and six-patch tool homes
# from run.sh, but publishes its own source/contract/stage evidence policy.
run_copy_on_drop_group() {
  local group=$1 profile=$2 tool_home=$3 profile_evidence=$4
  local selected_status=0 driver_status=0 evidence_dir compiler_sysroot schema
  local elapsed remaining group_timeout groups_left
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$group"; then
    :
  else
    selected_status=$?
    if [[ "$selected_status" -eq 1 ]]; then return 0; fi
    status=1
    return 0
  fi
  groups_left=$drop_groups_selected
  drop_groups_selected=$((drop_groups_selected - 1))
  elapsed=$((SECONDS - lane_started))
  remaining=$((lane_work_budget_seconds - elapsed - 140))
  group_timeout=0
  if (( remaining > 0 && groups_left > 0 )); then
    group_timeout=$((remaining / groups_left))
    (( group_timeout > 300 )) && group_timeout=300
  fi
  CURRENT_STAGE=$group
  evidence_dir="$allprooflogs/cases/$group"
  [[ ! -e "$evidence_dir" ]] || {
    printf 'refusing to reuse Drop evidence path: %s\n' "$evidence_dir" >&2
    driver_status=2
  }
  schema="$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp"
  compiler_sysroot=$(rustc --print sysroot)
  if (( driver_status == 0 && group_timeout > 0 )); then
    /usr/bin/time -v -o "$allprooflogs/group-$group-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${group_timeout}s" python3 \
      "$proof_root/research/challenge-8/merge/overnight/copy-on-drop-prove.py" \
      --profile "$profile" --profile-evidence "$profile_evidence" \
      --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" \
      --schema "$schema" --stage-seconds 30 --verifier-seconds 45 \
      --evidence "$evidence_dir" \
      > "$allprooflogs/group-$group.log" 2>&1 || driver_status=$?
  else
    if (( group_timeout == 0 )); then
      driver_status=124
      printf 'Drop diagnostic not run because the lane work budget was exhausted.\n' \
        > "$allprooflogs/group-$group.log"
      printf 'stage not run; lane budget exhausted\n' \
        > "$allprooflogs/group-$group-resources.txt"
    else
      printf 'Drop diagnostic not run because its evidence path already exists.\n' \
      > "$allprooflogs/group-$group.log"
      printf 'stage not run\n' > "$allprooflogs/group-$group-resources.txt"
    fi
  fi
  printf 'group_%s_timeout_seconds=%s\n' "$group" "$group_timeout" \
    >> "$evidence_root/drop-lane-budget.txt"
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}

run_copy_on_drop_group actual-copy-on-drop-resource-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" "$allprooflogs/build"
run_copy_on_drop_group actual-copy-on-drop-stock-diagnostic \
  stock-26.10 "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" "$allprooflogs"

# The independent saved runtime observation runs only when explicitly selected.
probe_driver_status=NOT_RUN
if python3 "$selection_tool" contains --selection "$selection_file" \
    --sha256 "$selection_sha" callback-destination-frame-probe; then
  CURRENT_STAGE=callback-destination-frame-runtime-probe
  probe_driver_status=0
  mkdir -p "$evidence_root/allprooflogs"
  timeout --signal=TERM --kill-after=10s 150s python3 \
    research/challenge-8/merge/cloud-build/callback-destination-frame.py \
    --proof-root "$proof_root" --evidence-root "$evidence_root" --work-root "$work_root" \
    > "$evidence_root/allprooflogs/callback-destination-frame-driver.log" 2>&1 || probe_driver_status=$?
  printf '%s\n' "$probe_driver_status" \
    > "$evidence_root/allprooflogs/callback-destination-frame-driver-exit-code.txt"
fi

# Relocate verifier case directories into the packager's required cases subtree;
# keep stage logs and process records outside it.
case_root="$evidence_root/allprooflogs/cases"
mkdir -p "$case_root"
for checked in "$evidence_root"/allprooflogs/checked-*; do
  [[ -d "$checked" ]] || continue
  target="$case_root/${checked##*/}"
  [[ ! -e "$target" ]] || {
    printf 'refusing duplicate case evidence path: %s\n' "$target" >&2
    status=1
    break
  }
  mv "$checked" "$target"
done

CURRENT_STAGE=selection-audit
set +e
python3 "$audit_tool" "$evidence_root" "$selection_file" \
  "$status" "$PROOF_SHA" "$CLOUD_BUILD_ID"
audit_status=$?
set -e
if (( audit_status != 0 )); then
  status=1
fi
printf '%s\n' "$status" > "$evidence_root/run-exit.txt"
CURRENT_STAGE=complete
exit "$status"
