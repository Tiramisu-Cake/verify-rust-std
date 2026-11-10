# PRE-BUILD — KANI5116 KT1

Candidate: commit containing this packet, identified by the full SHA in the PRE-BUILD REVIEW marker.
Branch: `experiment/kani-k1-kani5116-20261110`; stable owner `k1-merge`; slug `kani5116`; stage `kani5116-kt1`.
Request: `kani5116-kt1-calibration-20261110-01`. Build dispatch is pending coordinator exact-candidate GO; T0 is not started.
This is tooling preparation and test-only calibration, with no production macro fix or proof credit.

## Identities and packet

- Baseline for the static tooling review: `9b1758ab81`.
- Kani pin: `f046b70644e113be0df9c22c2e6ea44a65a57566`; toolchain remains `nightly-2026-10-23`.
- Patch: `research/challenge-8/kani-k1/kani5116/kt1/tests-only.patch`.
- Patch SHA-256: `46c68dfd5861ebd008c32d7580caa15cee9ac9b185dec960caf57d3d342f696f`.
- Expected Git index tree after apply: `a3822bcbbd45a864b364fc0c9fc6416cdf75da25` (includes the added fixture; HEAD alone is insufficient).
- Local preflight: fresh temporary checkout of the exact pin, digest check, `git apply --check --index -`, apply identical in-memory bytes, `git write-tree`; PASS.
- Read-only source checkout `/root/kani-src-f046b70644` remains clean. No local cargo/rustc/Kani/CBMC was run.
- Patch adds only `tests/kani/FunctionContracts/specialization_default_fn_5116.rs` (26 lines), based on [issue #5116](https://github.com/model-checking/kani/issues/5116).
- `manifest.json` duplicates the typed `kani_tests` request array for review; `applied-tree.json` records the independent local preflight identity.

## Request and native route

Existing request schema plus optional `kani_patch: {path, sha256}`; paths must be regular files beneath `research/`, with no symlink or `..` component.
The new kind uses `harnesses: []`, `kani_tests: [{suite, mode, file, expect, require_success, diagnostic?}]`, `test_timeout_seconds: 180`.
`harness_timeout_minutes: 29` is the whole-job work budget for this kind; the existing 30-minute dispatch overhead gives a 59-minute paid timeout.
The verify deadline is validation start + 53 minutes, leaving 6 minutes for summary/upload. Each native command is also bounded at 210 seconds, with compiletest's own child timeout 180 seconds; outer timeout kills its process group.
The branch-specific KT1 ledger includes finished costs and live reservations, additionally to the unchanged project ledger. Reserve: 59 × $0.0135 = **$0.7965**, cap **$0.80**. Repairs require actual remaining cap and fresh coordinator GO.
At GO record T0 and the 300-minute main / 30-minute closeout window before dispatch; do not dispatch outside it.

Preparation validates/apply-checks the patch and checks selector files and expected companions before dependency installation or compilation. A conflict, missing selector, unsafe path or digest error cannot fall back to an unpatched build.
Fresh Kani checkout every build; no Kani build cache is introduced.
New native route: `cargo build-dev -- --release`, then `cargo build -p compiletest`; only this new kind gets the documented release command form.
Per selector, from the Kani root: `cargo run -p compiletest -- --suite S --mode M --src-base tests/S --build-base ABS --exact '[M] S/file.rs' --force-rerun --color never --timeout 180`, with `RUST_TEST_THREADS=1`.
Positive expected-mode entries add `--require-success`; negative expected-mode entries require their specific diagnostic in their own `.out`/`.err`, and native PASS does not assert Kani exit success.
The script wrapper uses `target/kani/bin`; driver/compiler must match `target/release` byte-for-byte and have no competing `target/debug` binaries. compiletest itself is the separately built dev-profile binary.
These choices follow the pinned `.cargo/config.toml`, `docs/src/build-from-source.md:59`, `tools/build-kani/src/{parser,sysroot}.rs`, and compiletest's `main.rs`, `common.rs`, `runtest.rs`.

| exact native name | expected native result | require_success |
|---|---|---|
| `[kani] kani/FunctionContracts/generic_fn_pointer_argument.rs` | native PASS | `true` |
| `[kani] kani/Stubbing/stub_set_multiple_use.rs` | native PASS | `true` |
| `[expected] ui/function-contracts/trait_default_fn_err.rs` | native PASS | `false` |
| `[expected] expected/function-contract/generic_default_missing_required.rs` | native PASS | `false` |
| `[kani] kani/FunctionContracts/specialization_default_fn_5116.rs` | EXPECTED_REPRO_FAILURE: expected `fn` | `true` |

Gate requires one running test, exactly one requested terminal row, one consistent final native summary and the matching exit code per invocation. Filtering other candidates is allowed.
Repro acceptance additionally requires the normal compiletest verification-failure block for this exact source, an ordinary nonzero child exit, and actual `error: expected `fn`` in its own output. Build failures, timeout/kill, panic, foreign diagnostics, ignored/zero tests and incomplete/damaged reports are rejected.

## Static compatibility review

Only five tooling files change (listed/checksummed below). No cloudbuild YAML, Kani pin, toolchain, verify-std/library code, upstream production macros, pool, remote policy or IAM changes.
`validate_request`, `kani_args`, `verification_mode`, `summarize`, `render_md`, and `main` gain explicit optional/native branches; existing no-patch behavior is compared with the baseline across all six old kinds, valid/invalid requests, setup failure, missing logs and timeout.
Shell changes add a no-op-for-old-requests prepare stage and a native early return before verify-std. Existing kinds retain `cargo build-dev --release`, harness arguments, verification routes, timeout arithmetic and reserve rules.
Summary/check-tooling transport now fetches only summary JSON/Markdown and the bounded setup-error tail, so ordinary KT1 evidence reads do not download raw logs. Explicit legacy log commands are unchanged and are not authorized for this task.
`k1g.sh` accepts digits in the branch slug, enforces this branch's additional cap, pages native argv/binary evidence, and checks candidate request and published patch hashes in addition to the existing lane file bindings.

## Validation

- Full Python tooling suite: 102 tests PASS; service checks use only fake cargo/rustup/git/cloud commands, with real local proof tools excluded from PATH.
- Targeted `test_kani_k1.py` after the final native-runner exit guard: 82 tests PASS.
- Covered: bad path/hash, missing patch, symlink/`..`, apply conflict, missing/unknown/empty/duplicate selectors, wrong actual set/count, nonzero exit, timeout/kill, runner panic, ignored/filtered requested test, damaged/missing summary, foreign diagnostics, missing build identity, build/compiletest failure, deadline exhaustion, reservation cap, upload-before-gate, bounded summary-only fetch.
- `bash -n` for both shell scripts, embedded check-tooling Python parse, `git diff --check`: PASS.
- Native real-build calibration is pending; synthetic service results are not Kani verification evidence. This subset will not represent full upstream CI.

## After exact-candidate GO

1. Dispatch this pushed branch via `tools/k1g.sh`, then `k1g.sh watch BUILD` and end the turn; no status polling loop.
2. After wake-up: `k1g.sh summary BUILD`, `k1g.sh native BUILD [OFFSET [COUNT]]` following returned `next_offset`, `k1g.sh check-tooling BUILD APPROVED_SHA`, `k1g.sh budget BUILD`.
3. Compare pin/patch/applied tree with the identities above, and confirm all four native PASS plus exactly one EXPECTED_REPRO_FAILURE.
4. Write RESULT-KANI5116-KT1.md (at most 40 lines) with actual identities, tests/times/diagnostic, Kani and compiletest build times, spend, limitations and accepted full tooling-base SHA; commit/push `[skip ci]`, then the required review/completion marker and stop.

## Tooling blob SHA-256

```text
be3bf84d10a1383a87166a15b2c0aeaf4a6cc3605185db7c55d27726b7afe7ae  research/challenge-8/kani-k1/tools/gcb-k1.sh
5d93fd5cd92e9a905f10090265b2071e42e0a3beb19a62bf36a18836ce70234a  research/challenge-8/kani-k1/tools/k1g.sh
cdc68f433ee7e10ddfa2b99bffc0426f5f1952a6bac13238aa96f8a0b2a5a99d  research/challenge-8/kani-k1/tools/kani_k1.py
94faf5e36db81568e68cce4e95dca72f23b470ac4fdcdc9ed71f4e02f2ca035e  research/challenge-8/kani-k1/tools/test_gcb_native.py
1e67804b4b106adce6d0721eae2eaf86a5b0fdefd5bf196fadb1f32198fcc00b  research/challenge-8/kani-k1/tools/test_kani_k1.py
```

## Complete static tooling diff from 9b1758ab81 (git diff --unified=0)

```text
 research/challenge-8/kani-k1/tools/gcb-k1.sh       |  74 +++-
 research/challenge-8/kani-k1/tools/k1g.sh          |  54 ++-
 research/challenge-8/kani-k1/tools/kani_k1.py      | 406 ++++++++++++++++++++-
 .../challenge-8/kani-k1/tools/test_gcb_native.py   | 267 ++++++++++++++
 research/challenge-8/kani-k1/tools/test_kani_k1.py | 267 ++++++++++++++
 5 files changed, 1045 insertions(+), 23 deletions(-)
```

```diff
diff --git a/research/challenge-8/kani-k1/tools/gcb-k1.sh b/research/challenge-8/kani-k1/tools/gcb-k1.sh
index 049b30a394..f4091b4de7 100755
--- a/research/challenge-8/kani-k1/tools/gcb-k1.sh
+++ b/research/challenge-8/kani-k1/tools/gcb-k1.sh
@@ -34 +34,9 @@ valid() { [ -f "$K1_OUT/valid" ]; }
-total_minutes() { python3 -B -c 'import json,sys; r=json.load(open(sys.argv[1])); print(r["harness_timeout_minutes"] if r.get("kind") in ("partition", "autoharness", "inventory") else len(r["harnesses"]) * r["harness_timeout_minutes"])' "$K1_REQUEST"; }
+total_minutes() { python3 -B -c 'import json,sys; r=json.load(open(sys.argv[1])); print(r["harness_timeout_minutes"] if r.get("kind") in ("partition", "autoharness", "inventory", "kani-tests") else len(r["harnesses"]) * r["harness_timeout_minutes"])' "$K1_REQUEST"; }
+native() { python3 -B -c 'import json,sys; sys.exit(json.load(open(sys.argv[1]))["kind"] != "kani-tests")' "$K1_REQUEST"; }
+checkout_kani() {
+  rm -rf kani_build && mkdir kani_build
+  git -C kani_build init -q .
+  git -C kani_build remote add origin https://github.com/model-checking/kani.git
+  git -C kani_build fetch --depth 1 origin "$commit" --quiet
+  git -C kani_build checkout "$commit" --quiet
+}
@@ -62,0 +71,14 @@ stage() {
+    prepare)
+      valid || return 0
+      # Only new native/patch requests enter this preflight; all old no-patch build routes stay intact.
+      if ! python3 -B -c 'import json,sys; r=json.load(open(sys.argv[1])); sys.exit(not (r.get("kani_patch") or r["kind"] == "kani-tests"))' "$K1_REQUEST"; then return 0; fi
+      apt-get install -y -qq --no-install-recommends ca-certificates >/dev/null
+      commit=$(kani_commit); test -n "$commit"
+      checkout_kani
+      if ! python3 -B "$K1_TOOLS/kani_k1.py" prepare-kani --request "$K1_REQUEST" --tree kani_build --pin "$commit" \
+          --out "$K1_OUT/kani-build.json" 2> "$K1_OUT/request-error.txt"; then
+        rm -f "$K1_OUT/valid"
+        return 0
+      fi
+      touch "$K1_OUT/prepared" ;;
+
@@ -81,5 +103,7 @@ stage() {
-      rm -rf kani_build && mkdir kani_build
-      git -C kani_build init -q .
-      git -C kani_build remote add origin https://github.com/model-checking/kani.git
-      git -C kani_build fetch --depth 1 origin "$commit" --quiet
-      git -C kani_build checkout "$commit" --quiet
+      if [ ! -f "$K1_OUT/prepared" ]; then
+        # A failed preflight must never fall back to an unpatched build.
+        if python3 -B -c 'import json,sys; r=json.load(open(sys.argv[1])); sys.exit(not (r.get("kani_patch") or r["kind"] == "kani-tests"))' "$K1_REQUEST"; then
+          echo "required Kani preflight missing" >&2; return 1
+        fi
+        checkout_kani
+      fi
@@ -89 +113,13 @@ stage() {
-      (cd kani_build && cargo build-dev --release)
+      build_start=$(date +%s)
+      if native; then
+        (cd kani_build && cargo build-dev -- --release)
+      else
+        (cd kani_build && cargo build-dev --release)
+      fi
+      kani_build_s=$(( $(date +%s) - build_start ))
+      compiletest_build_s=0
+      if native; then
+        compiletest_start=$(date +%s)
+        (cd kani_build && cargo build -p compiletest)
+        compiletest_build_s=$(( $(date +%s) - compiletest_start ))
+      fi
@@ -91,0 +128,10 @@ stage() {
+      if [ -f "$K1_OUT/prepared" ]; then
+        version=$(kani_build/scripts/kani --version)
+        python3 -B - "$K1_OUT/kani-build.json" "$version" "$kani_build_s" "$compiletest_build_s" <<'PY'
+import json, sys
+from pathlib import Path
+p = Path(sys.argv[1]); d = json.loads(p.read_text())
+d.update(version=sys.argv[2], kani_build_s=int(sys.argv[3]), compiletest_build_s=int(sys.argv[4]))
+p.write_text(json.dumps(d, indent=2) + "\n")
+PY
+      fi
@@ -102,0 +149,7 @@ stage() {
+      if native; then
+        python3 -B "$K1_TOOLS/kani_k1.py" run-native --request "$K1_REQUEST" --tree kani_build --out "$K1_OUT" \
+          --deadline "$(( $(cat "$K1_OUT/start") + ($(total_minutes) + VERIFY_SLACK_MINUTES) * 60 ))" \
+          --head-sha "$(git rev-parse HEAD)" --build-id "${K1_BUILD_ID:-}" --kani-build "$K1_OUT/kani-build.json"
+        echo 0 > "$K1_OUT/rc"
+        return 0
+      fi
@@ -215,0 +269,3 @@ stage() {
+      native_args=()
+      [ ! -f "$K1_OUT/kani-build.json" ] || native_args+=(--kani-build "$K1_OUT/kani-build.json")
+      [ ! -f "$K1_OUT/native.json" ] || native_args+=(--native "$K1_OUT/native.json")
@@ -219 +275 @@ stage() {
-      python3 -B "$K1_TOOLS/kani_k1.py" summarize --request "$K1_REQUEST" "${log_args[@]}" "${peaks_args[@]}" "${inventory_args[@]}" \
+      python3 -B "$K1_TOOLS/kani_k1.py" summarize --request "$K1_REQUEST" "${log_args[@]}" "${peaks_args[@]}" "${inventory_args[@]}" "${native_args[@]}" \
@@ -242 +298 @@ if [ "${1:-}" != all ]; then stage "${1:-}"; exit; fi
-for s in validate deps build verify summarize; do
+for s in validate prepare deps build verify summarize; do
diff --git a/research/challenge-8/kani-k1/tools/k1g.sh b/research/challenge-8/kani-k1/tools/k1g.sh
index 729241b563..8cb3892309 100755
--- a/research/challenge-8/kani-k1/tools/k1g.sh
+++ b/research/challenge-8/kani-k1/tools/k1g.sh
@@ -14,0 +15 @@
+#   k1g.sh native BUILD [OFFSET [COUNT]] bounded native argv/cwd/binary evidence (COUNT <= 4)
@@ -98,2 +99,3 @@ ledger() {
-fetch() {  # fetch BUILD -> directory with summary/ and log/; only for finished builds, whose uploads are final
-  local id=$1 dir="$CACHE/$1" tmp status
+fetch() {  # summaries scope never downloads raw logs; legacy log commands retain their explicit route
+  local id=$1 scope=${2:-legacy} dir="$CACHE/$1" tmp status
+  [ "$scope" != summaries ] || dir="$CACHE/summary-$id"
@@ -112,0 +115,3 @@ fetch() {  # fetch BUILD -> directory with summary/ and log/; only for finished
+      if [ "$scope" = summaries ]; then
+        case "$rel" in summary/summary.json|summary/summary.md|log/stage-error.txt) ;; *) continue ;; esac
+      fi
@@ -124 +129 @@ case "$cmd" in
-    branch=${1:-}; [[ "$branch" =~ ^experiment/kani-k1-[a-z]+-[0-9]{8}$ ]] || die "branch must be experiment/kani-k1-<name>-<date>"
+    branch=${1:-}; [[ "$branch" =~ ^experiment/kani-k1-[a-z0-9]+-[0-9]{8}$ ]] || die "branch must be experiment/kani-k1-<name>-<date>"
@@ -136 +141 @@ case "$cmd" in
-    total=$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print(r["harness_timeout_minutes"] if r.get("kind") in ("partition", "autoharness", "inventory") else len(r["harnesses"]) * r["harness_timeout_minutes"])' "$work/request.json")
+    total=$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print(r["harness_timeout_minutes"] if r.get("kind") in ("partition", "autoharness", "inventory", "kani-tests") else len(r["harnesses"]) * r["harness_timeout_minutes"])' "$work/request.json")
@@ -145,0 +151,12 @@ case "$cmd" in
+    # KT1 has its own $0.80 cap in addition to the unchanged project ledger. This branch is dedicated
+    # to this stage; reservations include all its in-flight builds, repairs use actual finished cost.
+    if [[ "$branch" = experiment/kani-k1-kani5116-20261110 ]]; then
+      stage_ledger=$(G builds list --region="$REGION" --limit=1000 --format=json --filter="substitutions._BRANCH=$branch" \
+        | python3 -B "$TOOLS/kani_k1.py" ledger --price "$POOL_HIGHMEM=$PRICE_HIGHMEM" --price "$POOL_STANDARD=$PRICE_STANDARD") \
+        || die "cannot compute kani5116-kt1 ledger"
+      read -r stage_builds stage_used stage_reserved <<< "$stage_ledger"
+      [ "$stage_builds" -lt 1000 ] || die "KT1 ledger may undercount"
+      within_cap "$(python3 -c "print($stage_used + $stage_reserved + $cost)")" 0.80 \
+        || die "kani5116-kt1 budget exceeds \$0.80 including this reservation"
+      [ "$timeout" -le 59 ] || die "kani5116-kt1 timeout exceeds 59 min"
+    fi
@@ -201 +218 @@ case "$cmd" in
-    dir=$(fetch "$id")
+    dir=$(fetch "$id" summaries)
@@ -216,0 +234,7 @@ case "$cmd" in
+  native)
+    id=${1:-}; is_build "$id"; [ "$#" -le 3 ] || die "native accepts BUILD [OFFSET [COUNT]]"
+    offset=${2:-0}; count=${3:-1}
+    [[ "$offset" =~ ^[0-9]+$ ]] || die "OFFSET must be a non-negative integer"
+    [[ "$count" =~ ^[1-4]$ ]] || die "COUNT must be 1..4"
+    auth; dir=$(fetch "$id" summaries)
+    python3 -B "$TOOLS/kani_k1.py" page-native "$dir/summary/summary.json" "$offset" "$count" ;;
@@ -273 +297 @@ PY
-    dir=$(fetch "$id")
+    dir=$(fetch "$id" summaries)
@@ -293,0 +318,18 @@ for path in paths:
+request_path = "research/challenge-8/kani-k1/RUN-REQUEST.json"
+request_blob = subprocess.run(["git", "show", f"{head}:{request_path}"], capture_output=True, check=True).stdout
+request = json.loads(request_blob)
+if request.get("kani_patch") or request.get("kind") == "kani-tests":
+    want = hashlib.sha256(request_blob).hexdigest()
+    ok = summary.get("request_sha256") == want
+    bad += not ok
+    print(f"{'ok  ' if ok else 'DIFF'} candidate request SHA-256 {want}")
+    info = summary.get("kani_build") or {}
+    ok = info.get("patch") == request.get("kani_patch")
+    bad += not ok
+    print(f"{'ok  ' if ok else 'DIFF'} applied patch specification matches candidate request; tree={info.get('tree')}")
+    if request.get("kani_patch"):
+        spec = request["kani_patch"]
+        blob = subprocess.run(["git", "show", f"{head}:{spec['path']}"], capture_output=True, check=True).stdout
+        ok = hashlib.sha256(blob).hexdigest() == spec["sha256"]
+        bad += not ok
+        print(f"{'ok  ' if ok else 'DIFF'} published patch SHA-256 {spec['sha256']}")
diff --git a/research/challenge-8/kani-k1/tools/kani_k1.py b/research/challenge-8/kani-k1/tools/kani_k1.py
index 0a1b58d943..df41ecb162 100755
--- a/research/challenge-8/kani-k1/tools/kani_k1.py
+++ b/research/challenge-8/kani-k1/tools/kani_k1.py
@@ -36 +36 @@ AGENTS = {"k1-merge", "k1-network", "coordinator"}
-KINDS = {"measurement", "diagnostic", "resource", "partition", "autoharness", "inventory"}
+KINDS = {"measurement", "diagnostic", "resource", "partition", "autoharness", "inventory", "kani-tests"}
@@ -68 +68,4 @@ CONTROLS_CFG = "kani_smallsort_controls"
-OPTIONAL_REQUEST_KEYS = {"kani_jobs", "uninit_checks", "valid_value_checks", "controls", "worker_index", "worker_total", "inventory"}
+OPTIONAL_REQUEST_KEYS = {"kani_jobs", "uninit_checks", "valid_value_checks", "controls", "worker_index", "worker_total", "inventory",
+                         "kani_patch", "kani_tests", "test_timeout_seconds"}
+NATIVE_MAX_MINUTES = 29  # + unchanged 30 min dispatch overhead = 59 min / $0.7965 reserve
+NATIVE_SCHEMA = "kani-k1-native-tests-v1"
@@ -130,0 +134,222 @@ def _one_line(value: Any, limit: int) -> bool:
+def safe_relative(value: Any, prefix: str = "") -> bool:
+    return (isinstance(value, str) and len(value) <= 300 and value.startswith(prefix)
+            and bool(re.fullmatch(r"[A-Za-z0-9_./-]+", value))
+            and all(p not in ("", ".", "..") for p in value.split("/")) and not value.startswith("/"))
+
+
+def regular_inside(root: Path, relative: str) -> Path:
+    if not safe_relative(relative):
+        raise RequestError(f"unsafe relative path: {relative!r}")
+    path = root
+    for part in relative.split("/"):
+        path = path / part
+        if path.is_symlink():
+            raise RequestError(f"symlink in path: {relative}")
+    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
+        raise RequestError(f"missing/non-regular file: {relative}")
+    return path
+
+
+def native_name(entry: dict[str, Any]) -> str:
+    return f"[{entry['mode']}] {entry['suite']}/{entry['file']}"
+
+
+def validate_native_manifest(entries: Any) -> None:
+    if not isinstance(entries, list) or not 1 <= len(entries) <= 20:
+        raise RequestError("kani_tests must contain 1..20 typed selectors")
+    names = []
+    for e in entries:
+        if (not isinstance(e, dict) or not {"suite", "mode", "file", "expect", "require_success"} <= set(e)
+                or set(e) - {"suite", "mode", "file", "expect", "require_success", "diagnostic"}):
+            raise RequestError("native selector requires suite, mode, file, expect, require_success")
+        if (e["suite"], e["mode"]) not in (("kani", "kani"), ("ui", "expected"), ("expected", "expected")):
+            raise RequestError("unknown native suite/mode")
+        if not safe_relative(e["file"]) or not e["file"].endswith(".rs"):
+            raise RequestError("native file must be a safe relative .rs path inside its suite")
+        if e["expect"] not in ("pass", "fail") or type(e["require_success"]) is not bool:
+            raise RequestError("native expect must be pass/fail; require_success must be bool")
+        diagnostic = e.get("diagnostic")
+        if diagnostic is not None and not _one_line(diagnostic, 200):
+            raise RequestError("diagnostic must be a nonempty one-line substring")
+        if e["expect"] == "fail":
+            if e["mode"] != "kani" or diagnostic != "expected `fn`" or not e["require_success"]:
+                raise RequestError("expect fail is only the native kani repro with expected `fn` and require_success")
+        elif e["mode"] == "expected":
+            if not e["require_success"] and not diagnostic:
+                raise RequestError("negative expected-mode test needs a diagnostic; positive needs require_success")
+            if e["require_success"] and diagnostic:
+                raise RequestError("positive expected-mode test cannot declare a negative diagnostic")
+        elif not e["require_success"] or diagnostic:
+            raise RequestError("kani pass tests require success and no negative diagnostic")
+        names.append(native_name(e))
+    if len(set(names)) != len(names):
+        raise RequestError("duplicate native selectors")
+
+
+def patch_bytes(request: dict[str, Any], root: Path) -> bytes | None:
+    spec = request.get("kani_patch")
+    if spec is None:
+        return None
+    data = regular_inside(root, spec["path"]).read_bytes()
+    if hashlib.sha256(data).hexdigest() != spec["sha256"]:
+        raise RequestError("kani_patch SHA-256 mismatch")
+    if not data or len(data) > 4 * 1024 * 1024:
+        raise RequestError("kani_patch must be nonempty and at most 4 MiB")
+    return data
+
+
+def git_output(tree: Path, *args: str, data: bytes | None = None) -> str:
+    result = subprocess.run(["git", "-C", str(tree), *args], input=data, capture_output=True, timeout=120)
+    if result.returncode:
+        raise RequestError(f"git {args[0]} failed: {_clip(result.stderr.decode(errors='replace'))}")
+    return result.stdout.decode().strip()
+
+
+def prepare_kani(request: dict[str, Any], root: Path, tree: Path, pin: str) -> dict[str, Any]:
+    """Fresh checkout only. The same in-memory bytes are checked and applied; index tree includes additions."""
+    if git_output(tree, "rev-parse", "HEAD") != pin or git_output(tree, "status", "--porcelain", "--untracked-files=all"):
+        raise RequestError("patch preflight requires a clean checkout of the exact pin")
+    data = patch_bytes(request, root)
+    if data is not None:
+        git_output(tree, "apply", "--check", "--index", "-", data=data)
+        git_output(tree, "apply", "--index", "-", data=data)
+    if request["kind"] == "kani-tests":
+        for e in request["kani_tests"]:
+            regular_inside(tree, f"tests/{e['suite']}/{e['file']}")
+            if e["mode"] == "expected":
+                source = Path(f"tests/{e['suite']}/{e['file']}")
+                expected = source.with_suffix(".expected")
+                if not (tree / expected).exists():
+                    expected = source.parent / "expected"
+                regular_inside(tree, str(expected))
+    diffstat = git_output(tree, "diff", "--cached", "--stat", pin)
+    if len(diffstat.encode()) > 4096:
+        raise RequestError("patch diffstat exceeds bounded report size")
+    return {"pin": pin, "patch": request.get("kani_patch"), "tree": git_output(tree, "write-tree"),
+            "diffstat": diffstat}
+
+
+def native_argv(entry: dict[str, Any], timeout: int, build_base: Path) -> list[str]:
+    argv = ["cargo", "run", "-p", "compiletest", "--", "--suite", entry["suite"], "--mode", entry["mode"],
+            "--src-base", f"tests/{entry['suite']}", "--build-base", str(build_base), "--exact", native_name(entry),
+            "--force-rerun", "--color", "never", "--timeout", str(timeout)]
+    if entry["mode"] == "expected" and entry["require_success"]:
+        argv.append("--require-success")
+    return argv
+
+
+NATIVE_TOTAL_RE = re.compile(r"^test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out; finished in ([0-9.]+)s\s*$", re.M)
+NATIVE_ROW_RE = re.compile(r"^test (\[[^\n]+) \.\.\. (ok|FAILED|ignored)(?:\s+<[^>]+>)?\s*$", re.M)
+
+
+def parse_native_test(entry: dict[str, Any], text: str, code: int | None,
+                      own_output: str | None, timed_out: bool = False) -> dict[str, Any]:
+    name = native_name(entry)
+    running = re.findall(r"^running (\d+) tests?\s*$", text, re.M)
+    rows = NATIVE_ROW_RE.findall(text)
+    totals = NATIVE_TOTAL_RE.findall(text)
+    errors = []
+    if running != ["1"] or len(rows) != 1 or rows[0][0] != name or len(totals) != 1:
+        errors.append("native running/name/result/summary must identify exactly one requested test")
+    terminal = rows[0][1] if len(rows) == 1 else None
+    if totals:
+        outcome, passed, failed, ignored, measured, filtered, duration = totals[0]
+        if ((passed, failed, ignored, measured) != (("1", "0", "0", "0") if terminal == "ok" else ("0", "1", "0", "0"))
+                or outcome != ("ok" if terminal == "ok" else "FAILED")):
+            errors.append("native totals disagree with requested result (ignored/filtered requested test rejected)")
+    else:
+        duration = None
+    if timed_out or code not in (0, 1) or re.search(r"Process timed out|signal:|SIGKILL|SIGTERM|thread '[^']+' panicked|I/O failure during tests|could not compile", text):
+        errors.append("timeout/kill/build failure/runner panic is not a native result")
+    if (terminal == "ok" and code != 0) or (terminal == "FAILED" and code != 1):
+        errors.append("native exit/result mismatch")
+    diagnostic_line = None
+    if own_output is None:
+        errors.append("own test output missing")
+    else:
+        if re.search(r"Process timed out|signal:|SIGKILL|SIGTERM|thread '[^']+' panicked|internal compiler error", own_output):
+            errors.append("own test output contains a timeout/kill/panic")
+        if entry.get("diagnostic"):
+            diagnostic_line = next((line for line in own_output.splitlines() if entry["diagnostic"] in line), None)
+            if diagnostic_line is None:
+                errors.append("required diagnostic absent from this test's own output")
+    if entry["expect"] == "fail":
+        # ProcRes::fatal is compiletest's normal failure (resume_unwind), not a runner panic.
+        block = re.search(r"^---- " + re.escape(name) + r" stdout ----\n(.*?)^failures:\s*$", text, re.M | re.S)
+        if (terminal != "FAILED" or not block
+                or "error: test failed: expected verification success, got failure" not in block[1]
+                or not re.search(r"^status: exit status: [1-9][0-9]*$", block[1], re.M)
+                or not re.search(r"^command: .*\"kani\".*" + re.escape("tests/" + entry["suite"] + "/" + entry["file"]), block[1], re.M)):
+            errors.append("repro requires a normal completed compiletest verification failure for this file")
+        if own_output is not None and not re.search(r"^error: expected `fn`\s*$", own_output, re.M):
+            errors.append("repro diagnostic is not an actual compiler error")
+    elif terminal != "ok":
+        errors.append("requested native PASS did not pass")
+    return {"name": name, "expect": entry["expect"], "native_status": terminal,
+            "status": ("EXPECTED_REPRO_FAILURE" if entry["expect"] == "fail" else "PASS") if not errors else "ERROR",
+            "time_s": float(duration) if duration is not None else None, "exit_code": code,
+            "diagnostic": _clip(diagnostic_line) if diagnostic_line else None, "errors": errors,
+            "suite": entry["suite"], "mode": entry["mode"], "file": entry["file"], "require_success": entry["require_success"]}
+
+
+def bounded_command(argv: list[str], cwd: Path, log: Path, seconds: float,
+                    env: dict[str, str] | None = None) -> tuple[int | None, bool, float]:
+    """Separate process group: kill descendants on wall timeout, even if compiletest's child holds pipes."""
+    start = time.monotonic()
+    if seconds <= 0:
+        return None, True, 0.0
+    with log.open("wb") as stream:
+        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
+        try:
+            code = proc.wait(timeout=seconds)
+            timeout = False
+        except subprocess.TimeoutExpired:
+            os.killpg(proc.pid, signal.SIGKILL)
+            code = proc.wait()
+            timeout = True
+    return code, timeout, round(time.monotonic() - start, 3)
+
+
+def native_binary_identity(tree: Path) -> dict[str, Any]:
+    result: dict[str, Any] = {"kani_profile": "release", "compiletest_profile": "dev", "paths": {}}
+    for name in ("kani-driver", "kani-compiler"):
+        built = regular_inside(tree, f"target/release/{name}")
+        installed = tree / "target/kani/bin" / name  # build-dev intentionally installs copies/symlinks
+        if not installed.is_file() or installed.read_bytes() != built.read_bytes() or (tree / "target/debug" / name).exists():
+            raise RequestError(f"native Kani binary profile mismatch: {name}")
+        result["paths"][name] = {"invoked": str(installed), "resolved": str(installed.resolve()),
+                                  "release": str(built), "sha256": hashlib.sha256(built.read_bytes()).hexdigest()}
+    result["paths"]["kani"] = {"invoked": str(regular_inside(tree, "scripts/kani"))}
+    result["paths"]["compiletest"] = {"invoked": str(regular_inside(tree, "target/debug/compiletest"))}
+    return result
+
+
+def run_native(request: dict[str, Any], tree: Path, out: Path, deadline: float,
+               binding: dict[str, Any]) -> None:
+    report: dict[str, Any] = {"schema": NATIVE_SCHEMA, **binding, "tests": [], "complete": False,
+                              "binaries": native_binary_identity(tree)}
+    out.mkdir(parents=True, exist_ok=True)
+    report_path = out / "native.json"
+    report_path.write_text(json.dumps(report))
+    env = dict(os.environ, RUST_TEST_THREADS="1", CARGO_TERM_COLOR="never")
+    env.pop("RUST_TEST_NOCAPTURE", None)
+    for i, entry in enumerate(request["kani_tests"]):
+        build_base = out / f"native-{i}"
+        argv = native_argv(entry, request["test_timeout_seconds"], build_base)
+        log = out / f"native-{i}.log"
+        seconds = min(request["test_timeout_seconds"] + 30, deadline - time.time())
+        code, timeout, wall = bounded_command(argv, tree, log, seconds, env)
+        relative = Path(entry["file"])
+        base = build_base / relative.parent / relative.stem / relative.stem
+        # compiletest dump_output produces .out/.err for precisely this selector in a fresh build-base.
+        own = None
+        if base.with_suffix(".out").is_file() and base.with_suffix(".err").is_file():
+            own = base.with_suffix(".out").read_text(errors="replace") + "\n" + base.with_suffix(".err").read_text(errors="replace")
+        row = parse_native_test(entry, log.read_text(errors="replace") if log.exists() else "", code, own, timeout)
+        row.update(argv=argv, cwd=str(tree), env={"RUST_TEST_THREADS": "1"}, wall_s=wall)
+        report["tests"].append(row)
+        report_path.write_text(json.dumps(report, indent=2) + "\n")
+    report["complete"] = True
+    report_path.write_text(json.dumps(report, indent=2) + "\n")
+
+
@@ -147,0 +373,22 @@ def validate_request(data: Any, max_total_minutes: int | None = None) -> dict[st
+    if "kani_patch" in data:
+        patch = data["kani_patch"]
+        if (data["kind"] not in ("diagnostic", "kani-tests") or data["runner"] != STANDARD_RUNNER
+                or not isinstance(patch, dict) or set(patch) != {"path", "sha256"}
+                or not safe_relative(patch.get("path"), "research/")
+                or not isinstance(patch.get("sha256"), str)
+                or not re.fullmatch(r"[0-9a-f]{64}", patch["sha256"])):
+            raise RequestError("kani_patch requires diagnostic/kani-tests on standard runner and {path: research/..., sha256: 64 hex}; no .. or symlinks")
+    if data["kind"] == "kani-tests":
+        unsupported = set(data) & (OPTIONAL_REQUEST_KEYS - {"kani_patch", "kani_tests", "test_timeout_seconds"})
+        if unsupported or data["runner"] != STANDARD_RUNNER or data["harnesses"] != []:
+            raise RequestError("kani-tests requires standard runner, harnesses: [], and only native options")
+        cap = min(NATIVE_MAX_MINUTES, max_total_minutes) if max_total_minutes is not None else NATIVE_MAX_MINUTES
+        if type(data["harness_timeout_minutes"]) is not int or not 1 <= data["harness_timeout_minutes"] <= cap:
+            raise RequestError(f"kani-tests whole-job budget must be 1..{cap} minutes")
+        timeout = data.get("test_timeout_seconds")
+        if type(timeout) is not int or not 1 <= timeout <= 600 or timeout > data["harness_timeout_minutes"] * 60:
+            raise RequestError("test_timeout_seconds must be 1..600 and fit the whole-job budget")
+        validate_native_manifest(data.get("kani_tests"))
+        return data
+    if set(data) & {"kani_tests", "test_timeout_seconds"}:
+        raise RequestError("native selectors/timeouts are only for kani-tests")
@@ -351 +598 @@ def kani_args(request: dict[str, Any]) -> list[str]:
-    if request["kind"] == "inventory":
+    if request["kind"] in ("inventory", "kani-tests"):
@@ -393 +640 @@ def verification_mode(kind: str) -> str:
-            "diagnostic": "selected"}.get(kind, "invalid")
+            "diagnostic": "selected", "kani-tests": "kani-tests"}.get(kind, "invalid")
@@ -1153,0 +1401,22 @@ def summary_page(summary: dict[str, Any], offset: int, count: int) -> str:
+def native_page(summary: dict[str, Any], offset: int, count: int) -> str:
+    native = summary.get("native")
+    if not isinstance(native, dict) or not isinstance(native.get("tests"), list):
+        raise ValueError("no structured native report")
+    rows = native["tests"]
+    _page_bounds(len(rows), offset, count)
+    if not 1 <= count <= 4:
+        raise ValueError("native COUNT must be 1..4")
+    end = min(offset + count, len(rows))
+    page = {"head_sha": summary.get("head_sha"), "request_sha256": summary.get("request_sha256"),
+            "build_id": (summary.get("run") or {}).get("id"), "kani_build": summary.get("kani_build"),
+            "binaries": native.get("binaries"), "total": len(rows), "offset": offset}
+    while True:
+        page.update(tests=rows[offset:end], count=end-offset, next_offset=end if end < len(rows) else None)
+        text = json.dumps(page, ensure_ascii=False, indent=2) + "\n"
+        if len(text.encode()) <= MAX_MD_BYTES:
+            return text
+        end -= 1
+        if end <= offset:
+            raise ValueError("one native record exceeds the bounded page size")
+
+
@@ -1225 +1494,2 @@ def summarize(request_text: str | None, log_text: str | None, time_text: str | N
-              peaks_tracked: bool = False, inventory_text: str | None = None) -> dict[str, Any]:
+              peaks_tracked: bool = False, inventory_text: str | None = None,
+              native_text: str | None = None, kani_build_text: str | None = None) -> dict[str, Any]:
@@ -1277,0 +1548,67 @@ def summarize(request_text: str | None, log_text: str | None, time_text: str | N
+    if request.get("kani_patch") or request["kind"] == "kani-tests":
+        try:
+            info = json.loads(kani_build_text or "null")
+            if (not isinstance(info, dict) or info.get("pin") != kani_commit or info.get("patch") != request.get("kani_patch")
+                    or not re.fullmatch(r"[0-9a-f]{40}", info.get("tree", ""))
+                    or not _one_line(info.get("version"), 200) or build_outcome != "success"):
+                raise ValueError("missing/inconsistent Kani patch/tree/version/build identity")
+            summary["kani_build"] = info
+        except (ValueError, TypeError) as exc:
+            summary["status"] = "RUNNER_ERROR"
+            summary["inconsistencies"].append(str(exc))
+            return summary
+    if request["kind"] == "kani-tests":
+        summary["measurement_ok"] = None
+        summary["kani_exit_code"] = None
+        summary["native_runner_exit_code"] = exit_code
+        summary["notes"].append("Native compiletest results; negative expected-mode PASS does not establish a successful Kani exit.")
+        try:
+            if exit_code != 0:
+                raise ValueError("native runner did not exit successfully")
+            native = json.loads(native_text or "null")
+            bindings = {"schema": NATIVE_SCHEMA, "head_sha": head_sha, "build_id": summary["run"].get("id"),
+                        "request_sha256": summary["request_sha256"], "tree": summary["kani_build"]["tree"]}
+            if not isinstance(native, dict) or any(native.get(k) != v for k, v in bindings.items()):
+                raise ValueError("native report binding/schema mismatch or missing report")
+            rows = native.get("tests")
+            if (native.get("complete") is not True or not isinstance(rows, list)
+                    or [r.get("name") for r in rows] != [native_name(e) for e in request["kani_tests"]]):
+                raise ValueError("native actual set/order/count differs from requested selectors or report incomplete")
+            binaries = native.get("binaries") or {}
+            if (binaries.get("kani_profile") != "release" or binaries.get("compiletest_profile") != "dev"
+                    or set(binaries.get("paths") or {}) != {"kani", "kani-driver", "kani-compiler", "compiletest"}):
+                raise ValueError("native binary profiles/paths absent")
+            for binary in binaries["paths"].values():
+                if not _one_line(binary.get("invoked"), 500):
+                    raise ValueError("native invoked binary path absent")
+            for name in ("kani-driver", "kani-compiler"):
+                binary = binaries["paths"][name]
+                if (not _one_line(binary.get("release"), 500) or not _one_line(binary.get("resolved"), 500)
+                        or not re.fullmatch(r"[0-9a-f]{64}", binary.get("sha256", ""))):
+                    raise ValueError("native release binary identity absent")
+            if any(type(summary["kani_build"].get(key)) not in (float, int) or summary["kani_build"][key] < 0
+                   for key in ("kani_build_s", "compiletest_build_s")):
+                raise ValueError("native build timing missing")
+            for row, entry in zip(rows, request["kani_tests"]):
+                argv = native_argv(entry, request["test_timeout_seconds"], Path(row["argv"][row["argv"].index("--build-base") + 1]))
+                if (row["argv"] != argv or row.get("env") != {"RUST_TEST_THREADS": "1"} or not row.get("cwd")
+                        or row.get("expect") != entry["expect"]
+                        or any(row.get(key) != entry[key] for key in ("suite", "mode", "file", "require_success"))):
+                    raise ValueError("native argv/env/cwd/expect mismatch")
+                if (type(row.get("time_s")) not in (int, float) or not math.isfinite(row["time_s"]) or row["time_s"] < 0
+                        or type(row.get("wall_s")) not in (int, float) or not math.isfinite(row["wall_s"]) or row["wall_s"] < 0):
+                    raise ValueError("native timing missing/corrupt")
+                if row.get("status") != "ERROR":
+                    if (row.get("native_status") != ("FAILED" if entry["expect"] == "fail" else "ok")
+                            or row.get("exit_code") != (1 if entry["expect"] == "fail" else 0)
+                            or (entry.get("diagnostic") and entry["diagnostic"] not in (row.get("diagnostic") or ""))):
+                        raise ValueError("native terminal/exit/diagnostic inconsistent")
+            summary["native"] = native
+            summary["harnesses"] = rows
+            summary["expectation_met"] = all(r.get("status") == ("EXPECTED_REPRO_FAILURE" if e["expect"] == "fail" else "PASS")
+                                              and r.get("errors") == [] for r, e in zip(rows, request["kani_tests"]))
+            summary["status"] = "COMPLETE" if summary["expectation_met"] else "TOOL_ERROR"
+        except (ValueError, KeyError, TypeError, AttributeError) as exc:
+            summary["status"] = "INCONSISTENT"
+            summary["inconsistencies"].append(str(exc))
+        return summary
@@ -1557,0 +1895,15 @@ def render_md(summary: dict[str, Any]) -> str:
+    if summary.get("kani_build"):
+        info = summary["kani_build"]
+        lines[8:8] = [f"- Kani applied tree `{info['tree']}`, patch `{(info.get('patch') or {}).get('sha256')}`, version `{info['version']}`",
+                      f"- Kani build {info.get('kani_build_s')} s; compiletest build {info.get('compiletest_build_s')} s",
+                      f"- patch diffstat: {info.get('diffstat')}"]
+    if summary.get("native"):
+        native_lines = ["", "| native test | expectation | result | wall s | diagnostic |", "|---|---|---|---|---|"]
+        for row in summary["harnesses"]:
+            native_lines.append(f"| {row['name']} | {row['expect']} | {row['status']} | {row['wall_s']} | {row.get('diagnostic') or ''} |")
+        # Full argv, cwd, binary paths and profiles remain in the bounded structured summary.
+        lines = lines[:next(i for i, line in enumerate(lines) if line.startswith("| harness"))] + native_lines
+        lines += [f"- {note}" for note in summary["inconsistencies"]]
+        lines += [f"- {note}" for note in summary["notes"]]
+        lines += [f"- {row['name']}: {error}" for row in summary["harnesses"] for error in row.get("errors", [])]
+        return "\n".join(lines) + "\n"
@@ -1624,0 +1977,13 @@ def main(argv: list[str]) -> int:
+    prep = sub.add_parser("prepare-kani")
+    prep.add_argument("--request", required=True)
+    prep.add_argument("--tree", required=True)
+    prep.add_argument("--pin", required=True)
+    prep.add_argument("--out", required=True)
+    nt = sub.add_parser("run-native")
+    nt.add_argument("--request", required=True)
+    nt.add_argument("--tree", required=True)
+    nt.add_argument("--out", required=True)
+    nt.add_argument("--deadline", type=float, required=True)
+    nt.add_argument("--head-sha", required=True)
+    nt.add_argument("--build-id", required=True)
+    nt.add_argument("--kani-build", required=True)
@@ -1640,0 +2006,2 @@ def main(argv: list[str]) -> int:
+    s.add_argument("--native")
+    s.add_argument("--kani-build")
@@ -1659,0 +2027,4 @@ def main(argv: list[str]) -> int:
+    pn = sub.add_parser("page-native")
+    pn.add_argument("summary")
+    pn.add_argument("offset", type=int)
+    pn.add_argument("count", type=int)
@@ -1674,0 +2046,16 @@ def main(argv: list[str]) -> int:
+    if a.cmd in ("prepare-kani", "run-native"):
+        try:
+            text = Path(a.request).read_text()
+            request = validate_request(json.loads(text))
+            if a.cmd == "prepare-kani":
+                info = prepare_kani(request, Path.cwd(), Path(a.tree).resolve(), a.pin)
+                Path(a.out).write_text(json.dumps(info, indent=2) + "\n")
+            else:
+                info = json.loads(Path(a.kani_build).read_text())
+                run_native(request, Path(a.tree).resolve(), Path(a.out).resolve(), a.deadline,
+                           {"head_sha": a.head_sha, "build_id": a.build_id, "tree": info["tree"],
+                            "request_sha256": hashlib.sha256(text.encode()).hexdigest()})
+        except (OSError, ValueError, subprocess.SubprocessError, KeyError) as exc:
+            print(f"REQUEST_INVALID: {exc}", file=sys.stderr)
+            return 2
+        return 0
@@ -1700 +2087 @@ def main(argv: list[str]) -> int:
-    if a.cmd == "page-summary":
+    if a.cmd in ("page-summary", "page-native"):
@@ -1702 +2089,2 @@ def main(argv: list[str]) -> int:
-            print(summary_page(json.loads(Path(a.summary).read_text()), a.offset, a.count), end="")
+            renderer = native_page if a.cmd == "page-native" else summary_page
+            print(renderer(json.loads(Path(a.summary).read_text()), a.offset, a.count), end="")
@@ -1723,0 +2112 @@ def main(argv: list[str]) -> int:
+            patch_bytes(request, Path.cwd())
@@ -1752 +2141,2 @@ def main(argv: list[str]) -> int:
-                            _read_optional(a.peaks), a.peaks is not None, _read_optional(a.inventory))
+                            _read_optional(a.peaks), a.peaks is not None, _read_optional(a.inventory),
+                            _read_optional(a.native), _read_optional(a.kani_build))
diff --git a/research/challenge-8/kani-k1/tools/test_gcb_native.py b/research/challenge-8/kani-k1/tools/test_gcb_native.py
new file mode 100644
index 0000000000..c297945ee7
--- /dev/null
+++ b/research/challenge-8/kani-k1/tools/test_gcb_native.py
@@ -0,0 +1,267 @@
+"""Offline shell service checks. All build/cloud commands are fake executables, never real proof tools."""
+import copy
+import json
+import os
+from pathlib import Path
+import shutil
+import subprocess
+import tempfile
+import unittest
+
+from test_kani_k1 import NATIVE_REQ, NATIVE_ENTRY, native_log, REQ, GOOD_LOG, TIME
+import kani_k1 as k
+
+TOOLS = Path(__file__).resolve().parent
+LANE = Path("research/challenge-8/kani-k1")
+
+
+class CloudNativeServiceTests(unittest.TestCase):
+    def packet(self, root, scenario="ok", invalid=None):
+        tools = root / LANE / "tools"; tools.mkdir(parents=True)
+        shutil.copy(TOOLS / "kani_k1.py", tools)
+        # Keep real cargo/rustup inaccessible even on a developer machine with ~/.cargo/bin.
+        shell = (TOOLS / "gcb-k1.sh").read_text()
+        self.assertIn('export PATH="$HOME/.cargo/bin:$PATH"', shell)
+        shell = shell.replace('export PATH="$HOME/.cargo/bin:$PATH"', 'export PATH="$K1_SERVICE_BIN:/usr/bin:/bin"')
+        (tools / "gcb-k1.sh").write_text(shell)
+        config = root / "tool_config"; config.mkdir()
+        (config / "kani-version.toml").write_text('commit = "' + "b" * 40 + '"\n')
+        request = copy.deepcopy(NATIVE_REQ)
+        request["request_id"] = "kani5116-kt1-service"
+        if invalid:
+            request.update(invalid)
+        (root / LANE / "RUN-REQUEST.json").write_text(json.dumps(request))
+        (root / "native-log.txt").write_text(native_log())
+        (root / "selected-log.txt").write_text(GOOD_LOG)
+        bin_dir = root / "bin"; bin_dir.mkdir()
+        command = r'''#!/usr/bin/python3
+import json, os, sys
+from pathlib import Path
+root=Path(os.environ["SERVICE_ROOT"])
+name=Path(sys.argv[0]).name; args=sys.argv[1:]
+with (root/"commands.jsonl").open("a") as f: f.write(json.dumps([name,*args])+"\n")
+scenario=os.environ["SERVICE_SCENARIO"]
+if name == "git":
+    tree=root/"kani_build"
+    if args[:1] == ["-C"]: args=args[2:]
+    if args[:1] == ["rev-parse"]:
+        print(("b" if "-C" in sys.argv else "a")*40)
+    elif args[:1] == ["write-tree"]: print("c"*40)
+    elif args[:1] == ["diff"]: print("new fixture | 1 +")
+    elif args[:1] == ["apply"] and scenario == "conflict": sys.exit(1)
+    elif args[:1] == ["checkout"]:
+        for path,text in {
+            "tests/kani/FunctionContracts/repro.rs":"fn fixture() {}",
+            "kani-dependencies":"",
+            "scripts/setup/ubuntu/install_deps.sh":"#!/bin/sh\nexit 0\n",
+            "scripts/kani":"#!/bin/sh\necho 'kani 0.68.0'\n",
+        }.items():
+            p=tree/path; p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);p.chmod(0o755)
+elif name == "cargo":
+    if args[:1] == ["build-dev"]:
+        if scenario == "build-failure": sys.exit(7)
+        for name in ("kani-driver","kani-compiler"):
+            for path in ("target/release/"+name,"target/kani/bin/"+name):
+                p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b"release");p.chmod(0o755)
+    elif args[:1] == ["build"]:
+        if scenario == "compiletest-build-failure": sys.exit(8)
+        p=Path("target/debug/compiletest");p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b"compiletest");p.chmod(0o755)
+    elif args[:1] == ["run"]:
+        text=(root/"native-log.txt").read_text()
+        if scenario == "panic": text += "thread 'main' panicked at runner.rs\n"
+        if scenario == "zero": text=text.replace("running 1 test","running 0 tests")
+        if scenario == "damaged": text=text.split("test result:")[0]
+        if scenario == "compiletest-run-build-failure": text="error: could not compile compiletest\n"
+        print(text)
+        p=Path(args[args.index("--build-base")+1])/"FunctionContracts/repro/repro"
+        p.parent.mkdir(parents=True,exist_ok=True)
+        p.with_suffix(".out").write_text("")
+        p.with_suffix(".err").write_text("other test output" if scenario=="foreign" else "error: expected `fn`\n")
+        sys.exit(1)
+sys.exit(0)
+'''
+        for name in ("git", "cargo", "rustup", "apt-get"):
+            p = bin_dir / name; p.write_text(command); p.chmod(0o755)
+        env = dict(os.environ, SERVICE_ROOT=str(root), SERVICE_SCENARIO=scenario, K1_SERVICE_BIN=str(bin_dir),
+                   K1_BRANCH="experiment/kani-k1-kani5116-20261110", K1_SHA="a" * 40, K1_BUILD_ID="service-build")
+        env["PATH"] = str(bin_dir) + ":/usr/bin:/bin"
+        return env, tools / "gcb-k1.sh"
+
+    def test_native_end_to_end_summary_staged_and_gate_after_upload(self):
+        with tempfile.TemporaryDirectory() as d:
+            root = Path(d); env, script = self.packet(root)
+            run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=30)
+            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
+            output = root / "k1-out"
+            summary = json.loads((output / "upload/summary/summary.json").read_text())
+            self.assertTrue(k.gate_ok(summary), run.stdout + run.stderr)
+            self.assertEqual((output / "gate.rc").read_text().strip(), "0")
+            commands = [json.loads(line) for line in (root / "commands.jsonl").read_text().splitlines()]
+            self.assertIn(["cargo", "build-dev", "--", "--release"], commands)
+            self.assertIn(["cargo", "build", "-p", "compiletest"], commands)
+            self.assertEqual(sum(row[:2] == ["cargo", "run"] for row in commands), 1)
+            self.assertFalse((output / "kani.log").exists())
+            yaml = (TOOLS.parent / "gcb/cloudbuild.yaml").read_text()
+            self.assertLess(yaml.index("id: upload"), yaml.index("id: gate"))
+            self.assertIn("gate.rc", yaml)
+
+    def test_service_failures_are_uploaded_but_gate_rejects(self):
+        for scenario in ("build-failure", "compiletest-build-failure", "compiletest-run-build-failure", "zero", "damaged", "panic", "foreign"):
+            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as d:
+                root = Path(d); env, script = self.packet(root, scenario)
+                run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=30)
+                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
+                output = root / "k1-out"
+                summary = json.loads((output / "upload/summary/summary.json").read_text())
+                self.assertFalse(k.gate_ok(summary), scenario)
+                self.assertNotEqual((output / "gate.rc").read_text().strip(), "0")
+
+    def test_invalid_patch_and_conflict_never_reach_build(self):
+        for scenario, spec in (("ok", {"path": "research/missing.patch", "sha256": "1" * 64}),
+                               ("ok", {"path": "research/../escape.patch", "sha256": "1" * 64}),
+                               ("ok", {"path": "research/test.patch", "sha256": "1" * 64}),
+                               ("ok", {"path": "research/link.patch", "sha256": k.hashlib.sha256(b"test patch").hexdigest()}),
+                               ("conflict", None)):
+            with self.subTest(scenario=scenario, spec=spec), tempfile.TemporaryDirectory() as d:
+                root = Path(d)
+                path = root / "research/test.patch"; path.parent.mkdir()
+                path.write_bytes(b"test patch")
+                (path.parent / "link.patch").symlink_to(path)
+                if spec is None:
+                    spec = {"path": "research/test.patch", "sha256": k.hashlib.sha256(path.read_bytes()).hexdigest()}
+                env, script = self.packet(root, scenario, {"kani_patch": spec})
+                run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=30)
+                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
+                summary = json.loads((root / "k1-out/upload/summary/summary.json").read_text())
+                self.assertEqual(summary["status"], "REQUEST_INVALID", run.stdout)
+                self.assertFalse(k.gate_ok(summary))
+                commands = [json.loads(line) for line in (root / "commands.jsonl").read_text().splitlines()]
+                self.assertFalse(any(row[0] in ("cargo", "rustup") for row in commands))
+
+    def test_bad_selectors_rejected_before_build(self):
+        for selectors in ([], [NATIVE_ENTRY, NATIVE_ENTRY], [{**NATIVE_ENTRY, "file": "missing.rs"}],
+                          [{**NATIVE_ENTRY, "suite": "unknown"}]):
+            with self.subTest(selectors=selectors), tempfile.TemporaryDirectory() as d:
+                root = Path(d); env, script = self.packet(root, invalid={"kani_tests": selectors})
+                run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=20)
+                self.assertEqual(run.returncode, 0, run.stderr)
+                summary = json.loads((root / "k1-out/upload/summary/summary.json").read_text())
+                self.assertEqual(summary["status"], "REQUEST_INVALID")
+                commands = [json.loads(line) for line in (root / "commands.jsonl").read_text().splitlines()]
+                self.assertFalse(any(row[0] in ("cargo", "rustup") for row in commands))
+
+    def test_old_python_routes_and_error_statuses_equal_base(self):
+        source = subprocess.run(["git", "show", "9b1758ab81:research/challenge-8/kani-k1/tools/kani_k1.py"],
+                                cwd=TOOLS, capture_output=True, text=True, check=True).stdout
+        baseline = {"__name__": "base_tooling"}
+        exec(compile(source, "base_tooling", "exec"), baseline)
+        requests = [REQ, {**REQ, "kind": "diagnostic"},
+                    {**REQ, "kind": "resource", "runner": k.RESOURCE_RUNNER},
+                    {**REQ, "kind": "partition", "runner": k.STANDARD_RUNNER, "harnesses": [], "worker_index": 1, "worker_total": 2},
+                    {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harnesses": []},
+                    {**REQ, "kind": "inventory", "runner": k.STANDARD_RUNNER, "harnesses": [], "inventory": True}]
+        for request in requests:
+            for bad in (request, {**request, "harness_timeout_minutes": 0}, {**request, "runner": "invalid"}, {**request, "controls": "bad"}):
+                def validate(function):
+                    try:
+                        return function(copy.deepcopy(bad))
+                    except ValueError as exc:
+                        return str(exc)
+                self.assertEqual(validate(k.validate_request), validate(baseline["validate_request"]))
+            self.assertEqual(k.kani_args(request), baseline["kani_args"](request))
+            self.assertEqual(k.verification_mode(request["kind"]), baseline["verification_mode"](request["kind"]))
+            for log, code, outcome in ((GOOD_LOG, 1, "success"), ("", 1, "failure"), (None, None, "deps-failure"), (GOOD_LOG, 124, "success")):
+                args = (json.dumps(request), log, TIME, code, "a" * 40, "b" * 40)
+                self.assertEqual(k.summarize(*args, build_outcome=outcome), baseline["summarize"](*args, build_outcome=outcome))
+
+    def test_service_deadline_skips_native_verification(self):
+        with tempfile.TemporaryDirectory() as d:
+            root = Path(d); env, script = self.packet(root)
+            output = root / "k1-out"; output.mkdir()
+            for name in ("valid", "build.ok"):
+                (output / name).touch()
+            (output / "kani-args.txt").write_text("")
+            (output / "start").write_text("0")
+            run = subprocess.run(["bash", str(script), "verify"], cwd=root, env=env, capture_output=True, text=True, timeout=10)
+            self.assertEqual(run.returncode, 0, run.stderr)
+            self.assertTrue((output / "verify-skipped").exists())
+            self.assertFalse((root / "commands.jsonl").exists())
+
+
+class DispatchServiceTests(unittest.TestCase):
+    def test_native_reservation_and_stage_cap_before_submit(self):
+        for stage_minutes, expected_code in ((0, 0), (1, 2)):
+            with self.subTest(stage_minutes=stage_minutes), tempfile.TemporaryDirectory() as d:
+                root = Path(d); tools = root / "tools"; tools.mkdir()
+                for name in ("k1g.sh", "kani_k1.py"):
+                    shutil.copy(TOOLS / name, tools)
+                (root / "request.json").write_text(json.dumps(NATIVE_REQ))
+                (root / "cloudbuild.yaml").write_text("steps: []\n")
+                key = root / "fake-key"; key.touch()  # empty fake file, never reads credentials
+                bindir = root / "bin"; bindir.mkdir()
+                stub = r'''#!/usr/bin/python3
+import json,os,sys
+from pathlib import Path
+root=Path(os.environ["SERVICE_ROOT"]);args=sys.argv[1:];name=Path(sys.argv[0]).name
+with (root/"calls").open("a") as f: f.write(json.dumps([name,*args])+"\n")
+if name=="git":
+    if args[0]=="rev-parse":print("a"*40)
+    elif args[0]=="show":print((root/("request.json" if args[1].endswith("RUN-REQUEST.json") else "cloudbuild.yaml")).read_text())
+elif "auth" in args: print("k1-dispatcher@smallsort-k1.iam.gserviceaccount.com")
+elif "submit" in args:
+    (root/"submitted.json").write_text(json.dumps(args));print("11111111-1111-1111-1111-111111111111")
+elif "list" in args and "--format=json" in args:
+    scoped=any(a.startswith("--filter=substitutions._BRANCH=") for a in args)
+    minutes=int(os.environ["STAGE_MINUTES"])
+    print(json.dumps([{"id":"prior", "timeout":str(minutes*60)+"s", "options":{"pool":{"name":"projects/smallsort-k1/locations/us-central1/workerPools/k1-standard4"}}}] if scoped and minutes else []))
+'''
+                for name in ("git", "gcloud"):
+                    path = bindir / name; path.write_text(stub); path.chmod(0o755)
+                env = dict(os.environ, SERVICE_ROOT=str(root), STAGE_MINUTES=str(stage_minutes),
+                           K1_GCP_KEY=str(key), K1_GCLOUD_CONFIG=str(root / "gconfig"), PATH=str(bindir) + ":/usr/bin:/bin")
+                run = subprocess.run(["bash", str(tools / "k1g.sh"), "dispatch", "experiment/kani-k1-kani5116-20261110"],
+                                     cwd=root, env=env, capture_output=True, text=True, timeout=10)
+                self.assertEqual(run.returncode, expected_code, run.stdout + run.stderr)
+                submitted = root / "submitted.json"
+                if expected_code == 0:
+                    self.assertIn("--timeout=59m", json.loads(submitted.read_text()))
+                    self.assertIn("0.7965", run.stderr)
+                else:
+                    self.assertFalse(submitted.exists())
+                    self.assertIn("$0.80", run.stderr)
+
+    def test_summary_fetch_never_downloads_raw_logs(self):
+        with tempfile.TemporaryDirectory() as d:
+            root = Path(d); tools = root / "tools"; tools.mkdir()
+            for name in ("k1g.sh", "kani_k1.py"):
+                shutil.copy(TOOLS / name, tools)
+            key = root / "fake-key"; key.touch()
+            bindir = root / "bin"; bindir.mkdir()
+            stub = r'''#!/usr/bin/python3
+import json,os,sys
+from pathlib import Path
+args=sys.argv[1:];root=Path(os.environ["SERVICE_ROOT"])
+if "auth" in args:print("k1-dispatcher@smallsort-k1.iam.gserviceaccount.com")
+elif "describe" in args: print(json.dumps({"status":"SUCCESS"}))
+elif "ls" in args:
+    for rel in ("summary/summary.json","summary/summary.md","log/kani.log","log/time.txt","log/native-0.log"):
+        print("gs://smallsort-k1-k1-runs/runs/11111111-1111-1111-1111-111111111111/"+rel)
+elif "cp" in args:
+    url=args[-2]
+    with (root/"downloads").open("a") as f:f.write(url+"\n")
+    Path(args[-1]).write_text("{}" if url.endswith(".json") else "bounded summary\n")
+'''
+            path = bindir / "gcloud"; path.write_text(stub); path.chmod(0o755)
+            env = dict(os.environ, SERVICE_ROOT=str(root), K1_GCP_KEY=str(key), K1_GCLOUD_CONFIG=str(root / "gconfig"),
+                       K1_CACHE=str(root / "cache"), PATH=str(bindir) + ":/usr/bin:/bin")
+            run = subprocess.run(["bash", str(tools / "k1g.sh"), "summary", "11111111-1111-1111-1111-111111111111"],
+                                 cwd=root, env=env, capture_output=True, text=True, timeout=10)
+            self.assertEqual(run.returncode, 0, run.stderr)
+            self.assertEqual(run.stdout, "bounded summary\n")
+            downloaded = (root / "downloads").read_text().splitlines()
+            self.assertEqual(len(downloaded), 2)
+            self.assertTrue(all("/summary/summary." in url for url in downloaded))
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/research/challenge-8/kani-k1/tools/test_kani_k1.py b/research/challenge-8/kani-k1/tools/test_kani_k1.py
index 6991958e53..71269179e7 100644
--- a/research/challenge-8/kani-k1/tools/test_kani_k1.py
+++ b/research/challenge-8/kani-k1/tools/test_kani_k1.py
@@ -1229,0 +1230,267 @@ class CliTests(unittest.TestCase):
+NATIVE_ENTRY = {"suite": "kani", "mode": "kani", "file": "FunctionContracts/repro.rs",
+                "expect": "fail", "diagnostic": "expected `fn`", "require_success": True}
+NATIVE_REQ = {**REQ, "kind": "kani-tests", "runner": k.STANDARD_RUNNER, "harnesses": [],
+              "harness_timeout_minutes": 29, "test_timeout_seconds": 180, "kani_tests": [NATIVE_ENTRY]}
+
+
+def native_log(entry=NATIVE_ENTRY, result="FAILED"):
+    name = k.native_name(entry)
+    failure = (f"\nfailures:\n\n---- {name} stdout ----\n"
+               "error: test failed: expected verification success, got failure\n"
+               "status: exit status: 1\n"
+               f'command: "kani" "tests/{entry["suite"]}/{entry["file"]}"\n'
+               "stderr:\nerror: expected `fn`\n\nfailures:\n    " + name + "\n") if result == "FAILED" else ""
+    return (f"running 1 test\ntest {name} ... {result}\n" + failure +
+            f"test result: {'FAILED' if result == 'FAILED' else 'ok'}. "
+            f"{0 if result == 'FAILED' else 1} passed; {1 if result == 'FAILED' else 0} failed; "
+            "0 ignored; 0 measured; 999 filtered out; finished in 0.12s\n")
+
+
+class NativeTests(unittest.TestCase):
+    def test_typed_manifest_and_limits(self):
+        self.assertEqual(k.validate_request(copy.deepcopy(NATIVE_REQ)), NATIVE_REQ)
+        self.assertEqual(k.kani_args(NATIVE_REQ), [])
+        self.assertEqual(k.verification_mode("kani-tests"), "kani-tests")
+        malformed = [dict(NATIVE_REQ, kani_tests=[]), dict(NATIVE_REQ, kani_tests=[NATIVE_ENTRY, NATIVE_ENTRY]),
+                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "suite": "unknown"}]),
+                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "file": "../x.rs"}]),
+                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "file": ""}]),
+                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "diagnostic": "unrelated"}]),
+                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "require_success": False}]),
+                     dict(NATIVE_REQ, test_timeout_seconds=0), dict(NATIVE_REQ, test_timeout_seconds=True),
+                     dict(NATIVE_REQ, harness_timeout_minutes=30), dict(NATIVE_REQ, controls=False),
+                     dict(NATIVE_REQ, runner="ubuntu-latest"), dict(REQ, kani_tests=[NATIVE_ENTRY])]
+        for request in malformed:
+            with self.subTest(request=request), self.assertRaises(k.RequestError):
+                k.validate_request(request)
+        with self.assertRaises(k.RequestError):
+            k.validate_request(NATIVE_REQ, 28)
+        expected = {"suite": "ui", "mode": "expected", "file": "error.rs", "expect": "pass",
+                    "require_success": False, "diagnostic": "specific error"}
+        k.validate_native_manifest([expected])
+        positive = {key: value for key, value in {**expected, "require_success": True}.items() if key != "diagnostic"}
+        k.validate_native_manifest([positive])
+        for bad in ({key: value for key, value in expected.items() if key != "diagnostic"},
+                    {**expected, "require_success": True}, {**expected, "mode": "ui"}):
+            with self.assertRaises(k.RequestError):
+                k.validate_native_manifest([bad])
+
+    def test_exact_args_and_expected_success_policy(self):
+        argv = k.native_argv(NATIVE_ENTRY, 180, Path("/tmp/out"))
+        self.assertEqual(argv[:6], ["cargo", "run", "-p", "compiletest", "--", "--suite"])
+        self.assertEqual(argv[argv.index("--exact") + 1], "[kani] kani/FunctionContracts/repro.rs")
+        self.assertNotIn("--require-success", argv)
+        pos = {**NATIVE_ENTRY, "mode": "expected", "suite": "expected", "expect": "pass"}
+        self.assertIn("--require-success", k.native_argv(pos, 180, Path("/tmp/out")))
+        self.assertNotIn("--require-success", k.native_argv({**pos, "require_success": False}, 180, Path("/tmp/out")))
+
+    def test_completed_native_failure_only_and_own_diagnostic(self):
+        own = "error: expected `fn`\n --> tests/kani/FunctionContracts/repro.rs:4:1\n"
+        good = k.parse_native_test(NATIVE_ENTRY, native_log(), 1, own)
+        self.assertEqual(good["status"], "EXPECTED_REPRO_FAILURE", good)
+        self.assertEqual(good["time_s"], 0.12)
+        cases = [("error: could not compile `compiletest`\n" + own, 1, own, False),
+                 (native_log(), 124, own, False), (native_log(), -9, own, False),
+                 (native_log(), 1, own, True), (native_log() + "thread 'main' panicked at x\n", 1, own, False),
+                 (native_log(), 1, "other error", False), # matching diagnostic only in console/another test
+                 (native_log(), 1, None, False), (native_log(), 1, own + "signal: 9\n", False),
+                 (native_log(), 1, own + "thread 'rustc' panicked at x\n", False),
+                 (native_log().replace("status: exit status: 1", "status: signal: 9"), 1, own, False),
+                 (native_log().replace("expected verification success, got failure", "unrelated panic"), 1, own, False),
+                 (native_log().replace('"tests/kani/FunctionContracts/repro.rs"', '"other.rs"'), 1, own, False),
+                 (native_log(), 0, own, False), (native_log().replace("running 1 test", "running 0 tests"), 1, own, False),
+                 (native_log().replace(k.native_name(NATIVE_ENTRY), "[kani] kani/other.rs"), 1, own, False),
+                 (native_log() + native_log(), 1, own, False),
+                 (native_log().split("test result:")[0], 1, own, False),
+                 (native_log().replace("0 passed; 1 failed", "1 passed; 0 failed"), 1, own, False),
+                 (native_log().replace("0 ignored", "1 ignored"), 1, own, False),
+                 (native_log().replace("... FAILED", "... ignored"), 1, own, False),
+                 (native_log().replace("finished in 0.12s", "finished in damaged"), 1, own, False)]
+        for text, code, output, timeout in cases:
+            with self.subTest(text=text[:80], code=code, output=output, timeout=timeout):
+                self.assertEqual(k.parse_native_test(NATIVE_ENTRY, text, code, output, timeout)["status"], "ERROR")
+        passed = {**NATIVE_ENTRY, "expect": "pass"}; passed.pop("diagnostic")
+        self.assertEqual(k.parse_native_test(passed, native_log(passed, "ok"), 0, "SUCCESS FAILED")["status"], "PASS")
+        self.assertEqual(k.parse_native_test(passed, "VERIFICATION:- SUCCESSFUL", 0, "")["status"], "ERROR")
+        self.assertEqual(k.parse_native_test(passed, native_log(passed, "ok"), 1, "")["status"], "ERROR")
+
+    def test_negative_expected_native_pass_needs_own_diagnostic(self):
+        entry = {"suite": "ui", "mode": "expected", "file": "error.rs", "expect": "pass",
+                 "require_success": False, "diagnostic": "specific error"}
+        self.assertEqual(k.parse_native_test(entry, native_log(entry, "ok"), 0, "specific error")["status"], "PASS")
+        self.assertEqual(k.parse_native_test(entry, native_log(entry, "ok") + "specific error", 0, "other")["status"], "ERROR")
+
+    def test_patch_path_hash_and_fresh_pin_tree(self):
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp); tree = root / "kani"; tree.mkdir()
+            def git(*args):
+                return subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True, check=True).stdout.strip()
+            git("init", "-q")
+            (tree / "base").write_text("base\n")
+            git("add", "base")
+            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
+            pin = git("rev-parse", "HEAD")
+            research = root / "research"; research.mkdir()
+            patch_path = research / "tests.patch"
+            contents = ("diff --git a/tests/kani/FunctionContracts/repro.rs b/tests/kani/FunctionContracts/repro.rs\n"
+                        "new file mode 100644\n--- /dev/null\n+++ b/tests/kani/FunctionContracts/repro.rs\n"
+                        "@@ -0,0 +1 @@\n+fn test() {}\n")
+            patch_path.write_text(contents)
+            request = {**NATIVE_REQ, "kani_patch": {"path": "research/tests.patch", "sha256": hashlib.sha256(contents.encode()).hexdigest()}}
+            k.validate_request(request)
+            for path in ("../tests.patch", "/absolute.patch", "research/../tests.patch", "research//tests.patch"):
+                with self.assertRaises(k.RequestError):
+                    k.validate_request({**request, "kani_patch": {**request["kani_patch"], "path": path}})
+            (research / "link.patch").symlink_to(patch_path)
+            (root / "linked").symlink_to(research)
+            for bad in ({**request["kani_patch"], "path": "research/missing.patch"},
+                        {**request["kani_patch"], "path": "research/link.patch"},
+                        {**request["kani_patch"], "path": "linked/tests.patch"},
+                        {**request["kani_patch"], "sha256": "0" * 64}):
+                with self.assertRaises(k.RequestError):
+                    k.patch_bytes({**request, "kani_patch": bad}, root)
+            with self.assertRaises(k.RequestError):
+                k.prepare_kani(request, root, tree, "0" * 40)
+            info = k.prepare_kani(request, root, tree, pin)
+            self.assertNotEqual(info["tree"], git("rev-parse", "HEAD^{tree}"))
+            self.assertEqual(git("rev-parse", "HEAD"), pin)
+            self.assertIn("repro.rs", info["diffstat"])
+            with self.assertRaises(k.RequestError): # already applied/dirty is forbidden
+                k.prepare_kani(request, root, tree, pin)
+            git("reset", "--hard", "HEAD")
+            patch_path.write_text(contents.replace("/repro.rs", "/absent.rs").replace("+fn test() {}", "+conflict"))
+            request["kani_patch"]["sha256"] = hashlib.sha256(patch_path.read_bytes()).hexdigest()
+            with self.assertRaises(k.RequestError): # selector missing after successful apply
+                k.prepare_kani(request, root, tree, pin)
+            git("reset", "--hard", "HEAD")
+            patch_path.write_text("diff --git a/base b/base\n--- a/base\n+++ b/base\n@@ -1 +1 @@\n-missing context\n+replacement\n")
+            request["kani_patch"]["sha256"] = hashlib.sha256(patch_path.read_bytes()).hexdigest()
+            with self.assertRaises(k.RequestError):
+                k.prepare_kani(request, root, tree, pin)
+            self.assertEqual(git("status", "--porcelain"), "")
+
+    def summary(self):
+        text = json.dumps(NATIVE_REQ)
+        info = {"pin": "b" * 40, "patch": None, "tree": "c" * 40, "version": "kani 0.68.0",
+                "diffstat": "", "kani_build_s": 12, "compiletest_build_s": 2}
+        row = k.parse_native_test(NATIVE_ENTRY, native_log(), 1, "error: expected `fn`\n")
+        row.update(argv=k.native_argv(NATIVE_ENTRY, 180, Path("/tmp/out/native-0")), cwd="/workspace/src/kani_build",
+                   env={"RUST_TEST_THREADS": "1"}, wall_s=1)
+        native = {"schema": k.NATIVE_SCHEMA, "head_sha": "a" * 40, "build_id": "build-1",
+                  "request_sha256": hashlib.sha256(text.encode()).hexdigest(), "tree": info["tree"], "complete": True,
+                  "binaries": {"kani_profile": "release", "compiletest_profile": "dev", "paths": {
+                      "kani": {"invoked": "/kani/scripts/kani"}, "compiletest": {"invoked": "/kani/target/debug/compiletest"},
+                      **{name: {"invoked": "/kani/target/kani/bin/" + name, "release": "/kani/target/release/" + name,
+                                "resolved": "/kani/target/release/" + name, "sha256": "e" * 64}
+                         for name in ("kani-driver", "kani-compiler")}}}, "tests": [row]}
+        def summarize(report=native, build=info, outcome="success", code=0):
+            return k.summarize(text, None, None, code, "a" * 40, "b" * 40, run={"id": "build-1"},
+                               build_outcome=outcome, native_text=json.dumps(report), kani_build_text=json.dumps(build))
+        return native, info, summarize
+
+    def test_structured_report_gate_and_binding(self):
+        native, info, summarize = self.summary()
+        summary = summarize()
+        self.assertTrue(k.gate_ok(summary), summary)
+        self.assertIsNone(summary["kani_exit_code"])
+        self.assertEqual(summary["native_runner_exit_code"], 0)
+        self.assertIn("EXPECTED_REPRO_FAILURE", k.render_md(summary))
+        self.assertIn("EXPECTED_REPRO_FAILURE", k.summary_page(summary, 0, 20))
+        bad_reports = [None, {}, {**native, "head_sha": "d" * 40}, {**native, "build_id": "other"},
+                       {**native, "request_sha256": "f" * 64}, {**native, "tree": "d" * 40},
+                       {**native, "complete": False}, {**native, "tests": []},
+                       {**native, "tests": native["tests"] * 2}, {**native, "binaries": {}},
+                       {**native, "tests": [{**native["tests"][0], "status": "ERROR"}]},
+                       {**native, "tests": [{**native["tests"][0], "argv": ["bad"]}]},
+                       {**native, "tests": [{**native["tests"][0], "env": {"RUST_TEST_THREADS": "2"}}]},
+                       {**native, "tests": [{**native["tests"][0], "exit_code": 0}]},
+                       {**native, "tests": [{**native["tests"][0], "time_s": None}]},
+                       {**native, "tests": [{**native["tests"][0], "diagnostic": None}]},
+                       {**native, "tests": [{**native["tests"][0], "errors": ["timeout"]}]}]
+        for bad in bad_reports:
+            self.assertFalse(k.gate_ok(summarize(bad)), bad)
+        for bad in (None, {}, {**info, "pin": "d" * 40}, {**info, "version": ""}, {**info, "tree": "bad"}):
+            self.assertFalse(k.gate_ok(summarize(build=bad)), bad)
+        self.assertFalse(k.gate_ok(summarize(outcome="failure")))
+        for code in (None, 1, 124, -9):
+            self.assertFalse(k.gate_ok(summarize(code=code)))
+
+    def test_native_pagination_is_bounded_and_explicit(self):
+        native, info, summarize = self.summary()
+        summary = summarize()
+        page = json.loads(k.native_page(summary, 0, 1))
+        self.assertEqual(page["count"], 1)
+        self.assertIsNone(page["next_offset"])
+        self.assertIn("argv", page["tests"][0])
+        self.assertIn("binaries", page)
+        summary["native"]["tests"] *= 5
+        for row in summary["native"]["tests"]:
+            row["extra"] = "x" * 3000
+        text = k.native_page(summary, 0, 4)
+        self.assertLessEqual(len(text.encode()), 12000)
+        page = json.loads(text)
+        self.assertEqual(page["next_offset"], page["count"])
+        self.assertLess(page["count"], 4)
+        with self.assertRaises(ValueError):
+            k.native_page(summary, 0, 5)
+
+    def test_wall_timeout_and_deadline_never_invoke_tools_late(self):
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp); log = root / "test.log"
+            code, timeout, _ = k.bounded_command([sys.executable, "-c", "import time; time.sleep(10)"], root, log, 0.05)
+            self.assertTrue(timeout)
+            self.assertEqual(code, -9)
+            with patch.object(k.subprocess, "Popen") as popen:
+                self.assertEqual(k.bounded_command(["never-run"], root, log, -1), (None, True, 0.0))
+                popen.assert_not_called()
+
+    def test_runner_writes_partial_report_and_no_cross_test_output(self):
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp)
+            def command(argv, tree, log, seconds, env):
+                self.assertEqual(env["RUST_TEST_THREADS"], "1")
+                self.assertLessEqual(seconds, 210)
+                log.write_text(native_log())
+                base = Path(argv[argv.index("--build-base") + 1]) / "FunctionContracts/repro/repro"
+                base.parent.mkdir(parents=True)
+                base.with_suffix(".out").write_text("")
+                base.with_suffix(".err").write_text("error: expected `fn`\n")
+                return 1, False, 0.2
+            with patch.object(k, "native_binary_identity", return_value={"kani_profile": "release"}), patch.object(k, "bounded_command", side_effect=command):
+                k.run_native(NATIVE_REQ, root, root / "out", k.time.time() + 100, {"tree": "a" * 40})
+            report = json.loads((root / "out/native.json").read_text())
+            self.assertTrue(report["complete"])
+            self.assertEqual(report["tests"][0]["status"], "EXPECTED_REPRO_FAILURE")
+            with patch.object(k, "native_binary_identity", return_value={}), patch.object(k, "bounded_command", side_effect=OSError("exec failed")):
+                with self.assertRaises(OSError):
+                    k.run_native(NATIVE_REQ, root, root / "error", k.time.time() + 100, {})
+            self.assertFalse(json.loads((root / "error/native.json").read_text())["complete"])
+
+    def test_patch_supported_diagnostic_without_changing_old_args(self):
+        req = req_with(kind="diagnostic", runner=k.STANDARD_RUNNER)
+        patched = {**req, "kani_patch": {"path": "research/p.patch", "sha256": "1" * 64}}
+        self.assertEqual(k.kani_args(k.validate_request(patched)), k.kani_args(k.validate_request(req)))
+        self.assertEqual(k.verification_mode(patched["kind"]), "selected")
+        self.assertFalse(k.gate_ok(k.summarize(json.dumps(patched), GOOD_LOG, TIME, 1, "a" * 40, "b" * 40, build_outcome="success")))
+        info = {"pin": "b" * 40, "patch": patched["kani_patch"], "tree": "c" * 40, "version": "kani 0.68.0"}
+        summary = k.summarize(json.dumps(patched), GOOD_LOG, TIME, 1, "a" * 40, "b" * 40,
+                              build_outcome="success", kani_build_text=json.dumps(info))
+        self.assertTrue(k.gate_ok(summary), summary)
+
+    def test_release_binary_paths_must_match_and_debug_driver_is_rejected(self):
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp)
+            for relative in ("target/release/kani-driver", "target/release/kani-compiler", "target/kani/bin/kani-driver",
+                             "target/kani/bin/kani-compiler", "scripts/kani", "target/debug/compiletest"):
+                p = root / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b"fixture")
+            info = k.native_binary_identity(root)
+            self.assertEqual(info["kani_profile"], "release")
+            (root / "target/debug/kani-driver").write_bytes(b"debug")
+            with self.assertRaises(k.RequestError):
+                k.native_binary_identity(root)
+            (root / "target/debug/kani-driver").unlink()
+            (root / "target/kani/bin/kani-compiler").write_bytes(b"different")
+            with self.assertRaises(k.RequestError):
+                k.native_binary_identity(root)
+
+
```
