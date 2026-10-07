#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only, source-bound C ghost proofs for the SmallSort networks.

This proves mathematical composition of an *assumed* compare-exchange contract.
It does not verify Rust's swap_if_less, its ownership, or its panic behavior.
Generated C lives only in the Actions evidence directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
SOURCE_SHA256 = "32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959"
CALL_COUNTS = {9: 25, 13: 45}
TIMEOUT_SECONDS = 180


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_hosted() -> None:
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            platform.system() != "Linux"):
        raise RuntimeError("proof execution is restricted to GitHub-hosted Linux Actions")


def extract(size: int) -> tuple[list[tuple[int, int]], list[int]]:
    raw = SOURCE.read_bytes()
    if digest(raw) != SOURCE_SHA256:
        raise RuntimeError("pinned actual SmallSort SHA256 mismatch")
    source = raw.decode("utf-8")
    name = f"sort{size}_optimal"
    marker = f"fn {name}<T, F>(v: &mut [T], is_less: &mut F)"
    if source.count(marker) != 1:
        raise RuntimeError(f"ambiguous actual {name}")
    tail = source.split(marker, 1)[1]
    match = re.match(r"\nwhere\n    F: FnMut\(&T, &T\) -> bool,\n\{\n(.*?)\n\}\n", tail, re.S)
    if not match:
        raise RuntimeError(f"unexpected signature/body for {name}")
    body = match.group(1)
    calls = re.findall(r"^        swap_if_less\(v_base, (\d+), (\d+), is_less\);$", body, re.M)
    if len(calls) != CALL_COUNTS[size]:
        raise RuntimeError(f"unexpected compare-exchange count in {name}: {len(calls)}")
    pairs = [(int(a), int(b)) for a, b in calls]
    if any(not 0 <= a < b < size for a, b in pairs):
        raise RuntimeError(f"invalid index/order in {name}")
    # Fail closed on any additional executable statement, including another call.
    executable = [line.strip() for line in body.splitlines()
                  if line.strip() and not line.strip().startswith("//")]
    expected = [f"if v.len() < {size} {{", "intrinsics::abort();", "}",
                "let v_base = v.as_mut_ptr();", "unsafe {"]
    expected += [f"swap_if_less(v_base, {a}, {b}, is_less);" for a, b in pairs]
    expected += ["}"]
    if executable != expected:
        raise RuntimeError(f"unexpected executable statement in actual {name}")
    first_line = source[:source.index(marker)].count("\n") + 1
    body_offset = source.index(marker) + len(marker) + match.start(1)
    lines = [source[:body_offset + m.start()].count("\n") + 1 for m in
             re.finditer(r"^        swap_if_less\(v_base, \d+, \d+, is_less\);$", body, re.M)]
    return pairs, lines


def heading(title: str, params: str, requires: str = "true") -> list[str]:
    return ["/*@", f"lemma void {title}({params})", f"    requires {requires};",
            "    ensures true;", "{"]


def finish(lines: list[str]) -> str:
    return "\n".join(lines + ["}", "@*/", ""]) + "\n"


def params(prefix: str, n: int, extra: str = "") -> str:
    xs = ", ".join(f"int {prefix}{i}" for i in range(n))
    return xs + (", " + extra if extra else "")


def boolean_output_dag(n: int, pairs: list[tuple[int, int]]) -> tuple[str, list[str], list[tuple[str, str]]]:
    names = [f"y{i}" for i in range(n)]
    formal = ", ".join(f"bool y{i}" for i in range(n))
    actual = ", ".join(f"y{i}" for i in range(n))
    definitions = ["/*@",
                   "fixpoint bool ce_band(bool left, bool right) { return left && right; }",
                   "fixpoint bool ce_bor(bool left, bool right) { return left || right; }"]
    traces: list[tuple[str, str]] = []

    def reference(name: str) -> str:
        return name if name.startswith("y") else f"{name}({actual})"

    for step, (a, b) in enumerate(pairs):
        left, right = reference(names[a]), reference(names[b])
        lo, hi = f"network{n}_bit_wire{step}_lo", f"network{n}_bit_wire{step}_hi"
        definitions += [f"fixpoint bool {lo}({formal}) {{",
                        f"    return ce_band({left}, {right});",
                        "}",
                        f"fixpoint bool {hi}({formal}) {{",
                        f"    return ce_bor({left}, {right});",
                        "}"]
        names[a], names[b] = lo, hi
        traces.append((reference(lo), reference(hi)))
    outputs: list[str] = []
    for slot, name in enumerate(names):
        output = f"network{n}_bit_out{slot}"
        definitions += [f"fixpoint bool {output}({formal}) {{",
                        f"    return {reference(name)};",
                        "}"]
        outputs.append(f"{output}({actual})")
    definitions += ["@*/", ""]
    return "\n".join(definitions) + "\n", outputs, traces


def binary_proof(n: int, pairs: list[tuple[int, int]]) -> str:
    dag, outputs, traces = boolean_output_dag(n, pairs)
    out = ["// Abstract CE on binary ranks: (left,right) := (left && right,left || right)."]
    projection = lambda expression: re.sub(r"\by(\d+)\b", r"a\1", expression)
    out += ["/*@", f"lemma void network{n}_binary({', '.join(f'bool a{i}' for i in range(n))})",
            "    requires true;",
            "    ensures " + " &*&\n            ".join(
                f"!({projection(outputs[i])}) || ({projection(outputs[i + 1])})"
                for i in range(n - 1)) + ";",
            "{"]
    out += [f"    bool b{i} = a{i};" for i in range(n)]
    for step, (a, b) in enumerate(pairs):
        out += [f"    bool old{step} = b{a};",
                f"    b{a} = b{a} && b{b};",
                f"    b{b} = old{step} || b{b};",
                f"    assert b{a} == {projection(traces[step][0])};",
                f"    assert b{b} == {projection(traces[step][1])};"]
    for i in range(n - 1):
        out.append(f"    assert !b{i} || b{i + 1};")
    for i in range(n):
        out.append(f"    assert b{i} == {projection(outputs[i])};")
    return dag + finish(out)


RANK_HELPERS = """/*@
// Integer ranks are mathematical (unbounded) VeriFast ghost integers.
fixpoint int ce_min(int left, int right) {
    return left <= right ? left : right;
}
fixpoint int ce_max(int left, int right) {
    return left <= right ? right : left;
}

lemma void threshold_ce(int left, int right, int threshold)
    requires true;
    ensures (ce_min(left, right) > threshold) ==
            ((left > threshold) && (right > threshold)) &*&
            (ce_max(left, right) > threshold) ==
            ((left > threshold) || (right > threshold));
{
    if (left <= right) {
        assert ce_min(left, right) == left;
        assert ce_max(left, right) == right;
    } else {
        assert ce_min(left, right) == right;
        assert ce_max(left, right) == left;
    }
}

lemma void rank_from_threshold(int left, int right)
    requires !(left > right) || (right > right);
    ensures left <= right;
{
    assert !(right > right);
    assert !(left > right);
    assert left <= right;
}
@*/
"""


IDENTITY_HELPERS = """/*@
fixpoint int ce_choose(bool choice, int when_true, int when_false) {
    return choice ? when_true : when_false;
}
fixpoint int ce_occ(int identity, int sought) {
    return identity == sought ? 1 : 0;
}

lemma void pair_count_choice(bool choice, int left, int right, int sought)
    requires true;
    ensures ce_occ(ce_choose(choice, right, left), sought) +
            ce_occ(ce_choose(choice, left, right), sought) ==
            ce_occ(left, sought) + ce_occ(right, sought);
{
    if (choice) {
        assert ce_choose(choice, right, left) == right;
        assert ce_choose(choice, left, right) == left;
    } else {
        assert ce_choose(choice, right, left) == left;
        assert ce_choose(choice, left, right) == right;
    }
}
@*/
"""


def integer_ce(out: list[str], a: int, b: int, step: int,
               state: str = "v", tag: str = "",
               threshold: bool = False) -> None:
    name = f"{tag}{step}"
    out += [f"    int left{name} = {state}{a};",
            f"    int right{name} = {state}{b};"]
    if threshold:
        out.append(f"    threshold_ce(left{name}, right{name}, threshold);")
    out += [f"    {state}{a} = ce_min(left{name}, right{name});",
            f"    {state}{b} = ce_max(left{name}, right{name});"]


def output_dag(n: int, pairs: list[tuple[int, int]]) -> tuple[str, list[str], list[tuple[str, str]]]:
    """Pure, source-order CE wires; every definition has a body, no axioms."""
    names = [f"x{i}" for i in range(n)]
    arguments = ", ".join(f"int x{i}" for i in range(n))
    actuals = ", ".join(f"x{i}" for i in range(n))
    definitions = ["/*@", "// Pure output DAG, one min/max pair per actual Rust call."]
    traces: list[tuple[str, str]] = []

    def reference(name: str) -> str:
        return name if name.startswith("x") else f"{name}({actuals})"

    for step, (a, b) in enumerate(pairs):
        left = reference(names[a])
        right = reference(names[b])
        lo = f"network{n}_wire{step}_lo"
        hi = f"network{n}_wire{step}_hi"
        definitions += [f"fixpoint int {lo}({arguments}) {{",
                        f"    return ce_min({left}, {right});",
                        "}",
                        f"fixpoint int {hi}({arguments}) {{",
                        f"    return ce_max({left}, {right});",
                        "}"]
        names[a], names[b] = lo, hi
        traces.append((reference(lo), reference(hi)))
    outputs: list[str] = []
    for slot, name in enumerate(names):
        output = f"network{n}_out{slot}"
        definitions += [f"fixpoint int {output}({arguments}) {{",
                        f"    return {reference(name)};",
                        "}"]
        outputs.append(f"{output}({actuals})")
    definitions += ["@*/", ""]
    return "\n".join(definitions) + "\n", outputs, traces


def threshold_proof(n: int, pairs: list[tuple[int, int]]) -> str:
    dag, outputs, traces = output_dag(n, pairs)
    binary = binary_proof(n, pairs)
    _, bit_outputs, bit_traces = boolean_output_dag(n, pairs)
    bit_projection = lambda expression: re.sub(
        r"\by(\d+)\b", lambda match: f"(x{match.group(1)} > threshold)", expression)
    bit_inputs = ", ".join(f"x{i} > threshold" for i in range(n))
    out = ["// Universal threshold lemmas use an independent ghost threshold.",
           "// General rank ordering follows by instantiating each threshold at its right output."]
    arguments = ", ".join(f"x{i}" for i in range(n))
    for adjacent in range(n - 1):
        title = f"network{n}_threshold_at_{adjacent}"
        out += ["/*@", f"lemma void {title}({params('x', n, 'int threshold')})",
                "    requires true;",
                f"    ensures !({outputs[adjacent]} > threshold) || ({outputs[adjacent + 1]} > threshold);",
                "{"]
        out += [f"    bool b{i} = x{i} > threshold;" for i in range(n)]
        out += [f"    int r{i} = x{i};" for i in range(n)]
        for step, (a, b) in enumerate(pairs):
            out += [f"    assert b{a} == (r{a} > threshold);",
                    f"    assert b{b} == (r{b} > threshold);",
                    f"    bool oldb{step} = b{a};",
                    f"    b{a} = ce_band(oldb{step}, b{b});",
                    f"    b{b} = ce_bor(oldb{step}, b{b});"]
            integer_ce(out, a, b, step, state="r", tag="second", threshold=True)
            out += [f"    assert b{a} == (r{a} > threshold);",
                    f"    assert b{b} == (r{b} > threshold);",
                    f"    assert b{a} == {bit_projection(bit_traces[step][0])};",
                    f"    assert b{b} == {bit_projection(bit_traces[step][1])};",
                    f"    assert r{a} == {traces[step][0]};",
                    f"    assert r{b} == {traces[step][1]};"]
        out += [f"    network{n}_binary({bit_inputs});",
                f"    assert b{adjacent} == {bit_projection(bit_outputs[adjacent])};",
                f"    assert b{adjacent + 1} == {bit_projection(bit_outputs[adjacent + 1])};",
                f"    assert !b{adjacent} || b{adjacent + 1};",
                f"    assert r{adjacent} == {outputs[adjacent]};",
                f"    assert r{adjacent + 1} == {outputs[adjacent + 1]};",
                f"    assert !({outputs[adjacent]} > threshold) || ({outputs[adjacent + 1]} > threshold);",
                "}", "@*/", ""]
    out += ["/*@", f"lemma void network{n}_general_rank_order({params('x', n)})",
            "    requires true;",
            "    ensures " + " &*&\n            ".join(
                f"{outputs[i]} <= {outputs[i + 1]}" for i in range(n - 1)) + ";",
            "{"]
    for adjacent in range(n - 1):
        out += [f"    network{n}_threshold_at_{adjacent}({arguments}, {outputs[adjacent + 1]});",
                f"    rank_from_threshold({outputs[adjacent]}, {outputs[adjacent + 1]});",
                f"    assert {outputs[adjacent]} <= {outputs[adjacent + 1]};"]
    out += ["}", "@*/", ""]
    return binary + RANK_HELPERS + dag + "\n".join(out) + "\n"


def occurrence(i: int) -> str:
    return f"ce_occ(id{i}, q)"


def permutation_proof(n: int, pairs: list[tuple[int, int]]) -> str:
    out = ["// Identity multiplicity for arbitrary q and arbitrary comparator outcomes."]
    choices = ", ".join(f"bool c{i}" for i in range(len(pairs)))
    out += heading(f"network{n}_identity_permutation", "int q, " + choices)
    out += [f"    int id{i} = {i};" for i in range(n)]
    out.append("    int original_count = " + " + ".join(occurrence(i) for i in range(n)) + ";")
    for step, (a, b) in enumerate(pairs):
        out.append(f"    int pair_count{step} = {occurrence(a)} + {occurrence(b)};")
        out += [f"    int left{step} = id{a};",
                f"    int right{step} = id{b};",
                f"    pair_count_choice(c{step}, left{step}, right{step}, q);",
                f"    id{a} = ce_choose(c{step}, right{step}, left{step});",
                f"    id{b} = ce_choose(c{step}, left{step}, right{step});"]
        out.append(f"    assert {occurrence(a)} + {occurrence(b)} == pair_count{step};")
        out.append("    assert " + " + ".join(occurrence(i) for i in range(n)) + " == original_count;")
    out.append("    assert " + " + ".join(occurrence(i) for i in range(n)) + " == original_count;")
    return IDENTITY_HELPERS + finish(out)


def binary_run(n: int, pairs: list[tuple[int, int]], bits: int) -> tuple[int, ...]:
    state = [(bits >> i) & 1 for i in range(n)]
    for a, b in pairs:
        state[a], state[b] = state[a] & state[b], state[a] | state[b]
    return tuple(state)


def negative_sort(n: int, pairs: list[tuple[int, int]]) -> tuple[str, dict]:
    mutant = pairs[:-1]
    witness = next((bits for bits in range(1 << n)
                    if any(x > y for x, y in zip(binary_run(n, mutant, bits),
                                                  binary_run(n, mutant, bits)[1:]))), None)
    if witness is None:
        raise RuntimeError("omitting final comparator yielded no counterexample")
    state = binary_run(n, mutant, witness)
    bad = next(i for i in range(n - 1) if state[i] > state[i + 1])
    out = ["// Negative: omit the final actual CE; exact fixed binary witness."]
    out += heading(f"network{n}_negative_missing_last_ce", "")
    out += [f"    bool a{i} = {'true' if (witness >> i) & 1 else 'false'};" for i in range(n)]
    for step, (a, b) in enumerate(mutant):
        out += [f"    bool old{step} = a{a};", f"    a{a} = a{a} && a{b};",
                f"    a{b} = old{step} || a{b};"]
    out.append(f"    assert !a{bad} || a{bad + 1}; // TARGET_NEGATIVE_SORT")
    source = finish(out)
    return source, {"witness_bits": witness, "mutant_output": state,
                    "bad_adjacent": bad, "expected_predicate": "!(true) || false", "target_line": source.splitlines().index(
                        f"    assert !a{bad} || a{bad + 1}; // TARGET_NEGATIVE_SORT") + 1}


def negative_permutation(n: int) -> tuple[str, dict]:
    out = ["// Negative: a broken CE duplicates its left input instead of preserving both."]
    out += heading(f"network{n}_negative_duplicate_element", "")
    out += ["    int left = 0;", "    int right = 3;", "    int q = 3;",
            "    int before = (left == q ? 1 : 0) + (right == q ? 1 : 0);",
            "    right = left;",
            "    assert (left == q ? 1 : 0) + (right == q ? 1 : 0) == before; // TARGET_NEGATIVE_PERMUTATION"]
    source = finish(out)
    return source, {"expected_predicate": "((0 = 3 ? 1 : 0) + (0 = 3 ? 1 : 0)) = (0 + 1)", "target_line": source.splitlines().index(
        "    assert (left == q ? 1 : 0) + (right == q ? 1 : 0) == before; // TARGET_NEGATIVE_PERMUTATION") + 1}


def named_bodies(log: str) -> list[str]:
    # Diagnostic note headers repeat a function name without a timestamp.
    return re.findall(r"^\s*\d+(?:\.\d+)?s: .*: Verifying function '([^']+)'$", log, re.M)


def negative_gate(path: Path, source: str, log: str, status: int, metadata: dict,
                  unchanged: bool) -> bool:
    target = metadata["target_line"]
    bodies = re.findall(r"^lemma void (\w+)\(", source, re.M)
    errors = [line for line in log.splitlines() if "error:" in line]
    location = re.search(
        rf"{re.escape(path.name)}\({target},(\d+)-(\d+)\): error: Assertion might not hold\. \(Cannot prove ([^\n]+)\.\)", log)
    assertion_line = source.splitlines()[target - 1]
    columns = (location is not None and
               len(assertion_line) - len(assertion_line.lstrip()) + 1 <= int(location.group(1)) <
               int(location.group(2)) <= assertion_line.index(";") + 2)
    executed = re.search(rf"^\s*\d+(?:\.\d+)?s: .*{re.escape(path.name)}\({target},\d+-\d+\): Executing statement$", log, re.M) is not None
    return (status == 1 and unchanged and len(bodies) == 1 and
            named_bodies(log) == bodies and len(errors) == 1 and columns and executed and
            location.group(3) == metadata["expected_predicate"])


def run_case(tool: Path, evidence: Path, name: str, source: str,
             negative: dict | None = None) -> dict:
    path = evidence / f"{name}.c"
    path.write_text(source)
    if re.search(r"\bassume(?:_correct)?\s*\(|\blemma_auto\b", source):
        raise RuntimeError("unproved assumption/automatic lemma in generated proof")
    before = digest(path.read_bytes())
    command = ["timeout", "--signal=TERM", "--kill-after=5s", f"{TIMEOUT_SECONDS}s",
               str(tool), "-c", "-verbose", "1", str(path)]
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                              timeout=TIMEOUT_SECONDS + 10, check=False)
        exit_code = proc.returncode
        log = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        log = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        log += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        log += "\nTIMEOUT\n"
    log_path = evidence / f"{name}.log"
    log_path.write_text(log)
    changed = digest(path.read_bytes()) != before
    bodies = re.findall(r"^lemma void (\w+)\(", source, re.M)
    visited = named_bodies(log)
    errors = [line for line in log.splitlines() if "error:" in line]
    leak_checks = log.count("Leak check.")
    return_checks = log.count("Executing return statement")
    if negative is None:
        accepted = (exit_code == 0 and not changed and len(bodies) > 0 and
                    visited == bodies and not errors and
                    leak_checks >= len(bodies) and return_checks >= len(bodies) and
                    re.search(r"0 errors found \(\d+ statements verified\)\s*$", log) is not None)
    else:
        accepted = negative_gate(path, source, log, exit_code, negative, not changed)
    rejection_controls = None
    if negative is not None and accepted:
        target = negative["target_line"]
        mutants = {
            "other_line": re.sub(rf"\({target},(\d+-\d+)\): error:", rf"({target - 1},\1): error:", log),
            "other_predicate": log.replace(negative["expected_predicate"], "unrelated_predicate"),
            "no_body_execution": re.sub(r"^.*s: .*: Verifying function .*\n", "", log, flags=re.M),
            "no_target_execution": re.sub(rf"^.*s: .*\({target},\d+-\d+\): Executing statement\n", "", log, flags=re.M),
            "other_column": re.sub(rf"\({target},\d+-\d+\): error:", f"({target},1-2): error:", log),
        }
        rejection_controls = {key: value != log and not negative_gate(path, source, value, exit_code, negative, True)
                              for key, value in mutants.items()}
        rejection_controls["timeout"] = not negative_gate(path, source, log, 124, negative, True)
        rejection_controls["source_changed"] = not negative_gate(path, source, log, exit_code, negative, False)
        accepted = all(rejection_controls.values())
    return {"case": name, "command": command, "exit": exit_code,
            "source_sha256": before, "log_sha256": digest(log_path.read_bytes()),
            "source_unchanged": not changed, "accepted": accepted,
            "negative": negative, "expected_bodies": bodies,
            "classifier_rejection_controls": rejection_controls,
            "visited_bodies": visited, "errors": errors,
            "leak_checks": leak_checks, "return_checks": return_checks,
            "boundary": "universal ghost assertion harness; ensures true is not an exported Rust callee summary",
            "refinement": "not applicable to mathematical C ghosts; Rust bridge not proved",
            "log": str(log_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, choices=(9, 13), required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    require_hosted()
    tool = (args.tool_home / "bin/verifast").resolve(strict=True)
    if not tool.is_file():
        raise RuntimeError("stock VeriFast console not found")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    pairs, lines = extract(args.size)
    manifest = {"size": args.size, "actual_source": str(SOURCE.relative_to(ROOT)),
                "actual_source_sha256": SOURCE_SHA256, "actual_calls": [
                    {"step": i + 1, "a": a, "b": b, "line": line}
                    for i, ((a, b), line) in enumerate(zip(pairs, lines))],
                "verifast_binary_sha256": digest(tool.read_bytes()),
                "abstract_contract": "CE(a,b) writes min(a,b),max(a,b) for a total-order rank; preserves element identities and other positions",
                "cases": []}
    work = [(f"network{args.size}_binary", binary_proof(args.size, pairs), None),
            (f"network{args.size}_threshold", threshold_proof(args.size, pairs), None),
            (f"network{args.size}_identity_permutation", permutation_proof(args.size, pairs), None)]
    source, metadata = negative_sort(args.size, pairs)
    work.append((f"network{args.size}_negative_sort", source, metadata))
    source, metadata = negative_permutation(args.size)
    work.append((f"network{args.size}_negative_permutation", source, metadata))
    all_accepted = True
    for name, source, negative in work:
        result = run_case(tool, evidence, name, source, negative)
        manifest["cases"].append(result)
        (evidence / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{name}: {'PASS' if result['accepted'] else 'INCONCLUSIVE'}", flush=True)
        all_accepted &= result["accepted"]
    return 0 if all_accepted else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"proof preparation failed: {error}", file=sys.stderr)
        sys.exit(2)
