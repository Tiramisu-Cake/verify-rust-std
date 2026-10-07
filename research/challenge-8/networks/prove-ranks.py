#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only, exact-source SWO-to-rank network composition (C ghosts).

The pure relation is an immutable pullback of keys to occurrence IDs. This
does not prove the Rust comparator, ownership, safety, or unwind obligations.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import prove


HERE = Path(__file__).resolve().parent
CORE = HERE / "swo-rank.c"
LIST_INCLUDE = '//@ #include "list.gh"\n'


def domain(n: int) -> str:
    result = "nil"
    for i in reversed(range(n)):
        result = f"cons({i}, {result})"
    return result


def source_core() -> str:
    core = CORE.read_text()
    if core.count(LIST_INCLUDE) != 1:
        raise RuntimeError("expected exactly one stock list.gh include in SWO core")
    return core.replace(LIST_INCLUDE, "")


def generic_bridge() -> str:
    core = source_core()
    application = """/*@
lemma void swo_rank_application(fixpoint(int, int, bool) rel,
                                list<int> d, int x, int y, int q)
    requires finite_swo(rel, d) == true &*& mem(x, d) == true &*& mem(y, d) == true;
    ensures rel(x, y) == (swo_rank(rel, d, x) < swo_rank(rel, d, y)) &*&
            swo_equiv(rel, x, y) == (swo_rank(rel, d, x) == swo_rank(rel, d, y)) &*&
            0 <= swo_rank(rel, d, x) &*& swo_rank(rel, d, x) < length(d) &*&
            0 <= swo_rank(rel, d, y) &*& swo_rank(rel, d, y) < length(d);
{
    swo_rank_bridge(rel, d, x, y);
    swo_ce(rel, d, x, y, q);
}
@*/
"""
    return LIST_INCLUDE + prove.RANK_HELPERS + prove.IDENTITY_HELPERS + core + application


def identity_dag(n: int, pairs: list[tuple[int, int]]) -> tuple[str, list[str], list[tuple[str, str]]]:
    """One pure ID wire per actual CE output; initial IDs are occurrence indices."""
    names = [str(i) for i in range(n)]
    out = ["/*@", "// Fixed original occurrences; all choices read the same pure rel."]
    trace: list[tuple[str, str]] = []
    for step, (a, b) in enumerate(pairs):
        left, right = names[a], names[b]
        lo = f"network{n}_swo_wire{step}_lo"
        hi = f"network{n}_swo_wire{step}_hi"
        out += [f"fixpoint int {lo}(fixpoint(int, int, bool) rel) {{",
                f"    return ce_choose(rel({right}, {left}), {right}, {left});",
                "}",
                f"fixpoint int {hi}(fixpoint(int, int, bool) rel) {{",
                f"    return ce_choose(rel({right}, {left}), {left}, {right});",
                "}"]
        names[a], names[b] = f"{lo}(rel)", f"{hi}(rel)"
        trace.append((names[a], names[b]))
    outputs = []
    for slot, name in enumerate(names):
        fn = f"network{n}_swo_out{slot}"
        out += [f"fixpoint int {fn}(fixpoint(int, int, bool) rel) {{",
                f"    return {name};", "}"]
        outputs.append(f"{fn}(rel)")
    out += ["@*/", ""]
    return "\n".join(out), outputs, trace


def composition(n: int, pairs: list[tuple[int, int]]) -> str:
    rank_proof = prove.threshold_proof(n, pairs)
    rank_dag, rank_outputs, rank_trace = prove.output_dag(n, pairs)
    del rank_dag
    id_dag, id_outputs, id_trace = identity_dag(n, pairs)
    exact_domain = domain(n)
    rank_inputs = ", ".join(f"initial_rank{i}" for i in range(n))

    def projected(expression: str) -> str:
        return re.sub(r"\bx(\d+)\b", lambda m: f"initial_rank{m.group(1)}", expression)

    count = lambda prefix: " + ".join(f"ce_occ({prefix}{i}, q)" for i in range(n))
    def full_post(d: str) -> str:
        return " &*&\n            ".join(
            [f"mem({v}, {d}) == true" for v in id_outputs] +
            [f"!rel({id_outputs[i + 1]}, {id_outputs[i]})" for i in range(n - 1)] +
            [" + ".join(f"ce_occ({v}, q)" for v in id_outputs) +
             " == " + " + ".join(f"ce_occ({i}, q)" for i in range(n))])

    lines = ["/*@", f"lemma void network{n}_finite_swo_composition(fixpoint(int, int, bool) rel, list<int> d, int q)",
             "    requires finite_swo(rel, d) == true &*& " +
             " &*&\n             ".join(f"mem({i}, d) == true" for i in range(n)) + ";",
             "    ensures " + full_post("d") + ";",
             "{"]
    lines += [f"    int id{i} = {i};" for i in range(n)]
    lines += [f"    int initial_rank{i} = swo_rank(rel, d, {i});" for i in range(n)]
    lines += [f"    int rank{i} = initial_rank{i};" for i in range(n)]
    lines += [f"    assert mem(id{i}, d) == true;" for i in range(n)]
    lines += [f"    assert rank{i} == swo_rank(rel, d, id{i});" for i in range(n)]
    lines.append(f"    int original_count = {count('id')};")
    for step, (a, b) in enumerate(pairs):
        lines += [f"    int left{step} = id{a};",
                  f"    int right{step} = id{b};",
                  f"    int low_rank{step} = rank{a};",
                  f"    int high_rank{step} = rank{b};",
                  f"    swo_ce(rel, d, left{step}, right{step}, q);",
                  f"    id{a} = ce_choose(rel(right{step}, left{step}), right{step}, left{step});",
                  f"    id{b} = ce_choose(rel(right{step}, left{step}), left{step}, right{step});",
                  f"    rank{a} = ce_min(low_rank{step}, high_rank{step});",
                  f"    rank{b} = ce_max(low_rank{step}, high_rank{step});",
                  f"    assert mem(id{a}, d) == true && mem(id{b}, d) == true;",
                  f"    assert rank{a} == swo_rank(rel, d, id{a});",
                  f"    assert rank{b} == swo_rank(rel, d, id{b});",
                  f"    assert id{a} == {id_trace[step][0]};",
                  f"    assert id{b} == {id_trace[step][1]};",
                  f"    assert rank{a} == {projected(rank_trace[step][0])};",
                  f"    assert rank{b} == {projected(rank_trace[step][1])};",
                  f"    assert {count('id')} == original_count;"]
    lines.append(f"    network{n}_general_rank_order({rank_inputs});")
    for i in range(n):
        lines += [f"    assert id{i} == {id_outputs[i]};",
                  f"    assert rank{i} == {projected(rank_outputs[i])};",
                  f"    assert mem({id_outputs[i]}, d) == true;"]
    for i in range(n - 1):
        lines += [f"    assert rank{i} <= rank{i + 1};",
                  f"    assert rank{i} == swo_rank(rel, d, id{i});",
                  f"    assert rank{i + 1} == swo_rank(rel, d, id{i + 1});",
                  f"    swo_ordered_pair(rel, d, id{i}, id{i + 1});",
                  f"    assert !rel(id{i + 1}, id{i});",
                  f"    assert !rel({id_outputs[i + 1]}, {id_outputs[i]});"]
    lines += [f"    assert {count('id')} == original_count;", "}", ""]
    if n == 13:
        # Package the literal once. The wrapper opens a fresh symbolic witness
        # before instantiating the already checked composition theorem.
        lines += [f"lemma void network{n}_exact_domain()",
                  "    requires true;",
                  f"    ensures exists<list<int> >(?d) &*& d == {exact_domain} &*& " +
                  " &*&\n            ".join(f"mem({i}, d) == true" for i in range(n)) + ";",
                  "{",
                  f"    close exists<list<int> >({exact_domain});"]
        lines += [f"    assert mem({i}, {exact_domain}) == true;" for i in range(n)]
        lines += ["}", ""]
    lines += [f"lemma void network{n}_finite_swo_order(fixpoint(int, int, bool) rel, int q)",
              f"    requires finite_swo(rel, {exact_domain}) == true;",
              "    ensures " + full_post(exact_domain) + ";",
              "{"]
    if n == 13:
        lines += [f"    network{n}_exact_domain();",
                  "    open exists<list<int> >(?d);",
                  "    assert finite_swo(rel, d) == true;",
                  f"    network{n}_finite_swo_composition(rel, d, q);"]
    else:
        lines += [f"    assert mem({i}, {exact_domain}) == true;" for i in range(n)]
        lines += [f"    network{n}_finite_swo_composition(rel, {exact_domain}, q);"]
    lines += ["}", "@*/", ""]
    return (LIST_INCLUDE + rank_proof + prove.IDENTITY_HELPERS + source_core() + id_dag +
            "\n".join(lines))


def negative_missing_equiv_trans() -> tuple[str, dict]:
    # Keep one named body: the old fail-closed negative_gate requires precisely one.
    definitions = LIST_INCLUDE + source_core().split("lemma void swo_forall_at", 1)[0] + "@*/\n"
    source = definitions + """/*@
fixpoint bool bad_rel(int x, int y) { return x == 0 && y == 2; }
lemma void negative_missing_swo_equiv_trans()
    requires true;
    ensures true;
{
    list<int> d = cons(0, cons(1, cons(2, nil)));
    assert !bad_rel(0, 0) && !bad_rel(1, 1) && !bad_rel(2, 2);
    assert bad_rel(0, 2) == true;
    assert bad_rel(1, 2) == false;
    assert swo_equiv(bad_rel, 0, 1) == true;
    assert swo_equiv(bad_rel, 1, 2) == true;
    assert swo_equiv(bad_rel, 0, 2) == false;
    assert forall(d, (swo_irref_at)(bad_rel)) == true;
    assert forall(d, (swo_trans_plane)(bad_rel, d)) == true;
    assert forall(d, (swo_equiv_trans_plane)(bad_rel, d)) == false;
    assert finite_swo(bad_rel, d) == false;
    assert swo_rank(bad_rel, d, 1) == 0;
    assert swo_rank(bad_rel, d, 2) == 1;
    assert bad_rel(1, 2) == (swo_rank(bad_rel, d, 1) < swo_rank(bad_rel, d, 2)); // TARGET_NEGATIVE_ORDER
}
@*/
"""
    target_line = next(i for i, line in enumerate(source.splitlines(), 1)
                       if "TARGET_NEGATIVE_ORDER" in line)
    return source, {"expected_predicate":
                    "bad_rel(1, 2) <==> swo_rank(@bad_rel, cons(0, cons(1, cons(2, nil))), 1) < swo_rank(@bad_rel, cons(0, cons(1, cons(2, nil))), 2)",
                    "target_line": target_line,
                    "missing_law": "incomparability transitivity",
                    "counterexample": "only 0<2; 0~1 and 1~2 but 0 !~ 2"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, choices=(9, 13), required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    prove.require_hosted()
    tool = (args.tool_home / "bin/verifast").resolve(strict=True)
    if not tool.is_file():
        raise RuntimeError("stock VeriFast console not found")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    pairs, lines = prove.extract(args.size)
    manifest = {
        "size": args.size, "actual_source": str(prove.SOURCE.relative_to(prove.ROOT)),
        "actual_source_sha256": prove.SOURCE_SHA256,
        "actual_calls": [{"step": i + 1, "a": a, "b": b, "line": line}
                         for i, ((a, b), line) in enumerate(zip(pairs, lines))],
        "verifast_binary_sha256": prove.digest(tool.read_bytes()),
        "domain": "original distinct occurrence IDs 0..N-1; tied keys permitted",
        "relation": "one immutable pure fixpoint on IDs, rel(right,left) at every CE",
        "posts": "all output IDs in original domain; all adjacent !rel(right,left); complete arbitrary-q multiplicity",
        "boundary": "pure exact-source network composition; actual Rust comparator, ownership, memory safety, and unwind unproved",
        "cases": [],
    }
    negative, metadata = negative_missing_equiv_trans()
    work = [(f"network{args.size}_generic_swo_bridge", generic_bridge(), None),
            (f"network{args.size}_finite_swo_order", composition(args.size, pairs), None),
            (f"network{args.size}_negative_missing_equiv_trans", negative, metadata)]
    passed = True
    for name, source, expected in work:
        result = prove.run_case(tool, evidence, name, source, expected)
        result["boundary"] = ("checked pure ghost lemma contracts, including full SWO "
                              "comparison/equality/rank bounds and composed "
                              "membership/order/multiplicity; no Rust callee summary")
        manifest["cases"].append(result)
        (evidence / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{name}: {'PASS' if result['accepted'] else 'INCONCLUSIVE'}", flush=True)
        passed &= result["accepted"]
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"proof preparation failed: {error}", file=sys.stderr)
        sys.exit(2)
