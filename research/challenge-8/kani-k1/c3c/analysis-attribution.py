#!/usr/bin/env python3
"""Conservative CBMC argv -> printed-harness attribution for Kani summaries.

This helper intentionally does not demangle Rust symbols. Supply a source-bound
mapping of exact Kani metadata `mangled_name` values to `pretty_name` values.
"""
from __future__ import annotations

import os
import re
import shlex
import unittest
from collections.abc import Iterable, Mapping


def argv_tokens(argv: str | bytes | Iterable[str | bytes]) -> list[str]:
    """Decode `/proc/.../cmdline` bytes, a shell-rendered command, or argv tokens."""
    if isinstance(argv, bytes):
        return [x.decode("utf-8", "replace") for x in argv.split(b"\0") if x]
    if isinstance(argv, str):
        return shlex.split(argv)
    return [x.decode("utf-8", "replace") if isinstance(x, bytes) else x for x in argv]


def _function_values(tokens: list[str]) -> list[str]:
    values: list[str] = []
    for i, token in enumerate(tokens):
        if token == "--function" and i + 1 < len(tokens):
            values.append(tokens[i + 1])
        elif token.startswith("--function="):
            values.append(token.partition("=")[2])
    return values


def _manual_model_symbols(tokens: list[str], identities: Iterable[str]) -> set[str]:
    """Find exact v0 identities embedded in positional model paths.

    Kani's manual artifact stem is `<base>_<mangled-name>`; matching is exact
    over a supplied symbol, bounded by the stem separator and artifact suffix.
    It deliberately refuses partial family/identifier substring matches.
    """
    suffixes = (".goto", ".symtab.out", ".symtab", ".out")
    hits: set[str] = set()
    for token in tokens:
        if token.startswith("-"):
            continue
        base = os.path.basename(token)
        for suffix in suffixes:
            if base.endswith(suffix):
                stem = base[: -len(suffix)]
                break
        else:
            continue
        for symbol in identities:
            if symbol.startswith("_R") and stem.endswith("_" + symbol):
                hits.add(symbol)
    return hits


def attribute(argv: str | bytes | Iterable[str | bytes],
              metadata: Mapping[str, str]) -> dict[str, object]:
    """Return direct attribution only for one exact identity and one name.

    `metadata` maps exact Rust/Kani mangled names to displayed harness names.
    Ambiguous, missing, and hashed autoharness model paths remain unresolved.
    """
    tokens = argv_tokens(argv)
    identities = set(metadata)
    fn_hits = set(_function_values(tokens)) & identities
    model_hits = _manual_model_symbols(tokens, identities)
    # When present and recognized, --function is the more precise entry point.
    # If it conflicts with an exact manual model identity, fail closed.
    chosen = fn_hits if fn_hits else model_hits
    if fn_hits and model_hits and fn_hits != model_hits:
        return {"status": "conflicting-identities", "harness": None,
                "mangled": sorted(fn_hits | model_hits)}
    pretty = {metadata[x] for x in chosen}
    if len(chosen) == 1 and len(pretty) == 1:
        symbol = next(iter(chosen))
        return {"status": "direct", "harness": next(iter(pretty)), "mangled": symbol}
    if len(chosen) > 1 or len(pretty) > 1:
        return {"status": "ambiguous-identity", "harness": None,
                "mangled": sorted(chosen)}
    if any("_autoharness" in os.path.basename(t) for t in tokens):
        return {"status": "autoharness-hash-unresolved", "harness": None,
                "mangled": None}
    return {"status": "unresolved", "harness": None, "mangled": None}


class AttributionFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.meta = {
            "_RNvNtCs123_9smallsort15insertion_safety": "slice::sort::shared::smallsort::verify::insertion_safety",
            "_RNvNtCs123_9smallsort12merge_safety": "slice::sort::shared::smallsort::verify::merge_safety",
        }

    def test_manual_model_path_exact_symbol(self) -> None:
        got = attribute(["cbmc", "--no-malloc-may-fail",
                         "/tmp/verify__RNvNtCs123_9smallsort15insertion_safety.symtab.out",
                         "--verbosity", "9"], self.meta)
        self.assertEqual(got["status"], "direct")
        self.assertEqual(got["harness"], self.meta[next(iter(self.meta))])

    def test_function_option_exact_symbol(self) -> None:
        got = attribute(b"cbmc\0--function\0_RNvNtCs123_9smallsort12merge_safety\0model.goto\0",
                        self.meta)
        self.assertEqual(got["status"], "direct")
        self.assertEqual(got["harness"], self.meta["_RNvNtCs123_9smallsort12merge_safety"])

    def test_partial_symbol_does_not_match(self) -> None:
        got = attribute(["cbmc", "/tmp/verify__Rwrong_insertionsafety.goto"], self.meta)
        self.assertEqual(got["status"], "unresolved")

    def test_hashed_autoharness_stays_unresolved(self) -> None:
        got = attribute(["cbmc", "--no-malloc-may-fail", "/tmp/proof_abcd_autoharness.symtab.out"], self.meta)
        self.assertEqual(got["status"], "autoharness-hash-unresolved")

    def test_multiple_recognized_functions_fail_closed(self) -> None:
        got = attribute(["cbmc", "--function", "_RNvNtCs123_9smallsort15insertion_safety",
                         "--function", "_RNvNtCs123_9smallsort12merge_safety"], self.meta)
        self.assertEqual(got["status"], "ambiguous-identity")


if __name__ == "__main__":
    unittest.main()
