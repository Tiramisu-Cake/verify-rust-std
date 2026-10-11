#!/usr/bin/env python3
"""Cloud-only, evidence-only rustc Instance query; inert on import.

The owning driver calls run(a, c4, audit, manifest, ghost) after source and
phase admission, then ends this query-only phase without reconstructing a
verifier or running a proof. All subprocesses here are Cloud gated.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
import shutil

HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
EXPORTER = Path("src/rust_frontend/vf_mir_exporter/src/lib.rs")
PHASE = "SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11"
MARKER = "SORT4_BINDING_V1\t"
CALLERS = ("binding_selected_freeze", "binding_fallback_cell",
           "binding_unconstrained_generic")
METHODS = ("small_sort_threshold", "small_sort")


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError("COMPILER-BINDING: " + message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def line_at(text: str, needle: str) -> int:
    require(text.count(needle) == 1, "fixture inventory: " + needle)
    return text[:text.index(needle)].count("\n") + 1


def source_certificate(a, manifest: dict, pins: dict) -> tuple[bytes, dict]:
    base = a.proof_root
    fixture = base / HERE / pins["fixture_file"]
    require(fixture.is_file() and sha(fixture) == pins["fixture_sha256"], "fixture pin")
    small = base / "library/core/src/slice/sort/shared/smallsort.rs"
    quick = base / "library/core/src/slice/sort/stable/quicksort.rs"
    shared = base / "library/core/src/slice/sort/shared/mod.rs"
    expected = ((small, "actual_smallsort_source_sha256"),
                (quick, "actual_quicksort_source_sha256"),
                (shared, "actual_shared_source_sha256"))
    for path, field in expected:
        require(sha(path) == manifest[field], "actual source pin: " + field)
    small_text, quick_text, shared_text = (small.read_text(), quick.read_text(),
                                           shared.read_text())
    text = fixture.read_text()
    marker = ("#[unsafe(rustc_allow_lifetime_dependent_specialization)]\n"
              "pub(crate) trait FreezeMarker {}\n\n"
              "impl<T: Freeze> FreezeMarker for T {}")
    require(shared_text.count(marker) == 1 and text.count(marker) == 1,
            "exact FreezeMarker source mapping")
    block_start = small_text.index("pub(crate) trait StableSmallSortTypeImpl: Sized {")
    block_end = small_text.index("/// Using a trait allows us to specialize on `Freeze`", block_start)
    copied = small_text[block_start:block_end].rstrip()
    require(text.count(copied) == 1, "both original trait/impl blocks copied exactly")
    for constant in ("const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;",
                     "const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;"):
        require(small_text.count(constant) == 1 and text.count(constant) == 1,
                "threshold constant identity")
    guard = ("if len <= T::small_sort_threshold() {\n"
             "            T::small_sort(v, scratch, is_less);\n"
             "            return;\n        }")
    require(quick_text.count("if len <= T::small_sort_threshold() {\n"
                             "            T::small_sort(v, scratch, is_less);\n"
                             "            return;\n        }") == 1 and text.count(guard) == 3,
            "three exact base guards and operands")
    require(text.count("return; // diagnostic cut before partition and recursion") == 3 and
            text.count("// Diagnostic transitive-body cuts") == 1 and
            "F: FnMut(&T, &T) -> bool" in text and
            "F: FnMut(&Cell<u8>, &Cell<u8>) -> bool" in text,
            "cuts and real FnMut domain")
    default_start = line_at(text, "impl<T> StableSmallSortTypeImpl for T {")
    selected_start = line_at(text, "impl<T: FreezeMarker> StableSmallSortTypeImpl for T {")
    const_start = line_at(text, "const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;")
    caller_lines = {name: line_at(text, "fn " + name + "<") for name in CALLERS}
    regions = {"fallback": [default_start, selected_start - 1],
               "selected": [selected_start, const_start - 1]}
    lines = text.splitlines()
    method_lines = {}
    for kind, (low, high) in regions.items():
        method_lines[kind] = {}
        for method in METHODS:
            matches = [i for i in range(low, high + 1)
                       if "fn " + method + ("(" if method == METHODS[0] else "<")
                       in lines[i - 1]]
            require(len(matches) == 1, "unique " + kind + " " + method + " source line")
            method_lines[kind][method] = matches[0]
    certificate = {"fixture_sha256": sha(fixture), "actual_source_sha256": {
        "smallsort": sha(small), "quicksort": sha(quick), "FreezeMarker": sha(shared)},
        "copied_trait_and_both_impls_exact": True,
        "guard_statement_copies": 3,
        "diagnostic_nonbase_cuts": 3,
        "diagnostic_transitive_helper_cuts": True,
        "caller_lines": caller_lines, "impl_line_regions": regions,
        "method_lines": method_lines,
        "proof_credit": False}
    return fixture.read_bytes(), certificate


def normalize_compiler_debug(value: object) -> object:
    """Keep full DefPath/binder structure; numeric DefIds belong to one invocation."""
    if not isinstance(value, str):
        return value
    return re.sub(r"DefId\(\d+:\d+ ~ ([^)]+)\)", r"DefId(\1)", value)


def parse_records(log: str, certificate: dict) -> tuple[list[dict], dict]:
    lines = [line.split(MARKER, 1)[1] for line in log.splitlines() if MARKER in line]
    require(len(lines) == 6, "exactly six compiler call records")
    records = [json.loads(line) for line in lines]
    pairs: dict[tuple[str, str], dict] = {}
    regions = certificate["impl_line_regions"]
    summary: dict[str, dict[str, str]] = {name: {} for name in CALLERS}
    required = {"caller", "caller_def_id", "caller_source_file", "caller_span",
                "caller_line", "typing_env", "caller_clauses", "callee",
                "callee_def_id", "original_args", "operand", "arguments",
                "argument_count", "call_source_file", "call_span", "call_line",
                "resolution", "instance_kind", "resolved_path", "resolved_def_id",
                "resolved_args", "resolved_impl_id", "resolved_impl_path",
                "resolved_span", "resolved_impl_span", "resolved_line",
                "resolved_impl_line"}
    for row in records:
        require(set(row) == required, "exact machine record schema")
        caller = next((name for name in CALLERS if row["caller"] in (name, "lib::" + name)), None)
        method = next((name for name in METHODS if row["callee"].endswith("::" + name)), None)
        require(caller is not None and method is not None and
                "StableSmallSortTypeImpl" in row["callee"], "caller/callee inventory")
        key = (caller, method)
        require(key not in pairs, "duplicate call record")
        pairs[key] = row
        require("lib.rs" in row["caller_source_file"] and
                "lib.rs" in row["call_source_file"] and
                row["caller_line"] == certificate["caller_lines"][caller] and
                row["call_line"] > row["caller_line"], "caller source/span identity")
        require("FnMut" in row["caller_clauses"] and
                ("FreezeMarker" in row["caller_clauses"] if caller == CALLERS[0] else True),
                "real callback and Freeze caller clauses")
        require(row["original_args"] and row["operand"] and row["call_span"] and
                row["argument_count"] == (0 if method == METHODS[0] else 3),
                "original generic args and call operands")
        disposition = "unresolved"
        if row["resolution"] == "some":
            require(row["resolved_def_id"] and row["resolved_args"] and
                    row["resolved_span"] and row["instance_kind"],
                    "resolved instance identity")
            if row["resolved_impl_id"] and row["resolved_impl_span"] and \
                    row["instance_kind"].startswith("Item("):
                matching = [kind for kind, (low, high) in regions.items()
                            if row["resolved_impl_line"] == low and
                            row["resolved_line"] ==
                            certificate["method_lines"][kind][method] and
                            row["resolved_path"].endswith("::" + method)]
                if len(matching) == 1:
                    disposition = "observed_" + matching[0]
        elif row["resolution"] != "none":
            require(row["resolution"].startswith("error:"), "resolution state")
        summary[caller][method] = disposition
    require(set(pairs) == {(caller, method) for caller in CALLERS for method in METHODS},
            "all caller/method pairs")
    selected = all(value == "observed_selected" for value in summary[CALLERS[0]].values())
    fallback = all(value == "observed_fallback" for value in summary[CALLERS[1]].values())
    generic_safe = all(value != "observed_selected" for value in summary[CALLERS[2]].values())
    return records, {"per_caller": summary, "selected_pair_observed": selected,
                     "fallback_pair_observed": fallback,
                     "unconstrained_not_selected": generic_safe,
                     "selection_observation_complete": selected and fallback and generic_safe,
                     "binding_gate_open": False}


def run(a, c4, audit, manifest: dict, ghost) -> dict:
    result = {"classification": "COMPILER_BINDING_QUERY_INCONCLUSIVE",
              "accepted": False, "verification_accepted": False,
              "diagnostic_complete": False, "actual_caller_proved": False,
              "caller_bound_transfer_proved": False, "profile_accepted": False,
              "proof_credit": False, "selection_observation_complete": False,
              "binding_gate_open": False}
    try:
        require(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
                os.environ.get("LANE") == "o26-sort4-c1-current-recovery" and
                os.environ.get("SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID") == PHASE and
                manifest["phase_id"] == PHASE and not os.environ.get("GITHUB_ACTIONS"),
                "Cloud-only exact phase/lane")
        pins_path = a.proof_root / HERE / "COMPILER-SELECTED-INSTANCE-PINS.json"
        pins = json.loads(pins_path.read_text())
        require(pins["candidate"] == PHASE and pins["compiler_or_proof_executed"] is False,
                "candidate identity")
        fixture_bytes, cert = source_certificate(a, manifest, pins)
        save(a.evidence / "compiler-binding-source-certificate.json", cert)
        patch = a.proof_root / HERE / pins["patch_file"]
        require(sha(patch) == pins["patch_sha256"], "exporter patch SHA")
        tool = a.work_root / "sort4-compiler-binding-query-isolated-source"
        require(not tool.exists(), "fresh isolated source")
        production_before = audit.snapshot(a.production_source, a.proof_root)
        require(production_before["head"] == pins["source_commit"] and
                sha(a.production_source / EXPORTER) == pins["source_file_sha256"],
                "pinned production exporter")
        shutil.copytree(a.production_source, tool, symlinks=True)
        require(audit.snapshot(tool, a.proof_root) == production_before,
                "isolated copy identity")
        env = c4.clean_env(a, tool)
        for operation in ("--check", ""):
            argv = ["git", "-C", str(tool), "apply"]
            if operation:
                argv.append(operation)
            argv.append(str(patch))
            row = c4.stage(a, a.evidence / "compiler-binding", "exporter-patch" +
                           ("-check" if operation else ""), argv, env, 60, cwd=tool)
            require(row.get("exit") == 0, "isolated exporter patch " + operation)
        require(sha(tool / EXPORTER) == pins["patched_file_sha256"], "patched exporter SHA")
        save(a.evidence / "compiler-binding-tool-identity.json", {
            "production_head": production_before["head"],
            "production_exporter_sha256": pins["source_file_sha256"],
            "patched_exporter_sha256": sha(tool / EXPORTER),
            "patch_sha256": sha(patch), "schema_or_translation_change": False})
        compiler = a.compiler_sysroot / "bin/rustc"
        require(compiler.is_file(), "pinned compiler path")
        row = c4.stage(a, a.evidence / "compiler-binding", "compiler-version",
                       [str(compiler), "--version", "--verbose"], env, 30, cwd=tool)
        version_log = a.evidence / "compiler-binding" / "compiler-version.log"
        require(row.get("exit") == 0 and
                pins["rustc_commit"] in version_log.read_text(errors="replace"),
                "pinned compiler commit")
        env["RUSTC"] = str(compiler)
        row = c4.stage(a, a.evidence / "compiler-binding", "exporter-build",
                       ["make", "-C", str(tool / "src"),
                        "build-vf-rust-mir-exporter", "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
                       env, 900, cwd=tool)
        require(row.get("exit") == 0, "Cloud exporter build")
        exporter = tool / "bin/vf-rust-mir-exporter"
        require(exporter.is_file(), "built exporter binary")
        query_env = dict(env)
        query_env.update(SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID=PHASE,
                         SORT4_SELECTED_INSTANCE_EVIDENCE=PHASE,
                         SMALLSORT_EXECUTION_PROVIDER="cloud-build")
        query_results = {}
        for mode, extra in (("normal", []),
                            ("readonly", ["--vf-rust-mir-exporter:preprocess-readonly"])):
            fixture = a.evidence / "compiler-binding" / (mode + "-fixture")
            (fixture / "verified").mkdir(parents=True, exist_ok=False)
            (fixture / "original").mkdir()
            for name in ("verified/lib.rs", "original/lib.rs"):
                (fixture / name).write_bytes(fixture_bytes)
            binary = a.evidence / "compiler-binding" / (mode + "-mir.bin")
            row = c4.stage(a, a.evidence / "compiler-binding", mode + "-instance-query",
                           [str(exporter), "verified/lib.rs",
                            "--sysroot=" + str(a.compiler_sysroot), "--edition", "2021",
                            *extra], query_env, 180, cwd=fixture, stdout=binary)
            log_path = a.evidence / "compiler-binding" / (mode + "-instance-query.log")
            raw_log = log_path.read_text(errors="replace") if log_path.is_file() else ""
            raw_rows = [json.loads(line.split(MARKER, 1)[1]) for line in raw_log.splitlines()
                        if MARKER in line]
            save(a.evidence / "compiler-binding" / (mode + "-raw-records.json"), raw_rows)
            require(row.get("exit") == 0, "Cloud " + mode + " exporter query")
            # Preserve full compiler MIR for exact clauses, substitutions and
            # reborrow operand dataflow review before native binding admission.
            decoded = a.evidence / "compiler-binding" / (mode + "-mir.txt")
            decode = c4.stage(a, a.evidence / "compiler-binding", mode + "-mir-decode",
                              ["capnp", "decode", str(tool / "src/rust_frontend/vf_mir/vf_mir.capnp"), "VfMir"],
                              query_env, 60, cwd=fixture, stdin=binary, stdout=decoded)
            require(decode.get("exit") == 0, "Cloud " + mode + " MIR decode")
            require(all(sha(fixture / name) == pins["fixture_sha256"] for name in
                        ("verified/lib.rs", "original/lib.rs")),
                    mode + " immutable source pair")
            records, finding = parse_records(raw_log, cert)
            query_results[mode] = (records, finding, log_path)
        compare = ("caller", "caller_def_id", "typing_env", "caller_clauses",
                   "callee", "callee_def_id", "original_args", "argument_count",
                   "resolution", "instance_kind", "resolved_def_id", "resolved_args",
                   "resolved_impl_id", "resolved_impl_path", "resolved_line",
                   "resolved_impl_line")
        normal = query_results["normal"][0]
        readonly = query_results["readonly"][0]
        def indexed(rows: list[dict]) -> dict:
            return {(row["caller"], row["callee"]):
                    {key: normalize_compiler_debug(row[key]) for key in compare} for row in rows}
        require(indexed(normal) == indexed(readonly),
                "normal/readonly compiler identities and clauses differ")
        records, finding, log_path = query_results["normal"]
        save(a.evidence / "compiler-binding-records.json", {
            mode: rows for mode, (rows, _, _) in query_results.items()})
        result.update(classification=("COMPILER_BINDING_OBSERVED_EVIDENCE_ONLY"
                                      if finding["selection_observation_complete"] else
                                      "COMPILER_BINDING_UNRESOLVED_NO_PROOF_CREDIT"),
                      diagnostic_complete=True,
                      selection_observation_complete=finding["selection_observation_complete"],
                      compiler_binding=finding,
                      source_certificate_sha256=sha(a.evidence / "compiler-binding-source-certificate.json"),
                      raw_exporter_log_sha256={mode: sha(path) for mode, (_, _, path)
                                               in query_results.items()},
                      built_exporter_sha256=sha(exporter))
        require(audit.snapshot(a.production_source, a.proof_root) == production_before,
                "production source unchanged")
    except Exception as exc:
        result["reason"] = str(exc)
    save(a.evidence / "diagnostic-audit.json", result)
    save(a.evidence.parent.parent / "proof-audit.json", result)
    return result
