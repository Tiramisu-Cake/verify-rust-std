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
    error_line = end + 1
    headers = HEADER.findall(log)
    errors = [line for line in log.splitlines() if "error:" in line]
    executed = re.search(rf"^\s*\d+(?:\.\d+)?s: {re.escape(filename)}\({target},\d+-\d+\): Executing statement$", log, re.M) is not None
    error = re.search(rf"^{re.escape(filename)}\({error_line},\d+-\d+\): error: Assertion might not hold\. \(Cannot prove .+\.\)$", errors[0]) if len(errors) == 1 else None
    ok = status != 0 and headers.count(lemma) == 1 and executed and error is not None and unchanged
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

def check_case(tool, out, filename, lemma, negative, require_index=True):
    directory = out / filename.removesuffix(".c")
    directory.mkdir()
    for name in (("sort4-swo.gh", filename) if filename.startswith("sort4-swo-") else ("sort4-index.gh", filename)):
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
        ok = status == 0 and headers.count(lemma) == 1 and (not require_index or headers.count("s4_index_permutation") == 1) and (not filename.startswith("sort4-swo-") or headers.count("s4_swo_rank_bridge") == 1) and not errors and before == after
        classification = "PASS" if ok else "INCONCLUSIVE"
    if status in (124, 137):
        classification = "INCONCLUSIVE_TIMEOUT"
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
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--component", choices=("index", "order", "range", "swo"), required=True)
    parser.add_argument("--replay-index-evidence", type=Path)
    args = parser.parse_args()
    if any(os.environ.get(k) != v for k,v in (("GITHUB_ACTIONS","true"),("RUNNER_ENVIRONMENT","github-hosted"),("RUNNER_OS","Linux"))):
        parser.error("GitHub-hosted execution only")
    args.tool_home = args.tool_home.resolve()
    args.evidence = args.evidence.resolve()
    args.evidence.mkdir(parents=True, exist_ok=False)
    source_binding(args.evidence)
    replay_ok = replay_index(args.replay_index_evidence,args.evidence) if args.replay_index_evidence else True
    cases = {
        "index": (("sort4-index-lemmas.c", "s4_index_application", False),
                  ("sort4-index-negative.c", "s4_wrong_hi_duplicates_min", True)),
        "order": (("sort4-order-lemmas.c", "s4_rank_order_and_stability", False),
                  ("sort4-order-negative.c", "s4_wrong_equal_middle_order", True)),
        "range": (("sort4-range-lemmas.c", "s4_selected_cells_within_disjoint_spans", False),
                  ("sort4-range-negative.c", "s4_range_wrong_final_endpoint", True)),
        "swo": (("sort4-swo-lemmas.c", "s4_swo_rank_application", False),
                ("sort4-swo-negative.c", "s4_wrong_rank_bridge", True)),
    }[args.component]
    results = []
    for filename, lemma, negative in cases:
        result = check_case(args.tool_home, args.evidence, filename, lemma, negative, require_index=args.component != "swo")
        results.append(result)
        if result["classification"] in {"FALSE_THEOREM_PROVED", "INCONCLUSIVE_TIMEOUT"}:
            break
    gate = replay_ok and len(results) == len(cases) and all(r["classification"] in {"PASS","EXPECTED_TARGET_ASSERTION_FAILURE"} for r in results)
    (args.evidence / "results.json").write_text(json.dumps({"pass": gate, "cases": results}, indent=2) + "\n")
    return 0 if gate else 1

if __name__ == "__main__":
    raise SystemExit(main())
