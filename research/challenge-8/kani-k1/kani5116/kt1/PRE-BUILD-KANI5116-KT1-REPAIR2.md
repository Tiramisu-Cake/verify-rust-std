# PRE-BUILD — KANI5116 KT1 repair 2

Candidate: the full SHA supplied in PRE-BUILD REVIEW. No dispatch before a fresh exact-candidate coordinator GO.
Branch `experiment/kani-k1-kani5116-20261110`; owner `k1-merge`; slug `kani5116`; stage `kani5116-kt1`.
Coordinator explicitly reopened KT1 for tooling-only repair 2 after the prior closeout; no new phase or mission is inferred.
Original T0 remains **2026-11-10T20:23:42Z**; main deadline **2026-11-11T01:23:42Z**; closeout **01:53:42Z**. No clock reset.

## Evidence and repair scope

Latest completed build `490e5e95-27ef-45a3-a4bb-7da768cdb8cc` used `da417533949ff982103a53ed8385784e88d7c80e`: four native PASS, repro native FAILED / exit 1 / gate ERROR because the required own-output diagnostic was not confirmed.
`check-tooling` and pin/patch/applied-tree identities passed. Kani built in 276 s, compiletest in 18 s. Actual alternative repro error text was not exported, so no causal diagnosis of that failure is claimed.
The two completed own builds cost **$0.2295** total, zero reserved. Existing results remain in RESULT; no historical evidence is rewritten or reconstructed.
Only tooling observability changes: `tools/kani_k1.py`, `tools/test_kani_k1.py`, `tools/test_gcb_native.py`. Request metadata/budget and PRE-BUILD/RESULT are data changes.
No fixture, selector, expected diagnostic, test timeout, Kani pin, toolchain, applied tree, gate policy, Kani production macro, library, cloudbuild configuration or build command changes.

## Verified source-to-diagnostic path

Read only the authorized Kani checkout at `f046b70644e113be0df9c22c2e6ea44a65a57566`.
`tools/compiletest/src/runtest.rs:88` launches the child with stdout/stderr pipes; `dump_output` at line 154 writes those child streams verbatim to `.out` / `.err`.
`tools/compiletest/src/common.rs:179` and `output_base_name` derive `BUILD_BASE/relative_dir/stem/stem.out` and `.err`.
`ProcRes::fatal` at `runtest.rs:690` prints a failure block on compiletest stdout, but calls `json::extract_rendered` separately on the child streams. Therefore the console display and raw child files can differ; no normalization is added in this repair.
The gate still receives **raw Kani .out, newline, raw Kani .err**, decoded as UTF-8 with replacement, and searches these only for the required diagnostic. Compiletest console text and excerpts grant no diagnostic credit.
Native running/name/count/summary/exit/timeout/panic checks still see both compiletest streams; the normal completed-failure block requirement is unchanged.
AST comparison confirms `parse_native_test` is identical to the previous packet. All existing no-patch-kind tests and native negative/error paths remain included.

## New bounded structured fields

Each test with native `FAILED` **or** `expect: fail` gets `output_sources`, `diagnostic_provenance`, and `output_excerpt` in its native row, including an unexpectedly successful expect-fail test.
The runner captures compiletest stdout and stderr into distinct private files; only structured evidence is read through the already permitted `k1g.sh summary/native` interface.
`output_sources` has four distinct entries: `compiletest_stdout`, `compiletest_stderr`, `kani_stdout` (.out), `kani_stderr` (.err).
Each entry records its exact path, availability, raw-byte size and SHA-256, whether it supplies gate diagnostics, whether the required substring is present, and whether the exact expected-fn compiler-error line is present.
`diagnostic_provenance` records the raw-file order/policy and the first matching child source, or null. It never selects compiletest stdout/stderr as a gate source.
`output_excerpt` is explicitly **diagnostic_only**, aggregate **<=60 source lines and <=4096 bytes as indented JSON** per test, stricter than the requested 8 KiB ceiling.
Selection gives each nonempty stream an early error line and a tail line first, then more error/tail context; records retain source and original 1-based line number and are returned in original order per source.
Oversized individual lines use an error-centred window (or line start), with `start_char`/`clipped` flags. JSON escaping and UTF-8 are included in the byte bound. Source line counts, selected count and omitted count make omissions explicit.
Only bounded selected source lines enter summary fields; no separate raw-output upload/download is added. Passed positive tests retain their existing row shape.
The fields survive summary upload and bounded `k1g.sh native` paging, including UNVALIDATED_DIAGNOSTIC_ONLY pages when the overall artifact is rejected. Excerpt contents cannot change gate credit.

## Unchanged calibration packet and budget

Request: `kani5116-kt1-repair2-20261110-03`. The same five typed selectors and `test_timeout_seconds: 180` remain byte-for-byte equivalent to the previous request; `manifest.json` and test-only patch bytes are unchanged.
Pin: `f046b70644e113be0df9c22c2e6ea44a65a57566`; nightly-2026-10-23.
Patch SHA-256: `46c68dfd5861ebd008c32d7580caa15cee9ac9b185dec960caf57d3d342f696f`; expected applied tree: `a3822bcbbd45a864b364fc0c9fc6416cdf75da25`.
Remaining stage cap: $0.80 - $0.2295 = **$0.5705**. At the existing $0.0135/min rate, the largest whole-minute paid timeout fitting this balance is **42 minutes**.
Request whole-job field is **12 minutes**, plus the unchanged **30-minute overhead** gives **42 minutes** / **$0.5670 reserve**. Used + proposed reserve = **$0.7965 <= $0.80**, with $0.0035 rounding margin.
Existing runner verify deadline becomes validation start + **36 minutes**, leaving six minutes for summary/upload. Per-test outer timeout remains 210 seconds, inner compiletest child timeout 180 seconds, one Rust test thread.
Fresh source build, no Kani cache, same documented release Kani command and dev-profile compiletest. Dispatcher rechecks both stage and project ledgers at submit time.

## Validation

- Full Python tooling suite: **109 tests PASS**. After the final clipping/provenance corrections, all **6 NativeOutputEvidenceTests PASS** again.
- Added: split stdout/stderr with preserved exit; exact source paths/byte hashes and missing/empty files; raw JSON child output versus rendered console; missing-child-file matches do not become selected gate sources; error/tail selection; UTF-8/control/very long lines; 60-line/4-KiB limits and explicit clipping/omission; false-positive console/foreign diagnostics; FAILED positive and successful expect-fail capture; unchanged positive PASS shape; unchanged true own-stderr credit; 12-KiB structured paging and rejected-artifact diagnostic-only paging.
- Offline shell service checks verify excerpts survive staged summary upload, distinct stderr survives capture, and a console-only matching diagnostic still leaves gate false.
- Dispatcher service checks accept the new 42-minute reserve with 17 finished billed minutes ($0.2295) and reject the same reserve with 18 billed minutes ($0.2430); old 59-minute cases remain tested.
- Fixture/manifest/applied-tree files, five typed selectors, patch digest, pin and `parse_native_test` identity checks: PASS. `bash -n` and `git diff --check`: PASS.
- No local cargo/rustc/Kani/CBMC invocation, no subagents, no competing branch or PR code, no credentials/raw logs/archive reads, and no build dispatch during preparation.

## After new GO

Dispatch this exact pushed candidate via `k1g.sh`, then `watch BUILD` and end the turn. On notification read bounded summary/native pages following returned next_offset, run check-tooling against the approved candidate, price only own build IDs, and update RESULT (<=40 lines).
Inspect the repro's four source records/excerpt before assigning a cause. Do not grant expected-failure credit from excerpt or console text. KT1 remains open and unaccepted pending calibration.

## Tooling blob SHA-256

```text
60af9d2e9f2d704ed66e6201cfc990662e000d860a230967ab64ec0e20801897  research/challenge-8/kani-k1/tools/gcb-k1.sh
5d93fd5cd92e9a905f10090265b2071e42e0a3beb19a62bf36a18836ce70234a  research/challenge-8/kani-k1/tools/k1g.sh
c199cace580a89f5ee7113aafe2d6757bf23c698d873a0b14589d9f7908a43b9  research/challenge-8/kani-k1/tools/kani_k1.py
dd0311336fda33521d8fa2540dab11a45125a9452c8adde2cd1778ddc1dc9468  research/challenge-8/kani-k1/tools/test_gcb_native.py
e1fdd3a7e342a694dd8dfe0da4cd646d39255871afb9139a5823fe78685a95fe  research/challenge-8/kani-k1/tools/test_kani_k1.py
```

## Repair 2 diff from prior closeout 5d2d2fb3d73003fe70e85373ccf2f13841e3a0c3

```diff
diff --git a/research/challenge-8/kani-k1/tools/kani_k1.py b/research/challenge-8/kani-k1/tools/kani_k1.py
index 06bd53d2fd..47926f6b93 100755
--- a/research/challenge-8/kani-k1/tools/kani_k1.py
+++ b/research/challenge-8/kani-k1/tools/kani_k1.py
@@ -28,0 +29 @@ import time
+from contextlib import nullcontext
@@ -261,0 +263,66 @@ NATIVE_ROW_RE = re.compile(r"^test (\[[^\n]+) \.\.\. (ok|FAILED|ignored)(?:\s+<[
+NATIVE_EXCERPT_LINES = 60
+NATIVE_EXCERPT_BYTES = 4096  # whole excerpt as indented JSON, below the coordinator's 8 KiB bound
+NATIVE_OUTPUT_SOURCES = ("compiletest_stdout", "compiletest_stderr", "kani_stdout", "kani_stderr")
+
+
+def native_output_sources(paths: dict[str, Path], required: str | None) -> tuple[dict[str, str | None], dict[str, Any]]:
+    """Keep raw child .out/.err distinct from compiletest's potentially rendered failure display."""
+    texts: dict[str, str | None] = {}
+    metadata = {}
+    for source in NATIVE_OUTPUT_SOURCES:
+        path = paths[source]
+        raw = path.read_bytes() if path.is_file() else None
+        text = raw.decode(errors="replace") if raw is not None else None
+        texts[source] = text
+        metadata[source] = {"path": str(path), "available": raw is not None,
+                            "bytes": len(raw) if raw is not None else None,
+                            "sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None,
+                            "used_for_gate_diagnostic": source in ("kani_stdout", "kani_stderr"),
+                            "required_substring_found": required in text if required and text is not None else None,
+                            "expected_fn_error_line_found": bool(re.search(r"^error: expected `fn`\s*$", text, re.M)) if text is not None else None}
+    return texts, metadata
+
+
+def native_output_excerpt(texts: dict[str, str | None]) -> dict[str, Any]:
+    """Own invocation only. Prefer an error and tail from each stream, then more error/tail context."""
+    lines = {source: (texts.get(source) or "").splitlines() for source in NATIVE_OUTPUT_SOURCES}
+    errors = {source: [i for i, line in enumerate(rows) if "error" in line.lower()] for source, rows in lines.items()}
+    present = {source: [i for i, line in enumerate(rows) if line.strip()] for source, rows in lines.items()}
+    candidates = []
+    # Reserve early candidates for both kinds of context from each source, without letting one stream dominate.
+    for source in NATIVE_OUTPUT_SOURCES:
+        if errors[source]:
+            candidates.append((source, errors[source][0]))
+        if present[source]:
+            candidates.append((source, present[source][-1]))
+    for depth in range(1, 21):
+        for source in NATIVE_OUTPUT_SOURCES:
+            if len(errors[source]) > depth:
+                candidates.append((source, errors[source][-depth]))
+            if len(present[source]) > depth:
+                candidates.append((source, present[source][-depth - 1]))
+    result: dict[str, Any] = {"diagnostic_only": True, "selection": "error lines and tail, per source; original line order",
+                              "max_lines": NATIVE_EXCERPT_LINES, "max_json_bytes": NATIVE_EXCERPT_BYTES,
+                              "source_line_counts": {s: len(v) for s, v in lines.items()},
+                              "selected_line_count": 0, "omitted_line_count": sum(map(len, lines.values())), "records": []}
+    selected: dict[tuple[str, int], dict[str, Any]] = {}
+    for source, index in dict.fromkeys(candidates):
+        if len(selected) >= NATIVE_EXCERPT_LINES:
+            break
+        original = lines[source][index]
+        error = re.search("error", original, re.I)
+        start = max(0, error.start() - 40) if error else 0
+        text = original[start:start + 220]
+        # Count JSON escaping as well as UTF-8, so long Unicode/control lines cannot defeat the byte bound.
+        while len(json.dumps(text, ensure_ascii=False).encode()) > 260:
+            text = text[:-1]
+        record = {"source": source, "line": index + 1, "text": text,
+                  "start_char": start, "clipped": start != 0 or len(text) != len(original)}
+        trial = selected | {(source, index): record}
+        result.update(records=[trial[key] for key in sorted(trial, key=lambda key: (NATIVE_OUTPUT_SOURCES.index(key[0]), key[1]))],
+                      selected_line_count=len(trial), omitted_line_count=sum(map(len, lines.values())) - len(trial))
+        if len(json.dumps(result, ensure_ascii=False, indent=2).encode()) <= NATIVE_EXCERPT_BYTES:
+            selected = trial
+    result.update(records=[selected[key] for key in sorted(selected, key=lambda key: (NATIVE_OUTPUT_SOURCES.index(key[0]), key[1]))],
+                  selected_line_count=len(selected), omitted_line_count=sum(map(len, lines.values())) - len(selected))
+    return result
@@ -315 +382 @@ def bounded_command(argv: list[str], cwd: Path, log: Path, seconds: float,
-                    env: dict[str, str] | None = None) -> tuple[int | None, bool, float]:
+                    env: dict[str, str] | None = None, stderr_log: Path | None = None) -> tuple[int | None, bool, float]:
@@ -320,2 +387,2 @@ def bounded_command(argv: list[str], cwd: Path, log: Path, seconds: float,
-    with log.open("wb") as stream:
-        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
+    with log.open("wb") as stream, (stderr_log.open("wb") if stderr_log is not None else nullcontext(subprocess.STDOUT)) as error_stream:
+        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stream, stderr=error_stream, start_new_session=True)
@@ -358,0 +426 @@ def run_native(request: dict[str, Any], tree: Path, out: Path, deadline: float,
+        stderr_log = out / f"native-{i}.stderr.log"
@@ -360 +428 @@ def run_native(request: dict[str, Any], tree: Path, out: Path, deadline: float,
-        code, timeout, wall = bounded_command(argv, tree, log, seconds, env)
+        code, timeout, wall = bounded_command(argv, tree, log, seconds, env, stderr_log=stderr_log)
@@ -364,4 +432,7 @@ def run_native(request: dict[str, Any], tree: Path, out: Path, deadline: float,
-        own = None
-        if base.with_suffix(".out").is_file() and base.with_suffix(".err").is_file():
-            own = base.with_suffix(".out").read_text(errors="replace") + "\n" + base.with_suffix(".err").read_text(errors="replace")
-        row = parse_native_test(entry, log.read_text(errors="replace") if log.exists() else "", code, own, timeout)
+        texts, sources = native_output_sources({"compiletest_stdout": log, "compiletest_stderr": stderr_log,
+                                                "kani_stdout": base.with_suffix(".out"), "kani_stderr": base.with_suffix(".err")},
+                                               entry.get("diagnostic"))
+        own = (texts["kani_stdout"] + "\n" + texts["kani_stderr"]
+               if texts["kani_stdout"] is not None and texts["kani_stderr"] is not None else None)
+        console = (texts["compiletest_stdout"] or "") + "\n" + (texts["compiletest_stderr"] or "")
+        row = parse_native_test(entry, console, code, own, timeout)
@@ -368,0 +440,7 @@ def run_native(request: dict[str, Any], tree: Path, out: Path, deadline: float,
+        if row["native_status"] == "FAILED" or entry["expect"] == "fail":
+            selected_source = (next((s for s in ("kani_stdout", "kani_stderr") if sources[s]["required_substring_found"]), None)
+                               if row["diagnostic"] is not None else None)
+            row.update(output_sources=sources, output_excerpt=native_output_excerpt(texts),
+                       diagnostic_provenance={"gate_sources": ["kani_stdout", "kani_stderr"],
+                                              "representation": "raw UTF-8 with replacement; .out then newline then .err; no rendering or console fallback",
+                                              "selected_source": selected_source})
diff --git a/research/challenge-8/kani-k1/tools/test_gcb_native.py b/research/challenge-8/kani-k1/tools/test_gcb_native.py
index 96fc7a8d69..dfc39b3880 100644
--- a/research/challenge-8/kani-k1/tools/test_gcb_native.py
+++ b/research/challenge-8/kani-k1/tools/test_gcb_native.py
@@ -75,0 +76 @@ elif name == "cargo":
+        print("compiletest stderr context", file=sys.stderr)
@@ -101,0 +103,5 @@ sys.exit(0)
+            row = summary["native"]["tests"][0]
+            self.assertEqual(row["diagnostic_provenance"]["selected_source"], "kani_stderr")
+            self.assertTrue(row["output_excerpt"]["diagnostic_only"])
+            self.assertTrue(any(record["source"] == "compiletest_stderr" and "stderr context" in record["text"]
+                                for record in row["output_excerpt"]["records"]))
@@ -120,0 +127,7 @@ sys.exit(0)
+                if scenario == "foreign":
+                    row = summary["native"]["tests"][0]
+                    self.assertEqual(row["status"], "ERROR")
+                    self.assertTrue(row["output_sources"]["compiletest_stdout"]["required_substring_found"])
+                    self.assertFalse(row["output_sources"]["kani_stderr"]["required_substring_found"])
+                    self.assertTrue(any(record["source"] == "kani_stderr" and "other test output" in record["text"]
+                                        for record in row["output_excerpt"]["records"]))
@@ -196 +209 @@ class DispatchServiceTests(unittest.TestCase):
-        for stage_minutes, expected_code in ((0, 0), (1, 2)):
+        for stage_minutes, expected_code, request_minutes in ((0, 0, 29), (1, 2, 29), (17, 0, 12), (18, 2, 12)):
@@ -201 +214 @@ class DispatchServiceTests(unittest.TestCase):
-                (root / "request.json").write_text(json.dumps(NATIVE_REQ))
+                (root / "request.json").write_text(json.dumps({**NATIVE_REQ, "harness_timeout_minutes": request_minutes}))
@@ -219 +232,4 @@ elif "list" in args and "--format=json" in args:
-    print(json.dumps([{"id":"prior", "timeout":str(minutes*60)+"s", "options":{"pool":{"name":"projects/smallsort-k1/locations/us-central1/workerPools/k1-standard4"}}}] if scoped and minutes else []))
+    row={"id":"prior", "timeout":str(minutes*60)+"s", "options":{"pool":{"name":"projects/smallsort-k1/locations/us-central1/workerPools/k1-standard4"}}}
+    if os.environ["REQUEST_MINUTES"] == "12":
+        row.update(startTime="2026-11-10T00:00:00Z", finishTime=f"2026-11-10T00:{minutes:02d}:00Z")
+    print(json.dumps([row] if scoped and minutes else []))
@@ -223,0 +240 @@ elif "list" in args and "--format=json" in args:
+                           REQUEST_MINUTES=str(request_minutes),
@@ -230,2 +247,2 @@ elif "list" in args and "--format=json" in args:
-                    self.assertIn("--timeout=59m", json.loads(submitted.read_text()))
-                    self.assertIn("0.7965", run.stderr)
+                    self.assertIn(f"--timeout={request_minutes + 30}m", json.loads(submitted.read_text()))
+                    self.assertIn("0.7965" if request_minutes == 29 else "0.5670", run.stderr)
diff --git a/research/challenge-8/kani-k1/tools/test_kani_k1.py b/research/challenge-8/kani-k1/tools/test_kani_k1.py
index 3b226f5871..dd81f699e1 100644
--- a/research/challenge-8/kani-k1/tools/test_kani_k1.py
+++ b/research/challenge-8/kani-k1/tools/test_kani_k1.py
@@ -1475 +1475 @@ class NativeTests(unittest.TestCase):
-            def command(argv, tree, log, seconds, env):
+            def command(argv, tree, log, seconds, env, stderr_log=None):
@@ -1478,0 +1479 @@ class NativeTests(unittest.TestCase):
+                stderr_log.write_text("")
@@ -1521,0 +1523,131 @@ class NativeTests(unittest.TestCase):
+class NativeOutputEvidenceTests(unittest.TestCase):
+    def test_compiletest_stdout_and_stderr_are_separate_without_changing_exit(self):
+        with tempfile.TemporaryDirectory() as d:
+            root = Path(d); out = root / "stdout"; err = root / "stderr"
+            code, timeout, _ = k.bounded_command(
+                [sys.executable, "-c", "import sys; print('own stdout'); print('own stderr', file=sys.stderr); sys.exit(3)"],
+                root, out, 5, stderr_log=err)
+            self.assertEqual((code, timeout), (3, False))
+            self.assertEqual(out.read_text(), "own stdout\n")
+            self.assertEqual(err.read_text(), "own stderr\n")
+
+    def test_source_paths_hashes_and_raw_vs_rendered_provenance(self):
+        with tempfile.TemporaryDirectory() as d:
+            root = Path(d); paths = {s: root / s for s in k.NATIVE_OUTPUT_SOURCES}
+            paths["compiletest_stdout"].write_text("error: expected `fn`\n")
+            paths["compiletest_stderr"].write_text("compiletest failed\n")
+            paths["kani_stdout"].write_text("")
+            raw = json.dumps({"rendered": "error: expected `fn`\n"}).encode()
+            paths["kani_stderr"].write_bytes(raw)
+            texts, sources = k.native_output_sources(paths, "expected `fn`")
+            self.assertEqual(texts["kani_stderr"], raw.decode())
+            self.assertTrue(sources["compiletest_stdout"]["expected_fn_error_line_found"])
+            self.assertTrue(sources["kani_stderr"]["required_substring_found"])
+            self.assertFalse(sources["kani_stderr"]["expected_fn_error_line_found"])
+            self.assertFalse(sources["compiletest_stdout"]["used_for_gate_diagnostic"])
+            self.assertTrue(sources["kani_stderr"]["used_for_gate_diagnostic"])
+            self.assertEqual(sources["kani_stderr"]["sha256"], hashlib.sha256(raw).hexdigest())
+            self.assertEqual(sources["kani_stderr"]["bytes"], len(raw))
+            self.assertEqual(sources["kani_stderr"]["path"], str(paths["kani_stderr"]))
+            paths["kani_stderr"].unlink()
+            texts, sources = k.native_output_sources(paths, "expected `fn`")
+            self.assertIsNone(texts["kani_stderr"])
+            self.assertFalse(sources["kani_stderr"]["available"])
+            self.assertIsNone(sources["kani_stderr"]["sha256"])
+
+    def test_excerpt_bounds_error_priority_tail_unicode_and_long_lines(self):
+        texts = {source: "early error " + source + "\n" + "noise\n" * 200
+                 + "界" * 10000 + " error far into a Unicode line\n"
+                 + "control error " + "\x00" * 2000 + "\n" + "tail " + source + "\n"
+                 for source in k.NATIVE_OUTPUT_SOURCES}
+        excerpt = k.native_output_excerpt(texts)
+        self.assertLessEqual(len(json.dumps(excerpt, ensure_ascii=False, indent=2).encode()), 4096)
+        self.assertLessEqual(len(excerpt["records"]), 60)
+        self.assertGreater(excerpt["omitted_line_count"], 0)
+        self.assertTrue(excerpt["diagnostic_only"])
+        for source in k.NATIVE_OUTPUT_SOURCES:
+            records = [r for r in excerpt["records"] if r["source"] == source]
+            self.assertTrue(any("early error " + source in r["text"] for r in records))
+            self.assertTrue(any(r["text"] == "tail " + source for r in records))
+            self.assertEqual([r["line"] for r in records], sorted({r["line"] for r in records}))
+        clipped = k.native_output_excerpt({"kani_stderr": "x" * 10000 + " error: detail"})
+        record = clipped["records"][0]
+        self.assertIn("error: detail", record["text"])
+        self.assertTrue(record["clipped"])
+        self.assertGreater(record["start_char"], 0)
+        unicode_line = k.native_output_excerpt({"kani_stderr": "İ" * 10000 + " error: Unicode context"})
+        self.assertIn("error: Unicode context", unicode_line["records"][0]["text"])
+        empty = k.native_output_excerpt({})
+        self.assertEqual(empty["selected_line_count"], 0)
+        self.assertEqual(empty["omitted_line_count"], 0)
+
+    def run_case(self, root, entry=NATIVE_ENTRY, terminal="FAILED", own_err="error: different failure\n", stderr="stderr error context\n", own_out="Kani stdout tail\n"):
+        request = {**NATIVE_REQ, "kani_tests": [entry]}
+        def command(argv, tree, log, seconds, env, stderr_log=None):
+            log.write_text(native_log(entry, terminal))
+            stderr_log.write_text(stderr)
+            base = Path(argv[argv.index("--build-base") + 1]) / Path(entry["file"]).parent / Path(entry["file"]).stem / Path(entry["file"]).stem
+            base.parent.mkdir(parents=True)
+            base.with_suffix(".out").write_text(own_out)
+            if own_err is not None:
+                base.with_suffix(".err").write_text(own_err)
+            # This unrelated file must never supply gate diagnostics or excerpt text.
+            (root / "foreign.err").write_text("FOREIGN error: expected `fn`\n")
+            return (1 if terminal == "FAILED" else 0), False, 0.2
+        with patch.object(k, "native_binary_identity", return_value={"kani_profile": "release"}), patch.object(k, "bounded_command", side_effect=command):
+            k.run_native(request, root, root / "out", k.time.time() + 100, {})
+        return json.loads((root / "out/native.json").read_text())["tests"][0]
+
+    def test_failed_repro_excerpt_does_not_grant_console_or_foreign_diagnostic_credit(self):
+        with tempfile.TemporaryDirectory() as d:
+            row = self.run_case(Path(d))
+            self.assertEqual(row["native_status"], "FAILED")
+            self.assertEqual(row["status"], "ERROR")
+            self.assertIsNone(row["diagnostic"])
+            self.assertIsNone(row["diagnostic_provenance"]["selected_source"])
+            self.assertTrue(row["output_sources"]["compiletest_stdout"]["required_substring_found"])
+            self.assertFalse(row["output_sources"]["kani_stderr"]["required_substring_found"])
+            excerpt = json.dumps(row["output_excerpt"])
+            self.assertIn("different failure", excerpt)
+            self.assertIn("stderr error context", excerpt)
+            self.assertNotIn("FOREIGN", excerpt)
+            self.assertEqual({r["source"] for r in row["output_excerpt"]["records"]}, set(k.NATIVE_OUTPUT_SOURCES))
+        with tempfile.TemporaryDirectory() as d:
+            missing = self.run_case(Path(d), own_err=None, own_out="error: expected `fn`\n")
+            self.assertEqual(missing["status"], "ERROR")
+            self.assertIsNone(missing["diagnostic"])
+            self.assertIsNone(missing["diagnostic_provenance"]["selected_source"])
+            self.assertTrue(missing["output_sources"]["kani_stdout"]["required_substring_found"])
+            self.assertFalse(missing["output_sources"]["kani_stderr"]["available"])
+
+    def test_excerpt_condition_includes_failed_positive_and_successful_negative(self):
+        passed = {key: value for key, value in {**NATIVE_ENTRY, "expect": "pass"}.items() if key != "diagnostic"}
+        for entry, terminal, excerpt_required in ((passed, "FAILED", True), (NATIVE_ENTRY, "ok", True), (passed, "ok", False)):
+            with self.subTest(expect=entry["expect"], terminal=terminal), tempfile.TemporaryDirectory() as d:
+                row = self.run_case(Path(d), entry, terminal)
+                self.assertEqual("output_excerpt" in row, excerpt_required)
+                if terminal == "ok" and entry["expect"] == "pass":
+                    self.assertEqual(row["status"], "PASS")
+                else:
+                    self.assertEqual(row["status"], "ERROR")
+
+    def test_own_stderr_match_remains_gate_source_and_excerpt_pages_fit(self):
+        with tempfile.TemporaryDirectory() as d:
+            row = self.run_case(Path(d), own_err="error: expected `fn`\n" + "extra error detail\n" * 500)
+            self.assertEqual(row["status"], "EXPECTED_REPRO_FAILURE")
+            self.assertEqual(row["diagnostic_provenance"]["selected_source"], "kani_stderr")
+            native, info, summarize = NativeTests().summary()
+            native["tests"][0].update({key: row[key] for key in ("output_sources", "output_excerpt", "diagnostic_provenance")})
+            summary = summarize(report=native)
+            self.assertTrue(k.gate_ok(summary), summary)
+            text = k.native_page(summary, 0, 1)
+            self.assertLessEqual(len(text.encode()), 12000)
+            page = json.loads(text)
+            self.assertEqual(page["tests"][0]["output_excerpt"], row["output_excerpt"])
+            failed = summarize(report={**native, "complete": False})
+            page = json.loads(k.native_page(failed, 0, 1))
+            self.assertEqual(page["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
+            self.assertFalse(page["gate"])
+            self.assertIn("output_excerpt", page["tests"][0])
+
+
```

## Complete static tooling diff from 9b1758ab81 (git diff --unified=0)

```diff
diff --git a/research/challenge-8/kani-k1/tools/gcb-k1.sh b/research/challenge-8/kani-k1/tools/gcb-k1.sh
index 049b30a394..e6720b25cc 100755
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
@@ -213 +266,3 @@ stage() {
-      [ -f "$K1_OUT/build.ok" ] && valid && peaks_args=(--peaks "$K1_OUT/peaks.txt" --memcap "$K1_OUT/memcap.txt")
+      if [ -f "$K1_OUT/build.ok" ] && valid && ! native; then
+        peaks_args=(--peaks "$K1_OUT/peaks.txt" --memcap "$K1_OUT/memcap.txt")
+      fi
@@ -215,0 +271,3 @@ stage() {
+      native_args=()
+      [ ! -f "$K1_OUT/kani-build.json" ] || native_args+=(--kani-build "$K1_OUT/kani-build.json")
+      [ ! -f "$K1_OUT/native.json" ] || native_args+=(--native "$K1_OUT/native.json")
@@ -219 +277 @@ stage() {
-      python3 -B "$K1_TOOLS/kani_k1.py" summarize --request "$K1_REQUEST" "${log_args[@]}" "${peaks_args[@]}" "${inventory_args[@]}" \
+      python3 -B "$K1_TOOLS/kani_k1.py" summarize --request "$K1_REQUEST" "${log_args[@]}" "${peaks_args[@]}" "${inventory_args[@]}" "${native_args[@]}" \
@@ -242 +300 @@ if [ "${1:-}" != all ]; then stage "${1:-}"; exit; fi
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
index 0a1b58d943..47926f6b93 100755
--- a/research/challenge-8/kani-k1/tools/kani_k1.py
+++ b/research/challenge-8/kani-k1/tools/kani_k1.py
@@ -28,0 +29 @@ import time
+from contextlib import nullcontext
@@ -36 +37 @@ AGENTS = {"k1-merge", "k1-network", "coordinator"}
-KINDS = {"measurement", "diagnostic", "resource", "partition", "autoharness", "inventory"}
+KINDS = {"measurement", "diagnostic", "resource", "partition", "autoharness", "inventory", "kani-tests"}
@@ -68 +69,4 @@ CONTROLS_CFG = "kani_smallsort_controls"
-OPTIONAL_REQUEST_KEYS = {"kani_jobs", "uninit_checks", "valid_value_checks", "controls", "worker_index", "worker_total", "inventory"}
+OPTIONAL_REQUEST_KEYS = {"kani_jobs", "uninit_checks", "valid_value_checks", "controls", "worker_index", "worker_total", "inventory",
+                         "kani_patch", "kani_tests", "test_timeout_seconds"}
+NATIVE_MAX_MINUTES = 29  # + unchanged 30 min dispatch overhead = 59 min / $0.7965 reserve
+NATIVE_SCHEMA = "kani-k1-native-tests-v1"
@@ -130,0 +135,318 @@ def _one_line(value: Any, limit: int) -> bool:
+def bounded_version(value: Any) -> bool:
+    # Pinned version.rs prints the Kani release line followed by `CBMC <version>`.
+    # Preserve the actual stdout; rejecting every newline discards valid build identities.
+    return (isinstance(value, str) and len(value.encode()) <= 2048 and 1 <= len(value.splitlines()) <= 8
+            and all(_one_line(line, 400) for line in value.splitlines()))
+
+
+def diagnostic_json(text: str | None) -> Any:
+    """Bounded structured artifacts only, retained on failure without granting them gate credit."""
+    if text is None:
+        return {"state": "MISSING"}
+    if len(text.encode()) > 128 * 1024:
+        return {"state": "OVERSIZED", "bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
+    try:
+        return json.loads(text)
+    except ValueError:
+        return {"state": "INVALID_JSON", "bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
+
+
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
+NATIVE_EXCERPT_LINES = 60
+NATIVE_EXCERPT_BYTES = 4096  # whole excerpt as indented JSON, below the coordinator's 8 KiB bound
+NATIVE_OUTPUT_SOURCES = ("compiletest_stdout", "compiletest_stderr", "kani_stdout", "kani_stderr")
+
+
+def native_output_sources(paths: dict[str, Path], required: str | None) -> tuple[dict[str, str | None], dict[str, Any]]:
+    """Keep raw child .out/.err distinct from compiletest's potentially rendered failure display."""
+    texts: dict[str, str | None] = {}
+    metadata = {}
+    for source in NATIVE_OUTPUT_SOURCES:
+        path = paths[source]
+        raw = path.read_bytes() if path.is_file() else None
+        text = raw.decode(errors="replace") if raw is not None else None
+        texts[source] = text
+        metadata[source] = {"path": str(path), "available": raw is not None,
+                            "bytes": len(raw) if raw is not None else None,
+                            "sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None,
+                            "used_for_gate_diagnostic": source in ("kani_stdout", "kani_stderr"),
+                            "required_substring_found": required in text if required and text is not None else None,
+                            "expected_fn_error_line_found": bool(re.search(r"^error: expected `fn`\s*$", text, re.M)) if text is not None else None}
+    return texts, metadata
+
+
+def native_output_excerpt(texts: dict[str, str | None]) -> dict[str, Any]:
+    """Own invocation only. Prefer an error and tail from each stream, then more error/tail context."""
+    lines = {source: (texts.get(source) or "").splitlines() for source in NATIVE_OUTPUT_SOURCES}
+    errors = {source: [i for i, line in enumerate(rows) if "error" in line.lower()] for source, rows in lines.items()}
+    present = {source: [i for i, line in enumerate(rows) if line.strip()] for source, rows in lines.items()}
+    candidates = []
+    # Reserve early candidates for both kinds of context from each source, without letting one stream dominate.
+    for source in NATIVE_OUTPUT_SOURCES:
+        if errors[source]:
+            candidates.append((source, errors[source][0]))
+        if present[source]:
+            candidates.append((source, present[source][-1]))
+    for depth in range(1, 21):
+        for source in NATIVE_OUTPUT_SOURCES:
+            if len(errors[source]) > depth:
+                candidates.append((source, errors[source][-depth]))
+            if len(present[source]) > depth:
+                candidates.append((source, present[source][-depth - 1]))
+    result: dict[str, Any] = {"diagnostic_only": True, "selection": "error lines and tail, per source; original line order",
+                              "max_lines": NATIVE_EXCERPT_LINES, "max_json_bytes": NATIVE_EXCERPT_BYTES,
+                              "source_line_counts": {s: len(v) for s, v in lines.items()},
+                              "selected_line_count": 0, "omitted_line_count": sum(map(len, lines.values())), "records": []}
+    selected: dict[tuple[str, int], dict[str, Any]] = {}
+    for source, index in dict.fromkeys(candidates):
+        if len(selected) >= NATIVE_EXCERPT_LINES:
+            break
+        original = lines[source][index]
+        error = re.search("error", original, re.I)
+        start = max(0, error.start() - 40) if error else 0
+        text = original[start:start + 220]
+        # Count JSON escaping as well as UTF-8, so long Unicode/control lines cannot defeat the byte bound.
+        while len(json.dumps(text, ensure_ascii=False).encode()) > 260:
+            text = text[:-1]
+        record = {"source": source, "line": index + 1, "text": text,
+                  "start_char": start, "clipped": start != 0 or len(text) != len(original)}
+        trial = selected | {(source, index): record}
+        result.update(records=[trial[key] for key in sorted(trial, key=lambda key: (NATIVE_OUTPUT_SOURCES.index(key[0]), key[1]))],
+                      selected_line_count=len(trial), omitted_line_count=sum(map(len, lines.values())) - len(trial))
+        if len(json.dumps(result, ensure_ascii=False, indent=2).encode()) <= NATIVE_EXCERPT_BYTES:
+            selected = trial
+    result.update(records=[selected[key] for key in sorted(selected, key=lambda key: (NATIVE_OUTPUT_SOURCES.index(key[0]), key[1]))],
+                  selected_line_count=len(selected), omitted_line_count=sum(map(len, lines.values())) - len(selected))
+    return result
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
+                    env: dict[str, str] | None = None, stderr_log: Path | None = None) -> tuple[int | None, bool, float]:
+    """Separate process group: kill descendants on wall timeout, even if compiletest's child holds pipes."""
+    start = time.monotonic()
+    if seconds <= 0:
+        return None, True, 0.0
+    with log.open("wb") as stream, (stderr_log.open("wb") if stderr_log is not None else nullcontext(subprocess.STDOUT)) as error_stream:
+        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stream, stderr=error_stream, start_new_session=True)
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
+        stderr_log = out / f"native-{i}.stderr.log"
+        seconds = min(request["test_timeout_seconds"] + 30, deadline - time.time())
+        code, timeout, wall = bounded_command(argv, tree, log, seconds, env, stderr_log=stderr_log)
+        relative = Path(entry["file"])
+        base = build_base / relative.parent / relative.stem / relative.stem
+        # compiletest dump_output produces .out/.err for precisely this selector in a fresh build-base.
+        texts, sources = native_output_sources({"compiletest_stdout": log, "compiletest_stderr": stderr_log,
+                                                "kani_stdout": base.with_suffix(".out"), "kani_stderr": base.with_suffix(".err")},
+                                               entry.get("diagnostic"))
+        own = (texts["kani_stdout"] + "\n" + texts["kani_stderr"]
+               if texts["kani_stdout"] is not None and texts["kani_stderr"] is not None else None)
+        console = (texts["compiletest_stdout"] or "") + "\n" + (texts["compiletest_stderr"] or "")
+        row = parse_native_test(entry, console, code, own, timeout)
+        row.update(argv=argv, cwd=str(tree), env={"RUST_TEST_THREADS": "1"}, wall_s=wall)
+        if row["native_status"] == "FAILED" or entry["expect"] == "fail":
+            selected_source = (next((s for s in ("kani_stdout", "kani_stderr") if sources[s]["required_substring_found"]), None)
+                               if row["diagnostic"] is not None else None)
+            row.update(output_sources=sources, output_excerpt=native_output_excerpt(texts),
+                       diagnostic_provenance={"gate_sources": ["kani_stdout", "kani_stderr"],
+                                              "representation": "raw UTF-8 with replacement; .out then newline then .err; no rendering or console fallback",
+                                              "selected_source": selected_source})
+        report["tests"].append(row)
+        report_path.write_text(json.dumps(report, indent=2) + "\n")
+    report["complete"] = True
+    report_path.write_text(json.dumps(report, indent=2) + "\n")
+
+
@@ -147,0 +470,22 @@ def validate_request(data: Any, max_total_minutes: int | None = None) -> dict[st
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
@@ -351 +695 @@ def kani_args(request: dict[str, Any]) -> list[str]:
-    if request["kind"] == "inventory":
+    if request["kind"] in ("inventory", "kani-tests"):
@@ -393 +737 @@ def verification_mode(kind: str) -> str:
-            "diagnostic": "selected"}.get(kind, "invalid")
+            "diagnostic": "selected", "kani-tests": "kani-tests"}.get(kind, "invalid")
@@ -1153,0 +1498,28 @@ def summary_page(summary: dict[str, Any], offset: int, count: int) -> str:
+def native_page(summary: dict[str, Any], offset: int, count: int) -> str:
+    native = summary.get("native")
+    validated = isinstance(native, dict)
+    if not validated:
+        native = (summary.get("diagnostic_artifacts") or {}).get("native")
+    if not isinstance(native, dict) or not isinstance(native.get("tests"), list):
+        raise ValueError("no structured native report")
+    rows = native["tests"]
+    _page_bounds(len(rows), offset, count)
+    if not 1 <= count <= 4:
+        raise ValueError("native COUNT must be 1..4")
+    end = min(offset + count, len(rows))
+    page = {"head_sha": summary.get("head_sha"), "request_sha256": summary.get("request_sha256"),
+            "build_id": (summary.get("run") or {}).get("id"),
+            "kani_build": summary.get("kani_build") if validated else (summary.get("diagnostic_artifacts") or {}).get("kani_build"),
+            "validation": "VALIDATED" if validated else "UNVALIDATED_DIAGNOSTIC_ONLY",
+            "summary_status": summary.get("status"), "gate": gate_ok(summary),
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
@@ -1225 +1597,2 @@ def summarize(request_text: str | None, log_text: str | None, time_text: str | N
-              peaks_tracked: bool = False, inventory_text: str | None = None) -> dict[str, Any]:
+              peaks_tracked: bool = False, inventory_text: str | None = None,
+              native_text: str | None = None, kani_build_text: str | None = None) -> dict[str, Any]:
@@ -1277,0 +1651,74 @@ def summarize(request_text: str | None, log_text: str | None, time_text: str | N
+    if request["kind"] == "kani-tests":
+        summary["kani_exit_code"] = None
+        summary["native_runner_exit_code"] = exit_code
+    if request.get("kani_patch") or request["kind"] == "kani-tests":
+        try:
+            info = json.loads(kani_build_text or "null")
+            if (not isinstance(info, dict) or info.get("pin") != kani_commit or info.get("patch") != request.get("kani_patch")
+                    or not re.fullmatch(r"[0-9a-f]{40}", info.get("tree", ""))
+                    or not bounded_version(info.get("version")) or build_outcome != "success"):
+                raise ValueError("missing/inconsistent Kani patch/tree/version/build identity")
+            summary["kani_build"] = info
+        except (ValueError, TypeError) as exc:
+            summary["status"] = "RUNNER_ERROR"
+            summary["inconsistencies"].append(str(exc))
+            summary["diagnostic_artifacts"] = {"kani_build": diagnostic_json(kani_build_text),
+                                               "native": diagnostic_json(native_text)}
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
+            summary["diagnostic_artifacts"] = {"kani_build": diagnostic_json(kani_build_text),
+                                               "native": diagnostic_json(native_text)}
+        return summary
@@ -1536 +1983 @@ def render_md(summary: dict[str, Any]) -> str:
-    timeout_label = ("whole-job work budget" if req.get("kind") in ("autoharness", "partition", "inventory")
+    timeout_label = ("whole-job work budget" if req.get("kind") in ("autoharness", "partition", "inventory", "kani-tests")
@@ -1557,0 +2005,16 @@ def render_md(summary: dict[str, Any]) -> str:
+    if summary.get("kani_build"):
+        info = summary["kani_build"]
+        version = info["version"].replace("\n", "; ")
+        lines[8:8] = [f"- Kani applied tree `{info['tree']}`, patch `{(info.get('patch') or {}).get('sha256')}`, version `{version}`",
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
@@ -1624,0 +2088,13 @@ def main(argv: list[str]) -> int:
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
@@ -1640,0 +2117,2 @@ def main(argv: list[str]) -> int:
+    s.add_argument("--native")
+    s.add_argument("--kani-build")
@@ -1659,0 +2138,4 @@ def main(argv: list[str]) -> int:
+    pn = sub.add_parser("page-native")
+    pn.add_argument("summary")
+    pn.add_argument("offset", type=int)
+    pn.add_argument("count", type=int)
@@ -1674,0 +2157,16 @@ def main(argv: list[str]) -> int:
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
@@ -1700 +2198 @@ def main(argv: list[str]) -> int:
-    if a.cmd == "page-summary":
+    if a.cmd in ("page-summary", "page-native"):
@@ -1702 +2200,2 @@ def main(argv: list[str]) -> int:
-            print(summary_page(json.loads(Path(a.summary).read_text()), a.offset, a.count), end="")
+            renderer = native_page if a.cmd == "page-native" else summary_page
+            print(renderer(json.loads(Path(a.summary).read_text()), a.offset, a.count), end="")
@@ -1723,0 +2223 @@ def main(argv: list[str]) -> int:
+            patch_bytes(request, Path.cwd())
@@ -1752 +2252,2 @@ def main(argv: list[str]) -> int:
-                            _read_optional(a.peaks), a.peaks is not None, _read_optional(a.inventory))
+                            _read_optional(a.peaks), a.peaks is not None, _read_optional(a.inventory),
+                            _read_optional(a.native), _read_optional(a.kani_build))
diff --git a/research/challenge-8/kani-k1/tools/test_gcb_native.py b/research/challenge-8/kani-k1/tools/test_gcb_native.py
new file mode 100644
index 0000000000..dfc39b3880
--- /dev/null
+++ b/research/challenge-8/kani-k1/tools/test_gcb_native.py
@@ -0,0 +1,287 @@
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
+            "scripts/kani":"#!/bin/sh\nprintf 'Kani Rust Verifier 0.68.0 (standalone)\\nCBMC 6.8.0\\n'\n",
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
+        print("compiletest stderr context", file=sys.stderr)
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
+            self.assertEqual(summary["kani_build"]["version"], "Kani Rust Verifier 0.68.0 (standalone)\nCBMC 6.8.0")
+            self.assertIsNone(summary["resources"]["memcap"])
+            self.assertIsNone(summary["resources"]["peaks"])
+            row = summary["native"]["tests"][0]
+            self.assertEqual(row["diagnostic_provenance"]["selected_source"], "kani_stderr")
+            self.assertTrue(row["output_excerpt"]["diagnostic_only"])
+            self.assertTrue(any(record["source"] == "compiletest_stderr" and "stderr context" in record["text"]
+                                for record in row["output_excerpt"]["records"]))
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
+                if scenario == "foreign":
+                    row = summary["native"]["tests"][0]
+                    self.assertEqual(row["status"], "ERROR")
+                    self.assertTrue(row["output_sources"]["compiletest_stdout"]["required_substring_found"])
+                    self.assertFalse(row["output_sources"]["kani_stderr"]["required_substring_found"])
+                    self.assertTrue(any(record["source"] == "kani_stderr" and "other test output" in record["text"]
+                                        for record in row["output_excerpt"]["records"]))
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
+        for stage_minutes, expected_code, request_minutes in ((0, 0, 29), (1, 2, 29), (17, 0, 12), (18, 2, 12)):
+            with self.subTest(stage_minutes=stage_minutes), tempfile.TemporaryDirectory() as d:
+                root = Path(d); tools = root / "tools"; tools.mkdir()
+                for name in ("k1g.sh", "kani_k1.py"):
+                    shutil.copy(TOOLS / name, tools)
+                (root / "request.json").write_text(json.dumps({**NATIVE_REQ, "harness_timeout_minutes": request_minutes}))
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
+    row={"id":"prior", "timeout":str(minutes*60)+"s", "options":{"pool":{"name":"projects/smallsort-k1/locations/us-central1/workerPools/k1-standard4"}}}
+    if os.environ["REQUEST_MINUTES"] == "12":
+        row.update(startTime="2026-11-10T00:00:00Z", finishTime=f"2026-11-10T00:{minutes:02d}:00Z")
+    print(json.dumps([row] if scoped and minutes else []))
+'''
+                for name in ("git", "gcloud"):
+                    path = bindir / name; path.write_text(stub); path.chmod(0o755)
+                env = dict(os.environ, SERVICE_ROOT=str(root), STAGE_MINUTES=str(stage_minutes),
+                           REQUEST_MINUTES=str(request_minutes),
+                           K1_GCP_KEY=str(key), K1_GCLOUD_CONFIG=str(root / "gconfig"), PATH=str(bindir) + ":/usr/bin:/bin")
+                run = subprocess.run(["bash", str(tools / "k1g.sh"), "dispatch", "experiment/kani-k1-kani5116-20261110"],
+                                     cwd=root, env=env, capture_output=True, text=True, timeout=10)
+                self.assertEqual(run.returncode, expected_code, run.stdout + run.stderr)
+                submitted = root / "submitted.json"
+                if expected_code == 0:
+                    self.assertIn(f"--timeout={request_minutes + 30}m", json.loads(submitted.read_text()))
+                    self.assertIn("0.7965" if request_minutes == 29 else "0.5670", run.stderr)
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
index 6991958e53..dd81f699e1 100644
--- a/research/challenge-8/kani-k1/tools/test_kani_k1.py
+++ b/research/challenge-8/kani-k1/tools/test_kani_k1.py
@@ -1229,0 +1230,424 @@ class CliTests(unittest.TestCase):
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
+    def test_pinned_multiline_version_and_invalid_identity_diagnostics(self):
+        native, info, summarize = self.summary()
+        version = "Kani Rust Verifier 0.68.0 (standalone)\nCBMC 6.8.0"
+        summary = summarize(build={**info, "version": version})
+        self.assertTrue(k.gate_ok(summary), summary)
+        self.assertEqual(summary["kani_build"]["version"], version)
+        self.assertIn("version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.8.0`", k.render_md(summary))
+        for value in ("", "line\n" * 9, "x" * 401, ["Kani"], None):
+            failed = summarize(build={**info, "version": value})
+            self.assertFalse(k.gate_ok(failed))
+            self.assertIsNone(failed["kani_exit_code"])
+            self.assertEqual(failed["native_runner_exit_code"], 0)
+            self.assertEqual(failed["diagnostic_artifacts"]["kani_build"]["version"], value)
+            self.assertEqual(failed["diagnostic_artifacts"]["native"], native)
+            page = json.loads(k.native_page(failed, 0, 1))
+            self.assertEqual(page["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
+            self.assertFalse(page["gate"])
+            self.assertEqual(page["tests"], native["tests"])
+        failed = summarize(report={**native, "complete": False})
+        self.assertFalse(k.gate_ok(failed))
+        self.assertEqual(json.loads(k.native_page(failed, 0, 1))["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
+        self.assertEqual(k.diagnostic_json(None), {"state": "MISSING"})
+        self.assertEqual(k.diagnostic_json("{")["state"], "INVALID_JSON")
+        self.assertEqual(k.diagnostic_json("x" * (128 * 1024 + 1))["state"], "OVERSIZED")
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
+            def command(argv, tree, log, seconds, env, stderr_log=None):
+                self.assertEqual(env["RUST_TEST_THREADS"], "1")
+                self.assertLessEqual(seconds, 210)
+                log.write_text(native_log())
+                stderr_log.write_text("")
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
+class NativeOutputEvidenceTests(unittest.TestCase):
+    def test_compiletest_stdout_and_stderr_are_separate_without_changing_exit(self):
+        with tempfile.TemporaryDirectory() as d:
+            root = Path(d); out = root / "stdout"; err = root / "stderr"
+            code, timeout, _ = k.bounded_command(
+                [sys.executable, "-c", "import sys; print('own stdout'); print('own stderr', file=sys.stderr); sys.exit(3)"],
+                root, out, 5, stderr_log=err)
+            self.assertEqual((code, timeout), (3, False))
+            self.assertEqual(out.read_text(), "own stdout\n")
+            self.assertEqual(err.read_text(), "own stderr\n")
+
+    def test_source_paths_hashes_and_raw_vs_rendered_provenance(self):
+        with tempfile.TemporaryDirectory() as d:
+            root = Path(d); paths = {s: root / s for s in k.NATIVE_OUTPUT_SOURCES}
+            paths["compiletest_stdout"].write_text("error: expected `fn`\n")
+            paths["compiletest_stderr"].write_text("compiletest failed\n")
+            paths["kani_stdout"].write_text("")
+            raw = json.dumps({"rendered": "error: expected `fn`\n"}).encode()
+            paths["kani_stderr"].write_bytes(raw)
+            texts, sources = k.native_output_sources(paths, "expected `fn`")
+            self.assertEqual(texts["kani_stderr"], raw.decode())
+            self.assertTrue(sources["compiletest_stdout"]["expected_fn_error_line_found"])
+            self.assertTrue(sources["kani_stderr"]["required_substring_found"])
+            self.assertFalse(sources["kani_stderr"]["expected_fn_error_line_found"])
+            self.assertFalse(sources["compiletest_stdout"]["used_for_gate_diagnostic"])
+            self.assertTrue(sources["kani_stderr"]["used_for_gate_diagnostic"])
+            self.assertEqual(sources["kani_stderr"]["sha256"], hashlib.sha256(raw).hexdigest())
+            self.assertEqual(sources["kani_stderr"]["bytes"], len(raw))
+            self.assertEqual(sources["kani_stderr"]["path"], str(paths["kani_stderr"]))
+            paths["kani_stderr"].unlink()
+            texts, sources = k.native_output_sources(paths, "expected `fn`")
+            self.assertIsNone(texts["kani_stderr"])
+            self.assertFalse(sources["kani_stderr"]["available"])
+            self.assertIsNone(sources["kani_stderr"]["sha256"])
+
+    def test_excerpt_bounds_error_priority_tail_unicode_and_long_lines(self):
+        texts = {source: "early error " + source + "\n" + "noise\n" * 200
+                 + "界" * 10000 + " error far into a Unicode line\n"
+                 + "control error " + "\x00" * 2000 + "\n" + "tail " + source + "\n"
+                 for source in k.NATIVE_OUTPUT_SOURCES}
+        excerpt = k.native_output_excerpt(texts)
+        self.assertLessEqual(len(json.dumps(excerpt, ensure_ascii=False, indent=2).encode()), 4096)
+        self.assertLessEqual(len(excerpt["records"]), 60)
+        self.assertGreater(excerpt["omitted_line_count"], 0)
+        self.assertTrue(excerpt["diagnostic_only"])
+        for source in k.NATIVE_OUTPUT_SOURCES:
+            records = [r for r in excerpt["records"] if r["source"] == source]
+            self.assertTrue(any("early error " + source in r["text"] for r in records))
+            self.assertTrue(any(r["text"] == "tail " + source for r in records))
+            self.assertEqual([r["line"] for r in records], sorted({r["line"] for r in records}))
+        clipped = k.native_output_excerpt({"kani_stderr": "x" * 10000 + " error: detail"})
+        record = clipped["records"][0]
+        self.assertIn("error: detail", record["text"])
+        self.assertTrue(record["clipped"])
+        self.assertGreater(record["start_char"], 0)
+        unicode_line = k.native_output_excerpt({"kani_stderr": "İ" * 10000 + " error: Unicode context"})
+        self.assertIn("error: Unicode context", unicode_line["records"][0]["text"])
+        empty = k.native_output_excerpt({})
+        self.assertEqual(empty["selected_line_count"], 0)
+        self.assertEqual(empty["omitted_line_count"], 0)
+
+    def run_case(self, root, entry=NATIVE_ENTRY, terminal="FAILED", own_err="error: different failure\n", stderr="stderr error context\n", own_out="Kani stdout tail\n"):
+        request = {**NATIVE_REQ, "kani_tests": [entry]}
+        def command(argv, tree, log, seconds, env, stderr_log=None):
+            log.write_text(native_log(entry, terminal))
+            stderr_log.write_text(stderr)
+            base = Path(argv[argv.index("--build-base") + 1]) / Path(entry["file"]).parent / Path(entry["file"]).stem / Path(entry["file"]).stem
+            base.parent.mkdir(parents=True)
+            base.with_suffix(".out").write_text(own_out)
+            if own_err is not None:
+                base.with_suffix(".err").write_text(own_err)
+            # This unrelated file must never supply gate diagnostics or excerpt text.
+            (root / "foreign.err").write_text("FOREIGN error: expected `fn`\n")
+            return (1 if terminal == "FAILED" else 0), False, 0.2
+        with patch.object(k, "native_binary_identity", return_value={"kani_profile": "release"}), patch.object(k, "bounded_command", side_effect=command):
+            k.run_native(request, root, root / "out", k.time.time() + 100, {})
+        return json.loads((root / "out/native.json").read_text())["tests"][0]
+
+    def test_failed_repro_excerpt_does_not_grant_console_or_foreign_diagnostic_credit(self):
+        with tempfile.TemporaryDirectory() as d:
+            row = self.run_case(Path(d))
+            self.assertEqual(row["native_status"], "FAILED")
+            self.assertEqual(row["status"], "ERROR")
+            self.assertIsNone(row["diagnostic"])
+            self.assertIsNone(row["diagnostic_provenance"]["selected_source"])
+            self.assertTrue(row["output_sources"]["compiletest_stdout"]["required_substring_found"])
+            self.assertFalse(row["output_sources"]["kani_stderr"]["required_substring_found"])
+            excerpt = json.dumps(row["output_excerpt"])
+            self.assertIn("different failure", excerpt)
+            self.assertIn("stderr error context", excerpt)
+            self.assertNotIn("FOREIGN", excerpt)
+            self.assertEqual({r["source"] for r in row["output_excerpt"]["records"]}, set(k.NATIVE_OUTPUT_SOURCES))
+        with tempfile.TemporaryDirectory() as d:
+            missing = self.run_case(Path(d), own_err=None, own_out="error: expected `fn`\n")
+            self.assertEqual(missing["status"], "ERROR")
+            self.assertIsNone(missing["diagnostic"])
+            self.assertIsNone(missing["diagnostic_provenance"]["selected_source"])
+            self.assertTrue(missing["output_sources"]["kani_stdout"]["required_substring_found"])
+            self.assertFalse(missing["output_sources"]["kani_stderr"]["available"])
+
+    def test_excerpt_condition_includes_failed_positive_and_successful_negative(self):
+        passed = {key: value for key, value in {**NATIVE_ENTRY, "expect": "pass"}.items() if key != "diagnostic"}
+        for entry, terminal, excerpt_required in ((passed, "FAILED", True), (NATIVE_ENTRY, "ok", True), (passed, "ok", False)):
+            with self.subTest(expect=entry["expect"], terminal=terminal), tempfile.TemporaryDirectory() as d:
+                row = self.run_case(Path(d), entry, terminal)
+                self.assertEqual("output_excerpt" in row, excerpt_required)
+                if terminal == "ok" and entry["expect"] == "pass":
+                    self.assertEqual(row["status"], "PASS")
+                else:
+                    self.assertEqual(row["status"], "ERROR")
+
+    def test_own_stderr_match_remains_gate_source_and_excerpt_pages_fit(self):
+        with tempfile.TemporaryDirectory() as d:
+            row = self.run_case(Path(d), own_err="error: expected `fn`\n" + "extra error detail\n" * 500)
+            self.assertEqual(row["status"], "EXPECTED_REPRO_FAILURE")
+            self.assertEqual(row["diagnostic_provenance"]["selected_source"], "kani_stderr")
+            native, info, summarize = NativeTests().summary()
+            native["tests"][0].update({key: row[key] for key in ("output_sources", "output_excerpt", "diagnostic_provenance")})
+            summary = summarize(report=native)
+            self.assertTrue(k.gate_ok(summary), summary)
+            text = k.native_page(summary, 0, 1)
+            self.assertLessEqual(len(text.encode()), 12000)
+            page = json.loads(text)
+            self.assertEqual(page["tests"][0]["output_excerpt"], row["output_excerpt"])
+            failed = summarize(report={**native, "complete": False})
+            page = json.loads(k.native_page(failed, 0, 1))
+            self.assertEqual(page["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
+            self.assertFalse(page["gate"])
+            self.assertIn("output_excerpt", page["tests"][0])
+
+
```
