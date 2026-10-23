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


def domain13_members() -> str:
    """Checked membership-only context, deliberately independent of rel."""
    return (LIST_INCLUDE + "/*@\nlemma void network13_domain_members(list<int> d)\n"
            + f"    requires d == {domain(13)};\n"
            + "    ensures " + " &*&\n            ".join(
                f"mem({i}, d) == true" for i in range(13)) + ";\n{\n"
            + "\n".join(f"    assert mem({i}, d) == true;" for i in range(13))
            + "\n}\n@*/\n")


def composition(n: int, pairs: list[tuple[int, int]], exact: bool = True) -> str:
    rank_proof = prove.threshold_proof(n, pairs)
    rank_dag, rank_outputs, rank_trace = prove.output_dag(n, pairs)
    del rank_dag
    id_dag, id_outputs, id_trace = identity_dag(n, pairs)
    exact_domain = domain(n)
    rank_inputs = ", ".join(f"initial_rank{i}" for i in range(n))

    def projected(expression: str) -> str:
        return re.sub(r"\bx(\d+)\b", lambda m: f"initial_rank{m.group(1)}", expression)

    count = lambda prefix: " + ".join(f"ce_occ({prefix}{i}, q)" for i in range(n))
    def full_post(d: str, separator: str = " &*&\n            ") -> str:
        return separator.join(
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
    if not exact:
        if n != 13:
            raise RuntimeError("symbolic component selection is restricted to N13")
        return (LIST_INCLUDE + rank_proof + prove.IDENTITY_HELPERS + source_core() +
                id_dag + "\n".join(lines + ["@*/", ""]))
    if n == 13:
        lines += [domain13_members().replace(LIST_INCLUDE, "").replace("/*@\n", "").replace("@*/\n", "")]
        # A checked, pure equality chunk delays exposing the literal domain
        # in the export lemma's fresh symbolic context. No heap is described.
        lines += [f"predicate network13_exact_domain(list<int> d) = d == {exact_domain};", "",
                  "predicate network13_original_members(list<int> d) = " +
                  " &*& ".join(f"mem({i}, d) == true" for i in range(n)) + ";", "",
                  "predicate network13_swo_package(fixpoint(int, int, bool) rel, list<int> d) = finite_swo(rel, d) == true;", "",
                  "lemma void network13_domain_package(list<int> d)",
                  f"    requires d == {exact_domain};",
                  "    ensures network13_exact_domain(d) &*& network13_original_members(d);", "{",
                  "    network13_domain_members(d);",
                  "    close network13_original_members(d);",
                  "    close network13_exact_domain(d);", "}", "",
                  "lemma void network13_swo_package_create(fixpoint(int, int, bool) rel, list<int> d)",
                  "    requires finite_swo(rel, d) == true;",
                  "    ensures network13_swo_package(rel, d);", "{",
                  "    close network13_swo_package(rel, d);", "}", "",
                  "lemma void network13_export_members(list<int> d, " +
                  ", ".join(f"int value{i}" for i in range(n)) + ")",
                  "    requires network13_exact_domain(d) &*& " +
                  " &*&\n             ".join(f"mem(value{i}, d) == true" for i in range(n)) + ";",
                  "    ensures " + " &*&\n            ".join(
                      f"mem(value{i}, {exact_domain}) == true" for i in range(n)) + ";", "{",
                  "    open network13_exact_domain(d);"]
        lines += [f"    assert mem(value{i}, {exact_domain}) == true;" for i in range(n)]
        lines += ["}", "",
                  "lemma void network13_finite_swo_export(fixpoint(int, int, bool) rel, list<int> d, int q)",
                  "    requires finite_swo(rel, d) == true &*& network13_original_members(d) &*& network13_exact_domain(d);",
                  "    ensures " + full_post(exact_domain) + ";", "{",
                  "    open network13_original_members(d);",
                  "    network13_finite_swo_composition(rel, d, q);",
                  "    network13_export_members(d, " + ", ".join(id_outputs) + ");"]
        lines += ["}", ""]
        lines += ["lemma void network13_finite_swo_export_packed(fixpoint(int, int, bool) rel, list<int> d, int q)",
                  "    requires network13_swo_package(rel, d) &*& network13_original_members(d) &*& network13_exact_domain(d);",
                  "    ensures " + full_post(exact_domain) + ";", "{",
                  "    open network13_swo_package(rel, d);",
                  "    network13_finite_swo_export(rel, d, q);",
                  "}", ""]
        # Shape5 batches the same pure facts in one ExprAsn when opened.
        # All public/original posts retain the separating-conjunction default.
        # The checked producer still calls the unchanged shape3 body.
        lines += ["predicate network13_exact_result(fixpoint(int, int, bool) rel, int q) = " +
                  full_post(exact_domain, " &&\n            ") + ";", "",
                  "lemma void network13_finite_swo_result_package(fixpoint(int, int, bool) rel, list<int> d, int q)",
                  "    requires network13_swo_package(rel, d) &*& network13_original_members(d) &*& network13_exact_domain(d);",
                  "    ensures network13_exact_result(rel, q);", "{",
                  "    network13_finite_swo_export_packed(rel, d, q);",
                  "    close network13_exact_result(rel, q);",
                  "}", ""]
        # Checked congruence records that a symbolic formal domain equal to the
        # exact source-ID list has precisely the original finite-SWO premise.
        lines += [f"lemma void network{n}_domain_laws_equal(fixpoint(int, int, bool) rel, list<int> d)",
                  f"    requires d == {exact_domain};",
                  f"    ensures finite_swo(rel, d) == finite_swo(rel, {exact_domain});",
                  "{}", ""]
        lines += [f"lemma void network{n}_finite_swo_order(fixpoint(int, int, bool) rel, list<int> d, int q)",
                  f"    requires finite_swo(rel, d) == true &*& d == {exact_domain};"]
    else:
        lines += [f"lemma void network{n}_finite_swo_order(fixpoint(int, int, bool) rel, int q)",
                  f"    requires finite_swo(rel, {exact_domain}) == true;"]
    # The public N13 theorem exports all original facts in one pure formula,
    # so its negative callers do not repeat the measured Sep assumption cost.
    public_separator = " &&\n            " if n == 13 else " &*&\n            "
    lines += ["    ensures " + full_post(exact_domain, public_separator) + ";", "{"]
    if n == 13:
        lines += ["    network13_domain_package(d);",
                  "    network13_swo_package_create(rel, d);",
                  "    network13_finite_swo_result_package(rel, d, q);",
                  "    open network13_exact_result(rel, q);"]
    else:
        lines += [f"    assert mem({i}, {exact_domain}) == true;" for i in range(n)]
        lines += [f"    network{n}_finite_swo_composition(rel, {exact_domain}, q);"]
    lines += ["}", "@*/", ""]
    return (LIST_INCLUDE + rank_proof + prove.IDENTITY_HELPERS + source_core() + id_dag +
            "\n".join(lines))


def negative_exact_post(kind: str, pairs: list[tuple[int, int]]) -> tuple[str, dict]:
    """Call the full exact theorem, then demand one deliberately false post.

    Membership uses an absent occurrence; order demands strict reversal of
    the guaranteed adjacent order. These controls preserve the checked unit.
    """
    if kind not in ("membership", "order"):
        raise ValueError("unknown exact negative")
    source = composition(13, pairs, exact=True)
    predicate = (f"mem(13, {domain(13)}) == true" if kind == "membership" else
                 "rel(network13_swo_out1(rel), network13_swo_out0(rel)) == true")
    source += (f"/*@\nlemma void network13_negative_{kind}(fixpoint(int, int, bool) rel, list<int> d, int q)\n"
               f"    requires finite_swo(rel, d) == true &*& d == {domain(13)};\n"
               "    ensures true;\n{\n    network13_finite_swo_order(rel, d, q);\n"
               f"    assert {predicate}; // TARGET_NEGATIVE_EXACT\n}}\n@*/\n")
    target = next(i for i, line in enumerate(source.splitlines(), 1)
                  if "TARGET_NEGATIVE_EXACT" in line)
    # Exact stock diagnostic spelling is checked, never inferred from a
    # nonzero exit. An unexpected printer spelling remains INCONCLUSIVE.
    expected = (f"mem(13, {domain(13)}) <==> true" if kind == "membership" else
                "unboxed_bool(@(@(rel, network13_swo_out1(rel)), network13_swo_out0(rel))) <==> true")
    return source, {"target_line": target, "expected_predicate": expected,
                    "expected_bodies": re.findall(r"^lemma void (\w+)\(", source, re.M),
                    "control": kind}


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
    parser.add_argument("--scope", choices=("exact", "symbolic"), default="exact")
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    prove.require_hosted()
    if args.scope == "symbolic" and args.size != 13:
        raise RuntimeError("symbolic component selection is restricted to N13")
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
    if args.scope == "symbolic":
        manifest["scope"] = ("partial component verification: full symbolic-domain "
                             "N13 composition; exact literal-domain specialization remains unaccepted")
        manifest["domain"] = ("symbolic finite-SWO list containing every original "
                              "occurrence ID 0..12")
        manifest["posts"] = ("all 13 output IDs in symbolic domain; all 12 adjacent "
                             "!rel(right,left); complete arbitrary-q multiplicity")
    negative, metadata = negative_missing_equiv_trans()
    composed_name = ("network13_symbolic_swo_composition" if args.scope == "symbolic"
                     else f"network{args.size}_finite_swo_order")
    work = [(f"network{args.size}_generic_swo_bridge", generic_bridge(), None),
            (composed_name, composition(args.size, pairs, args.scope == "exact"), None),
            (f"network{args.size}_negative_missing_equiv_trans", negative, metadata)]
    passed = True
    for name, source, expected in work:
        # R13e: previous stock runs spend 87-119s on already checked rank bodies
        # and another 27-37s on the full SWO network, leaving too little time for
        # exact-domain summary instantiation. Only that complete N13 case gets
        # 300s; all proof predicates/gates and the stock tool stay unchanged.
        original_limit = prove.TIMEOUT_SECONDS
        case_limit = (240 if args.scope == "symbolic" and name == composed_name else
                      300 if args.size == 13 and name == "network13_finite_swo_order" else
                      original_limit)
        prove.TIMEOUT_SECONDS = case_limit
        try:
            result = prove.run_case(tool, evidence, name, source, expected)
        finally:
            prove.TIMEOUT_SECONDS = original_limit
        result["case_timeout_seconds"] = case_limit
        result["boundary"] = ("checked pure ghost lemma contracts, including full SWO "
                              "comparison/equality/rank bounds and composed "
                              "membership/order/multiplicity; no Rust callee summary")
        if args.scope == "symbolic":
            result["scope"] = ("partial component verification; exact literal-domain "
                               "specialization remains unaccepted")
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
