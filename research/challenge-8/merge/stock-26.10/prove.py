#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only exact-source admission and pure merge geometry proof harness."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
# Keep the strict, previously accepted rejection classifier at its original
# path and pin. This copied harness never adapts classifier semantics.
FROZEN = HERE.parents[1] / "networks/prove.py"
FROZEN_SHA256 = "994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4"
GEOMETRY = HERE / "geometry.c"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


SIGNATURES = {
    "merge_up": """unsafe fn merge_up<T, F: FnMut(&T, &T) -> bool>(
    mut left_src: *const T,
    mut right_src: *const T,
    mut dst: *mut T,
    is_less: &mut F,
) -> (*const T, *const T, *mut T) {""",
    "merge_down": """unsafe fn merge_down<T, F: FnMut(&T, &T) -> bool>(
    mut left_src: *const T,
    mut right_src: *const T,
    mut dst: *mut T,
    is_less: &mut F,
) -> (*const T, *const T, *mut T) {""",
    "bidirectional_merge": """unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &[T],
    dst: *mut T,
    is_less: &mut F,
) {""",
}

OPERATIONS = {
    "merge_up": [
        "unsafe {",
        "let is_l = !is_less(&*right_src, &*left_src);",
        "let src = if is_l { left_src } else { right_src };",
        "ptr::copy_nonoverlapping(src, dst, 1);",
        "right_src = right_src.add(!is_l as usize);",
        "left_src = left_src.add(is_l as usize);",
        "dst = dst.add(1);",
        "}",
        "(left_src, right_src, dst)",
    ],
    "merge_down": [
        "unsafe {",
        "let is_l = !is_less(&*right_src, &*left_src);",
        "let src = if is_l { right_src } else { left_src };",
        "ptr::copy_nonoverlapping(src, dst, 1);",
        "right_src = right_src.wrapping_sub(is_l as usize);",
        "left_src = left_src.wrapping_sub(!is_l as usize);",
        "dst = dst.sub(1);",
        "}",
        "(left_src, right_src, dst)",
    ],
    "bidirectional_merge": [
        "let len = v.len();", "let src = v.as_ptr();",
        "let len_div_2 = len / 2;", "unsafe {",
        "intrinsics::assume(len_div_2 != 0);", "}", "unsafe {",
        "let mut left = src;", "let mut right = src.add(len_div_2);",
        "let mut dst = dst;", "let mut left_rev = src.add(len_div_2 - 1);",
        "let mut right_rev = src.add(len - 1);",
        "let mut dst_rev = dst.add(len - 1);",
        "for _ in 0..len_div_2 {",
        "(left, right, dst) = merge_up(left, right, dst, is_less);",
        "(left_rev, right_rev, dst_rev) = merge_down(left_rev, right_rev, dst_rev, is_less);",
        "}",
        "let left_end = left_rev.wrapping_add(1);",
        "let right_end = right_rev.wrapping_add(1);",
        "if !len.is_multiple_of(2) {",
        "let left_nonempty = left < left_end;",
        "let last_src = if left_nonempty { left } else { right };",
        "ptr::copy_nonoverlapping(last_src, dst, 1);",
        "left = left.add(left_nonempty as usize);",
        "right = right.add((!left_nonempty) as usize);",
        "}",
        "if left != left_end || right != right_end {",
        "panic_on_ord_violation();", "}", "}",
    ],
}

# Body bytes admitted by the previous stock 26.09 source certificate. The new
# full-source pin and shifted locations must not disguise any body change.
ACCEPTED_BODY_SHA256 = {
    "merge_up": "0ca042e27b297c765dcd972bed404d30535e716600c762d84542371fe74bf7ba",
    "merge_down": "0022e177284c62796ea1b944d257a1ebab2573b8c2ee0c6412ae3835e50294c7",
    "bidirectional_merge": "7e312114db3dc90c4e7164d4ff10e1e9df931a6977ae02b89a596aa4f56083d8",
}


def admit_source() -> dict:
    raw = SOURCE.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise RuntimeError("full pinned SmallSort source SHA256 changed")
    source = raw.decode("utf-8")
    certificate = {
        "source_git_commit": "cd371e035c7e573760c43bf934d53e8118ee3e7d",
        "tool_profile": "official-stock-VeriFast-26.10-f76012fb518703b1d98e243ac4f487f16877cfcb; compiler-nightly-2026-09-25",
        "full_source_sha256": SOURCE_SHA256,
        "functions": [],
    }
    for name, signature in SIGNATURES.items():
        if source.count(signature) != 1:
            raise RuntimeError(f"missing or ambiguous exact {name} signature")
        start = source.index(signature)
        end = source.find("\n}\n", start)
        if end == -1:
            raise RuntimeError(f"missing exact closing brace for {name}")
        body = source[start:end + 2]
        entries = []
        for match in re.finditer(r"^.*$", body, re.M):
            line = match.group(0)
            active = line.split("//", 1)[0].strip()
            if active and not active.startswith("unsafe fn") and not active.startswith(
                    ("mut left_src:", "mut right_src:", "mut dst:", "is_less:",
                     ") ->", "v:", "dst:")):
                line_number = source[:start + match.start()].count("\n") + 1
                entries.append({"line": line_number, "statement": active})
        # The signature begins with `unsafe fn` and may span several lines;
        # only lines after its opening brace are executable statements.
        opening = body.index("{") + 1
        closing_line = source[:start].count("\n") + 1 + body.count("\n")
        statement_entries = [entry for entry in entries
                             if source[:start + opening].count("\n") + 1 < entry["line"] < closing_line]
        if [entry["statement"] for entry in statement_entries] != OPERATIONS[name]:
            raise RuntimeError(f"active {name} statements/order changed")
        body_hash = sha(body.encode())
        if body_hash != ACCEPTED_BODY_SHA256[name]:
            raise RuntimeError(f"{name} body bytes differ from the accepted stock 26.09 source")
        if name == "merge_up" and [e["line"] for e in statement_entries if e["statement"].startswith((
                "let is_l", "ptr::copy_nonoverlapping", "right_src =", "left_src =", "dst ="))] != [698, 700, 701, 702, 703]:
            raise RuntimeError("merge_up operation lines changed")
        if name == "merge_down" and [e["line"] for e in statement_entries if e["statement"].startswith((
                "let is_l", "ptr::copy_nonoverlapping", "right_src =", "left_src =", "dst ="))] != [731, 733, 734, 735, 736]:
            raise RuntimeError("merge_down operation lines changed")
        if name == "bidirectional_merge" and [e["line"] for e in statement_entries if e["statement"].startswith((
                "for _", "(left, right", "(left_rev", "let left_end", "let right_end",
                "if !len", "let left_nonempty", "let last_src", "ptr::copy_nonoverlapping",
                "left =", "right =", "if left !=", "panic_on"))] != [811, 812, 813, 816, 817, 820, 821, 822, 823, 824, 825, 831, 832]:
            raise RuntimeError("bidirectional_merge operation lines changed")
        certificate["functions"].append({
            "name": name, "signature": signature,
            "signature_sha256": sha(signature.encode()),
            "body_sha256": body_hash,
            "body_sha256_matches_accepted_stock_26_09": True,
            "first_line": source[:start].count("\n") + 1,
            "statements": statement_entries,
        })
    return certificate


def frozen_classifier():
    if sha(FROZEN.read_bytes()) != FROZEN_SHA256:
        raise RuntimeError("accepted network classifier hash changed")
    spec = importlib.util.spec_from_file_location("frozen_network_prove", FROZEN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen network classifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def negative_case(core: str, name: str, body: list[str], target: str,
                  expected_predicate: str) -> tuple[str, dict]:
    prefix = core.split("lemma void mg_merge_up_access", 1)[0] + "@*/\n"
    source = prefix + "/*@\nlemma void " + name + "()\n    requires true;\n    ensures true;\n{\n"
    source += "\n".join("    " + line for line in body + [target]) + "\n}\n@*/\n"
    line = next(i for i, row in enumerate(source.splitlines(), 1) if "TARGET_NEGATIVE" in row)
    return source, {"target_line": line, "expected_predicate": expected_predicate}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    frozen = frozen_classifier()
    frozen.require_hosted()
    certificate = admit_source()
    tool = (args.tool_home / "bin/verifast").resolve(strict=True)
    if not tool.is_file():
        raise RuntimeError("stock VeriFast console not found")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "source-admission.json").write_text(json.dumps(certificate, indent=2) + "\n")
    core = GEOMETRY.read_text()
    if core.count("lemma void mg_merge_up_access") != 1:
        raise RuntimeError("geometry definitions/lemma boundary changed")
    negative_read = negative_case(core, "mg_negative_read_at_n", [
        "int m = 1; int e = 0; int k = 1; int a = 0;",
        "int n = mg_n(m, e);",
        "int right = mg_right(m, k, a);",
        "assert right == n;",
    ], "assert right < n; // TARGET_NEGATIVE_READ", "mg_right(1, 1, 0) < mg_n(1, 0)")
    negative_advance = negative_case(core, "mg_negative_both_forward_advance", [
        "int m = 1; int k = 0; int a = 0;",
        "int left_after = a + 1;",
        "int right_after = mg_right(m, k, a) + 1;",
        "assert left_after == 1 && right_after == 2;",
    ], "assert left_after + right_after == m + k + 1; // TARGET_NEGATIVE_ADVANCE", "((0 + 1) + (mg_right(1, 0, 0) + 1)) = ((1 + 0) + 1)")
    negative_wrap = negative_case(core, "mg_negative_read_wrapped_left", [
        "int m = 1; int e = 0; int k = 0; int d = 0;",
        "assert mg_down_event(m, e, k, d, false) == true;",
        "int left_after = mg_left_rev(m, k, d) - 1;",
        "assert left_after == -1;",
    ], "assert 0 <= left_after; // TARGET_NEGATIVE_WRAP_READ", "0 <= (mg_left_rev(1, 0, 0) - 1)")
    cases = [("merge_geometry_full", core, None),
             ("merge_geometry_negative_read", *negative_read),
             ("merge_geometry_negative_advance", *negative_advance),
             ("merge_geometry_negative_wrap_read", *negative_wrap)]
    manifest = {"scope": "pure arbitrary-length merge cursor geometry; Rust pointer/resource/unwind transfer open",
                "domain": "n>=2, n=2m+e, m>=1, e in {0,1}, independent pair decisions and odd residual branch",
                "posts": "all modeled ordered reads/copies/writes and advances safe; terminal endpoints, scalar guards, write count",
                "tool_profile": "official-stock-VeriFast-26.10-f76012fb518703b1d98e243ac4f487f16877cfcb; compiler-nightly-2026-09-25",
                "actual_source": str(SOURCE.relative_to(ROOT)),
                "source_admission_sha256": sha((evidence / "source-admission.json").read_bytes()),
                "source_admission": certificate,
                "verifast_binary_sha256": sha(tool.read_bytes()),
                "frozen_classifier_sha256": FROZEN_SHA256,
                "cases": []}
    passed = True
    for name, source, expected in cases:
        result = frozen.run_case(tool, evidence, name, source, expected)
        result["boundary"] = "checked pure mathematical geometry; actual Rust pointer/resource/unwind transfer open"
        manifest["cases"].append(result)
        (evidence / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{name}: {'PASS' if result['accepted'] else 'INCONCLUSIVE'}", flush=True)
        passed &= result["accepted"]
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"merge geometry preparation failed: {error}", file=sys.stderr)
        sys.exit(2)
