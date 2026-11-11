"""Synthetic service/error-path tests for the bounded KANI3300 trace reader."""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diagnostic_trace as dt  # noqa: E402
import kani_k1 as k  # noqa: E402

ROOT = Path(__file__).resolve().parent
NAME = "slice::sort::shared::smallsort::verify::trace::smoke"
PIN = "a" * 40
TREE = "b" * 40
APPLIED = "c" * 40
PATCH = "d" * 64
REQUEST = {
    "schema": k.SCHEMA, "request_id": "trace-smoke", "agent": "coordinator", "kind": "diagnostic",
    "purpose": "synthetic trace test", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 3,
    "harnesses": [{"name": NAME, "expect": "SUCCESS"}],
    "kani_patch": {"path": "research/patch.diff", "sha256": PATCH},
    "diagnostic_trace": {"filters": ["crate::IndexRange::len"], "library_tree": TREE,
                         "base_pin": PIN, "expected_applied_tree": APPLIED},
}


def sidecar(directory: Path, request_text: str, *, state="COMPLETE", stage=dt.STAGE,
            trace_id=None, records=None, footer=True):
    trace_id = trace_id or hashlib.sha256(request_text.encode()).hexdigest()
    invocation = "compiler-1"
    events = records if records is not None else [{"kind": "mir", "data": {"target": "IndexRange::len"}}]
    rows = [{"schema": dt.SCHEMA, "kind": "header", "trace_id": trace_id, "stage": stage,
             "invocation": invocation, "seq": 0,
             "data": {"filters": REQUEST["diagnostic_trace"]["filters"]}}]
    rows += [{"schema": dt.SCHEMA, "kind": row["kind"], "trace_id": trace_id, "stage": stage,
              "invocation": invocation, "seq": i + 1, "data": row["data"]} for i, row in enumerate(events)]
    if footer:
        rows.append({"schema": dt.SCHEMA, "kind": "footer", "trace_id": trace_id, "stage": stage,
                     "invocation": invocation, "seq": len(events) + 1,
                     "data": {"state": state, "seen_records": len(events), "emitted_records": len(events),
                              "omitted_records": 0, "bytes_before_footer": 42, "coverage": ["mir"]}})
    (directory / "kani3300-trace-1-0.jsonl").write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))


def collect(directory, request_text=None, *, outcome="success", library_tree=TREE, kani_commit=PIN,
            applied=APPLIED):
    text = request_text or json.dumps(REQUEST, separators=(",", ":"))
    req = k.validate_request(json.loads(text))
    return dt.collect_trace(directory, build_id="build-1", head_sha="f" * 40,
                            request_sha256=hashlib.sha256(text.encode()).hexdigest(), request=req,
                            kani_commit=kani_commit, kani_build={"tree": applied},
                            tooling={"tools/x.py": "e" * 64}, build_outcome=outcome,
                            effective_argv=["kani", "--harness", NAME], effective_env={},
                            actual_library_tree=library_tree)


class DiagnosticTraceTests(unittest.TestCase):
    def test_opt_out_summary_unchanged_even_with_hostile_ambient_trace_env(self):
        req = copy.deepcopy(REQUEST)
        req.pop("diagnostic_trace")
        req.pop("kani_patch")
        env = dict(os.environ, KANI3300_TRACE_DIR="; touch /tmp/nope", KANI3300_TRACE_FILTER="$(id)",
                   KANI3300_TRACE_ID="bad", KANI3300_TRACE_STAGE="bad")
        script = (ROOT / "gcb-k1.sh").read_text()
        self.assertIn("unset KANI3300_TRACE_DIR KANI3300_TRACE_FILTER KANI3300_TRACE_ID KANI3300_TRACE_STAGE", script)
        self.assertEqual(env["KANI3300_TRACE_FILTER"], "$(id)")
        # With no trace dir option the established summary object has no new trace field.
        core = k._summarize_core(json.dumps(req), "", None, 1, "f" * 40, PIN, build_outcome="failure")
        out = k.summarize(json.dumps(req), "", None, 1, "f" * 40, PIN, build_outcome="failure")
        self.assertEqual(out, core)

    def test_invalid_filter_rejected_before_environment_write(self):
        bad = copy.deepcopy(REQUEST)
        bad["diagnostic_trace"]["filters"] = ["x;$(touch /tmp/nope)"]
        with self.assertRaises(k.RequestError):
            k.validate_request(bad)
        with tempfile.TemporaryDirectory() as tmp:
            request, output = Path(tmp) / "request.json", Path(tmp) / "env"
            request.write_text(json.dumps(bad))
            proc = subprocess.run([sys.executable, "-I", str(ROOT / "kani_k1.py"), "trace-env",
                                   "--request", str(request), "--out", str(output), "--trace-dir", tmp],
                                  capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(output.exists())
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp); tools = workspace / "research/challenge-8/kani-k1/tools"
            tools.mkdir(parents=True)
            for name in ("kani_k1.py", "diagnostic_trace.py", "gcb-k1.sh"):
                shutil.copy2(ROOT / name, tools / name)
            req_path = workspace / "research/challenge-8/kani-k1/RUN-REQUEST.json"
            req_path.write_text(json.dumps(bad))
            (workspace / "tool_config").mkdir(); (workspace / "tool_config/kani-version.toml").write_text(f'commit = "{PIN}"\n')
            fakebin = workspace / "fakebin"; fakebin.mkdir()
            (fakebin / "apt-get").write_text("#!/bin/sh\nexit 0\n"); (fakebin / "apt-get").chmod(0o755)
            git_stub = fakebin / "git"
            git_stub.write_text(f"#!/bin/sh\necho '{'f' * 40}'\n"); git_stub.chmod(0o755)
            env = dict(os.environ, PATH=f"{fakebin}:/usr/bin:/bin", K1_BRANCH="experiment/kani-k1-smoke-20261111",
                       K1_SHA="f" * 40)
            proc = subprocess.run(["bash", str(tools / "gcb-k1.sh"), "validate"], cwd=workspace, env=env,
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse((workspace / "k1-out/valid").exists())
            self.assertFalse((workspace / "k1-out/trace.env").exists())
            self.assertIn("diagnostic_trace filters", proc.stderr)

    def test_valid_env_is_exact_and_request_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            request, output = Path(tmp) / "request.json", Path(tmp) / "env"
            raw = json.dumps(REQUEST, separators=(",", ":")); request.write_text(raw)
            k.write_trace_env(request, output, Path(tmp) / "trace")
            values = dict(line.split("=", 1) for line in output.read_text().splitlines())
            self.assertEqual(values["KANI3300_TRACE_FILTER"], "crate::IndexRange::len")
            self.assertEqual(values["KANI3300_TRACE_ID"], hashlib.sha256(raw.encode()).hexdigest())
            self.assertEqual(values["KANI3300_TRACE_STAGE"], dt.STAGE)

    def test_complete_and_paged_summary_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); raw = json.dumps(REQUEST, separators=(",", ":"))
            sidecar(directory, raw)
            result = collect(directory, raw)
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["identity"]["library_tree"], TREE)
            summary = {"run": {"id": "build-1"}, "diagnostic_trace": result}
            page = json.loads(dt.trace_field_page(summary, "records", 0, 20, "build-1"))
            self.assertEqual(page["next_start"], None)
            self.assertTrue(page["complete"])
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                dt.trace_field_page(summary, "records", 0, 20, "build-2")

    def test_missing_malformed_null_partial_oversized_and_timeout(self):
        raw = json.dumps(REQUEST, separators=(",", ":"))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.assertEqual(collect(directory, raw)["state"], "MISSING")
            sidecar(directory, raw, footer=False)
            self.assertEqual(collect(directory, raw)["state"], "INVALID")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); sidecar(directory, raw, state="PARTIAL")
            self.assertEqual(collect(directory, raw)["state"], "PARTIAL")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); sidecar(directory, raw, state="OVERSIZED")
            self.assertEqual(collect(directory, raw)["state"], "OVERSIZED")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); (directory / "kani3300-trace-1-0.jsonl").write_text("null\n")
            self.assertEqual(collect(directory, raw)["state"], "INVALID")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); sidecar(directory, raw)
            self.assertEqual(collect(directory, raw, outcome="timeout")["state"], "TIMEOUT")

    def test_source_stage_and_target_identity_mismatch_stays_diagnostic(self):
        raw = json.dumps(REQUEST, separators=(",", ":"))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); sidecar(directory, raw, stage="wrong-stage")
            self.assertEqual(collect(directory, raw)["state"], "INVALID")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); sidecar(directory, raw)
            result = collect(directory, raw, library_tree="0" * 40)
            self.assertEqual(result["state"], "INVALID")
            self.assertIn("actual library tree differs from request", result["errors"])
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); sidecar(directory, raw)
            result = collect(directory, raw, applied="0" * 40)
            self.assertEqual(result["state"], "INVALID")
            self.assertIn("actual applied Kani tree differs from request", result["errors"])
        # The request/verdict parser remains independent of trace validity.
        summary = k._summarize_core(json.dumps(REQUEST), "", None, 1, "f" * 40, PIN,
                                    build_outcome="success",
                                    kani_build_text=json.dumps({"pin": PIN, "patch": REQUEST["kani_patch"],
                                                                "tree": APPLIED, "version": "kani test"}))
        self.assertNotEqual(summary["status"], "INVALID")

    def test_record_and_page_byte_caps(self):
        raw = json.dumps(REQUEST, separators=(",", ":"))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            records = [{"kind": "x", "data": {"v": "x" * 2100}}]
            sidecar(directory, raw, records=records)
            self.assertEqual(collect(directory, raw)["state"], "INVALID")

    def service_run(self, *, traced: bool, result: str, producer: str = "valid"):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            tools = workspace / "research/challenge-8/kani-k1/tools"
            tools.mkdir(parents=True)
            for name in ("kani_k1.py", "diagnostic_trace.py", "gcb-k1.sh"):
                shutil.copy2(ROOT / name, tools / name)
            time_stub = workspace / "synthetic-time"
            time_stub.write_text("#!/bin/sh\n[ \"${1:-}\" = -v ] && shift\nexec \"$@\"\n")
            time_stub.chmod(0o755)
            gcb_copy = tools / "gcb-k1.sh"
            gcb_copy.write_text(gcb_copy.read_text().replace("/usr/bin/time", str(time_stub)))
            (workspace / "scripts").mkdir()
            (workspace / "tool_config").mkdir()
            (workspace / "library").mkdir()
            (workspace / "tool_config/kani-version.toml").write_text(f'commit = "{PIN}"\n')
            request = copy.deepcopy(REQUEST)
            if not traced:
                request.pop("diagnostic_trace"); request.pop("kani_patch")
            request["harnesses"] = [{"name": NAME, "expect": "SUCCESS"}]
            request_path = workspace / "research/challenge-8/kani-k1/RUN-REQUEST.json"
            request_path.write_text(json.dumps(request, separators=(",", ":")))
            out = workspace / "k1-out"; out.mkdir()
            for marker in ("validated", "valid", "build.ok", "deps.ok"):
                (out / marker).touch()
            (out / "start").write_text(str(int(__import__("time").time()) - 1) + "\n")
            (out / "kani-args.txt").write_text("--harness\n" + NAME + "\n--exact\n--harness-timeout\n3m\n--jobs=1\n--output-format=terse\n")
            (out / "rc").write_text("1\n")
            if traced:
                (out / "trace").mkdir()
                k.write_trace_env(request_path, out / "trace.env", out / "trace")
                (out / "kani-build.json").write_text(json.dumps({"pin": PIN, "patch": request["kani_patch"],
                                                                  "tree": APPLIED, "version": "kani test"}))
            fakebin = workspace / "fakebin"; fakebin.mkdir()
            git_stub = fakebin / "git"
            git_stub.write_text(f'''#!/bin/sh
case "$*" in
  "rev-parse HEAD") echo "{'f' * 40}" ;;
  "rev-parse HEAD:library") echo "{TREE}" ;;
  *) exec /usr/bin/git "$@" ;;
esac
''')
            git_stub.chmod(0o755)
            capture = workspace / "env.snapshot"
            run_script = workspace / "scripts/run-kani.sh"
            run_script.write_text(f'''#!/bin/bash
set -eu
printf '%s\\n' "${{KANI3300_TRACE_DIR-UNSET}}" "${{KANI3300_TRACE_FILTER-UNSET}}" "${{KANI3300_TRACE_ID-UNSET}}" "${{KANI3300_TRACE_STAGE-UNSET}}" > "{capture}"
if [ -n "${{KANI3300_TRACE_DIR:-}}" ] && [ "{producer}" = valid ]; then
python3 - "$KANI3300_TRACE_DIR" "$KANI3300_TRACE_ID" "$KANI3300_TRACE_STAGE" "$KANI3300_TRACE_FILTER" <<'PY'
import json,sys
from pathlib import Path
d=Path(sys.argv[1]); tid,stage,filters=sys.argv[2:]; filters=filters.split(';'); inv='compiler-1'
rows=[{{"schema":"kani3300-trace-v1","kind":"header","trace_id":tid,"stage":stage,"invocation":inv,"seq":0,"data":{{"filters":filters}}}},
{{"schema":"kani3300-trace-v1","kind":"mir","trace_id":tid,"stage":stage,"invocation":inv,"seq":1,"data":{{"target":"IndexRange::len"}}}},
{{"schema":"kani3300-trace-v1","kind":"footer","trace_id":tid,"stage":stage,"invocation":inv,"seq":2,"data":{{"state":"COMPLETE","seen_records":1,"emitted_records":1,"omitted_records":0,"bytes_before_footer":200,"coverage":["mir"]}}}}]
(d/'kani3300-trace-1-0.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\\n' for r in rows))
PY
elif [ -n "${{KANI3300_TRACE_DIR:-}}" ] && [ "{producer}" = oversized ]; then
python3 - "$KANI3300_TRACE_DIR" <<'PY'
from pathlib import Path
import sys
(Path(sys.argv[1])/'kani3300-trace-oversized.jsonl').write_bytes(b'x'*(1024*1024+1))
PY
fi
if [ "{result}" = fail ]; then
  cat <<'LOG'
Checking harness {NAME}...
Failed Checks: test diagnostic failure
VERIFICATION:- FAILED
Verification Time: 0.01s
Summary:
Complete - 0 successfully verified harnesses, 1 failures, 1 total.
LOG
  exit 1
fi
cat <<'LOG'
Checking harness {NAME}...
VERIFICATION:- SUCCESSFUL
Verification Time: 0.01s
Summary:
Complete - 1 successfully verified harnesses, 0 failures, 1 total.
LOG
exit 0
''')
            run_script.chmod(0o755)
            env = dict(os.environ, PATH=f"{fakebin}:/usr/bin:/bin", HOME="/root", K1_BUILD_ID="12345678-1234-1234-1234-123456789012",
                       KANI3300_TRACE_DIR="; touch /tmp/nope", KANI3300_TRACE_FILTER="$(id)", KANI3300_TRACE_ID="bad",
                       KANI3300_TRACE_STAGE="bad")
            verify = subprocess.run(["bash", str(tools / "gcb-k1.sh"), "verify"], cwd=workspace, env=env,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(verify.returncode, 0, verify.stderr)
            self.assertTrue(capture.exists(), f"runner not invoked: stdout={verify.stdout!r} stderr={verify.stderr!r} time={((out / 'time.txt').read_text() if (out / 'time.txt').exists() else 'missing')!r}")
            summary = subprocess.run(["bash", str(tools / "gcb-k1.sh"), "summarize"], cwd=workspace, env=env,
                                     capture_output=True, text=True, timeout=20)
            self.assertEqual(summary.returncode, 0, summary.stderr)
            data = json.loads((out / "summary/summary.json").read_text())
            observed_env = capture.read_text().splitlines()
            return data, observed_env, json.loads(request_path.read_text())

    def test_gcb_service_preserves_verdict_and_exports_only_valid_trace_env(self):
        data, observed, request = self.service_run(traced=True, result="fail")
        self.assertTrue(observed[0].endswith("/k1-out/trace"))
        self.assertEqual(observed[1], ";".join(request["diagnostic_trace"]["filters"]))
        self.assertEqual(observed[2], hashlib.sha256(json.dumps(request, separators=(",", ":")).encode()).hexdigest())
        self.assertEqual(observed[3], dt.STAGE)
        self.assertEqual(data["kani_exit_code"], 1)
        self.assertEqual(data["status"], "COMPLETE", data)
        self.assertFalse(data["expectation_met"])
        self.assertEqual(data["diagnostic_trace"]["state"], "COMPLETE")

    def test_gcb_service_missing_oversized_and_opt_out(self):
        missing, env_missing, _ = self.service_run(traced=True, result="ok", producer="missing")
        self.assertEqual(missing["diagnostic_trace"]["state"], "MISSING", missing["diagnostic_trace"])
        self.assertEqual(missing["status"], "COMPLETE")
        self.assertEqual(missing["kani_exit_code"], 0)
        self.assertNotEqual(env_missing[0], "UNSET")
        oversized, _, _ = self.service_run(traced=True, result="ok", producer="oversized")
        self.assertEqual(oversized["diagnostic_trace"]["state"], "OVERSIZED")
        self.assertEqual(oversized["status"], "COMPLETE")
        self.assertEqual(oversized["kani_exit_code"], 0)
        optout, optout_env, _ = self.service_run(traced=False, result="ok")
        self.assertEqual(optout_env, ["UNSET"] * 4)
        self.assertNotIn("diagnostic_trace", optout)
        self.assertEqual(optout["kani_exit_code"], 0)

    def test_producer_overflow_sentinel(self):
        raw = json.dumps(REQUEST, separators=(",", ":"))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "kani3300-trace-overflow.jsonl").write_text(json.dumps({
                "schema": dt.SCHEMA, "kind": "overflow", "state": "OVERSIZED",
                "trace_id": hashlib.sha256(raw.encode()).hexdigest(), "stage": dt.STAGE,
                "omitted_invocations": "one-or-more"}) + "\n")
            self.assertEqual(collect(directory, raw)["state"], "OVERSIZED")

    def test_k1g_trace_field_uses_cached_summary_only_and_checks_build_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); cache = root / "cache"; build = "12345678-1234-1234-1234-123456789012"
            summary_dir = cache / f"summary-{build}" / "summary"; summary_dir.mkdir(parents=True)
            payload = {"run": {"id": build}, "diagnostic_trace": {
                "state": "PARTIAL", "complete": False, "identity": {"build_id": build},
                "records": [{"kind": "target", "data": {"which": 1}}, {"kind": "op", "data": {"which": 2}}],
                "omitted": 1}}
            (summary_dir / "summary.json").write_text(json.dumps(payload))
            key, gcfg, fakebin = root / "key", root / "gcfg", root / "bin"
            key.write_text("synthetic"); fakebin.mkdir()
            gcloud = fakebin / "gcloud"
            gcloud.write_text("#!/bin/sh\nprintf '%s\\n' 'k1-dispatcher@smallsort-k1.iam.gserviceaccount.com'\n")
            gcloud.chmod(0o755)
            env = dict(os.environ, PATH=f"{fakebin}:/usr/bin:/bin", K1_CACHE=str(cache), K1_GCP_KEY=str(key),
                       K1_GCLOUD_CONFIG=str(gcfg))
            good = subprocess.run(["bash", str(ROOT / "k1g.sh"), "trace-field", build, "records", "0", "1"],
                                  cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(good.returncode, 0, good.stderr)
            page = json.loads(good.stdout)
            self.assertEqual(page["records"], payload["diagnostic_trace"]["records"][:1])
            self.assertEqual(page["next_start"], 1)
            self.assertEqual(page["omitted"], 1)
            payload["run"]["id"] = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            (summary_dir / "summary.json").write_text(json.dumps(payload))
            bad = subprocess.run(["bash", str(ROOT / "k1g.sh"), "trace-field", build, "records", "0", "1"],
                                 cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("identity mismatch", bad.stderr)


if __name__ == "__main__":
    unittest.main()
