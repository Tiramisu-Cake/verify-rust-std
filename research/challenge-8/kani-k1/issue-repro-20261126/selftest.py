import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path
spec = importlib.util.spec_from_file_location("run", sys.argv[1]); run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
bool_out = """Checking harness bool_order_probe...
RESULTS:
Check 1: bool_order_probe.cover.1
\t - Status: SATISFIED
\t - Description: "cover condition: a != b"
\t - Location: bool_order.rs:5:5 in function bool_order_probe

Check 2: bool_order_probe.assertion.1
\t - Status: FAILURE
\t - Description: "bool less-than matches its truth table"
\t - Location: bool_order.rs:6:5 in function bool_order_probe

SUMMARY:
 ** 1 of 2 failed
Failed Checks: bool less-than matches its truth table

VERIFICATION:- FAILED
"""
p = run.parse(bool_out); assert run.judge("BOOL_PROBE", 1, False, p)[0] == "MATCH", p
assert run.judge("BOOL_PROBE", 0, False, p)[0] == "MISMATCH"
assert run.judge("SUCCESS", 1, False, p)[0] == "MISMATCH"
ok = "Check 1: x.cover.1\n\t - Status: SATISFIED\n\t - Description: \"c\"\n\nVERIFICATION:- SUCCESSFUL\n"
assert run.judge("SUCCESS", 0, False, run.parse(ok))[0] == "MATCH"
assert run.judge("SUCCESS", 0, True, run.parse(ok))[0] == "MISMATCH"
# SUCCESS needs parsed checks and every cover SATISFIED
assert run.judge("SUCCESS", 0, False, run.parse("VERIFICATION:- SUCCESSFUL\n"))[0] == "MISMATCH"
assert run.judge("SUCCESS", 0, False, run.parse(ok.replace("SATISFIED", "UNSATISFIABLE")))[0] == "MISMATCH"
assert run.judge("SUCCESS", 0, False, run.parse(ok.replace("x.cover.1", "x.assertion.1")))[0] == "MISMATCH"
assert run.judge("SUCCESS", 0, False, run.parse(ok.replace("Check 1: x.cover.1\n\t - Status: SATISFIED\n\t - Description: \"c\"\n\n", "Check 1: x.cover.1\n\t - Status: SATISFIED\n\nCheck 2: x.cover.2\n\t - Status: UNREACHABLE\n\n")))[0] == "MISMATCH"
# limits fit the 20 min probes step
assert sum(c[-1] for c in run.COMMANDS) + 4 * run.VERSION_LIMIT <= 20 * 60 - 60
cast = f"""Check 1: array_elem_cast_nonzero.unsupported_construct.1
\t - Status: FAILURE
\t - Description: "{run.CAST_TEXT}"

Check 2: array_elem_cast_nonzero.cover.1
\t - Status: UNREACHABLE
\t - Description: "cover condition: true"

VERIFICATION:- FAILED
"""
assert run.judge("CAST_UNSUPPORTED", 1, False, run.parse(cast))[0] == "MATCH"
assert run.judge("CAST_UNSUPPORTED", 1, False, run.parse(cast.replace("UNREACHABLE", "SATISFIED")))[0] == "MISMATCH"
assert run.judge("CAST_UNSUPPORTED", 1, False, run.parse(cast.replace("4]`", "8]`")))[0] == "MISMATCH"
# Stream scan across chunk boundaries, counts, first three, prefix cap
s = run.Stream("stdout", True)
data = b"a\n" + b"x warning: ign" ; s.feed(data); s.feed(b"oring lt\n"); s.feed(b"warning: ignoring gt\nwarning: ignoring le\nwarning: ignoring ge")
s.close(); assert s.count == 4 and [l["text"] for l in s.first] == ["x warning: ignoring lt", "warning: ignoring gt", "warning: ignoring le"], (s.count, s.first)
big = run.Stream("stdout", True); big.feed(b"warning: ignoring " + b"y" * (run.LINE_LIMIT + 10) + b"\n" + b"z" * run.STREAM_LIMIT); big.close()
assert big.count == 1 and big.first[0]["truncated_at_bytes"] == run.LINE_LIMIT and len(big.kept) == run.STREAM_LIMIT
# run_command: exit code, capture, timeout kill
code, to, sec, st = run.run_command(["bash", "-c", "echo hi; echo err >&2; exit 3"], "/", dict(os.environ), 10, False)
assert (code, to, bytes(st["stdout"].kept), bytes(st["stderr"].kept)) == (3, False, b"hi\n", b"err\n")
code, to, sec, st = run.run_command(["bash", "-c", "sleep 30"], "/", dict(os.environ), 1, False)
assert to and sec < 10
# gate: positive and negative with a scratch repo whose parent stands in for TRIGGER_PARENT
with tempfile.TemporaryDirectory() as d:
    d = Path(d); g = lambda *a: subprocess.run(["git", "-C", str(d), *a], check=True, capture_output=True, text=True).stdout.strip()
    g("init", "-q"); g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "p")
    parent = g("rev-parse", "HEAD"); (d / "f").write_text("x"); g("add", "f"); g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "t")
    sha, tree = g("rev-parse", "HEAD"), g("rev-parse", "HEAD^{tree}")
    run.TRIGGER_PARENT = parent
    ev = d.parent / (d.name + "-event.json"); ev.write_text(json.dumps({"after": sha, "ref": run.REF, "deleted": False, "repository": {"full_name": run.FORK}}))
    env = {"ISSUE_REPRO_TRIGGER_TREE": tree.upper(), "GITHUB_REPOSITORY": run.FORK, "GITHUB_EVENT_NAME": "push", "GITHUB_REF": run.REF,
           "GITHUB_RUN_ATTEMPT": "1", "GITHUB_SHA": sha, "GITHUB_EVENT_PATH": str(ev), "GITHUB_RUN_ID": "1"}
    assert run.gate(env, d)["tree"] == tree
    for key, value in [("ISSUE_REPRO_TRIGGER_TREE", "0" * 40), ("ISSUE_REPRO_TRIGGER_TREE", ""), ("GITHUB_RUN_ATTEMPT", "2"),
                       ("GITHUB_REF", "refs/heads/x"), ("GITHUB_EVENT_NAME", "workflow_dispatch"), ("GITHUB_SHA", parent)]:
        try: run.gate(env | {key: value}, d); raise AssertionError(key)
        except run.RunError: pass
    run.TRIGGER_PARENT = "0" * 40
    try: run.gate(env, d); raise AssertionError("parent")
    except run.RunError: pass
    ev.unlink()
md = run.summary_markdown({"status": "MATCH", "trigger": {"commit": "c", "tree": "t", "run_id": "1", "attempt": "1"}, "sources": run.SOURCES,
    "commands": [{"command": "kani a | b", "exit": 1, "timed_out": False, "terminal": "FAILED", "failed": run.parse(cast)["failed"], "covers": run.parse(cast)["covers"], "expectation": "e", "verdict": "MATCH"},
                 {"command": "kani v", "exit": 1, "timed_out": False, "terminal": "FAILED", "failed": [], "covers": [], "expectation": "e", "verdict": "OBSERVE", "timed_out": False, "bytes": {"stdout": 1, "stderr": 0},
                  "ignoring": {"count": 1, "by_stream": {"stdout": 1, "stderr": 0}, "first_three": [{"stream": "stdout", "text": "warning: ignoring lt", "truncated_at_bytes": None}]}}],
    "versions": {"kani": {"argv": ["kani", "--version"], "exit": 0, "stdout": "kani 0.67.0\n"}}})
assert "kani a \\| b" in md and "warning: ignoring lt" in md
# incremental summary: INCOMPLETE without the scan row renders, state dir comes from RUNNER_TEMP
with tempfile.TemporaryDirectory() as d:
    d = Path(d); s = {"status": "INCOMPLETE", "trigger": {"commit": "c", "tree": "t", "run_id": "1", "attempt": "1"}, "sources": run.SOURCES,
                      "commands": [], "versions": {}}
    text = run.write_summary(d, s)
    assert "INCOMPLETE" in text and "0 of 6 run" in text and "Not run yet." in text and json.loads((d / "summary.json").read_text())["status"] == "INCOMPLETE"
    old_env = os.environ.get("RUNNER_TEMP"); os.environ["RUNNER_TEMP"] = str(d)
    try: assert run.state_dir() == d / "ch8-issue-repro" and (d / "ch8-issue-repro").is_dir()
    finally:
        if old_env is None: os.environ.pop("RUNNER_TEMP")
        else: os.environ["RUNNER_TEMP"] = old_env
print("selftest OK")
