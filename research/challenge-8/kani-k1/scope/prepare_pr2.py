#!/usr/bin/env python3
"""Prepare/apply a budget-only ungate patch to a temporary tree; static inventories only."""
import csv
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from prepare_scope import FAILED, tsv
from source_inventory import BASELINE, HERE, MODULES, ROOT, inventory, records, source
from source_items import CFG, fingerprints, imports, items, key


def was_gated(item, baseline):
    if item["kind"] == "use":
        leaves = {leaf: i["gated"] for i in baseline if i["kind"] == "use"
                  for leaf in imports(i["body"])}
        flags = {leaves[leaf] for leaf in imports(item["body"])}
        assert len(flags) == 1, item
        return flags.pop()
    matches = [i for i in baseline if key(i) == key(item)]
    assert len(matches) == 1, key(item)
    return matches[0]["gated"]


def associated_proofs(module, current, proofs):
    """Transitive local identifier references; association is a static forecast, not resolution."""
    symbols = {}
    for idx, item in enumerate(current):
        if item["kind"] in ("fn", "macro"):
            symbols[item["name"]] = idx
        elif item["kind"] == "use":
            for path in imports(item["body"]):
                symbols[path.rsplit("::", 1)[-1]] = idx
    graph = {idx: {symbols[t] for t in re.findall(r"\b\w+\b", i["body"])
                   if t in symbols} for idx, i in enumerate(current) if i["kind"] != "use"}
    result = {idx: [] for idx in range(len(current))}
    for proof in proofs:
        name = proof["name"].rsplit("::", 1)[-1]
        roots = [idx for idx, i in enumerate(current)
                 if (i["kind"] == "fn" and i["name"] == name) or
                 (i["kind"] == "call" and proof["macro"] is not None
                  and i["body"].startswith(proof["macro"] + "!")
                  and re.search(r"\b" + re.escape(name) + r"\b", i["body"]))]
        assert len(roots) == 1, (module, name, roots)
        pending, seen = roots[:], set()
        while pending:
            idx = pending.pop()
            if idx in seen:
                continue
            seen.add(idx)
            pending.extend(graph.get(idx, set()) - seen)
        for idx in seen:
            result[idx].append(proof["name"])
    return result


def main():
    base, current_proofs = inventory(BASELINE), inventory()
    gates, patches, ungated_text, per_file = [], [], {}, {}
    for module in MODULES:
        before, current_text = source(module, BASELINE), source(module)
        old_items, current = items(before), items(current_text)
        associations = associated_proofs(module, current,
                                        [r for r in current_proofs if r["module"] == module])
        edits = []
        for idx, item in enumerate(current):
            if not item["gated"] or was_gated(item, old_items):
                continue
            attrs = current_text[item["start"]:item["content"]]
            assert attrs.count(CFG) == 1
            pos = item["start"] + attrs.index(CFG)
            assert current_text.startswith(CFG + "\n", pos)
            names = sorted(set(associations[idx]))
            assert names, (module, item["name"])
            direct = item["kind"] in ("call", "fn") and any(
                re.search(r"\b" + re.escape(n.rsplit("::", 1)[-1]) + r"\b", item["body"])
                for n in names)
            gates.append(dict(file=str(ROOT / (module + ".rs")),
                              line=current_text.count("\n", 0, pos) + 1,
                              item=item["name"], kind=item["kind"],
                              harmonics="|".join(names),
                              harmonic_count=len(names),
                              origin="SCOPE-proof" if direct else "SCOPE-B-review-helper"))
            edits.append(pos)
        after = current_text
        for pos in sorted(edits, reverse=True):
            after = after[:pos] + after[pos + len(CFG) + 1:]
        ungated_text[module] = after
        assert fingerprints(before) == fingerprints(after), module
        assert after.count(CFG) == before.count(CFG), module
        assert [was_gated(i, old_items) for i in items(after)] == [i["gated"] for i in items(after)]
        if edits:
            path = str(ROOT / (module + ".rs"))
            patches.extend(difflib.unified_diff(current_text.splitlines(True), after.splitlines(True),
                                                fromfile="a/" + path, tofile="b/" + path))
            per_file[module] = len(edits)
    patch = "".join(patches)
    removed = [line for line in patch.splitlines() if line.startswith("-") and not line.startswith("---")]
    added = [line for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++")]
    assert removed and all(line == "-" + CFG for line in removed)
    assert not added
    assert len(removed) == len(gates)
    tsv(HERE / "budget-gates.tsv", gates)
    (HERE / "pr2-ungate.patch").write_text(patch)

    with tempfile.TemporaryDirectory(prefix="smallsort-scope-pr2-") as temp:
        tree = Path(temp)
        shutil.copytree(ROOT, tree / ROOT)
        shutil.copy2(ROOT.with_suffix(".rs"), (tree / ROOT).with_suffix(".rs"))
        subprocess.run(["git", "apply", "--check", str(HERE.resolve() / "pr2-ungate.patch")],
                       cwd=tree, check=True, capture_output=True)
        subprocess.run(["git", "apply", str(HERE.resolve() / "pr2-ungate.patch")],
                       cwd=tree, check=True, capture_output=True)
        after_proofs = []
        for module in MODULES:
            text = (tree / ROOT / (module + ".rs")).read_text()
            assert text == ungated_text[module], module
            after_proofs.extend(records(module, text=text))
        ordinary = sorted(r["name"] for r in after_proofs if not r["opt_in"])
        assert ordinary == sorted(r["name"] for r in base if not r["opt_in"])
        assert Counter(r["name"] for r in after_proofs) == Counter(r["name"] for r in base)
        assert {r["name"] for r in after_proofs if r["opt_in"]} == {r["name"] for r in base if r["opt_in"]}
        failed = set((HERE / "controls-failed.txt").read_text().splitlines())
        assert failed == {r["name"] for r in after_proofs if r["opt_in"] and
                          r["name"].split("::verify::", 1)[-1] in FAILED}
        original_failed = subprocess.check_output(
            ["git", "show", "f3785b07:" + str((HERE / "controls-failed.txt").relative_to(Path.cwd()))],
            text=True)
        assert original_failed == (HERE / "controls-failed.txt").read_text()
        (HERE / "pr2-ordinary.txt").write_text("\n".join(ordinary) + "\n")
    report = dict(result="PASS_STATIC_PR2_FORECAST_ONLY", baseline=BASELINE,
                  patch_applied_to_temporary_source_copy=True,
                  budget_cfg_lines=len(gates), by_file=per_file,
                  gate_origins=dict(Counter(r["origin"] for r in gates)),
                  ordinary=len(ordinary), expected_baseline_ordinary=328,
                  all_names=len(after_proofs), pre_existing_opt_in_unchanged=True,
                  controls_failed=len(failed), controls_failed_manifest_unchanged=True,
                  patch_only_removes_budget_cfg_lines=True,
                  patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),
                  library_tree=subprocess.check_output(["git", "rev-parse", "HEAD:library"], text=True).strip(),
                  limitations=["Source forecast, not Rust expansion or kani list",
                               "Helper-to-harness association uses local token references",
                               "Historical CI evidence does not establish PR2 on the new SHA",
                               "No builds or compiler/prover runs"])
    (HERE / "pr2-static-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
