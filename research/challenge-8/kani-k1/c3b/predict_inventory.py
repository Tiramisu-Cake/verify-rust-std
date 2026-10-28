#!/usr/bin/env python3
"""Static, deliberately narrow predictor for SmallSort ordinary Kani proof names.

This understands direct proof attributes and the local macro shapes that emit proof functions in
the six ordinary verify modules. It is a source forecast only; pinned `kani list` remains authority.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = "library/core/src/slice/sort/shared/smallsort/verify"
PREFIX = "slice::sort::shared::smallsort::verify::"
MODULES = ("assembly", "comparators", "correct", "merge", "network", "smoke")
BASELINE = "691dca04d6"


def mask_comments_strings(source: str) -> str:
    """Blank comments and literals while retaining offsets/newlines for simple Rust token scanning."""
    chars = list(source)
    i, n = 0, len(source)

    def blank(a: int, b: int) -> None:
        for j in range(a, b):
            if chars[j] != "\n":
                chars[j] = " "

    while i < n:
        if source.startswith("//", i):
            end = source.find("\n", i)
            end = n if end < 0 else end
            blank(i, end)
            i = end
            continue
        if source.startswith("/*", i):
            start, depth = i, 1
            i += 2
            while i < n and depth:
                if source.startswith("/*", i):
                    depth += 1
                    i += 2
                elif source.startswith("*/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            blank(start, i)
            continue
        # Raw strings, including byte raw strings.
        raw = re.match(r"(?:b)?r(#+)?\"", source[i:])
        if raw:
            hashes = raw.group(1) or ""
            end_token = '"' + hashes
            end = source.find(end_token, i + raw.end())
            end = n if end < 0 else end + len(end_token)
            blank(i, end)
            i = end
            continue
        quote_at = i + 1 if source.startswith(("b\"", "c\""), i) else i
        if source[quote_at:quote_at + 1] == '"':
            start = i
            i = quote_at + 1
            while i < n:
                if source[i] == "\\":
                    i += 2
                elif source[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            blank(start, i)
            continue
        if source[i] == "'":
            # A char literal has a closing quote within a short token; `'a` lifetimes do not.
            j = i + 1
            if j < n and source[j] == "\\":
                j += 2
            else:
                j += 1
            if j < n and source[j] == "'":
                blank(i, j + 1)
                i = j + 1
                continue
        i += 1
    return "".join(chars)


def matching(masked: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    for i in range(start, len(masked)):
        if masked[i] == opening:
            depth += 1
        elif masked[i] == closing:
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f"unbalanced Rust delimiter {opening}{closing} at byte {start}")


def split_args(masked: str) -> list[str]:
    args, start, stack = [], 0, []
    pairs = {"(": ")", "[": "]", "{": "}"}
    for i, char in enumerate(masked):
        if char in pairs:
            stack.append(pairs[char])
        elif stack and char == stack[-1]:
            stack.pop()
        elif char == "," and not stack:
            args.append(masked[start:i].strip())
            start = i + 1
    tail = masked[start:].strip()
    if tail:
        args.append(tail)
    return args


def attached_controls(source: str, position: int) -> bool:
    lines = source[:position].splitlines()
    i = len(lines) - 1
    seen_attr = False
    while i >= 0 and i >= len(lines) - 8:
        line = lines[i].strip()
        if not line or line.startswith(("//", "/*", "*")):
            i -= 1
            continue
        if line.startswith("#["):
            seen_attr = True
            if re.search(r"#\[\s*cfg\s*\(\s*kani_smallsort_controls\s*\)\s*\]", line):
                return True
            i -= 1
            continue
        break
    return False if seen_attr else False


def macro_definitions(source: str, masked: str) -> tuple[list[tuple[int, int]], dict[str, tuple[list[int], list[int]]]]:
    spans: list[tuple[int, int]] = []
    macros: dict[str, tuple[list[int], list[int]]] = {}
    for found in re.finditer(r"\bmacro_rules!\s*([A-Za-z_]\w*)\s*\{", masked):
        body_open = masked.find("{", found.start(), found.end())
        body_close = matching(masked, body_open, "{", "}")
        spans.append((found.start(), body_close + 1))
        name = found.group(1)
        if attached_controls(source, found.start()):
            continue
        body = masked[body_open + 1:body_close]
        pattern_start = len(body) - len(body.lstrip())
        first_close = matching(body, pattern_start, "(", ")") if body[pattern_start:pattern_start + 1] == "(" else -1
        if first_close < 0:
            continue
        pattern_args = split_args(body[pattern_start + 1:first_close])
        positions: dict[str, int] = {}
        for index, arg in enumerate(pattern_args):
            variable = re.search(r"\$(\w+)\s*:", arg)
            if variable:
                positions[variable.group(1)] = index
        generated: list[int] = []
        excluded: list[int] = []
        for fn in re.finditer(r"\bfn\s+\$(\w+)\b", body):
            var = fn.group(1)
            if var not in positions:
                continue
            if attached_controls(source[body_open + 1:body_close], fn.start()):
                excluded.append(positions[var])
            else:
                generated.append(positions[var])
        if generated or excluded:
            macros[name] = (generated, excluded)
    return spans, macros


def blank_spans(masked: str, spans: list[tuple[int, int]]) -> str:
    chars = list(masked)
    for start, end in spans:
        for i in range(start, end):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def module_names(source: str, module: str) -> list[str]:
    masked = mask_comments_strings(source)
    spans, macros = macro_definitions(source, masked)
    outside = blank_spans(masked, spans)
    names: list[str] = []
    proof_re = re.compile(r"#\[\s*kani\s*::\s*proof(?:_for_contract)?\b[^\]]*\]")
    for proof in proof_re.finditer(outside):
        if attached_controls(source, proof.start()):
            continue
        nearby = outside[proof.end():proof.end() + 600]
        fn = re.search(r"\bfn\s+([A-Za-z_]\w*)\s*(?:<|\()", nearby)
        if fn:
            names.append(fn.group(1))

    for call in re.finditer(r"\b([A-Za-z_]\w*)\s*!\s*\(", outside):
        macro = call.group(1)
        if macro not in macros or attached_controls(source, call.start()):
            continue
        paren = outside.find("(", call.start(), call.end())
        close = matching(outside, paren, "(", ")")
        args = split_args(outside[paren + 1:close])
        include, exclude = macros[macro]
        for index in include:
            if index < len(args):
                value = re.match(r"\s*([A-Za-z_]\w*)\b", args[index])
                if value:
                    names.append(value.group(1))
        # Excluded generated names are intentionally omitted; indices are retained for audit clarity.
        _ = exclude
    if len(names) != len(set(names)):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"{module}: duplicate predicted names: {duplicates[:5]}")
    return names


def inventory(revision: str) -> list[str]:
    names = []
    for module in MODULES:
        path = f"{ROOT}/{module}.rs"
        source = subprocess.run(["git", "show", f"{revision}:{path}"], check=True,
                                capture_output=True, text=True).stdout
        names.extend(f"{PREFIX}{module}::{name}" for name in module_names(source, module))
    return sorted(names)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument("--out", default="research/challenge-8/kani-k1/c3b/predicted-ordinary.txt")
    parser.add_argument("--check-baseline", action="store_true")
    args = parser.parse_args()
    current = inventory(args.revision)
    if args.check_baseline:
        baseline = inventory(BASELINE)
        print(f"baseline {BASELINE}: {len(baseline)} names (expected 325)")
        if len(baseline) != 325:
            print("baseline parse count mismatch", flush=True)
            return 1
    Path(args.out).write_text("\n".join(current) + "\n")
    print(f"{args.revision}: {len(current)} predicted ordinary names -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
