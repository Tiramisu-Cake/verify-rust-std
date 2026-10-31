#!/usr/bin/env python3
"""P1-CLEAN static proof-name sets: ordinary, cfg-on (controls) and retired (`cfg(any())`).

Usage: python3 -I source_sets.py [REV]  (default: working tree). Prints JSON with the three sets.
Extends scope/source_inventory.py: the merge submodules specdiag (module gated by controls) and
specfix (ordinary module) are included, and `#[cfg(any())]` marks an item as retired in both
cfg settings. A static forecast only; the pinned `kani list` (native inventory) is the authority.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
REPO = K1.parents[2]
spec = importlib.util.spec_from_file_location("predict", K1 / "c3b/predict_inventory.py")
predict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predict)
spec2 = importlib.util.spec_from_file_location("srcinv", K1 / "scope/source_inventory.py")
srcinv = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(srcinv)

ROOT = "library/core/src/slice/sort/shared/smallsort/verify"
PREFIX = "slice::sort::shared::smallsort::verify::"
# (module path, file, cfg class of the module declaration)
MODULES = [(m, f"{m}.rs", "ordinary") for m in
           ("assembly", "comparators", "correct", "merge", "network", "smoke", "types")]
MODULES += [("mutations", "mutations.rs", "controls"),
            ("merge::specdiag", "merge/specdiag.rs", "controls"),
            ("merge::specfix", "merge/specfix.rs", None)]  # None: read from merge.rs


def text_at(rel, rev):
    path = f"{ROOT}/{rel}"
    if rev is None:
        p = REPO / path
        return p.read_text() if p.exists() else ""
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def cfg_class(attrs):
    if re.search(r"#\[\s*cfg\s*\(\s*any\s*\(\s*\)\s*\)\s*\]", attrs):
        return "retired"
    if re.search(r"#\[\s*cfg\s*\(\s*kani_smallsort_controls\s*\)\s*\]", attrs):
        return "controls"
    if re.search(r"#\[\s*cfg\s*\(", attrs):
        raise ValueError(f"unknown cfg: {attrs}")
    return "ordinary"


def combine(*classes):
    order = {"ordinary": 0, "controls": 1, "retired": 2}
    return max(classes, key=order.__getitem__)


def records(module, text):
    masked = predict.mask_comments_strings(text)
    spans, macros = [], {}
    for match in re.finditer(r"\bmacro_rules!\s*(\w+)\s*\{", masked):
        opening = masked.find("{", match.start(), match.end())
        closing = predict.matching(masked, opening, "{", "}")
        spans.append((match.start(), closing + 1))
        _, macro_attrs = srcinv.attributes(masked, match.start())
        body = masked[opening + 1:closing]
        body = re.sub(r"\$\(\s*#\[\$attr\]\s*\)\*", lambda m: " " * len(m[0]), body)
        first = len(body) - len(body.lstrip())
        if body[first:first + 1] != "(":
            continue
        # Every arm: pattern `( ... ) => { ... };`
        pos, generated = first, {}
        while True:
            m = re.compile(r"\s*\(").match(body, pos)
            if not m:
                break
            pstart = m.end() - 1
            pend = predict.matching(body, pstart, "(", ")")
            arrow = re.compile(r"\s*=>\s*\{").match(body, pend + 1)
            if not arrow:
                break
            bstart = arrow.end() - 1
            bend = predict.matching(body, bstart, "{", "}")
            args = predict.split_args(body[pstart + 1:pend])
            positions = {}
            for i, arg in enumerate(args):
                for var in re.finditer(r"\$(\w+)\s*:", arg):
                    positions[var[1]] = i
            arm_body = body[bstart:bend + 1]
            for fn in re.finditer(r"\bfn\s+\$(\w+)\b", arm_body):
                _, attrs = srcinv.attributes(arm_body, fn.start())
                if not re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs):
                    continue
                key = (positions[fn[1]], combine(cfg_class(attrs), cfg_class(macro_attrs)))
                generated.setdefault(key, attrs)
            semi = re.compile(r"\s*;?").match(body, bend + 1)
            pos = semi.end()
        if generated:
            macros[match[1]] = generated
    outside = predict.blank_spans(masked, spans)
    out = []
    for fn in re.finditer(r"\bfn\s+(\w+)\s*(?:<|\()", outside):
        start, attrs = srcinv.attributes(masked, fn.start())
        if not re.search(r"kani\s*::\s*proof(?:_for_contract)?\b", attrs):
            continue
        target = re.search(r"proof_for_contract\(\s*([\w:]+)\s*\)", attrs)
        stubs = re.findall(r"stub_verified\(\s*([\w:]+)\s*\)", attrs)
        out.append(dict(name=PREFIX + module + "::" + fn[1], cls=cfg_class(attrs),
                        line=text.count("\n", 0, start) + 1, pfc=target[1] if target else None,
                        stub_verified=stubs))
    for call in re.finditer(r"\b(\w+)\s*!\s*\(", outside):
        if call[1] not in macros:
            continue
        paren = outside.find("(", call.start(), call.end())
        end = predict.matching(outside, paren, "(", ")")
        args = predict.split_args(outside[paren + 1:end])
        start, attrs = srcinv.attributes(masked, call.start())
        seen = set()
        for (index, cls), proof_attrs in macros[call[1]].items():
            if index >= len(args):
                continue
            arg_attrs = re.match(r"^(?:#\[[^]]+\]\s*)*", args[index].strip())[0]
            name = args[index].strip()[len(arg_attrs):].strip()
            if not re.fullmatch(r"\w+", name) or name in seen:
                continue
            seen.add(name)
            target = re.search(r"proof_for_contract\(\s*([\w:]+)\s*\)", proof_attrs)
            stubs = re.findall(r"stub_verified\(\s*([\w:]+)\s*\)", proof_attrs)
            cls = combine(cls, cfg_class(attrs), cfg_class(arg_attrs) if arg_attrs else "ordinary")
            out.append(dict(name=PREFIX + module + "::" + name, cls=cls,
                            line=text.count("\n", 0, start) + 1, macro=call[1],
                            pfc=target[1] if target else None, stub_verified=stubs))
    return out


def sets(rev=None):
    merge_text = text_at("merge.rs", rev)
    m = re.search(r"((?:#\[[^\]]*\]\s*)*)pub\(super\) mod specfix;", merge_text)
    specfix_cls = cfg_class(m[1]) if m else "absent"
    allrecs = []
    for module, rel, mcls in MODULES:
        text = text_at(rel, rev)
        if not text:
            continue
        mcls = specfix_cls if mcls is None else mcls
        for r in records(module, text):
            r["cls"] = combine(r["cls"], mcls)
            r["file"] = rel
            allrecs.append(r)
    names = [r["name"] for r in allrecs if r["cls"] != "retired"]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        raise ValueError(f"duplicate names: {dup[:5]}")
    ordinary = sorted(r["name"] for r in allrecs if r["cls"] == "ordinary")
    cfg_on = sorted(r["name"] for r in allrecs if r["cls"] in ("ordinary", "controls"))
    retired = sorted(r["name"] for r in allrecs if r["cls"] == "retired")
    return dict(ordinary=ordinary, cfg_on=cfg_on, retired=retired, records=allrecs)


if __name__ == "__main__":
    rev = sys.argv[1] if len(sys.argv) > 1 else None
    s = sets(rev)
    print(json.dumps({k: (v if k != "records" else len(v)) for k, v in s.items()}, indent=1))
