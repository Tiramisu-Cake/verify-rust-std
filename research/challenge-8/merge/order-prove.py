#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only exact bidirectional stable merge and constructive SWO pullback."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PINS = {
    "geometry.c": "4594f159400bcfeeea87e3086e5765472d121dced7385bd2ef216a83bf24dea8",
    "functional-ids.c": "20a7d91564bbf49e8f2e8bb0436a7ccc7eec2e7928f6267486a6ab0f291ab814",
    "functional-prove.py": "e7189989a64d5bf6352596f695ee4f6a8c2199a208c4a0c46b234e362c09e496",
}
SWO_PIN = "e5c3f29d4e5f84284afdf0cd4936054a23ca261f092e77d355895cf359f62051"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load_a():
    for name, digest in PINS.items():
        if sha((HERE / name).read_bytes()) != digest:
            raise RuntimeError("accepted A component changed: " + name)
    spec = importlib.util.spec_from_file_location("accepted_merge_a", HERE / "functional-prove.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def negative_cases(geometry, ids, order):
    # Definitions only, isolating each false functional obligation from helpers.
    source = '//@ #include "nat.gh"\n' + geometry.split("lemma void mg_merge_up_access", 1)[0] + "@*/\n"
    source += ids.split("lemma void fa_threshold_step", 1)[0] + "@*/\n"
    source += order.split("lemma void mb_at", 1)[0] + "@*/\n"
    source += """/*@
fixpoint int neg_equal_key(int id) { return 0; }
fixpoint int neg_reverse_key(int id) { return id == 0 ? 1 : 0; }
@*/
"""
    bodies = [
        ("tie", "false, false", "cons(1, cons(0, nil))", "neg_equal_key",
         "mb_lt(neg_equal_key, 1, 0) == true", "mb_lt(neg_equal_key, 1, 0) = true"),
        ("comparator", "true, true", "cons(0, cons(1, nil))", "neg_reverse_key",
         "neg_reverse_key(0) <= neg_reverse_key(1)", "neg_reverse_key(0) <= neg_reverse_key(1)"),
    ]
    result = []
    for label, choice, output, key, assertion, predicate in bodies:
        unit = source + f"""/*@
lemma void mb_negative_{label}()
    requires true;
    ensures true;
{{
    list<pair<bool,bool> > ds = cons(pair({choice}),nil);
    assert mg_guard_pass(1,0,mg_end_a(ds,0),mg_end_d(ds,0),false)==true;
    assert fa_output(1,0,0,0,0,ds,false)=={output};
    assert fa_count(fa_output(1,0,0,0,0,ds,false),0)==1;
    assert fa_count(fa_output(1,0,0,0,0,ds,false),1)==1;
    assert mb_faithful({key},1,0,0,0,0,ds)==false;
    assert mb_sorted({key},fa_output(1,0,0,0,0,ds,false))==false;
    assert {assertion}; // TARGET_NEGATIVE_{label}
}}
@*/
"""
        line = next(i for i, text in enumerate(unit.splitlines(),1) if "TARGET_NEGATIVE_" in text)
        result.append(("merge_order_negative_" + label, unit,
                       {"target_line": line, "expected_predicate": predicate}))
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    a = load_a()
    admitted = a.admitted_harness()
    frozen = admitted.frozen_classifier()
    frozen.require_hosted()
    certificate = admitted.admit_source()
    tool = (args.tool_home / "bin/verifast").resolve(strict=True)
    geometry = (HERE / "geometry.c").read_text()
    ids = (HERE / "functional-ids.c").read_text()
    order = (HERE / "functional-order.c").read_text()
    nat_include = '//@ #include "nat.gh"'
    if order.count(nat_include) != 1:
        raise RuntimeError("stock nat header admission failed")
    order = order.replace(nat_include, "")
    pullback = (HERE / "functional-swo.c").read_text()
    core_path = HERE.parent / "networks/swo-rank.c"
    core_bytes = core_path.read_bytes()
    if sha(core_bytes) != SWO_PIN:
        raise RuntimeError("accepted SWO bodies changed")
    core = core_bytes.decode()
    include = '//@ #include "list.gh"'
    if core.count(include) != 1:
        raise RuntimeError("SWO header admission failed")
    # Duplicate include removed exactly; every definition and body retained.
    core = core.replace(include, "")
    common = nat_include + "\n" + geometry + "\n" + ids + "\n" + order
    full = common + frozen.RANK_HELPERS + frozen.IDENTITY_HELPERS + core + pullback
    duplicate, duplicate_metadata = a.negative_case(geometry, ids)
    cases = [("merge_order_full", full, None),
             ("merge_order_negative_duplicate", duplicate, duplicate_metadata)]
    cases += negative_cases(geometry, ids, order)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True,exist_ok=True)
    cert = evidence / "source-admission.json"
    cert.write_text(json.dumps(certificate,indent=2)+"\n")
    manifest = {
        "scope": "arbitrary-length exact bidirectional mathematical stable merge; actual Rust open",
        "domain": "n>=2; exact original occurrence domain; fixed finite SWO; sorted original halves; immutable keys; faithful normally returning comparisons; scalar odd choice",
        "posts": "scalar guard; full G2 trace; exact A destination coverage/trace/output/ID multiplicities; all-pairs sorting and original-ID stability for equivalent keys",
        "tool_profile": "official-stock-VeriFast-26.09",
        "source_admission_sha256": sha(cert.read_bytes()),
        "source_admission": certificate,
        "accepted_component_pins": PINS,
        "swo_core_sha256": SWO_PIN,
        "order_sha256": sha(order.encode()),
        "pullback_sha256": sha(pullback.encode()),
        "frozen_classifier_sha256": admitted.FROZEN_SHA256,
        "verifast_binary_sha256": sha(tool.read_bytes()),
        "cases": [],
    }
    passed = True
    for name, source, expected in cases:
        result = frozen.run_case(tool,evidence,name,source,expected)
        manifest["cases"].append(result)
        (evidence / "results.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print(f"{name}: {'PASS' if result['accepted'] else 'INCONCLUSIVE'}",flush=True)
        passed &= result["accepted"]
    return 0 if passed else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"stable merge preparation failed: {error}",file=sys.stderr)
        sys.exit(2)
