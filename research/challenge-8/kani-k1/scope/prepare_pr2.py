#!/usr/bin/env python3
"""Create the INTEG Part 2 candidate by removing only budget and positive DIRECT gates."""
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

from prepare_scope import tsv
from source_inventory import BASELINE, HERE, MODULES, ROOT, inventory, records, source
from source_items import CFG, imports, items, key


def associated_proofs(module, current, proofs):
    """Transitive local identifier references; association is a static forecast."""
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
    current_proofs = inventory()
    class_by_name = {r["name"].split("::verify::", 1)[-1]: r["class"]
                     for r in csv.DictReader((HERE / "manifest.tsv").open(), delimiter="\t")}
    allowed = {"budget-deferred", "positive-direct"}
    gates, patches, ungated_text, per_file = [], [], {}, {}
    for module in MODULES:
        before, current_text = source(module, BASELINE), source(module)
        old_by_key = {key(i): i for i in items(before)}
        current = items(current_text)
        associations = associated_proofs(module, current,
                                         [r for r in current_proofs if r["module"] == module])
        edits = []
        for idx, item in enumerate(current):
            if not item["gated"]:
                continue
            old = old_by_key.get(key(item))
            if old and old["gated"]:
                continue
            names = sorted(set(associations[idx]))
            classes = {class_by_name[n.split("::verify::", 1)[-1]] for n in names}
            has_target = bool(classes & allowed)
            safe_helper_classes = allowed | {"preexisting-opt-in"}
            if (not names or not has_target or not classes <= safe_helper_classes or
                    (item["kind"] in ("call", "fn") and not classes <= allowed)):
                continue
            attrs = current_text[item["start"]:item["content"]]
            assert attrs.count(CFG) == 1, item
            pos = item["start"] + attrs.index(CFG)
            assert current_text.startswith(CFG + "\n", pos)
            line_start = current_text.rfind("\n", 0, pos) + 1
            assert current_text[line_start:pos].strip() == ""
            edits.append((line_start, pos + len(CFG) + 1))
            gates.append(dict(file=str(ROOT / (module + ".rs")),
                              line=current_text.count("\n", 0, pos) + 1,
                              item=item["name"], kind=item["kind"],
                              harmonics="|".join(names), harmonic_count=len(names),
                              **{"class": "+".join(sorted(classes))},
                              origin="SCOPE-proof" if item["kind"] in ("call", "fn")
                              else "SCOPE-budget-helper"))
        # The paired insertion macro takes cfg on its Cell proof as a metavariable
        # attribute. These are budget gates in the old P1 selection too.
        for proof in (r for r in current_proofs if r["module"] == module and
                      r["macro"] == "insertion_offset_group_cases" and
                      class_by_name[r["name"].split("::verify::", 1)[-1]] == "budget-deferred"):
            call_start = proof["offset"]
            name = proof["name"].rsplit("::", 1)[-1]
            name_pos = current_text.find(name, call_start)
            assert name_pos >= 0, proof["name"]
            attr_pos = current_text.rfind(CFG, call_start, name_pos)
            assert attr_pos >= call_start and current_text[attr_pos + len(CFG):name_pos].strip() == "", proof["name"]
            line_start = current_text.rfind("\n", 0, attr_pos) + 1
            assert current_text[line_start:attr_pos].strip() == ""
            edits.append((line_start, attr_pos + len(CFG) + 1))
            gates.append(dict(file=str(ROOT / (module + ".rs")),
                              line=current_text.count("\n", 0, attr_pos) + 1,
                              item="macro argument cfg: " + name, kind="macro-argument",
                              harmonics=proof["name"], harmonic_count=1,
                              **{"class": "budget-deferred"}, origin="SCOPE-proof"))
        after = current_text
        for start, end in sorted(edits, reverse=True):
            after = after[:start] + after[end:]
        ungated_text[module] = after
        assert after.count(CFG) == current_text.count(CFG) - len(edits), module
        if edits:
            path = str(ROOT / (module + ".rs"))
            patches.extend(difflib.unified_diff(current_text.splitlines(True), after.splitlines(True),
                                                fromfile="a/" + path, tofile="b/" + path, n=1))
            per_file[module] = len(edits)

    patch = "".join(patches)
    removed = [line for line in patch.splitlines() if line.startswith("-") and not line.startswith("---")]
    added = [line for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++")]
    assert removed and all(line[1:].strip() == CFG for line in removed)
    assert not added and len(removed) == len(gates)
    tsv(HERE / "budget-gates.tsv", gates)
    (HERE / "pr2-ungate.patch").write_text(patch)

    with tempfile.TemporaryDirectory(prefix="smallsort-integ-pr2-") as temp:
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
        expected = sorted(r["name"] for r in current_proofs
                          if class_by_name[r["name"].split("::verify::", 1)[-1]] in
                          {"ordinary", "budget-deferred", "positive-direct"})
        assert ordinary == expected, (len(ordinary), len(expected))
        assert len(ordinary) == 339
        assert Counter(r["name"] for r in after_proofs) == Counter(r["name"] for r in current_proofs)
        expected_optin = {r["name"] for r in current_proofs
                          if class_by_name[r["name"].split("::verify::", 1)[-1]] not in
                          {"ordinary", "budget-deferred", "positive-direct"}}
        assert {r["name"] for r in after_proofs if r["opt_in"]} == expected_optin
        (HERE / "pr2-ordinary.txt").write_text("\n".join(ordinary) + "\n")

    report = dict(result="PASS_STATIC_PR2_FORECAST_ONLY", baseline=BASELINE,
                  patch_applied_to_temporary_source_copy=True, budget_cfg_lines=len(gates),
                  by_file=per_file, gate_classes=dict(Counter(r["class"] for r in gates)),
                  gate_origins=dict(Counter(r["origin"] for r in gates)),
                  ordinary=len(ordinary), expected_p2_candidate_ordinary=339,
                  all_names=len(after_proofs), retained_classes=["retired-duplicate",
                  "timeout-diagnostic", "expected-fail", "deferred-unsupported",
                  "preexisting-opt-in"], patch_only_removes_budget_cfg_lines=True,
                  patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),
                  library_tree=subprocess.check_output(["git", "rev-parse", "HEAD:library"], text=True).strip(),
                  limitations=["Source forecast, not Rust expansion or actual kani list",
                               "Helper-to-harness association uses local token references",
                               "Positive DIRECT in P2 is a candidate; macOS CI is UNKNOWN",
                               "No compilation, Kani, CBMC or CI executed"])
    (HERE / "pr2-static-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
