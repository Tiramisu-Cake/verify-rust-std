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
# The shared dispatcher supplies the absolute execution cutoff, including its
# upload reserve. Short late-window Builds must not inherit a1600-second lane.
[[ "${SMALLSORT_DEADLINE_EPOCH:-}" =~ ^[0-9]+$ ]] || {
  printf 'shared execution deadline is missing\n' >&2
  exit 2
}
lane_available=$((SMALLSORT_DEADLINE_EPOCH - $(date +%s)))
(( lane_available > 140 )) || {
  printf 'shared execution deadline leaves no lane/evidence budget\n' >&2
  exit 2
}
(( lane_available >= lane_work_budget_seconds )) || lane_work_budget_seconds=$lane_available
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
guard_construction_groups_selected=0
for candidate in guard-construction-fragment-diagnostic guard-construction-fragment-stock-diagnostic; do
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$candidate"; then
    guard_construction_groups_selected=$((guard_construction_groups_selected + 1))
  else
    selection_status=$?
    if [[ "$selection_status" -ne 1 ]]; then
      printf 'guard construction selection validation failed for %s\n' "$candidate" >&2
      exit 2
    fi
  fi
done
guard_construction_v3_groups_selected=0
for candidate in guard-construction-nonprecise-v3-diagnostic guard-construction-nonprecise-v3-stock-diagnostic guard-construction-fbc-v4-diagnostic guard-construction-fbc-v4-stock-diagnostic; do
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$candidate"; then
    guard_construction_v3_groups_selected=$((guard_construction_v3_groups_selected + 1))
  else
    selection_status=$?
    if [[ "$selection_status" -ne 1 ]]; then
      printf 'V3 guard construction selection validation failed for %s\n' "$candidate" >&2
      exit 2
    fi
  fi
done
guard_geometry_groups_selected=0
for candidate in guard-drop-geometry-v3-diagnostic guard-drop-geometry-v3-stock-diagnostic; do
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$candidate"; then
    guard_geometry_groups_selected=$((guard_geometry_groups_selected + 1))
  else
    selection_status=$?
    if [[ "$selection_status" -ne 1 ]]; then
      printf 'guard geometry selection validation failed for %s\n' "$candidate" >&2
      exit 2
    fi
  fi
done
onecell_selected=0
if python3 "$selection_tool" contains --selection "$selection_file" \
    --sha256 "$selection_sha" insertion-onecell-guard-diagnostic; then
  onecell_selected=1
else
  selected_status=$?
  if [[ "$selected_status" -ne 1 ]]; then
    printf 'one-cell selection validation failed\n' >&2
    exit 2
  fi
fi
or_join_selected=0
if python3 "$selection_tool" contains --selection "$selection_file" \
    --sha256 "$selection_sha" mir-or-join-seven-diagnostic; then
  or_join_selected=1
else
  selection_status=$?
  if [[ "$selection_status" -ne 1 ]]; then
    printf 'MIR-OR-JOIN selection validation failed\n' >&2
    exit 2
  fi
fi

or_join_reserve=900
if (( or_join_selected > 0 )); then
  or_join_trial_mode=$(python3 - "$proof_root/research/challenge-8/merge/overnight/or-join-liveness/PINNED-INPUTS.json" <<'ORMODE'
import json,pathlib,sys
mode=json.loads(pathlib.Path(sys.argv[1]).read_text()).get("trial_mode","FULL_TARGET")
if mode not in {"FULL_TARGET","SHAPE_CONTROLS_ONLY"}:
    raise SystemExit("unknown OR trial mode")
print(mode)
ORMODE
)
  [[ "$or_join_trial_mode" != SHAPE_CONTROLS_ONLY ]] || or_join_reserve=450
fi

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
  "research/challenge-8/merge/overnight/or-join-liveness/preflight-source.py",
  "research/challenge-8/merge/overnight/or-join-liveness/admit-source.py",
  "research/challenge-8/merge/overnight/or-join-liveness/audit-seven.py",
  "research/challenge-8/merge/overnight/or-join-liveness/control-driver.py",
  "research/challenge-8/merge/overnight/or-join-liveness/control-exporter.py",
  "research/challenge-8/merge/overnight/guard-ownership/construction/prepare.py",
  "research/challenge-8/merge/overnight/guard-ownership/construction/prove.py",
  "research/challenge-8/merge/overnight/guard-ownership/construction/nonprecise-v3/prepare.py",
  "research/challenge-8/merge/overnight/guard-ownership/construction/fbc-v4/prepare.py",
  "research/challenge-8/merge/overnight/guard-ownership/drop-geometry/prepare.py",
  "research/challenge-8/merge/overnight/guard-ownership/drop-geometry/prove.py",
  "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prepare.py",
  "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py",
  "research/challenge-8/merge/cloud-build/guard-geometry-audit.py",
])
for rel in paths:
    if not rel.endswith(".py"):
        continue
    source = proof / rel
    ast.parse(source.read_bytes(), filename=rel)
    print("AST OK", rel)
STATIC
  python3 - "$proof_root/research/challenge-8/merge/overnight/or-join-liveness/PINNED-INPUTS.json" <<'ORJOINJSON'
import json, pathlib, sys
manifest=json.loads(pathlib.Path(sys.argv[1]).read_text())
if manifest.get("component") != "MIR-OR-JOIN-LIVENESS":
    raise SystemExit("MIR-OR-JOIN manifest component identity mismatch")
print("JSON OK MIR-OR-JOIN manifest; admission state remains enforced by pinned component scripts")
ORJOINJSON
  bash -n "$proof_root/research/challenge-8/merge/overnight/run.sh"
  bash -n "$proof_root/research/challenge-8/merge/overnight/build.sh"
  bash -n "$proof_root/research/challenge-8/merge/overnight/or-join-liveness/run-seven.sh"
  bash -n "$proof_root/research/challenge-8/merge/overnight/or-join-liveness/build-seven.sh"
  bash -n "$proof_root/research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/build-profile.sh"
  printf 'bash -n OK retained and MIR-OR-JOIN build/run scripts\n'
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
  matrix_reserve=$((300 * drop_groups_selected + 140))
  matrix_reserve=$((matrix_reserve + 180 * guard_construction_groups_selected))
  matrix_reserve=$((matrix_reserve + 180 * guard_construction_v3_groups_selected + 240 * guard_geometry_groups_selected + 450 * onecell_selected))
  (( or_join_selected == 0 )) || matrix_reserve=$((matrix_reserve + or_join_reserve))
  matrix_budget=$((lane_work_budget_seconds - elapsed - matrix_reserve))
  (( matrix_budget > 0 )) || matrix_budget=1
  matrix_timeout=900
  (( matrix_budget < matrix_timeout )) && matrix_timeout=$matrix_budget
elif (( or_join_selected > 0 )); then
  elapsed=$((SECONDS - lane_started))
  matrix_budget=$((lane_work_budget_seconds - elapsed - or_join_reserve - 140))
  matrix_budget=$((matrix_budget - 180 * guard_construction_groups_selected))
  matrix_budget=$((matrix_budget - 180 * guard_construction_v3_groups_selected - 240 * guard_geometry_groups_selected - 450 * onecell_selected))
  (( matrix_budget > 0 )) || matrix_budget=1
  matrix_timeout=650
  (( matrix_budget < matrix_timeout )) && matrix_timeout=$matrix_budget
fi
if (( drop_groups_selected == 0 && or_join_selected == 0 && (guard_construction_groups_selected > 0 || guard_construction_v3_groups_selected > 0 || guard_geometry_groups_selected > 0 || onecell_selected > 0) )); then
  elapsed=$((SECONDS - lane_started))
  matrix_budget=$((lane_work_budget_seconds - elapsed - 140 - 180 * guard_construction_groups_selected - 180 * guard_construction_v3_groups_selected - 240 * guard_geometry_groups_selected - 450 * onecell_selected))
  (( matrix_budget > 0 )) || matrix_budget=1
  matrix_timeout=900
  (( matrix_budget < matrix_timeout )) && matrix_timeout=$matrix_budget
fi
matrix_remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
(( matrix_remaining > 0 )) || matrix_remaining=1
(( matrix_remaining >= matrix_timeout )) || matrix_timeout=$matrix_remaining

printf 'lane_work_budget_seconds=%s\nselected_drop_groups=%s\nor_join_selected=%s\nretained_matrix_timeout_seconds=%s\n' \
  "$lane_work_budget_seconds" "$drop_groups_selected" "$or_join_selected" "$matrix_timeout" \
  > "$evidence_root/lane-work-budget.txt"
timeout --signal=TERM --kill-after=10s "${matrix_timeout}s" \
  bash research/challenge-8/merge/overnight/run.sh merge_geometry || status=$?
printf '%s\n' "$status" > "$evidence_root/matrix-exit.txt"
[[ ! -e "$allprooflogs/group-not-run.txt" ]] || {
  printf 'runner unexpectedly created group-not-run.txt\n' >&2
  status=1
}
mv "$group_not_run_template" "$allprooflogs/group-not-run.txt"

# Reuse the retained read_cases admission to publish a literal-source pin for
# later Cloud trials. This records provenance only; it adds no verifier proof
# or caller-bridge claim.
CURRENT_STAGE=bounded-source-pin
python3 - "$proof_root" "$allprooflogs" "$evidence_root" \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" \
  "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" <<'SOURCEPIN'
import hashlib, importlib.util, json, pathlib, sys

proof, logs, evidence, experimental_home, stock_home = map(pathlib.Path, sys.argv[1:])
fixture = logs / "bidirectional-small-cases.rs"
admission_path = logs / "bidirectional-small-cases.admission.json"
group_status = logs / "group-status.txt"
target = evidence / "bounded-source-pin"
case_root = target / "cases"
case_name = "bidirectional_merge_len23"
source_path = proof / "library/core/src/slice/sort/shared/smallsort.rs"
harness = proof / "research/challenge-8/merge/overnight/pointer-prove.py"
source_sha = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
base_console_sha = "9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1"
candidate = {
    "schema": "smallsort-bounded-source-pin-v1",
    "accepted": False,
    "classification": "INCONCLUSIVE",
    "admission_state": "INCONCLUSIVE",
    "scope": "literal bounded actual-source candidate provenance only; no proof result or caller bridge",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

try:
    if not fixture.is_file() or not admission_path.is_file() or not group_status.is_file():
        raise RuntimeError("bidirectional source preparation evidence is missing")
    statuses = [line.split() for line in group_status.read_text().splitlines()]
    if [row for row in statuses if len(row) == 2 and row[0] ==
            "bidirectional-small-source-preparation"] != [[
                "bidirectional-small-source-preparation", "0"]]:
        raise RuntimeError("bidirectional source preparation did not complete exactly once with exit 0")
    if sha(source_path) != source_sha:
        raise RuntimeError("actual SmallSort source SHA differs from its frozen pin")
    if sha(stock_home / "bin/verifast") != base_console_sha:
        raise RuntimeError("stock base console differs from its frozen binary pin")
    if not (experimental_home / "bin/verifast").is_file():
        raise RuntimeError("fresh experimental console is missing")

    admission = json.loads(admission_path.read_text())
    bidirectional = admission.get("cases", {}).get("bidirectional_merge", {})
    if (admission.get("source_admission", {}).get("full_source_sha256") != source_sha or
            bidirectional.get("body_present") is not True or
            bidirectional.get("ghost_strip_exact") is not True):
        raise RuntimeError("preparer certificate does not bind the exact actual body")

    spec = importlib.util.spec_from_file_location("retained_pointer_prove", harness)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load retained pointer-prove parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case_root.mkdir(parents=True, exist_ok=False)
    manifest, _ = module.read_cases(fixture, case_root, [case_name])
    case_meta = manifest["cases"][case_name]
    original = case_root / case_name / "original/lib.rs"
    verified = case_root / case_name / "verified/lib.rs"
    actual = source_path.read_bytes()
    verified_bytes = verified.read_bytes()
    signature = b"unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>("
    guard = b"if left != left_end || right != right_end {"
    if actual.count(signature) != 1 or actual.count(guard) != 1:
        raise RuntimeError("actual body signature or panic guard is missing/ambiguous")
    if verified_bytes.count(signature) != 1 or verified_bytes.count(guard) != 1:
        raise RuntimeError("extracted verified signature or panic guard is missing/ambiguous")
    expected_bodies = module.body_names(verified_bytes)
    required_bodies = {
        "merge_up", "merge_down", "panic_on_ord_violation", "bidirectional_merge",
        "bidirectional_small_left_cell_association",
        "bidirectional_small_current_cell_alias",
    }
    if (case_meta.get("ghost_strip_exact_bytes") is not True or
            case_meta.get("expected_bodies") != expected_bodies or
            not required_bodies.issubset(set(expected_bodies)) or
            case_meta.get("original_sha256") != sha(original) or
            case_meta.get("verified_sha256") != sha(verified) or
            bidirectional.get("exact_source_sha256") is None):
        raise RuntimeError("retained parser manifest does not bind both extracted source forms")
    start = actual.index(signature)
    end = actual.index(b"\n}\n", start) + 2
    actual_signature_line = actual[:start].count(b"\n") + 1
    actual_guard_line = actual[:actual.index(guard)].count(b"\n") + 1
    verified_signature_line = verified_bytes[:verified_bytes.index(signature)].count(b"\n") + 1
    verified_guard_line = verified_bytes[:verified_bytes.index(guard)].count(b"\n") + 1
    if (actual_signature_line, actual_guard_line) != (754, 831):
        raise RuntimeError("actual source signature/guard line locations changed")
    if verified_signature_line < 1 or verified_guard_line <= verified_signature_line:
        raise RuntimeError("extracted source signature/guard order is invalid")
    if hashlib.sha256(actual[start:end]).hexdigest() != bidirectional["exact_source_sha256"]:
        raise RuntimeError("preparer exact body hash does not match the pinned source body")
    candidate.update({
        "admission_state": "PINNED_LITERAL_CANDIDATE",
        "classification": "SOURCE_PROVENANCE_ONLY",
        "fixture_sha256": manifest["fixture_sha256"],
        "retained_pointer_prove_sha256": sha(harness),
        "verified_lib_sha256": sha(verified),
        "original_lib_sha256": sha(original),
        "actual_bidirectional_body_sha256": bidirectional["exact_source_sha256"],
        "source_signature": signature.decode(),
        "actual_source_signature_line": actual_signature_line,
        "guard_statement": guard.decode(),
        "actual_source_guard_line": actual_guard_line,
        "verified_signature_line": verified_signature_line,
        "verified_guard_line": verified_guard_line,
        "expected_bodies": expected_bodies,
        "required_bodies": sorted(required_bodies),
        "small_sort_source_sha256": source_sha,
        "base_stock_console_sha256": base_console_sha,
        "fresh_experimental_console_sha256": sha(experimental_home / "bin/verifast"),
        "case": case_name,
        "accepted": False,
    })
except Exception as error:
    candidate["reason"] = str(error)

target.mkdir(parents=True, exist_ok=True)
(evidence / "bounded-source-pin.json").write_text(json.dumps(candidate, sort_keys=True, indent=2) + "\n")
SOURCEPIN

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
    >> "$evidence_root/lane-work-budget.txt"
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}

run_copy_on_drop_group actual-copy-on-drop-resource-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" "$allprooflogs/build"
run_copy_on_drop_group actual-copy-on-drop-stock-diagnostic \
  stock-26.10 "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" "$allprooflogs"

run_guard_construction_group() {
  local group=$1 profile=$2 tool_home=$3 profile_evidence=$4
  local selected_status=0 driver_status=0 remaining group_timeout groups_left evidence_dir
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$group"; then
    :
  else
    selected_status=$?
    if [[ "$selected_status" -eq 1 ]]; then return 0; fi
    status=1
    return 0
  fi
  groups_left=$guard_construction_groups_selected
  guard_construction_groups_selected=$((guard_construction_groups_selected - 1))
  CURRENT_STAGE=$group
  evidence_dir="$allprooflogs/cases/$group"
  remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
  group_timeout=0
  if (( remaining > 0 && groups_left > 0 )); then
    group_timeout=$((remaining / groups_left))
    (( group_timeout > 180 )) && group_timeout=180
  fi
  if [[ -e "$evidence_dir" ]]; then
    printf 'refusing to reuse guard-construction evidence path: %s\n' "$evidence_dir" >&2
    driver_status=2
  elif (( group_timeout > 0 )); then
    /usr/bin/time -v -o "$allprooflogs/group-$group-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${group_timeout}s" python3 \
      "$proof_root/research/challenge-8/merge/overnight/guard-ownership/construction/prove.py" \
      --profile "$profile" --profile-evidence "$profile_evidence" \
      --tool-home "$tool_home" --compiler-sysroot "$(rustc --print sysroot)" \
      --schema "$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp" \
      --stage-seconds 30 --verifier-seconds 35 --evidence "$evidence_dir" \
      > "$allprooflogs/group-$group.log" 2>&1 || driver_status=$?
  else
    driver_status=124
    printf 'NOT_RUN: lane budget exhausted\n' > "$allprooflogs/group-$group.log"
    printf 'NOT_RUN\n' > "$allprooflogs/group-$group-resources.txt"
  fi
  printf 'group_%s_timeout_seconds=%s\n' "$group" "$group_timeout" \
    >> "$evidence_root/lane-work-budget.txt"
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}
run_guard_construction_group guard-construction-fragment-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" "$allprooflogs/build"
run_guard_construction_group guard-construction-fragment-stock-diagnostic \
  stock-26.10 "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" "$allprooflogs"

run_guard_construction_v3_group() {
  local group=$1 profile=$2 tool_home=$3 profile_evidence=$4 variant=${5:-v3}
  local selected_status=0 driver_status=0 remaining group_timeout groups_left evidence_dir
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$group"; then
    :
  else
    selected_status=$?
    if [[ "$selected_status" -eq 1 ]]; then return 0; fi
    status=1
    return 0
  fi
  groups_left=$guard_construction_v3_groups_selected
  guard_construction_v3_groups_selected=$((guard_construction_v3_groups_selected - 1))
  CURRENT_STAGE=$group
  evidence_dir="$allprooflogs/cases/$group"
  remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
  group_timeout=0
  if (( remaining > 0 && groups_left > 0 )); then
    group_timeout=$((remaining / groups_left))
    if (( onecell_selected > 0 )); then
      (( group_timeout > 120 )) && group_timeout=120
    else
      (( group_timeout > 180 )) && group_timeout=180
    fi
  fi
  if [[ -e "$evidence_dir" ]]; then
    printf 'refusing to reuse V3 guard-construction evidence path: %s\n' "$evidence_dir" >&2
    driver_status=2
  elif (( group_timeout > 0 )); then
    /usr/bin/time -v -o "$allprooflogs/group-$group-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${group_timeout}s" python3 \
      "$proof_root/research/challenge-8/merge/overnight/guard-ownership/construction/prove.py" \
      --variant "$variant" --profile "$profile" --profile-evidence "$profile_evidence" \
      --tool-home "$tool_home" --compiler-sysroot "$(rustc --print sysroot)" \
      --schema "$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp" \
      --stage-seconds 30 --verifier-seconds 35 --evidence "$evidence_dir" \
      > "$allprooflogs/group-$group.log" 2>&1 || driver_status=$?
  else
    driver_status=124
    printf 'NOT_RUN: lane budget exhausted\n' > "$allprooflogs/group-$group.log"
    printf 'NOT_RUN\n' > "$allprooflogs/group-$group-resources.txt"
  fi
  printf 'group_%s_timeout_seconds=%s\n' "$group" "$group_timeout" \
    >> "$evidence_root/lane-work-budget.txt"
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}
run_guard_construction_v3_group guard-construction-nonprecise-v3-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" "$allprooflogs/build"
run_guard_construction_v3_group guard-construction-nonprecise-v3-stock-diagnostic \
  stock-26.10 "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" "$allprooflogs"

run_guard_construction_v3_group guard-construction-fbc-v4-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" "$allprooflogs/build" v4
run_guard_construction_v3_group guard-construction-fbc-v4-stock-diagnostic \
  stock-26.10 "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" "$allprooflogs" v4

run_guard_geometry_group() {
  local group=$1 profile=$2 tool_home=$3 profile_evidence=$4
  local selected_status=0 driver_status=0 remaining group_timeout groups_left evidence_dir
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$group"; then
    :
  else
    selected_status=$?
    if [[ "$selected_status" -eq 1 ]]; then return 0; fi
    status=1
    return 0
  fi
  groups_left=$guard_geometry_groups_selected
  guard_geometry_groups_selected=$((guard_geometry_groups_selected - 1))
  CURRENT_STAGE=$group
  evidence_dir="$allprooflogs/cases/$group"
  remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
  group_timeout=0
  if (( remaining > 0 && groups_left > 0 )); then
    group_timeout=$((remaining / groups_left))
    (( group_timeout > 240 )) && group_timeout=240
  fi
  if [[ -e "$evidence_dir" ]]; then
    printf 'refusing to reuse guard geometry evidence path: %s\n' "$evidence_dir" >&2
    driver_status=2
  elif (( group_timeout > 0 )); then
    /usr/bin/time -v -o "$allprooflogs/group-$group-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${group_timeout}s" python3 \
      "$proof_root/research/challenge-8/merge/overnight/guard-ownership/drop-geometry/prove.py" \
      --profile "$profile" --profile-evidence "$profile_evidence" \
      --tool-home "$tool_home" --compiler-sysroot "$(rustc --print sysroot)" \
      --schema "$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp" \
      --stage-seconds 30 --verifier-seconds 35 --evidence "$evidence_dir" \
      > "$allprooflogs/group-$group.log" 2>&1 || driver_status=$?
  else
    driver_status=124
    printf 'NOT_RUN: lane budget exhausted\n' > "$allprooflogs/group-$group.log"
    printf 'NOT_RUN\n' > "$allprooflogs/group-$group-resources.txt"
  fi
  printf 'group_%s_timeout_seconds=%s\n' "$group" "$group_timeout" \
    >> "$evidence_root/lane-work-budget.txt"
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}
run_guard_geometry_group guard-drop-geometry-v3-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" "$allprooflogs/build"
run_guard_geometry_group guard-drop-geometry-v3-stock-diagnostic \
  stock-26.10 "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" "$allprooflogs"

# One opt-in translator rebase and quiescent source-linked one-cell fragment.
# All retained selected constructor controls above execute before this group.
onecell_group=insertion-onecell-guard-diagnostic
if python3 "$selection_tool" contains --selection "$selection_file" \
    --sha256 "$selection_sha" "$onecell_group"; then
  CURRENT_STAGE=$onecell_group
  onecell_component="$proof_root/research/challenge-8/merge/overnight/guard-ownership/insertion-onecell"
  onecell_home="$RUNNER_TEMP/challenge8-merge-overnight/verifast-tracked-md-source"
  onecell_build="$allprooflogs/tracked-md-build"
  onecell_case="$allprooflogs/cases/$onecell_group"
  onecell_status=0
  onecell_remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
  onecell_build_timeout=$onecell_remaining
  (( onecell_build_timeout <= 300 )) || onecell_build_timeout=300
  if (( onecell_build_timeout > 0 )); then
    /usr/bin/time -v -o "$allprooflogs/group-$onecell_group-build-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${onecell_build_timeout}s" \
      bash "$onecell_component/build-profile.sh" \
        "$RUNNER_TEMP/challenge8-merge-overnight/source" "$onecell_home" \
        "$onecell_build" "$allprooflogs/build" \
      > "$allprooflogs/group-$onecell_group.log" 2>&1 || onecell_status=$?
  else
    onecell_status=124
    printf 'NOT_RUN: lane budget exhausted before tracked-MD build\n' \
      > "$allprooflogs/group-$onecell_group.log"
    printf 'NOT_RUN\n' > "$allprooflogs/group-$onecell_group-build-resources.txt"
  fi
  if (( onecell_status == 0 )); then
    onecell_remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
    onecell_proof_timeout=$onecell_remaining
    (( onecell_proof_timeout <= 300 )) || onecell_proof_timeout=300
    if (( onecell_proof_timeout > 0 )); then
      /usr/bin/time -v -o "$allprooflogs/group-$onecell_group-resources.txt" \
        timeout --signal=TERM --kill-after=10s "${onecell_proof_timeout}s" \
        python3 "$onecell_component/prove.py" \
          --profile experimental-merge-allocation-span-onecell-v1 \
          --profile-evidence "$onecell_build" --tool-home "$onecell_home" \
          --compiler-sysroot "$(rustc --print sysroot)" \
          --schema "$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp" \
          --stage-seconds 25 --verifier-seconds 35 --evidence "$onecell_case" \
        >> "$allprooflogs/group-$onecell_group.log" 2>&1 || onecell_status=$?
    else
      onecell_status=124
      printf 'NOT_RUN: lane budget exhausted before one-cell proof\n' \
        >> "$allprooflogs/group-$onecell_group.log"
      printf 'NOT_RUN\n' > "$allprooflogs/group-$onecell_group-resources.txt"
    fi
  else
    printf 'NOT_RUN: tracked-MD profile build failed\n' \
      > "$allprooflogs/group-$onecell_group-resources.txt"
  fi
  printf 'onecell_build_timeout_seconds=%s\nonecell_proof_timeout_seconds=%s\n' \
    "$onecell_build_timeout" "${onecell_proof_timeout:-0}" \
    >> "$evidence_root/lane-work-budget.txt"
  printf '%s %s\n' "$onecell_group" "$onecell_status" \
    >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$onecell_status" \
    > "$allprooflogs/group-$onecell_group-exit-code.txt"
  if (( onecell_status != 0 )); then status=1; fi
else
  selected_status=$?
  if [[ "$selected_status" -ne 1 ]]; then
    printf 'one-cell group selection validation failed\n' >&2
    status=1
  fi
fi

run_mir_or_join_group() {
  local group=mir-or-join-seven-diagnostic selected_status=0 driver_status=0
  local elapsed remaining group_timeout group_evidence component fixture schema sysroot base
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$group"; then
    :
  else
    selected_status=$?
    if [[ "$selected_status" -eq 1 ]]; then return 0; fi
    status=1
    return 0
  fi
  CURRENT_STAGE=$group
  group_evidence="$allprooflogs/cases/$group"
  component="$proof_root/research/challenge-8/merge/overnight/or-join-liveness"
  fixture="$allprooflogs/bidirectional-small-cases.rs"
  schema="$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp"
  sysroot=$(rustc --print sysroot)
  base="$RUNNER_TEMP/challenge8-merge-overnight/source"
  elapsed=$((SECONDS - lane_started))
  remaining=$((lane_work_budget_seconds - elapsed - 140))
  group_timeout=0
  if (( remaining > 0 )); then
    group_timeout=1300
    (( remaining < group_timeout )) && group_timeout=$remaining
  fi
  if [[ -e "$group_evidence" ]]; then
    printf 'refusing to reuse MIR-OR-JOIN evidence path: %s\n' "$group_evidence" >&2
    driver_status=2
  elif (( group_timeout > 0 )); then
    export OR_JOIN_WORK_SECONDS="$group_timeout"
    /usr/bin/time -v -o "$allprooflogs/group-$group-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${group_timeout}s" \
      bash "$component/run-seven.sh" "$base" "$allprooflogs/build" \
        "$fixture" "$schema" "$sysroot" "$group_evidence" \
      > "$allprooflogs/group-$group.log" 2>&1 || driver_status=$?
  else
    driver_status=124
    mkdir -p "$group_evidence"
    printf 'MIR-OR-JOIN group not started: shared lane work budget exhausted.\n' \
      > "$allprooflogs/group-$group.log"
    printf 'stage not run; lane budget exhausted\n' \
      > "$allprooflogs/group-$group-resources.txt"
    python3 - "$group_evidence/seven-audit.json" <<'PARTIAL'
import json,pathlib,sys
pathlib.Path(sys.argv[1]).write_text(json.dumps({
  "component":"MIR-OR-JOIN-LIVENESS","accepted":False,
  "component_gates_complete":False,"diagnostic_complete":False,
  "classification":"INCONCLUSIVE","failed_stage":"lane-budget"
},sort_keys=True,indent=2)+"\n")
PARTIAL
    printf '124\n' > "$group_evidence/seven-run-exit-code.txt"
  fi
  if [[ -d "$group_evidence" && ! -f "$group_evidence/manifest-PINNED-INPUTS.json" ]]; then
    cp "$component/PINNED-INPUTS.json" "$group_evidence/manifest-PINNED-INPUTS.json"
  fi
  printf 'mir_or_join_work_seconds=%s\n' "$group_timeout" \
    >> "$evidence_root/lane-work-budget.txt"
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}

run_mir_or_join_group

run_guard_payload_group() {
  local group=$1 profile=$2 tool_home=$3 profile_evidence=$4
  local selected_status=0 driver_status=0 remaining group_timeout
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$group"; then
    :
  else
    selected_status=$?
    if [[ "$selected_status" -eq 1 ]]; then return 0; fi
    status=1; return 0
  fi
  CURRENT_STAGE=$group
  remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
  group_timeout=$remaining
  (( group_timeout <= 240 )) || group_timeout=240
  if (( group_timeout > 0 )); then
    /usr/bin/time -v -o "$allprooflogs/group-$group-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${group_timeout}s" python3 \
      "$proof_root/research/challenge-8/merge/overnight/guard-ownership/prove.py" \
      --profile "$profile" --profile-evidence "$profile_evidence" \
      --tool-home "$tool_home" --compiler-sysroot "$(rustc --print sysroot)" \
      --schema "$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp" \
      --stage-seconds 30 --verifier-seconds 35 \
      --evidence "$allprooflogs/cases/$group" \
      > "$allprooflogs/group-$group.log" 2>&1 || driver_status=$?
  else
    driver_status=124
    printf 'NOT_RUN: lane budget exhausted\n' > "$allprooflogs/group-$group.log"
    printf 'NOT_RUN\n' > "$allprooflogs/group-$group-resources.txt"
  fi
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}
run_guard_payload_group guard-payload-own-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" "$allprooflogs/build"
run_guard_payload_group guard-payload-own-stock-diagnostic \
  stock-26.10 "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" "$allprooflogs"

# Isolated physical permission controls; no new callee summary or trusted rule.
run_memory_cell_group() {
  local group=$1 profile=$2 tool_home=$3 dirname=$4
  local selected_status=0 driver_status=0 remaining group_timeout compiler_sysroot
  if python3 "$selection_tool" contains --selection "$selection_file" \
      --sha256 "$selection_sha" "$group"; then
    :
  else
    selected_status=$?
    if [[ "$selected_status" -eq 1 ]]; then return 0; fi
    status=1; return 0
  fi
  CURRENT_STAGE=$group
  compiler_sysroot=$(rustc --print sysroot)
  remaining=$((lane_work_budget_seconds - (SECONDS - lane_started) - 140))
  group_timeout=$remaining
  (( group_timeout <= 180 )) || group_timeout=180
  if (( group_timeout > 0 )); then
    /usr/bin/time -v -o "$allprooflogs/group-$group-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${group_timeout}s" env \
      LD_LIBRARY_PATH="$compiler_sysroot/lib:$tool_home/bin:/tmp/vfdeps-adf88dc/lib:${LD_LIBRARY_PATH:-}" \
      python3 \
      "$proof_root/research/challenge-8/merge/overnight/pointer-prove.py" \
      --profile "$profile" --scope 'matched one/two full points-to rights to same current non-ZST destination cell; diagnostic only' \
      --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" \
      --schema "$RUNNER_TEMP/challenge8-merge-overnight/vf_mir.capnp" \
      --fixture "$proof_root/research/challenge-8/merge/overnight/current-owner-memory-cell-cases.rs" \
      --verifier-seconds 45 --evidence "$allprooflogs/$dirname" \
      > "$allprooflogs/group-$group.log" 2>&1 || driver_status=$?
  else
    driver_status=124
    printf 'NOT_RUN: lane budget exhausted\n' > "$allprooflogs/group-$group.log"
    printf 'NOT_RUN\n' > "$allprooflogs/group-$group-resources.txt"
  fi
  printf '%s %s\n' "$group" "$driver_status" >> "$allprooflogs/group-status.txt"
  printf '%s\n' "$driver_status" > "$allprooflogs/group-$group-exit-code.txt"
  if (( driver_status != 0 )); then status=1; fi
}
run_memory_cell_group current-owner-memory-cell-diagnostic \
  experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \
  "$RUNNER_TEMP/challenge8-merge-overnight/source" checked-current-owner-memory-cell
run_memory_cell_group current-owner-memory-cell-stock-diagnostic \
  stock-26.10-current-owner-memory-cell \
  "$RUNNER_TEMP/challenge8-merge-overnight/verifast-26.10" checked-current-owner-memory-cell-stock

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
