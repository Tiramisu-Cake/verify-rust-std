#!/usr/bin/env python3
"""Static source inventory for SmallSort Kani proof harnesses.

This intentionally recognizes the local Rust proof attribute and declarative macro
shapes used by verify.rs. It is a source-level forecast, not a compiler inventory.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE_ROOT = REPO / "library/core/src/slice/sort/shared/smallsort/verify.rs"
PREFIX = "slice::sort::shared::smallsort::verify::"
ORDINARY_EXPECTED = HERE.parent / "integwrapfix/ordinary-expected.txt"
CFG_ON_EXPECTED = HERE / "cfg-on-expected.txt"
HISTORICAL_CFG_ON = HERE.parent / "integwrap/cfg-on-expected.txt"
REPORT = HERE / "source-inventory.json"
CFG_ATTRIBUTE = re.compile(r"#\s*\[\s*cfg\s*\(([^]]*)\)\s*\]")

spec = importlib.util.spec_from_file_location(
    "kani_k1_predict_inventory", HERE.parent / "c3b/predict_inventory.py"
)
predict = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(predict)


def attr_block(masked: str, position: int) -> str:
    """Return all adjacent outer attributes immediately before a Rust item."""
    end = position
    cursor = end - 1
    pieces = []
    while cursor >= 0:
        while cursor >= 0 and masked[cursor].isspace():
            cursor -= 1
        if cursor < 0 or masked[cursor] != "]":
            break
        depth = 1
        left = cursor - 1
        while left >= 0 and depth:
            if masked[left] == "]":
                depth += 1
            elif masked[left] == "[":
                depth -= 1
            left -= 1
        if left < 0 or masked[left] != "#":
            break
        pieces.append(masked[left:cursor + 1])
        cursor = left - 1
    return "\n".join(reversed(pieces))


def gate_state(attrs: str, inherited: tuple[str, ...] = ()) -> tuple[str, ...]:
    cfg_values = [re.sub(r"\s+", "", match.group(1)) for match in CFG_ATTRIBUTE.finditer(attrs)]
    unknown = sorted(set(cfg_values) - {"kani_smallsort_controls", "any()"})
    if unknown:
        raise ValueError(f"unknown cfg attribute(s): {unknown}")
    gates = list(inherited)
    if re.search(r"#\[\s*cfg\s*\(\s*kani_smallsort_controls\s*\)\s*\]", attrs):
        gates.append("kani_smallsort_controls")
    if re.search(r"#\[\s*cfg\s*\(\s*any\s*\(\s*\)\s*\)\s*\]", attrs):
        gates.append("cfg(any())")
    return tuple(dict.fromkeys(gates))


def active(gates: tuple[str, ...], controls: bool) -> bool:
    return "cfg(any())" not in gates and (controls or "kani_smallsort_controls" not in gates)


def resolve_module(parent: Path, module: str) -> Path:
    module_base = parent.parent if parent.name == "mod.rs" else parent.with_suffix("")
    candidates = (module_base / f"{module}.rs", module_base / module / "mod.rs")
    found = [candidate for candidate in candidates if candidate.is_file()]
    if len(found) != 1:
        raise ValueError(f"expected one source for module {module} declared in {parent}; found {found}")
    return found[0]


def module_sources(path: Path, inherited: tuple[str, ...] = (), visited=None):
    """Walk external module declarations in declaration order, with inherited cfg gates."""
    if visited is None:
        visited = set()
    resolved = path.resolve()
    if resolved in visited:
        raise ValueError(f"module cycle or duplicate module path: {resolved}")
    visited.add(resolved)
    text = resolved.read_text()
    masked = predict.mask_comments_strings(text)
    # Validate every cfg attribute in each walked source, including non-harness items.
    gate_state(masked)
    yield resolved, text, inherited
    for found in re.finditer(r"\b(?:pub(?:\([^)]*\))?\s+)?mod\s+([A-Za-z_]\w*)\s*;", masked):
        attrs = attr_block(masked, found.start())
        gates = gate_state(attrs, inherited)
        child = resolve_module(resolved, found.group(1))
        yield from module_sources(child, gates, visited)


def macro_proofs(text: str, masked: str):
    """Map macro names to (argument index, gates, attribute) proof emitters."""
    spans: list[tuple[int, int]] = []
    macros: dict[str, list[dict]] = {}
    for found in re.finditer(r"\bmacro_rules!\s*([A-Za-z_]\w*)\s*\{", masked):
        opening = masked.find("{", found.start(), found.end())
        closing = predict.matching(masked, opening, "{", "}")
        spans.append((found.start(), closing + 1))
        name = found.group(1)
        macro_attrs = attr_block(masked, found.start())
        body = masked[opening + 1:closing]
        first = len(body) - len(body.lstrip())
        if body[first:first + 1] != "(":
            continue
        pattern_end = predict.matching(body, first, "(", ")")
        args = predict.split_args(body[first + 1:pattern_end])
        positions: dict[str, int] = {}
        for index, arg in enumerate(args):
            for variable in re.finditer(r"\$(\w+)\s*:", arg):
                positions[variable.group(1)] = index
        emitters = []
        for fn in re.finditer(r"\bfn\s+\$(\w+)\b", body):
            var = fn.group(1)
            if var not in positions:
                raise ValueError(f"unmapped proof macro variable: {resolved_name(name, var)}")
            arm_start = body.rfind("=>", 0, fn.start()) + 2
            attrs = body[arm_start:fn.start()]
            if not re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs):
                continue
            gates = gate_state(attrs, gate_state(macro_attrs))
            emitters.append(dict(index=positions[var], gates=gates, attribute=attrs.strip()))
        if emitters:
            # Several matcher arms may emit the same proof shape with the same
            # name parameter; one invocation selects one arm, so retain that
            # declaration only once in the static inventory.
            unique = {}
            for emitter in emitters:
                unique[(emitter["index"], emitter["gates"])] = emitter
            macros[name] = list(unique.values())
    return spans, macros


def resolved_name(macro: str, variable: str) -> str:
    return f"{macro}!/$${variable}"


def records(path: Path, text: str, inherited: tuple[str, ...]):
    masked = predict.mask_comments_strings(text)
    spans, macros = macro_proofs(text, masked)
    outside = predict.blank_spans(masked, spans)
    result = []
    for found in re.finditer(r"\bfn\s+([A-Za-z_]\w*)\s*(?:<|\()", outside):
        attrs = attr_block(masked, found.start())
        if not re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs):
            continue
        gates = gate_state(attrs, inherited)
        result.append(dict(name=found.group(1), gates=gates, origin="direct",
                           line=text.count("\n", 0, found.start()) + 1))
    for call in re.finditer(r"\b([A-Za-z_]\w*)\s*!\s*\(", outside):
        macro = call.group(1)
        if macro not in macros:
            continue
        paren = outside.find("(", call.start(), call.end())
        close = predict.matching(outside, paren, "(", ")")
        args = predict.split_args(outside[paren + 1:close])
        call_attrs = attr_block(masked, call.start())
        call_gates = gate_state(call_attrs, inherited)
        for emitter in macros[macro]:
            index = emitter["index"]
            if index >= len(args):
                raise ValueError(f"missing macro argument {index} at {path}:{call.start()}")
            raw_arg = args[index]
            arg = re.sub(r"^(?:\s*#\[[^]]+\]\s*)+", "", raw_arg).strip()
            ident = re.fullmatch(r"([A-Za-z_]\w*)", arg)
            if not ident:
                raise ValueError(f"nonliteral proof name for {macro}! at {path}:{call.start()}: {arg!r}")
            arg_gates = gate_state(raw_arg, inherited)
            gates = tuple(dict.fromkeys((*call_gates, *arg_gates, *emitter["gates"])))
            result.append(dict(name=ident.group(1), gates=gates, origin=f"macro:{macro}",
                               line=text.count("\n", 0, call.start()) + 1))
    return result


def inventory(controls: bool):
    result = []
    files = []
    visited = set()
    for path, text, inherited in module_sources(SOURCE_ROOT):
        if path in visited:
            continue
        visited.add(path)
        rel = path.relative_to(REPO).as_posix()
        files.append(rel)
        for item in records(path, text, inherited):
            gates = item.pop("gates")
            if active(gates, controls):
                module_parts = list(path.relative_to(SOURCE_ROOT.parent).with_suffix("").parts)
                if module_parts and module_parts[0] == SOURCE_ROOT.stem:
                    module_parts = module_parts[1:]
                module_path = "::".join(module_parts)
                result.append({"name": PREFIX + (module_path + "::" if module_path else "") + item["name"],
                               "source": rel, "line": item["line"],
                               "origin": item["origin"], "gates": list(gates)})
    names = [item["name"] for item in result]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate harness names: {duplicates[:10]}")
    return sorted(result, key=lambda item: item["name"]), files


def compare(actual: list[str], expected_path: Path):
    if not expected_path.is_file():
        return dict(status="MISSING_EXPECTED_FILE", expected_file=str(expected_path.relative_to(REPO)),
                    expected_count=None, missing_names=[], unexpected_names=[])
    expected = expected_path.read_text().splitlines()
    duplicate_expected = sorted(name for name, count in Counter(expected).items() if count > 1)
    return dict(status="EXACT" if set(actual) == set(expected) and len(actual) == len(expected)
                and not duplicate_expected else "MISMATCH",
                expected_file=str(expected_path.relative_to(REPO)), expected_count=len(expected),
                expected_sha256=hashlib.sha256(expected_path.read_bytes()).hexdigest(),
                duplicate_expected_names=duplicate_expected,
                missing_names=sorted(set(expected) - set(actual)),
                unexpected_names=sorted(set(actual) - set(expected)))


def historical_cfg_replacement_check(expected_path: Path):
    if not HISTORICAL_CFG_ON.is_file() or not expected_path.is_file():
        return dict(status="MISSING_EXPECTED_FILE",
                    historical_file=str(HISTORICAL_CFG_ON.relative_to(REPO)),
                    expected_file=str(expected_path.relative_to(REPO)))
    old = PREFIX + "correct::contract_insert_tail_u8_prefix"
    new = PREFIX + "network::contract_insert_tail_u8_prefix"
    historical = HISTORICAL_CFG_ON.read_text().splitlines()
    expected = expected_path.read_text().splitlines()
    old_count, new_count = historical.count(old), historical.count(new)
    transformed = [new if name == old else name for name in historical]
    return dict(status="EXACT_FULL_REPLACEMENT" if old_count == 1 and new_count == 0
                and transformed == expected else "MISMATCH",
                historical_file=str(HISTORICAL_CFG_ON.relative_to(REPO)),
                historical_sha256=hashlib.sha256(HISTORICAL_CFG_ON.read_bytes()).hexdigest(),
                expected_file=str(expected_path.relative_to(REPO)),
                expected_sha256=hashlib.sha256(expected_path.read_bytes()).hexdigest(),
                replaced_old_name=old, replacement_name=new,
                historical_old_name_count=old_count,
                historical_replacement_name_count=new_count,
                transformed_count=len(transformed), expected_count=len(expected),
                missing_names=sorted(set(transformed) - set(expected)),
                unexpected_names=sorted(set(expected) - set(transformed)))


def main():
    ordinary, files = inventory(controls=False)
    cfg_on, cfg_files = inventory(controls=True)
    if files != cfg_files:
        raise ValueError("module traversal changed between cfg modes")
    ordinary_names = [item["name"] for item in ordinary]
    cfg_on_names = [item["name"] for item in cfg_on]
    historical_check = historical_cfg_replacement_check(CFG_ON_EXPECTED)
    file_hashes = {rel: hashlib.sha256((REPO / rel).read_bytes()).hexdigest() for rel in files}
    ordinary_expected = compare(ordinary_names, ORDINARY_EXPECTED)
    cfg_on_expected = compare(cfg_on_names, CFG_ON_EXPECTED)
    expected_counts = len(ordinary) == 200 and len(cfg_on) == 382
    checks_pass = (expected_counts and ordinary_expected["status"] == "EXACT"
                   and cfg_on_expected["status"] == "EXACT"
                   and historical_check["status"] == "EXACT_FULL_REPLACEMENT")
    report = dict(
        status="PASS" if checks_pass else "FAIL",
        source_root=str(SOURCE_ROOT.relative_to(REPO)),
        source_files=files,
        source_file_sha256=file_hashes,
        required_counts={"ordinary": 200, "cfg_on": 382},
        exact_counts_pass=expected_counts,
        scope="verify.rs external module tree, including macro-generated proof items",
        method="Rust comments and strings are masked; direct proof attributes, proof-producing local declarative macros, module cfg gates, and kani_smallsort_controls gates are parsed statically.",
        limitation="Source-level name prediction only; it does not expand Rust macros or establish compiler/Kani inventory membership.",
        ordinary=dict(count=len(ordinary), expected=ordinary_expected, harnesses=ordinary),
        cfg_on=dict(count=len(cfg_on), expected=cfg_on_expected,
                    historical_full_replacement=historical_check, harnesses=cfg_on),
    )
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"ordinary_count": len(ordinary), "ordinary_expected": report["ordinary"]["expected"],
                      "cfg_on_count": len(cfg_on), "cfg_on_expected": report["cfg_on"]["expected"],
                      "cfg_on_historical_replacement": historical_check["status"],
                      "source_files": files}, indent=2))
    return 0 if checks_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
