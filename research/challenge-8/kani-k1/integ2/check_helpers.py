#!/usr/bin/env python3
"""Token-use warning forecast under two cfgs; not Rust resolution, expansion or compilation."""
import json
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scope"))
from source_inventory import BASELINE, MODULES, source
HERE = Path(__file__).resolve().parent / "scope"
from source_items import imports, items


def inspect(module, text, controls):
    active = [i for i in items(text) if controls or not i["gated"]]
    candidates, checked = [], []
    dead_allowed = "#![allow(dead_code)]" in text
    for item in active:
        kind, name = item["kind"], item["name"]
        if kind not in ("macro", "fn", "use"):
            continue
        if kind == "fn" and (dead_allowed or "kani::proof" in item["attrs"] or
                             item["body"].lstrip().startswith("pub")):
            continue
        symbols = list(imports(item["body"])) if kind == "use" else [name]
        others = "\n".join(i["body"] for i in active if i is not item and i["kind"] != "use")
        for symbol in symbols:
            short = symbol.rsplit("::", 1)[-1]
            if short == "*":
                continue
            uses = len(re.findall(r"\b" + re.escape(short) + r"\b", others))
            record = dict(module=module, kind=kind, symbol=short, references=uses)
            checked.append(record)
            if uses == 0:
                candidates.append((module, kind, short))
    return candidates, checked


def main():
    report = dict(result="PASS_STATIC_HELPER_USE_FORECAST_ONLY", configurations={})
    for controls in (False, True):
        old, new, checked = [], [], []
        for module in MODULES:
            if module == "mutations" and not controls:
                continue
            old.extend(inspect(module, source(module, BASELINE), controls)[0])
            warnings, records = inspect(module, source(module), controls)
            new.extend(warnings)
            checked.extend(records)
        added = sorted(set(new) - set(old))
        assert not added, added
        cfg = "controls" if controls else "ordinary"
        report["configurations"][cfg] = dict(
            new_unused_candidates=added, existing_candidates=sorted(set(new)),
            checked=checked)
    report["limitations"] = [
        "Top-level cfg and token references only; no Rust name resolution or macro expansion",
        "An occurrence in an unused macro can overestimate use; compiler warning checks remain required",
        "Existing allow(dead_code) in merge/network is preserved; no new allow attributes",
        "No builds, rustc, cargo, Kani or CBMC were run"]
    (HERE / "helper-use-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: dict(new_unused_candidates=v["new_unused_candidates"],
                             existing_candidates=v["existing_candidates"],
                             checked=len(v["checked"]))
                      for k, v in report["configurations"].items()}, indent=2))


if __name__ == "__main__":
    main()
