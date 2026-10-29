#!/usr/bin/env python3
"""Narrow static forecast of this source's proof items; not compiler expansion/kani list."""
import importlib.util
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("predict", HERE.parent / "c3b/predict_inventory.py")
predict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predict)
ROOT = Path(predict.ROOT)
MODULES = (*predict.MODULES, "types", "mutations")
PREFIX = predict.PREFIX
BASELINE = "e96555151df91080fa0ccc106f60ee38a919c50e"
P6 = "6cfc76cb211d088aebaff8a449bcac953e97f942"


def source(module, revision=None):
    path = ROOT / (module + ".rs")
    if revision:
        result = subprocess.run(["git", "show", f"{revision}:{path}"],
                                capture_output=True, text=True)
        if result.returncode:
            return ""
        return result.stdout
    return path.read_text()


def attributes(masked, position):
    """Walk complete preceding attributes, including multiline stub attributes."""
    end = position
    i = end - 1
    while i >= 0:
        while i >= 0 and masked[i].isspace():
            i -= 1
        if i < 0 or masked[i] != "]":
            break
        depth = 1
        j = i - 1
        while j >= 0 and depth:
            depth += (masked[j] == "]") - (masked[j] == "[")
            j -= 1
        if j < 0 or masked[j] != "#":
            break
        i = j - 1
    start = i + 1
    return start, masked[start:end]


def gated(attrs):
    return bool(re.search(r"#\[\s*cfg\s*\(\s*kani_smallsort_controls\s*\)\s*\]", attrs))


def records(module, revision=None):
    text = source(module, revision)
    masked = predict.mask_comments_strings(text)
    spans, macros = [], {}
    for match in re.finditer(r"\bmacro_rules!\s*(\w+)\s*\{", masked):
        opening = masked.find("{", match.start(), match.end())
        closing = predict.matching(masked, opening, "{", "}")
        spans.append((match.start(), closing + 1))
        _, macro_attrs = attributes(masked, match.start())
        body = masked[opening + 1:closing]
        # This macro's optional attribute splice is empty at its sole invocation.
        # Preserve offsets while allowing the surrounding fixed attributes to be read.
        body = re.sub(r"\$\(\s*#\[\$attr\]\s*\)\*", lambda m: " " * len(m[0]), body)
        first = len(body) - len(body.lstrip())
        if body[first:first + 1] != "(":
            continue
        pattern_end = predict.matching(body, first, "(", ")")
        args = predict.split_args(body[first + 1:pattern_end])
        positions = {}
        for i, arg in enumerate(args):
            var = re.search(r"\$(\w+)\s*:", arg)
            if var:
                positions[var[1]] = i
        generated = {}
        for fn in re.finditer(r"\bfn\s+\$(\w+)\b", body):
            _, attrs = attributes(body, fn.start())
            if not re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs):
                continue
            var = fn[1]
            if var not in positions:
                raise ValueError(f"unmapped proof macro variable: {module}/{match[1]}/{var}")
            key = (positions[var], gated(attrs) or gated(macro_attrs))
            generated[key] = attrs
        if generated:
            macros[match[1]] = generated
    outside = predict.blank_spans(masked, spans)
    result = []
    for fn in re.finditer(r"\bfn\s+(\w+)\s*(?:<|\()", outside):
        start, attrs = attributes(masked, fn.start())
        if not re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs):
            continue
        opening = masked.find("{", fn.end())
        closing = predict.matching(masked, opening, "{", "}")
        result.append(dict(name=PREFIX + module + "::" + fn[1], module=module,
                           opt_in=gated(attrs), offset=start, macro=None, args=[],
                           attributes=attrs.strip(), entry=text[start:closing + 1].strip()))
    for call in re.finditer(r"\b(\w+)\s*!\s*\(", outside):
        if call[1] not in macros:
            continue
        paren = outside.find("(", call.start(), call.end())
        end = predict.matching(outside, paren, "(", ")")
        args = predict.split_args(outside[paren + 1:end])
        if call[1] == "unstable_freeze_network_cases":
            assert args[2] == "[]", "optional proof attribute splice requires a new source audit"
        start, attrs = attributes(masked, call.start())
        for (index, control), proof_attrs in macros[call[1]].items():
            name = args[index].strip()
            if not re.fullmatch(r"\w+", name):
                raise ValueError(f"nonliteral proof name: {name}")
            result.append(dict(name=PREFIX + module + "::" + name, module=module,
                               opt_in=control or gated(attrs), offset=start,
                               macro=call[1], args=args, attributes=proof_attrs.strip(),
                               entry=text[start:end + 1].strip() + ";"))
    for r in result:
        r["path"] = str(ROOT / (module + ".rs"))
        r["line"] = text.count("\n", 0, r["offset"]) + 1
    return result


def inventory(revision=None):
    result = [r for module in MODULES for r in records(module, revision)]
    names = [r["name"] for r in result]
    assert len(names) == len(set(names)), "duplicate static proof names"
    return sorted(result, key=lambda r: r["name"])


if __name__ == "__main__":
    import collections
    for revision in (P6, BASELINE, None):
        items = inventory(revision)
        print(revision or "working tree", len(items),
              dict(collections.Counter("opt-in" if r["opt_in"] else "ordinary" for r in items)))
