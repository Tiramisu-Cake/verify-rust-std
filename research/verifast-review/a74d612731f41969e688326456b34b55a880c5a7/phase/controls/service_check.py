#!/usr/bin/env python3
"""Synthetic service checks for the retirement gate; no compiler/toolchain use."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / "run.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("incoming_span_service_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ast_call(callee: str, argument: str, line: int) -> str:
    loc = f'loc("verified/lib.rs({line},1-20)")'
    var = f'LitPat(Var({loc},"{argument}"))'
    return f'CallExpr({loc},"{callee}",[],[],[{var}],Static)'


def tree_for(mir):
    def statement(event: str, local: str, line: int):
        return {"kind": {event: {"name": local}},
                "sourceInfo": {"span": {"regular": {"lo": {"line": line}}}}}
    ids = {"tmp0": "_1", "tmp1": "_2", "other0": "_3", "other1": "_4"}
    debug = [{"name": {"name": name}, "value": {"place": {
                "local": {"name": local}, "projection": []}}}
             for name, local in ids.items()]
    decls = [{"id": {"name": local}} for local in ids.values()]
    block = {"id": {"index": 0}, "statements": [
        statement("storageLive", ids["tmp0"], 3),
        statement("storageDead", ids["tmp0"], 10),
        statement("storageLive", ids["tmp1"], 12),
    ]}
    return {"bodies": [{"defPath": "span_retired_local_reuse",
                        "varDebugInfo": debug, "localDecls": decls,
                        "basicBlocks": [block]}]}


def main() -> int:
    runner = load_runner()
    real_mir, ast = runner._helpers()
    parsed = tree_for(real_mir)

    class SyntheticCapnpText:
        def __init__(self, _source):
            pass
        def parse(self):
            return parsed

    class SyntheticMir:
        CapnpText = SyntheticCapnpText
        path = staticmethod(real_mir.path)
        vdi_map = staticmethod(real_mir.vdi_map)

    runner._helpers = lambda: (SyntheticMir, ast)
    rows = {}
    with tempfile.TemporaryDirectory(prefix="incoming-span-service-") as temp_dir:
        case = Path(temp_dir)
        (case / "decode.out").write_text("synthetic decoded MIR")
        unrelated = [
            ast_call("vf__rust_storage_dead", "other0", 8),
            ast_call("vf__rust_storage_live", "other1", 9),
        ]
        ordered = unrelated + [
            ast_call("vf__rust_storage_dead", "tmp0", 10),
            ast_call("vf__rust_storage_live", "tmp1", 12),
        ]
        (case / "proof-ast.ml").write_text("[" + ";".join(ordered) + "]")
        rows["matching_markers_amid_other_lifetimes"] = runner.retired_mir_ast_gate(case)
        assert rows["matching_markers_amid_other_lifetimes"]["admitted"] is True
        (case / "proof-ast.ml").write_text("[" + ";".join(unrelated + [
            ast_call("vf__rust_storage_dead", "tmp0_shadow", 10),
            ast_call("vf__rust_storage_live", "tmp1", 12),
        ]) + "]")
        rows["reject_wrong_mir_mapped_dead_local"] = runner.retired_mir_ast_gate(case)
        assert rows["reject_wrong_mir_mapped_dead_local"]["admitted"] is False
    result = {
        "schema": "incoming-span-lifetime-retirement-service-controls-v1",
        "accepted": False,
        "toolchain_or_proof_run": False,
        "inputs_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (RUNNER_PATH, HERE / "service_check.py",
                                       HERE / "span-controls.rs", HERE / "MANIFEST.json")},
        "checks": {name: {"admitted": row["admitted"], "reason": row["reason"]}
                   for name, row in rows.items()},
        "positive_gate": rows["matching_markers_amid_other_lifetimes"],
        "negative_gate": rows["reject_wrong_mir_mapped_dead_local"],
    }
    (HERE / "SERVICE-CONTROLS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["checks"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
