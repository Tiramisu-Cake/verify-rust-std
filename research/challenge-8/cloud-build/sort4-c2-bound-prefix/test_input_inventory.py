#!/usr/bin/env python3
"""Saved-data-only regression for the C2 live tuple / JSON list boundary."""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    producer = load(here.parent / "sort4-native-entry-c1/c2_discovery.py",
                    "c2_discovery_inventory_test")
    consumer = load(here / "driver.py", "c2_bound_inventory_test")
    saved = json.loads((args.evidence / "c2-discovery-result.json").read_text())
    saved_inv = saved["diagnostic"]["ast_inventory"]
    assert consumer.complete_input_inventory(saved_inv)
    assert isinstance(saved_inv["runtime_inventory"]
                      ["c2_fnmut_at_expected_source_line"][0], list)

    ast_text = (args.evidence / "actual-c2-unbound-scaffold-ast.ml").read_text()
    live_inv = producer.unbound_scaffold_ast_inventory(ast_text)
    assert consumer.complete_input_inventory(live_inv)
    assert isinstance(live_inv["runtime_inventory"]
                      ["c2_fnmut_at_expected_source_line"][0], tuple)
    assert json.loads(json.dumps(live_inv)) == saved_inv

    for field, wrong in (("status", "NOT_CONFIRMED"),
                         ("fnmut_count", 4), ("selector_count", 7),
                         ("copy_count", 3)):
        mutant = deepcopy(live_inv)
        target = mutant if field == "status" else mutant["runtime_inventory"]
        target[field] = wrong
        assert not consumer.complete_input_inventory(mutant), field
    for row in ([(224, "std::ops::FnMut::call_mut")],
                [(223, "unexpected::call_mut")],
                [(223, "std::ops::FnMut::call_mut"),
                 (223, "std::ops::FnMut::call_mut")]):
        mutant = deepcopy(live_inv)
        mutant["runtime_inventory"]["c2_fnmut_at_expected_source_line"] = row
        assert not consumer.complete_input_inventory(mutant), row

    profile = json.loads((here / "profile.json").read_text())
    source = (args.evidence / "c2-discovery-fixture/verified/lib.rs").read_bytes()
    operand = b"v_base.add(3), &*v_base.add(2)"
    assert source.count(operand) == 1
    assert consumer.sha(args.evidence / "c2-discovery-fixture/verified/lib.rs") == profile["annotated_source_sha256"]
    swapped = source.replace(operand, b"v_base.add(2), &*v_base.add(3)", 1)
    assert producer.digest(swapped) != profile["annotated_source_sha256"]
    print("PASS: live tuple, saved JSON list, status/count/row/source-operand mutants")


if __name__ == "__main__":
    main()
