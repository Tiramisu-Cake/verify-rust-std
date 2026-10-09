#!/usr/bin/env python3
"""Cloud-only fail-closed audit of isolated print-only post-mark TEST evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
PATCH_SHA = "57c271e5db2c72d69162a16fec10d975cd68fd7619a02ca54aa80a58426d3c6d"
STOCK_CORE = "adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0"
TEST_CORE = "de821f944772683239d4fb7115e9602aa6fcf0cdb3be598f235ba7580a81417b"
TRANSLATOR = "0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a"


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline_audit():
    path = HERE / "sort4-ast-audit.py"
    spec = importlib.util.spec_from_file_location("postmark_existing_sort4_preflight", path)
    need(spec is not None and spec.loader is not None, "reviewed sort4 baseline audit absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def first_error(log: str) -> str | None:
    rows = [line for line in log.splitlines()
            if ": error:" in line or line.startswith("Fatal error:")]
    return rows[0] if rows else None


def classify(a: argparse.Namespace) -> dict:
    prior = baseline_audit().preflight(a.baseline)
    fixture = a.baseline / "actual-sort4-fixture"
    expected_counts = {"normal": (55, 137, 54), "readonly": (28, 110, 27)}
    for mode, (blocks, locals_, unwind) in expected_counts.items():
        inventory = json.loads((fixture / f"{mode}-graph-inventory.json").read_text())
        need(inventory.get("basic_block_count") == blocks and
             inventory.get("local_declaration_count") == locals_ and
             inventory.get("unwind_action_count") == unwind and
             inventory.get("cleanup_block_count") == 0 and
             inventory.get("full_function_record_sha256") ==
                 prior["complete_graph_sha256"][mode] and
             (fixture / f"{mode}-mir.bin").is_file() and
             (fixture / f"{mode}-mir.bin").stat().st_size > 0 and
             sha(fixture / f"{mode}-mir.txt") == inventory.get("decoded_mir_sha256"),
             f"{mode}: complete local/block inventory or MIR artifact differs")
    manifest = json.loads(a.manifest.read_text())
    need(manifest.get("classification") ==
         "ISOLATED_PRINT_ONLY_VERIFIER_CORE_TEST_NOT_ACCEPTED" and
         manifest.get("accepted") is False and
         manifest.get("verification_accepted") is False and
         manifest.get("patch_sha256") == PATCH_SHA and
         manifest.get("stock_verifast_ml_sha256") == STOCK_CORE and
         manifest.get("test_verifast_ml_sha256") == TEST_CORE and
         manifest.get("production_translator_sha256") == TRANSLATOR and
         manifest.get("verified_source_sha256") == prior["source_sha256"] and
         manifest.get("original_source_sha256") == prior["original_sha256"] and
         manifest.get("complete_normal_mir_sha256") ==
             prior["complete_graph_sha256"]["normal"] and
         manifest.get("complete_readonly_mir_sha256") ==
             prior["complete_graph_sha256"]["readonly"] and
         manifest.get("scope_rewrite_enabled") is False and
         manifest.get("kernel_operations_changed") is False and
         manifest.get("normal_blocks") == 55 and
         manifest.get("normal_local_declarations") == 137 and
         manifest.get("normal_unwind_actions") == 54 and
         manifest.get("readonly_blocks") == 28 and
         manifest.get("readonly_local_declarations") == 110 and
         manifest.get("readonly_unwind_actions") == 27 and
         manifest.get("fnmut_calls") == 5 and
         manifest.get("select_calls") == 8 and
         manifest.get("copy_calls") == 4,
         "TEST manifest or exact baseline differs")
    production, probe = a.production_source, a.probe_source
    core = Path("src/verifast.ml")
    translator = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
    schema = Path("src/rust_frontend/vf_mir/vf_mir.capnp")
    need(sha(production / core) == STOCK_CORE and sha(probe / core) == TEST_CORE and
         sha(production / translator) == TRANSLATOR and
         (production / translator).read_bytes() == (probe / translator).read_bytes() and
         (production / schema).read_bytes() == (probe / schema).read_bytes(),
         "isolated verifier core, production translator or schema differs")
    inputs = a.probe_output.parent / "inputs-sha256.txt"
    rows = inputs.read_text().splitlines() if inputs.is_file() else []
    need(sum(row.startswith(PATCH_SHA + "  ") and
             row.endswith("/verifast-actual-sort4-postmark-print-TEST.patch")
             for row in rows) == 1,
         "print TEST patch pin absent from Cloud inputs")
    off_log = a.probe_off_log.read_text(errors="replace")
    on_log = a.probe_log.read_text(errors="replace")
    off_error, on_error = first_error(off_log), first_error(on_log)
    expected = prior["baseline_refusal"]
    need(a.probe_off_exit not in (0, 124, 137) and
         a.probe_exit not in (0, 124, 137) and
         "Verifying function 'sort4_stable'" in off_log and
         "Verifying function 'sort4_stable'" in on_log and
         off_error == on_error == expected and
         "verified/lib.rs(185,13-36)" in expected and
         "No such function: __vf_sort4_first_unwind" in expected,
         "on/off console changed stock first refusal")
    need(a.probe_off_output.is_dir() and
         not any(a.probe_off_output.iterdir()) and
         "SORT4-POSTMARK-TEST:" not in off_log,
         "default-off console emitted post-mark data")
    before = a.probe_output / "postmark-before.marshal"
    after = a.probe_output / "postmark-after.marshal"
    trace = a.probe_output / "postmark-local-trace.txt"
    need(a.probe_output.is_dir() and
         {p.name for p in a.probe_output.iterdir()} ==
             {before.name, after.name, trace.name} and
         all(p.is_file() and p.stat().st_size > 0 for p in (before, after, trace)) and
         before.read_bytes() == after.read_bytes() and
         "SORT4-POSTMARK-TEST: snapshot=" in on_log,
         "post-mark AST identity or single output set differs")
    lines = trace.read_text().splitlines()
    need(lines and lines[0] ==
         "classification=PRINT_ONLY_POSTMARK_TEST locals_to_free=LAZY_OR_UNOBSERVED",
         "post-mark trace status missing")
    blocks = [line for line in lines[1:] if line.startswith("block ")]
    locals_ = [line for line in lines[1:] if line.startswith("local ")]
    need(blocks and len(locals_) >= 137 and
         len(blocks) + len(locals_) == len(lines) - 1,
         "post-mark block/local inventory absent or malformed")
    parsed = {}
    local_re = re.compile(
        r"^local path=(\S+) name=(\S+) loc=(\S+) address_taken=(true|false) "
        r"owner=(\S+) type_marshal_hex=([0-9a-f]+) init_marshal_hex=([0-9a-f]+)$")
    for line in locals_:
        match = local_re.fullmatch(line)
        need(match is not None, "malformed post-mark local row")
        path, name, loc, taken, owner, ty_hex, init_hex = match.groups()
        need(len(ty_hex) % 2 == len(init_hex) % 2 == 0 and
             path not in parsed and "verified/lib.rs:" in loc,
             "duplicate or unbound local, location, type or initializer")
        parsed[path] = {"name": name, "location": loc,
                        "address_taken": taken, "owner": owner,
                        "type_sha256": hashlib.sha256(bytes.fromhex(ty_hex)).hexdigest(),
                        "init_sha256": hashlib.sha256(bytes.fromhex(init_hex)).hexdigest()}
    selected = manifest["selected_tuple_locals"]
    block_paths = {line.split(" ", 2)[1].removeprefix("path=") for line in blocks}
    selected_rows = {name: [row for row in parsed.values() if row["name"] == name]
                     for name in selected}
    need(len(selected) == 5 and all(len(rows) == 1 and
         rows[0]["owner"] in block_paths and
         rows[0]["type_sha256"] and rows[0]["init_sha256"]
         for rows in selected_rows.values()),
         "selected tuple type/initializer/unique block owner unobserved")
    return {**prior,
            "classification": "PRINT_ONLY_POSTMARK_LOCAL_TYPES_DIAGNOSTIC",
            "diagnostic_complete": True, "verification_accepted": False,
            "accepted": False, "scope_rewrite_enabled": False,
            "kernel_operations_changed": False,
            "storage_cleanup_proved": False,
            "later_cleanup_observation": "UNOBSERVED_LAZY_OR_PATH_DEPENDENT",
            "postmark_ast_sha256": sha(before),
            "postmark_ast_identical_before_after_print": True,
            "postmark_trace_sha256": sha(trace),
            "selected_tuple_locals": selected_rows,
            "block_rows": blocks, "local_row_count": len(locals_),
            "off_first_error": off_error, "on_first_error": on_error,
            "off_exit": a.probe_off_exit, "on_exit": a.probe_exit}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=("preflight", "classify"))
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    for name in ("manifest", "probe-off-log", "probe-off-output", "probe-log",
                 "probe-output", "production-source", "probe-source"):
        p.add_argument("--" + name, type=Path)
    for name in ("probe-off-exit", "probe-exit"):
        p.add_argument("--" + name, type=int)
    a = p.parse_args()
    need(not a.output.exists(), "refusing to replace diagnostic audit")
    if a.command == "preflight":
        result = baseline_audit().preflight(a.baseline)
    else:
        need(all(getattr(a, name.replace('-', '_')) is not None for name in
                 ("manifest", "probe-off-log", "probe-off-output", "probe-off-exit",
                  "probe-log", "probe-output", "probe-exit", "production-source",
                  "probe-source")), "classification inputs incomplete")
        result = classify(a)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"],
                      "accepted": False}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
