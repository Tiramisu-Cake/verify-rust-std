#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only checks of isolated stock VeriFast sort4 ghost theorems."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STD = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
STD_BLOB = "e555fce440872898e47fd5114f32eb15401d07df"
HEADER = re.compile(r"^\s*\d+(?:\.\d+)?s: .*: Verifying function '([^']+)'$", re.M)
SOURCE_MAP = (
    ("a", "v_base.add(c1 as usize)", "s4_a", "c1 ? 1 : 0"),
    ("b", "v_base.add(!c1 as usize)", "s4_b", "c1 ? 0 : 1"),
    ("c", "v_base.add(2 + c2 as usize)", "s4_c", "2 + (c2 ? 1 : 0)"),
    ("d", "v_base.add(2 + (!c2 as usize))", "s4_d", "2 + (c2 ? 0 : 1)"),
    ("min", "hint::select_unpredictable(c3, c, a)", "s4_min", "s4_select(c3, s4_c(c2), s4_a(c1))"),
    ("max", "hint::select_unpredictable(c4, b, d)", "s4_max", "s4_select(c4, s4_b(c1), s4_d(c2))"),
    ("unknown_left", "hint::select_unpredictable(c3, a, hint::select_unpredictable(c4, c, b))", "s4_left", "s4_select(c3, s4_a(c1), s4_select(c4, s4_c(c2), s4_b(c1)))"),
    ("unknown_right", "hint::select_unpredictable(c4, d, hint::select_unpredictable(c3, b, c))", "s4_right", "s4_select(c4, s4_d(c2), s4_select(c3, s4_b(c1), s4_c(c2)))"),
    ("lo", "hint::select_unpredictable(c5, unknown_right, unknown_left)", "s4_lo", "s4_select(c5, s4_right(c1,c2,c3,c4), s4_left(c1,c2,c3,c4))"),
    ("hi", "hint::select_unpredictable(c5, unknown_left, unknown_right)", "s4_hi", "s4_select(c5, s4_left(c1,c2,c3,c4), s4_right(c1,c2,c3,c4))"),
)
COMPARISONS = (
    "let c1 = is_less(&*v_base.add(1), &*v_base);",
    "let c2 = is_less(&*v_base.add(3), &*v_base.add(2));",
    "let c3 = is_less(&*c, &*a);", "let c4 = is_less(&*d, &*b);",
    "let c5 = is_less(&*unknown_right, &*unknown_left);",
)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def source_binding(out):
    source = STD.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(source)).encode() + b"\0" + source).hexdigest()
    if blob != STD_BLOB:
        raise ValueError("pinned SmallSort source changed")
    text = source.decode()
    start = text.index("pub unsafe fn sort4_stable<")
    body = text[start:text.index("\n/// SAFETY:", start)]
    header = (HERE / "sort4-index.gh").read_text()
    mapping = []
    for variable, expression, fixpoint, rhs in SOURCE_MAP:
        runtime = f"let {variable} = {expression};"
        definition = re.search(rf"fixpoint int {fixpoint}\([^{{]*\)\s*\{{\s*return ([^;]+);\s*\}}", header)
        ok = body.count(runtime) == 1 and definition is not None and definition.group(1) == rhs
        mapping.append({"variable": variable, "runtime": runtime, "fixpoint": fixpoint,
                        "rhs": rhs, "source_line": text[:text.index(runtime,start)].count("\n") + 1,
                        "matched": ok})
        if not ok:
            raise ValueError(f"source/formula correspondence changed: {variable}")
    if any(body.count(expression) != 1 for expression in COMPARISONS):
        raise ValueError("five comparison operand expressions changed")
    for i, variable in enumerate(("min", "lo", "hi", "max")):
        destination = "dst" if i == 0 else f"dst.add({i})"
        if body.count(f"ptr::copy_nonoverlapping({variable}, {destination}, 1);") != 1:
            raise ValueError("output source/order/destination offset changed")
    result = {"std_blob": blob, "std_sha256": digest(source), "mapping": mapping,
              "comparisons": COMPARISONS, "boundary": "pure formulas; pointer/callee/runtime bridge unproved"}
    (out / "source-binding.json").write_text(json.dumps(result, indent=2) + "\n")
    (out / "actual-sort4.txt").write_text(body)

def negative_target(log, filename, lemma, source, status, unchanged):
    lines = source.decode().splitlines()
    markers = [i for i, line in enumerate(lines) if line.strip() == "// TARGET_ASSERTION"]
    if len(markers) != 1 or not lines[markers[0]+1].lstrip().startswith("assert "):
        raise ValueError("negative target marker missing/ambiguous")
    start = markers[0] + 1
    end = next(i for i in range(start, len(lines)) if ";" in lines[i])
    target = start + 1
    headers = HEADER.findall(log)
    errors = [line for line in log.splitlines() if "error:" in line]
    executed = re.search(rf"^\s*\d+(?:\.\d+)?s: {re.escape(filename)}\({target},\d+-\d+\): Executing statement$", log, re.M) is not None
    error = re.fullmatch(rf"{re.escape(filename)}\((\d+),(\d+)-(\d+)\): error: Assertion might not hold\. \(Cannot prove (.+)\.\)", errors[0]) if len(errors) == 1 else None
    error_line = int(error.group(1)) if error else None
    location = False
    if error and target <= error_line <= end + 1:
        column, after_column = int(error.group(2)), int(error.group(3))
        line = lines[error_line - 1]
        first_column = len(line) - len(line.lstrip()) + 1
        last_column = line.index(";", 0) + 1 if error_line == end + 1 else len(line)
        # The error must point into this assertion, including a multi-line
        # expression's first line; a neighbouring statement is not accepted.
        location = first_column <= column < after_column <= last_column + 1
    vc = error.group(4) if error else ""
    if filename == "sort4-swo-composition-negative.c":
        # The C1 all-equal mutant must fail the stable middle-ID order, not an
        # unrelated assertion that happens to share the source statement.
        expected = ("s4_less(relation16(false", "s4_equiv(relation16(false",
                    "s4_right(false, false, false, false) < s4_left(false, false, false, false)")
        location = location and all(fragment in vc for fragment in expected)
    ok = status != 0 and headers.count(lemma) == 1 and executed and location and unchanged
    return ok, target, error_line, "\n".join(lines[start:end+1])

def replay_index(saved, out):
    files = list(saved.rglob("sort4-index-negative/result.json"))
    if len(files) != 1:
        raise ValueError("saved N4 negative artifact missing/ambiguous")
    checked = files[0].parents[1]
    environment = (checked.parent / "environment.txt").read_text()
    if "Source SHA: fa74d92a120cc6990e5f65b94b31e72f2fb50d2f" not in environment or "official-stock-26.09" not in environment:
        raise ValueError("saved N4 source/profile binding mismatch")
    results = []
    for filename, lemma, negative in (("sort4-index-lemmas.c","s4_index_application",False),
                                      ("sort4-index-negative.c","s4_wrong_hi_duplicates_min",True)):
        directory = checked / filename.removesuffix(".c")
        original = json.loads((directory / "result.json").read_text())
        hashes = {name: digest((directory / name).read_bytes()) for name in original["before"]}
        unchanged = hashes == original["before"] == original["after"]
        if hashes["sort4-index.gh"] != "f9714e658f859232810adf85913f17e46c9b6ba81fb26552197a39c063067cbc":
            raise ValueError("saved index theorem header identity mismatch")
        log = (directory / "verifast.log").read_text()
        if negative:
            ok,target,end,assertion = negative_target(log,filename,lemma,(directory/filename).read_bytes(),original["verifast_exit"],unchanged)
        else:
            headers = HEADER.findall(log)
            ok = original["verifast_exit"] == 0 and headers.count(lemma) == 1 and headers.count("s4_index_permutation") == 1 and "error:" not in log and unchanged
            target=end=assertion=None
        results.append({"file":filename,"pass":ok,"original_classification":original["classification"],
                        "target_statement_line":target,"target_error_line":end,"target_assertion":assertion})
    gate = all(r["pass"] for r in results)
    (out/"saved-index-derived.json").write_text(json.dumps({"run":37548475221,"source_sha":"fa74d92a120cc6990e5f65b94b31e72f2fb50d2f","pass":gate,"cases":results},indent=2)+"\n")
    print(f"saved N4 index replay: {'PASS' if gate else 'INCONCLUSIVE'}")
    return gate

def replay_network(saved, out):
    """Reclassify only the exact saved C1 proof; never invoke VeriFast here."""
    roots = [p.parent for p in saved.rglob("environment.txt")
             if p.parent.name == "verifast-sort4-swo_network"]
    if len(roots) != 1:
        raise ValueError("saved C1 artifact missing/ambiguous")
    root = roots[0]
    checked = root / "checked"
    environment = (root / "environment.txt").read_text()
    required = (
        "Source SHA: 0383012d9a8e5266c6ac34503b6b886fa795882a",
        "Profile: official-stock-26.09",
        "Source pin: 809de4596839b739dd999f9e462242c835e3af46",
        "Component: swo_network", "Budget: 30 minutes",
        "Hosted: github-hosted/Linux",
        "da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa  /home/runner/work/_temp/verifast-sort4-swo_network/verifast-26.09-linux.tar.gz",
        "dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc  /home/runner/work/_temp/verifast-sort4-swo_network/verifast-26.09/bin/verifast",
        "20018bb55b65e4861763dc3b6b6f19fa08e2f60b53da9f4efe05207586401f59  research/challenge-8/run-verifast-sort4-components.sh",
        "99583bcaa3b0cf8494131de80f2856b896ee9985a4b8ddbb1589f5062d929a93  research/challenge-8/check-sort4-logical.py",
    )
    environment_lines = set(environment.splitlines())
    if not all(line in environment_lines for line in required):
        raise ValueError("saved C1 source/profile/tool identity mismatch")
    if json.loads((checked / "source-binding.json").read_text()) != json.loads((out / "source-binding.json").read_text()):
        raise ValueError("saved C1 actual-source binding differs from current pinned source")
    raw = json.loads((checked / "results.json").read_text())
    if raw["pass"] is not False or len(raw["cases"]) != 2:
        raise ValueError("saved C1 raw two-case outcome changed")
    cases = (("sort4-swo-composition.c", "s4_swo_choice_network", "PASS",
              ("sort4-index.gh", "sort4-order.gh", "sort4-swo.gh", "sort4-swo-composition.c")),
             ("sort4-swo-composition-negative.c", "s4_swo_wrong_equal_middle_order", "INCONCLUSIVE",
              ("sort4-index.gh", "sort4-swo.gh", "sort4-swo-composition-negative.c")))
    results = []
    for index, (filename, lemma, old_class, names) in enumerate(cases):
        directory = checked / filename.removesuffix(".c")
        original = json.loads((directory / "result.json").read_text())
        if raw["cases"][index] != original or original["file"] != filename or original["lemma"] != lemma or original["classification"] != old_class:
            raise ValueError("saved C1 case metadata mismatch")
        before = {name: digest((directory / name).read_bytes()) for name in names}
        if set(original["before"]) != set(names) or before != original["before"] or before != original["after"]:
            raise ValueError("saved C1 proof/header source changed during original run")
        for name in names:
            if digest((HERE / name).read_bytes()) != before[name]:
                raise ValueError(f"current proof/header differs from saved C1: {name}")
            if f"{before[name]}  research/challenge-8/{name}" not in environment_lines:
                raise ValueError(f"saved C1 environment fixture hash mismatch: {name}")
        command = original["command"]
        if command[:4] != ["timeout", "--signal=TERM", "--kill-after=5s", "300s"] or command[5:] != ["-c", "-verbose", "1", filename] or not command[4].endswith("/verifast-26.09/bin/verifast"):
            raise ValueError("saved C1 verifier command differs")
        log = (directory / "verifast.log").read_text()
        headers = HEADER.findall(log)
        errors = [line for line in log.splitlines() if "error:" in line]
        if headers != original["function_headers"] or errors != original["errors"]:
            raise ValueError("saved C1 raw log differs from recorded result")
        if index == 0:
            expected_headers = ("s4_index_permutation", "s4_rank_order_and_stability",
                "s4_swo_laws_at", "s4_equivalent_predecessor", "s4_predecessor_count_equal",
                "s4_equivalent_ranks", "s4_predecessor_count_strict", "s4_predecessor_count_bound",
                "s4_less_rank", "s4_swo_rank_bridge", lemma)
            application = log.rfind(f"Verifying function '{lemma}'")
            ok = (original["verifast_exit"] == 0 and tuple(headers) == expected_headers and
                  not errors and application >= 0 and
                  "Executing return statement" in log[application:] and
                  "Leak check." in log[application:] and
                  log.rstrip().endswith("0 errors found (194 statements verified)"))
            target = error_line = assertion = None
        else:
            ok, target, error_line, assertion = negative_target(
                log, filename, lemma, (directory / filename).read_bytes(),
                original["verifast_exit"], before == original["after"])
            preceding = all(re.search(
                rf"^\s*\d+(?:\.\d+)?s: {re.escape(filename)}\({line},\d+-\d+\): Executing statement$",
                log, re.M) is not None for line in (14, 15, 18, 19))
            ok = (ok and preceding and original["verifast_exit"] == 1 and
                  target == 21 and error_line == 21)
        results.append({"file": filename, "original_classification": old_class,
                        "derived_classification": "PASS" if index == 0 and ok else
                        "EXPECTED_TARGET_ASSERTION_FAILURE" if index == 1 and ok else "INCONCLUSIVE",
                        "pass": ok, "target_statement_line": target,
                        "actual_error_line": error_line, "target_assertion": assertion,
                        "saved_hashes": before})
    negative = checked / "sort4-swo-composition-negative"
    source = (negative / "sort4-swo-composition-negative.c").read_bytes()
    log = (negative / "verifast.log").read_text()
    wrong_location = log.replace("(21,42-44): error:", "(19,42-44): error:")
    wrong_column = log.replace("(21,42-44): error:", "(21,1-2): error:")
    wrong_vc = log.replace("s4_equiv(relation16(false", "unrelated_predicate(relation16(false")
    tests = {"other_assertion_line": wrong_location,
             "outside_assertion_column": wrong_column,
             "wrong_verification_condition": wrong_vc}
    if any(mutant == log for mutant in tests.values()):
        raise ValueError("saved C1 mutation anchor missing")
    rejected = {name: not negative_target(mutant, "sort4-swo-composition-negative.c",
                "s4_swo_wrong_equal_middle_order", source, 1, True)[0]
                for name, mutant in tests.items()}
    gate = all(case["pass"] for case in results) and all(rejected.values())
    (out / "saved-network-derived.json").write_text(json.dumps({
        "run": 37585795831, "source_sha": "0383012d9a8e5266c6ac34503b6b886fa795882a",
        "profile": "official-stock-26.09", "replay_only": True,
        "verifier_invoked": False, "pass": gate, "cases": results,
        "synthetic_mutants_rejected": rejected}, indent=2) + "\n")
    print(f"saved C1 network replay: {'PASS' if gate else 'INCONCLUSIVE'}")
    return gate

def check_case(tool, out, filename, lemma, negative, require_index=True):
    directory = out / filename.removesuffix(".c")
    directory.mkdir()
    if filename == "sort4-swo-composition.c":
        sources = ("sort4-index.gh", "sort4-order.gh", "sort4-swo.gh", filename)
    elif filename == "sort4-swo-composition-negative.c":
        sources = ("sort4-index.gh", "sort4-swo.gh", filename)
    else:
        sources = ("sort4-swo.gh", filename) if filename.startswith("sort4-swo-") else ("sort4-index.gh", filename)
    for name in sources:
        data = (HERE / name).read_bytes()
        if re.search(rb"\bassume(?:_correct)?\s*\(|\blemma_auto\b", data):
            raise ValueError("assumption or automatic lemma in owned fixture")
        (directory / name).write_bytes(data)
    fixture = directory / filename
    before = {p.name: digest(p.read_bytes()) for p in directory.iterdir() if p.suffix in {".c", ".gh"}}
    command = ["timeout", "--signal=TERM", "--kill-after=5s", "300s",
               str(tool / "bin/verifast"), "-c", "-verbose", "1", filename]
    with (directory / "verifast.log").open("wb") as log:
        status = subprocess.run(command, cwd=directory, stdout=log, stderr=subprocess.STDOUT).returncode
    log = (directory / "verifast.log").read_text(errors="replace")
    after = {name: digest((directory / name).read_bytes()) for name in before}
    headers = HEADER.findall(log)
    errors = [line for line in log.splitlines() if "error:" in line]
    target = None
    target_error_line = None
    target_assertion = None
    if negative:
        ok,target,target_error_line,target_assertion = negative_target(log,filename,lemma,fixture.read_bytes(),status,before == after)
        classification = "EXPECTED_TARGET_ASSERTION_FAILURE" if ok else "INCONCLUSIVE"
        if status == 0:
            classification = "FALSE_THEOREM_PROVED"
    else:
        ok = status == 0 and headers.count(lemma) == 1 and (not require_index or headers.count("s4_index_permutation") == 1) and (not filename.startswith("sort4-swo-") or headers.count("s4_swo_rank_bridge") == 1) and (filename != "sort4-swo-composition.c" or headers.count("s4_rank_order_and_stability") == 1) and not errors and before == after
        classification = "PASS" if ok else "INCONCLUSIVE"
    if status == 124:
        classification = "INCONCLUSIVE_TIMEOUT"
    elif status == 137:
        classification = "INCONCLUSIVE_TERMINATED"
    result = {"file": filename, "lemma": lemma, "command": command, "verifast_exit": status,
              "function_headers": headers, "errors": errors, "target_line": target,
              "target_error_line": target_error_line, "target_assertion": target_assertion,
              "before": before, "after": after, "classification": classification,
              "refinement": "not applicable: ghost-only C theorem, no executable Rust adapter"}
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{filename}: {classification}")
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--component", choices=("index", "order", "range", "swo", "swo_network"), required=True)
    parser.add_argument("--replay-index-evidence", type=Path)
    parser.add_argument("--replay-network-evidence", type=Path)
    args = parser.parse_args()
    if any(os.environ.get(k) != v for k,v in (("GITHUB_ACTIONS","true"),("RUNNER_ENVIRONMENT","github-hosted"),("RUNNER_OS","Linux"))):
        parser.error("GitHub-hosted execution only")
    if args.replay_network_evidence and (args.component != "swo_network" or args.replay_index_evidence):
        parser.error("saved C1 replay is only for the swo_network component")
    if not args.replay_network_evidence and args.tool_home is None:
        parser.error("--tool-home is required for verifier cases")
    if args.tool_home is not None:
        args.tool_home = args.tool_home.resolve()
    args.evidence = args.evidence.resolve()
    args.evidence.mkdir(parents=True, exist_ok=False)
    source_binding(args.evidence)
    if args.replay_network_evidence:
        return 0 if replay_network(args.replay_network_evidence.resolve(), args.evidence) else 1
    replay_ok = replay_index(args.replay_index_evidence,args.evidence) if args.replay_index_evidence else True
    cases = {
        "index": (("sort4-index-lemmas.c", "s4_index_application", False),
                  ("sort4-index-negative.c", "s4_wrong_hi_duplicates_min", True)),
        "order": (("sort4-order-lemmas.c", "s4_rank_order_and_stability", False),
                  ("sort4-order-negative.c", "s4_wrong_equal_middle_order", True)),
        "range": (("sort4-range-lemmas.c", "s4_selected_cells_within_disjoint_spans", False),
                  ("sort4-range-negative.c", "s4_range_wrong_final_endpoint", True)),
        "swo_network": (("sort4-swo-composition.c", "s4_swo_choice_network", False),
                        ("sort4-swo-composition-negative.c", "s4_swo_wrong_equal_middle_order", True)),
        "swo": (("sort4-swo-lemmas.c", "s4_swo_rank_application", False),
                ("sort4-swo-negative.c", "s4_wrong_rank_bridge", True)),
    }[args.component]
    results = []
    for filename, lemma, negative in cases:
        result = check_case(args.tool_home, args.evidence, filename, lemma, negative, require_index=args.component != "swo")
        results.append(result)
        if result["classification"] in {"FALSE_THEOREM_PROVED", "INCONCLUSIVE_TIMEOUT", "INCONCLUSIVE_TERMINATED"}:
            break
    gate = replay_ok and len(results) == len(cases) and all(r["classification"] in {"PASS","EXPECTED_TARGET_ASSERTION_FAILURE"} for r in results)
    (args.evidence / "results.json").write_text(json.dumps({"pass": gate, "cases": results}, indent=2) + "\n")
    return 0 if gate else 1

if __name__ == "__main__":
    raise SystemExit(main())
