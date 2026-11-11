"""Offline shell service checks. All build/cloud commands are fake executables, never real proof tools."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_kani_k1 import NATIVE_REQ, NATIVE_ENTRY, native_log, REQ, GOOD_LOG, TIME
import test_kani_k1 as fixtures
import kani_k1 as k

TOOLS = Path(__file__).resolve().parent
LANE = Path("research/challenge-8/kani-k1")


class CloudNativeServiceTests(unittest.TestCase):
    def packet(self, root, scenario="ok", invalid=None):
        tools = root / LANE / "tools"; tools.mkdir(parents=True)
        shutil.copy(TOOLS / "kani_k1.py", tools)
        # Keep real cargo/rustup inaccessible even on a developer machine with ~/.cargo/bin.
        shell = (TOOLS / "gcb-k1.sh").read_text()
        self.assertIn('export PATH="$HOME/.cargo/bin:$PATH"', shell)
        shell = shell.replace('export PATH="$HOME/.cargo/bin:$PATH"', 'export PATH="$K1_SERVICE_BIN:/usr/bin:/bin"')
        (tools / "gcb-k1.sh").write_text(shell)
        config = root / "tool_config"; config.mkdir()
        (config / "kani-version.toml").write_text('commit = "' + "b" * 40 + '"\n')
        request = copy.deepcopy(NATIVE_REQ)
        request["request_id"] = "kani5116-kt1-service"
        if invalid:
            request.update(invalid)
        (root / LANE / "RUN-REQUEST.json").write_text(json.dumps(request))
        (root / "native-log.txt").write_text(native_log())
        (root / "selected-log.txt").write_text(GOOD_LOG)
        bin_dir = root / "bin"; bin_dir.mkdir()
        command = r'''#!/usr/bin/python3
import json, os, sys
from pathlib import Path
root=Path(os.environ["SERVICE_ROOT"])
name=Path(sys.argv[0]).name; args=sys.argv[1:]
with (root/"commands.jsonl").open("a") as f: f.write(json.dumps([name,*args])+"\n")
scenario=os.environ["SERVICE_SCENARIO"]
if name == "git":
    tree=root/"kani_build"
    if args[:1] == ["-C"]: args=args[2:]
    if args[:1] == ["rev-parse"]:
        print(("b" if "-C" in sys.argv else "a")*40)
    elif args[:1] == ["write-tree"]: print("c"*40)
    elif args[:1] == ["diff"]: print("new fixture | 1 +")
    elif args[:1] == ["apply"] and scenario == "conflict": sys.exit(1)
    elif args[:1] == ["checkout"]:
        for path,text in {
            "tests/kani/FunctionContracts/repro.rs":"fn fixture() {}",
            "kani-dependencies":"",
            "scripts/setup/ubuntu/install_deps.sh":"#!/bin/sh\nexit 0\n",
            "scripts/kani":"#!/bin/sh\nprintf 'Kani Rust Verifier 0.68.0 (standalone)\\nCBMC 6.8.0\\n'\n",
        }.items():
            p=tree/path; p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);p.chmod(0o755)
elif name == "cargo":
    if args[:1] == ["build-dev"]:
        if scenario == "build-failure": sys.exit(7)
        for name in ("kani-driver","kani-compiler"):
            for path in ("target/release/"+name,"target/kani/bin/"+name):
                p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b"release");p.chmod(0o755)
    elif args[:1] == ["build"]:
        if scenario == "compiletest-build-failure": sys.exit(8)
        p=Path("target/debug/compiletest");p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b"compiletest");p.chmod(0o755)
    elif args[:1] == ["run"]:
        text=(root/"native-log.txt").read_text()
        if scenario == "panic": text += "thread 'main' panicked at runner.rs\n"
        if scenario == "zero": text=text.replace("running 1 test","running 0 tests")
        if scenario == "damaged": text=text.split("test result:")[0]
        if scenario == "compiletest-run-build-failure": text="error: could not compile compiletest\n"
        print(text)
        print("compiletest stderr context", file=sys.stderr)
        p=Path(args[args.index("--build-base")+1])/"FunctionContracts/repro/repro"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.with_suffix(".out").write_text("")
        p.with_suffix(".err").write_text("other test output" if scenario=="foreign" else "error: expected `fn`\n")
        sys.exit(1)
sys.exit(0)
'''
        for name in ("git", "cargo", "rustup", "apt-get"):
            p = bin_dir / name; p.write_text(command); p.chmod(0o755)
        env = dict(os.environ, SERVICE_ROOT=str(root), SERVICE_SCENARIO=scenario, K1_SERVICE_BIN=str(bin_dir),
                   K1_BRANCH="experiment/kani-k1-kani5116-20261110", K1_SHA="a" * 40, K1_BUILD_ID="service-build")
        env["PATH"] = str(bin_dir) + ":/usr/bin:/bin"
        return env, tools / "gcb-k1.sh"

    def test_native_end_to_end_summary_staged_and_gate_after_upload(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); env, script = self.packet(root)
            run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            output = root / "k1-out"
            summary = json.loads((output / "upload/summary/summary.json").read_text())
            self.assertTrue(k.gate_ok(summary), run.stdout + run.stderr)
            self.assertEqual((output / "gate.rc").read_text().strip(), "0")
            self.assertEqual(summary["kani_build"]["version"], "Kani Rust Verifier 0.68.0 (standalone)\nCBMC 6.8.0")
            self.assertIsNone(summary["resources"]["memcap"])
            self.assertIsNone(summary["resources"]["peaks"])
            row = summary["native"]["tests"][0]
            self.assertEqual(row["diagnostic_provenance"]["selected_source"], "kani_stderr")
            self.assertTrue(row["output_excerpt"]["diagnostic_only"])
            self.assertTrue(any(record["source"] == "compiletest_stderr" and "stderr context" in record["text"]
                                for record in row["output_excerpt"]["records"]))
            commands = [json.loads(line) for line in (root / "commands.jsonl").read_text().splitlines()]
            self.assertIn(["cargo", "build-dev", "--", "--release"], commands)
            self.assertIn(["cargo", "build", "-p", "compiletest"], commands)
            self.assertEqual(sum(row[:2] == ["cargo", "run"] for row in commands), 1)
            self.assertFalse((output / "kani.log").exists())
            yaml = (TOOLS.parent / "gcb/cloudbuild.yaml").read_text()
            self.assertLess(yaml.index("id: upload"), yaml.index("id: gate"))
            self.assertIn("gate.rc", yaml)

    def test_service_failures_are_uploaded_but_gate_rejects(self):
        for scenario in ("build-failure", "compiletest-build-failure", "compiletest-run-build-failure", "zero", "damaged", "panic", "foreign"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as d:
                root = Path(d); env, script = self.packet(root, scenario)
                run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                output = root / "k1-out"
                summary = json.loads((output / "upload/summary/summary.json").read_text())
                self.assertFalse(k.gate_ok(summary), scenario)
                self.assertNotEqual((output / "gate.rc").read_text().strip(), "0")
                if scenario == "foreign":
                    row = summary["native"]["tests"][0]
                    self.assertEqual(row["status"], "ERROR")
                    self.assertTrue(row["output_sources"]["compiletest_stdout"]["required_substring_found"])
                    self.assertFalse(row["output_sources"]["kani_stderr"]["required_substring_found"])
                    self.assertTrue(any(record["source"] == "kani_stderr" and "other test output" in record["text"]
                                        for record in row["output_excerpt"]["records"]))

    def test_invalid_patch_and_conflict_never_reach_build(self):
        for scenario, spec in (("ok", {"path": "research/missing.patch", "sha256": "1" * 64}),
                               ("ok", {"path": "research/../escape.patch", "sha256": "1" * 64}),
                               ("ok", {"path": "research/test.patch", "sha256": "1" * 64}),
                               ("ok", {"path": "research/link.patch", "sha256": k.hashlib.sha256(b"test patch").hexdigest()}),
                               ("conflict", None)):
            with self.subTest(scenario=scenario, spec=spec), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                path = root / "research/test.patch"; path.parent.mkdir()
                path.write_bytes(b"test patch")
                (path.parent / "link.patch").symlink_to(path)
                if spec is None:
                    spec = {"path": "research/test.patch", "sha256": k.hashlib.sha256(path.read_bytes()).hexdigest()}
                env, script = self.packet(root, scenario, {"kani_patch": spec})
                run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                summary = json.loads((root / "k1-out/upload/summary/summary.json").read_text())
                self.assertEqual(summary["status"], "REQUEST_INVALID", run.stdout)
                self.assertFalse(k.gate_ok(summary))
                commands = [json.loads(line) for line in (root / "commands.jsonl").read_text().splitlines()]
                self.assertFalse(any(row[0] in ("cargo", "rustup") for row in commands))

    def test_bad_selectors_rejected_before_build(self):
        for selectors in ([], [NATIVE_ENTRY, NATIVE_ENTRY], [{**NATIVE_ENTRY, "file": "missing.rs"}],
                          [{**NATIVE_ENTRY, "suite": "unknown"}]):
            with self.subTest(selectors=selectors), tempfile.TemporaryDirectory() as d:
                root = Path(d); env, script = self.packet(root, invalid={"kani_tests": selectors})
                run = subprocess.run(["bash", str(script), "all"], cwd=root, env=env, capture_output=True, text=True, timeout=20)
                self.assertEqual(run.returncode, 0, run.stderr)
                summary = json.loads((root / "k1-out/upload/summary/summary.json").read_text())
                self.assertEqual(summary["status"], "REQUEST_INVALID")
                commands = [json.loads(line) for line in (root / "commands.jsonl").read_text().splitlines()]
                self.assertFalse(any(row[0] in ("cargo", "rustup") for row in commands))

    def test_old_python_routes_and_error_statuses_equal_base(self):
        source = subprocess.run(["git", "show", "9b1758ab81:research/challenge-8/kani-k1/tools/kani_k1.py"],
                                cwd=TOOLS, capture_output=True, text=True, check=True).stdout
        baseline = {"__name__": "base_tooling"}
        exec(compile(source, "base_tooling", "exec"), baseline)
        requests = [REQ, {**REQ, "kind": "diagnostic"},
                    {**REQ, "kind": "resource", "runner": k.RESOURCE_RUNNER},
                    {**REQ, "kind": "partition", "runner": k.STANDARD_RUNNER, "harnesses": [], "worker_index": 1, "worker_total": 2},
                    {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harnesses": []},
                    {**REQ, "kind": "inventory", "runner": k.STANDARD_RUNNER, "harnesses": [], "inventory": True}]
        for request in requests:
            for bad in (request, {**request, "harness_timeout_minutes": 0}, {**request, "runner": "invalid"}, {**request, "controls": "bad"}):
                def validate(function):
                    try:
                        return function(copy.deepcopy(bad))
                    except ValueError as exc:
                        return str(exc)
                self.assertEqual(validate(k.validate_request), validate(baseline["validate_request"]))
            self.assertEqual(k.kani_args(request), baseline["kani_args"](request))
            self.assertEqual(k.verification_mode(request["kind"]), baseline["verification_mode"](request["kind"]))
            for log, code, outcome in ((GOOD_LOG, 1, "success"), ("", 1, "failure"), (None, None, "deps-failure"), (GOOD_LOG, 124, "success")):
                args = (json.dumps(request), log, TIME, code, "a" * 40, "b" * 40)
                self.assertEqual(k.summarize(*args, build_outcome=outcome), baseline["summarize"](*args, build_outcome=outcome))

    def test_service_deadline_skips_native_verification(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); env, script = self.packet(root)
            output = root / "k1-out"; output.mkdir()
            for name in ("valid", "build.ok"):
                (output / name).touch()
            (output / "kani-args.txt").write_text("")
            (output / "start").write_text("0")
            run = subprocess.run(["bash", str(script), "verify"], cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue((output / "verify-skipped").exists())
            self.assertFalse((root / "commands.jsonl").exists())


class DispatchServiceTests(unittest.TestCase):
    def test_native_reservation_and_stage_cap_before_submit(self):
        for stage_minutes, expected_code, request_minutes in ((0, 0, 29), (26, 0, 29), (111, 0, 29), (112, 2, 29), (128, 0, 12), (129, 2, 12)):
            with self.subTest(stage_minutes=stage_minutes), tempfile.TemporaryDirectory() as d:
                root = Path(d); tools = root / "tools"; tools.mkdir()
                for name in ("k1g.sh", "kani_k1.py"):
                    shutil.copy(TOOLS / name, tools)
                (root / "request.json").write_text(json.dumps({**NATIVE_REQ, "harness_timeout_minutes": request_minutes}))
                (root / "cloudbuild.yaml").write_text("steps: []\n")
                key = root / "fake-key"; key.touch()  # empty fake file, never reads credentials
                bindir = root / "bin"; bindir.mkdir()
                stub = r'''#!/usr/bin/python3
import json,os,sys
from pathlib import Path
root=Path(os.environ["SERVICE_ROOT"]);args=sys.argv[1:];name=Path(sys.argv[0]).name
with (root/"calls").open("a") as f: f.write(json.dumps([name,*args])+"\n")
if name=="git":
    if args[0]=="rev-parse":print("a"*40)
    elif args[0]=="show":print((root/("request.json" if args[1].endswith("RUN-REQUEST.json") else "cloudbuild.yaml")).read_text())
elif "auth" in args: print("k1-dispatcher@smallsort-k1.iam.gserviceaccount.com")
elif "submit" in args:
    (root/"submitted.json").write_text(json.dumps(args));print("11111111-1111-1111-1111-111111111111")
elif "list" in args and "--format=json" in args:
    scoped=any(a.startswith("--filter=substitutions._BRANCH=") for a in args)
    minutes=int(os.environ["STAGE_MINUTES"])
    row={"id":"prior", "timeout":str(minutes*60)+"s", "options":{"pool":{"name":"projects/smallsort-k1/locations/us-central1/workerPools/k1-standard4"}}}
    if os.environ["REQUEST_MINUTES"] == "12":
        row.update(startTime="2026-11-10T00:00:00Z", finishTime=f"2026-11-10T{minutes // 60:02d}:{minutes % 60:02d}:00Z")
    print(json.dumps([row] if scoped and minutes else []))
'''
                for name in ("git", "gcloud"):
                    path = bindir / name; path.write_text(stub); path.chmod(0o755)
                env = dict(os.environ, SERVICE_ROOT=str(root), STAGE_MINUTES=str(stage_minutes),
                           REQUEST_MINUTES=str(request_minutes),
                           K1_GCP_KEY=str(key), K1_GCLOUD_CONFIG=str(root / "gconfig"), PATH=str(bindir) + ":/usr/bin:/bin")
                run = subprocess.run(["bash", str(tools / "k1g.sh"), "dispatch", "experiment/kani-k1-kani5116-20261110"],
                                     cwd=root, env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(run.returncode, expected_code, run.stdout + run.stderr)
                submitted = root / "submitted.json"
                if expected_code == 0:
                    self.assertIn(f"--timeout={request_minutes + 30}m", json.loads(submitted.read_text()))
                    self.assertIn("0.7965" if request_minutes == 29 else "0.5670", run.stderr)
                else:
                    self.assertFalse(submitted.exists())
                    self.assertIn("$2.30", run.stderr)

    def test_summary_fetch_never_downloads_raw_logs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); tools = root / "tools"; tools.mkdir()
            for name in ("k1g.sh", "kani_k1.py"):
                shutil.copy(TOOLS / name, tools)
            key = root / "fake-key"; key.touch()
            bindir = root / "bin"; bindir.mkdir()
            stub = r'''#!/usr/bin/python3
import json,os,sys
from pathlib import Path
args=sys.argv[1:];root=Path(os.environ["SERVICE_ROOT"])
if "auth" in args:print("k1-dispatcher@smallsort-k1.iam.gserviceaccount.com")
elif "describe" in args: print(json.dumps({"status":"SUCCESS"}))
elif "ls" in args:
    for rel in ("summary/summary.json","summary/summary.md","log/kani.log","log/time.txt","log/native-0.log"):
        print("gs://smallsort-k1-k1-runs/runs/11111111-1111-1111-1111-111111111111/"+rel)
elif "cp" in args:
    url=args[-2]
    with (root/"downloads").open("a") as f:f.write(url+"\n")
    Path(args[-1]).write_text('{"native":{"tests":[{"file":"test.rs","errors":["failure"]}]}}' if url.endswith(".json") else "bounded summary\n")
'''
            path = bindir / "gcloud"; path.write_text(stub); path.chmod(0o755)
            env = dict(os.environ, SERVICE_ROOT=str(root), K1_GCP_KEY=str(key), K1_GCLOUD_CONFIG=str(root / "gconfig"),
                       K1_CACHE=str(root / "cache"), PATH=str(bindir) + ":/usr/bin:/bin")
            run = subprocess.run(["bash", str(tools / "k1g.sh"), "summary", "11111111-1111-1111-1111-111111111111"],
                                 cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout, "bounded summary\n")
            downloaded = (root / "downloads").read_text().splitlines()
            self.assertEqual(len(downloaded), 2)
            self.assertTrue(all("/summary/summary." in url for url in downloaded))
            # A fresh native-field fetch must use the same summaries-only scope.
            shutil.rmtree(root / "cache")
            (root / "downloads").unlink()
            run = subprocess.run(["bash", str(tools / "k1g.sh"), "native-field",
                                  "11111111-1111-1111-1111-111111111111", "0", "errors"],
                                 cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["value"], ["failure"])
            downloaded = (root / "downloads").read_text().splitlines()
            self.assertEqual(len(downloaded), 2)
            self.assertTrue(all("/summary/summary." in url for url in downloaded))


class NativeFieldServiceTests(unittest.TestCase):
    BUILD = "11111111-1111-1111-1111-111111111111"

    def test_cached_field_cli_pages_identity_and_error_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bindir = root / "bin"; bindir.mkdir()
            stub = bindir / "gcloud"
            stub.write_text('#!/bin/sh\ncase " $* " in *" auth list "*) echo fake-account;; *) exit 99;; esac\n')
            stub.chmod(0o755)
            key = root / "fake-key"; key.touch()
            cache = root / "cache" / ("summary-" + self.BUILD) / "summary"
            cache.mkdir(parents=True)
            path = cache / "summary.json"
            summary = fixtures.NativeFieldPageTests().summary()
            summary["run"]["id"] = self.BUILD
            original = json.dumps(summary).encode()
            path.write_bytes(original)
            env = dict(os.environ, K1_GCP_KEY=str(key), K1_GCLOUD_CONFIG=str(root / "gconfig"),
                       K1_CACHE=str(root / "cache"), PATH=str(bindir) + ":/usr/bin:/bin")
            def run(*args):
                return subprocess.run(["bash", str(TOOLS / "k1g.sh"), "native-field", *args],
                                      cwd=root, env=env, capture_output=True, text=True, timeout=10)
            start, received = 0, []
            while True:
                result = run(self.BUILD, "0", "errors", str(start), "80")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertLessEqual(len(result.stdout.encode()), k.MAX_MD_BYTES)
                page = json.loads(result.stdout)
                self.assertEqual(page["build_id"], self.BUILD)
                self.assertEqual(page["summary_file"], str(path))
                self.assertEqual(page["summary_sha256"], k.hashlib.sha256(original).hexdigest())
                received.extend(page["value"])
                if page["next_start"] is None:
                    break
                self.assertGreater(page["next_start"], start)
                start = page["next_start"]
            self.assertEqual(len(received), 15)
            for args, message in (((self.BUILD,), "accepts BUILD OFFSET FIELD"),
                    ((self.BUILD, "0", "errors", "0", "1", "extra"), "accepts BUILD OFFSET FIELD"),
                    (("bad", "0", "errors"), "UUID"), ((self.BUILD, "-1", "errors"), "OFFSET"),
                    ((self.BUILD, "0", "errors", "-1"), "START"),
                    ((self.BUILD, "0", "errors", "0", "81"), "COUNT"),
                    ((self.BUILD, "1", "errors"), "native offset"),
                    ((self.BUILD, "0", "missing"), "unknown native field"),
                    ((self.BUILD, "0", "errors", "16"), "exceeds total")):
                with self.subTest(args=args):
                    result = run(*args)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertIn(message, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
            summary["diagnostic_artifacts"]["native"]["tests"][0]["errors"] = ["x" * 20000]
            for text, message in ((json.dumps(summary), "one native field unit"),
                    ("{", "Expecting"), ("null", "summary must be an object"),
                    ('{"native":{"tests":null}}', "no structured native report"),
                    ('{"native":{"tests":[null]}}', "native record must be an object"),
                    ('{"diagnostic_artifacts":null}', "no structured native report")):
                with self.subTest(message=message):
                    path.write_text(text)
                    result = run(self.BUILD, "0", "errors")
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("page-native-field: " + message, result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertNotIn("Traceback", result.stderr)
            path.unlink()
            result = run(self.BUILD, "0", "errors")
            self.assertEqual(result.returncode, 2)
            self.assertIn("page-native-field:", result.stderr)


if __name__ == "__main__":
    unittest.main()
