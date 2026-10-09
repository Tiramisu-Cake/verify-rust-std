#!/usr/bin/env python3
"""Cloud-only, no-proof-credit C2 source/MIR/AST discovery driver.

The pure byte and AST classifiers in this module are safe to exercise on
synthetic inputs. ``run_discovery`` invokes the compiler, MIR tools, and
VeriFast only from the assigned Cloud lane after the bounded C1 gate passes.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any


HERE = Path("research/challenge-8/cloud-build/sort4-native-entry-c1")
PIN = HERE / "C2-SOURCE-PIN.json"
DRAFT = HERE / "C2-ANNOTATION-DRAFT.rs"
PROFILE = HERE / "C2-DISCOVERY-PROFILE.json"
PATCH = HERE / "verifast-actual-c2-discovery-TEST.patch"
C1_PROFILE = HERE / "C1-PREFIX-PROFILE.json"
C1_PATCH = HERE / "verifast-actual-c1-prefix-TEST.patch"
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
KERNEL = Path("src/verifast.ml")
RUNTIME_C2 = b"        let c2 = is_less(&*v_base.add(3), &*v_base.add(2));"
ANNOTATED_C2 = (b"        let c2 = is_less/*@::<F, (&'cmp2 T, &'cmp2 T), 'cmp2>@*/"
                b"(&*v_base.add(3), &*v_base.add(2));")
C2_SOURCE_LINE = ANNOTATED_C2.decode("ascii")
GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/(?:\r?\n)?", re.S)
GHOST_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
FUNC_NAME = "sort4_stable"
C2_PLACEHOLDER = "__vf_sort4_C2_UNBOUND_LIFETIME_DECL_PLACEHOLDER"
C2_PLACEHOLDER_SOURCE_LINE = 196
C2_SCAFFOLD_CLASS = "EXPERIMENTAL_C2_UNBOUND_SCAFFOLD_ONLY_NOT_PROOF"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_ghost(source: bytes) -> bytes:
    """Match the project capture's byte-preserving ghost stripper."""
    return GHOST_LINE.sub(b"", GHOST_BLOCK.sub(b"", source))


def insertion_from_draft(draft: bytes) -> bytes:
    """Drop explanatory ordinary comments and return only C2 code bytes."""
    start = b"        //@ let cmp2_k = begin_lifetime();"
    starts = [m.start() for m in re.finditer(re.escape(start), draft)]
    calls = [m.start() for m in re.finditer(re.escape(ANNOTATED_C2), draft)]
    need(len(starts) == len(calls) == 1, "C2 draft start/call is missing or ambiguous")
    need(draft[:starts[0]].splitlines() and
         all(line.lstrip().startswith(b"//") or not line.strip()
             for line in draft[:starts[0]].splitlines()),
         "unexpected executable bytes precede C2 draft body")
    body = draft[starts[0]:]
    need(body.count(ANNOTATED_C2) == 1 and
         body.count(b"__vf_sort4_second_unwind();") == 1 and
         body.count(b"end_lft_binding::<'cmp2>();") == 1 and
         body.count(b"recover_pair::<T>(v_base + 3, v_base + 2);") == 2 and
         body.count(b"join_four_owned_cells::<T>(v_base, t);") == 2,
         "C2 source-body operation inventory differs")
    return body


def prepare_c2_bytes(base_verified: bytes, original: bytes,
                     draft: bytes, pin: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    """Splice the reviewed C2 ghost body at the unique original source call."""
    need(digest(base_verified) == pin.get("base_verified_sha256"),
         "frozen C1 verified source hash differs from C2 source pin")
    need(digest(original) == pin.get("ghost_stripped_runtime_sha256"),
         "frozen original source hash differs from C2 source pin")
    body = insertion_from_draft(draft)
    old_call = RUNTIME_C2 + b"\n"
    need(base_verified.count(old_call) == 1,
         "exact source-195 C2 call including its line ending is not unique")
    # The prepared C1 fixture already has source-linked first-call annotations.
    # Anchor C2 immediately after its ordinary C1 normal-path join.
    join = b"        //@ join_four_owned_cells::<T>(v_base, t);"
    c1_join = [m.start() for m in re.finditer(re.escape(join), base_verified)]
    c2_at = base_verified.index(RUNTIME_C2)
    prior_joins = [at for at in c1_join if at < c2_at]
    need(len(prior_joins) == 1 and
         base_verified.count(b"__vf_sort4_first_unwind();") == 1,
         "C1 boundary is missing or ambiguous")
    # Consume the original line ending too: the draft body already terminates
    # its annotated call with one newline. Leaving the original newline adds a
    # blank source line and fails the reviewed ECD83 whole-file pin.
    c2_end = c2_at + len(old_call)
    # The draft's inline ghost type ascription strips back to the exact C2
    # statement removed from the frozen C1 fixture.
    annotated = base_verified[:c2_at] + body + base_verified[c2_end:]
    stripped = strip_ghost(annotated)
    need(stripped == original, "C2 ghost stripping changed original runtime bytes")
    expected_hash = pin.get("annotated_verified_sha256")
    need(digest(annotated) == expected_hash,
         "C2 annotated source does not match the reviewed ECD83 source pin")
    inventory = source_inventory(annotated, pin)
    need(inventory["source_contract_ok"], "C2 marker/cut/call source contract differs")
    return annotated, {
        "base_verified_sha256": digest(base_verified),
        "annotated_verified_sha256": digest(annotated),
        "ghost_stripped_runtime_sha256": digest(stripped),
        "draft_sha256": digest(draft), "source_inventory": inventory,
        "ghost_strip_byte_identical": True,
    }


def source_inventory(source: bytes, pin: dict[str, Any]) -> dict[str, Any]:
    text = source.decode("utf-8", errors="strict")
    lines = text.splitlines()
    expected = pin.get("source_lines", {})
    marker_lines = {"c1_marker": [], "c2_marker": [], "c1_cut": [],
                    "c2_cut": [], "c2_call": [], "c2_lft_annotation": []}
    for n, line in enumerate(lines, 1):
        if "__vf_sort4_first_unwind();" in line:
            marker_lines["c1_marker"].append(n)
        if "__vf_sort4_second_unwind();" in line:
            marker_lines["c2_marker"].append(n)
        if "end_lft_binding::<'cmp>();" in line:
            marker_lines["c1_cut"].append(n)
        if "end_lft_binding::<'cmp2>();" in line:
            marker_lines["c2_cut"].append(n)
        if line == C2_SOURCE_LINE:
            marker_lines["c2_call"].append(n)
        if line.strip() == "/*@ let_lft 'cmp2 = cmp2_k; @*/":
            marker_lines["c2_lft_annotation"].append(n)
    expected.setdefault("c2_lft_annotation", C2_PLACEHOLDER_SOURCE_LINE)
    unique_expected = all(len(marker_lines[key]) == 1 and
                          marker_lines[key][0] == expected.get(key)
                          for key in marker_lines)
    ordered = (marker_lines["c1_marker"][0] < marker_lines["c1_cut"][0] <
               marker_lines["c2_marker"][0] < marker_lines["c2_call"][0] <
               marker_lines["c2_cut"][0]) if unique_expected else False
    return {"source_lines": marker_lines,
            "expected_source_lines": expected,
            "source_contract_ok": (unique_expected and ordered and
                                   marker_lines["c2_lft_annotation"] == [C2_PLACEHOLDER_SOURCE_LINE]),
            "full_verified_source_sha256": digest(source),
            "original_runtime_call_preserved": source.count(ANNOTATED_C2) == 1}


def named_function_span(text: str, name: str = FUNC_NAME) -> tuple[str | None, dict[str, int]]:
    """Select exactly one serialized AST Func whose final name field is name."""
    name_hits = list(re.finditer(r'"' + re.escape(name) + r'"\s*,\s*\[', text))
    spans: dict[int, str] = {}
    for hit in name_hits:
        starts = list(re.finditer(r"Func\s*\(", text[:hit.start()]))
        if not starts:
            continue
        start = starts[-1].start()
        opening = starts[-1].end() - 1
        depth, quoted, escaped, end = 0, False, False, None
        for at in range(opening, len(text)):
            char = text[at]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    end = at + 1
                    break
        if end is not None and hit.start() < end:
            spans[start] = text[start:end]
    if len(spans) != 1:
        return None, {"name_occurrences": len(name_hits), "function_spans": len(spans)}
    return next(iter(spans.values())), {"name_occurrences": len(name_hits),
                                        "function_spans": len(spans)}


def ast_runtime_inventory(text: str, c2_line: int = 223) -> dict[str, Any]:
    body, shape = named_function_span(text)
    if body is None:
        return {"status": "NOT_CONFIRMED", **shape}
    calls = [(int(line), callee) for line, callee in re.findall(
        r'CallExpr\s*\(\s*loc\s+"verified/lib\.rs\((\d+),[^\"]+"\s*,\s*"([^\"]+)"', body)]
    fnmut = [(line, callee) for line, callee in calls if callee == "std::ops::FnMut::call_mut"]
    c2_fnmut = [(line, callee) for line, callee in fnmut if line == c2_line]
    selectors = [(line, callee) for line, callee in calls if "select" in callee.lower()]
    copies = [(line, callee) for line, callee in calls
              if "copy_nonoverlapping" in callee.lower() or
              callee.lower() in ("copy", "copy_from_slice")]
    ok = len(fnmut) == 5 and len(c2_fnmut) == 1 and len(selectors) == 8 and len(copies) == 4
    return {"status": "CONFIRMED_C2_ORIGINAL_DECL_RUNTIME_INVENTORY" if ok else "NOT_CONFIRMED",
            "named_function": FUNC_NAME, "named_function_ast_sha256": digest(body.encode()),
            "fnmut_count": len(fnmut), "fnmut_calls": fnmut,
            "c2_fnmut_at_expected_source_line": c2_fnmut,
            "selector_count": len(selectors), "selector_calls": selectors,
            "copy_count": len(copies), "copy_calls": copies,
            "expected": {"fnmut": 5, "c2_fnmut_line": c2_line,
                         "selectors": 8, "copies": 4}, **shape}


def _constructor_spans(text: str, constructor: str) -> list[tuple[int, int]]:
    """Return balanced serialized-AST constructor spans, respecting quoted strings."""
    spans = []
    for match in re.finditer(r"(?<![\w])" + re.escape(constructor) + r"\s*\(", text):
        opening = text.find("(", match.start())
        depth, quoted, escaped = 0, False, False
        for at in range(opening, len(text)):
            ch = text[at]
            if quoted:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    quoted = False
            elif ch == '"':
                quoted = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    spans.append((match.start(), at + 1))
                    break
    return spans


def unbound_scaffold_ast_inventory(text: str, c2_line: int = 223) -> dict[str, Any]:
    """Require the emitted target AST's exact unbound declaration/placeholder block."""
    runtime = ast_runtime_inventory(text, c2_line)
    runtime_ok = runtime.get("status") == "CONFIRMED_C2_ORIGINAL_DECL_RUNTIME_INVENTORY"
    runtime["status"] = "C2_RUNTIME_INVENTORY_PRESERVED" if runtime_ok else "NOT_CONFIRMED"
    body, shape = named_function_span(text)
    if body is None:
        return {"status": "NOT_CONFIRMED", "runtime_inventory": runtime, **shape}
    decls = _constructor_spans(body, "TypeWithTypeidDecl")
    decl_texts = [body[start:end] for start, end in decls]
    named_decls = []
    for span, text in zip(decls, decl_texts):
        match = re.search(r'"\'(cmp2?)"', text)
        if match:
            named_decls.append((span, match.group(1)))
    decl_names = [name for _, name in named_decls]
    cmp2_decls = [span for span, name in named_decls if name == "cmp2"]
    placeholders = [m.start() for m in re.finditer(re.escape(C2_PLACEHOLDER), body)]
    calls = _constructor_spans(body, "CallExpr")
    expr_stmts = _constructor_spans(body, "ExprStmt")
    blocks = _constructor_spans(body, "BlockStmt")
    pures = _constructor_spans(body, "PureStmt")
    decl_span = cmp2_decls[0] if len(cmp2_decls) == 1 else None
    call_spans = [span for span in calls if C2_PLACEHOLDER in body[span[0]:span[1]]]
    call_span = call_spans[0] if len(call_spans) == 1 else None
    decl_text = body[decl_span[0]:decl_span[1]] if decl_span else ""
    compact_decl = re.sub(r"\s+", "", decl_text)
    # Locations are tuples serialized before declaration payloads; check payload
    # structure independently of their concrete source-span formatting.
    declaration_shape = ("TypeWithTypeidDecl" in compact_decl and
                         bool(re.search(r'"\'cmp2"', decl_text)) and
                         "typeid_of_lft" in compact_decl and
                         "cmp2_k" in compact_decl and
                         "LitPat(Var" in compact_decl and "Static" in compact_decl)
    enclosing_blocks = [span for span in blocks if decl_span and call_span and
                        span[0] <= decl_span[0] < decl_span[1] <= span[1] and
                        span[0] <= call_span[0] < call_span[1] <= span[1]]
    smallest_blocks = [span for span in enclosing_blocks
                       if not any((other[1] - other[0]) < (span[1] - span[0])
                                  for other in enclosing_blocks)]
    scaffold_block = smallest_blocks[0] if len(smallest_blocks) == 1 else None
    enclosing_pures = [span for span in pures if scaffold_block and
                       span[0] <= scaffold_block[0] < scaffold_block[1] <= span[1]]
    smallest_pures = [span for span in enclosing_pures
                      if not any((other[1] - other[0]) < (span[1] - span[0])
                                 for other in enclosing_pures)]
    scaffold_pure = smallest_pures[0] if len(smallest_pures) == 1 else None
    enclosing_exprs = [span for span in expr_stmts if call_span and
                       span[0] <= call_span[0] < call_span[1] <= span[1]]
    smallest_exprs = [span for span in enclosing_exprs
                      if not any((other[1] - other[0]) < (span[1] - span[0])
                                 for other in enclosing_exprs)]
    scaffold_expr = smallest_exprs[0] if len(smallest_exprs) == 1 else None
    call_text = body[call_span[0]:call_span[1]] if call_span else ""
    compact_call = re.sub(r"\s+", "", call_text)
    exact_placeholder_call = (C2_PLACEHOLDER in call_text and
                              compact_call.count('"' + C2_PLACEHOLDER +
                                                 '",[],[],[],Static)') == 1 and
                              compact_call.endswith('"' + C2_PLACEHOLDER +
                                                    '",[],[],[],Static)'))
    block_text = body[scaffold_block[0]:scaffold_block[1]] if scaffold_block else ""
    block_decl_count = sum(1 for start, end in decls if scaffold_block and
                           scaffold_block[0] <= start < end <= scaffold_block[1])
    block_expr_count = sum(1 for start, end in expr_stmts if scaffold_block and
                           scaffold_block[0] <= start < end <= scaffold_block[1])
    location_ok = (f"verified/lib.rs({C2_PLACEHOLDER_SOURCE_LINE}," in
                   (body[scaffold_pure[0]:scaffold_pure[1]] if scaffold_pure else ""))
    structure_ok = (decl_names.count("cmp") == 1 and decl_names.count("cmp2") == 1 and
                    not any(name not in ("cmp", "cmp2") and name.startswith("cmp") for name in decl_names) and
                    len(cmp2_decls) == len(placeholders) == len(call_spans) == 1 and
                    block_decl_count == block_expr_count == 1 and
                    declaration_shape and scaffold_block is not None and scaffold_pure is not None and
                    scaffold_expr is not None and exact_placeholder_call and location_ok and
                    block_text.find(decl_text) < block_text.find(call_text))
    status = "CONFIRMED_C2_UNBOUND_SCAFFOLD_RUNTIME_INVENTORY" if (
        runtime_ok and structure_ok
    ) else "NOT_CONFIRMED"
    return {"status": status, "runtime_inventory": runtime,
            "placeholder": C2_PLACEHOLDER,
            "placeholder_occurrences_in_target": len(placeholders),
            "placeholder_source_line": C2_PLACEHOLDER_SOURCE_LINE,
            "type_with_typeid_decl_count_in_target": len(decls),
            "cmp_type_with_typeid_decl_count_in_target": decl_names.count("cmp"),
            "cmp2_type_with_typeid_decl_count_in_target": decl_names.count("cmp2"),
            "declaration_count_inside_scaffold_block": block_decl_count,
            "expression_statement_count_inside_scaffold_block": block_expr_count,
            "other_cmp_lifetime_declarations": [name for name in decl_names if name.startswith("cmp") and name not in ("cmp", "cmp2")],
            "typeid_of_lft_and_cmp2_k_shape": declaration_shape,
            "placeholder_call_exact": exact_placeholder_call,
            "same_pure_block_and_order": scaffold_block is not None and scaffold_pure is not None and
                                         scaffold_expr is not None and
                                         bool(block_text) and block_text.find(decl_text) < block_text.find(call_text),
            "placeholder_location_is_source_196": location_ok,
            "full_target_ast_sha256": digest(body.encode()),
            "not_a_bound_lifetime_ast": True}


def _record(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _run_stage(a, name: str, argv: list[str], cwd: Path, env: dict[str, str],
               *, cap: int = 180, stdin_path: Path | None = None,
               stdout_path: Path | None = None) -> int:
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 30)
    need(seconds > 0, f"deadline before C2 stage {name}")
    log = a.evidence / f"c2-{name}.log"
    stderr_path = a.evidence / f"c2-{name}-stderr.log" if stdout_path else None
    resources = a.evidence / f"c2-{name}-resources.txt"
    out_file = stdout_path.open("wb") if stdout_path else log.open("wb")
    err_file = stderr_path.open("wb") if stderr_path else subprocess.STDOUT
    in_file = stdin_path.open("rb") if stdin_path else open(os.devnull, "rb")
    stage_env = env.copy()
    stage_env["PWD"] = str(cwd)
    try:
        code = subprocess.run(("/usr/bin/time", "-v", "-o", str(resources),
                               "timeout", "--signal=TERM", "--kill-after=10s",
                               f"{seconds}s", *argv), cwd=cwd, env=stage_env,
                              stdin=in_file, stdout=out_file,
                              stderr=err_file, check=False).returncode
    finally:
        in_file.close()
        out_file.close()
        if stderr_path:
            err_file.close()
    _record(a.evidence / f"c2-{name}-stage.json", {
        "argv": argv, "cwd": str(cwd), "exit": code,
        "timeout_seconds": seconds,
        "log": str(log.relative_to(a.evidence)) if stdout_path is None else None,
        "stdout": str(stdout_path.relative_to(a.evidence)) if stdout_path else None,
        "stdout_sha256": digest(stdout_path.read_bytes()) if stdout_path and stdout_path.is_file() else None,
        "stderr": str(stderr_path.relative_to(a.evidence)) if stderr_path else None,
        "stderr_sha256": digest(stderr_path.read_bytes()) if stderr_path and stderr_path.is_file() else None,
        "stderr_merged_into_log": stdout_path is None,
        "effective_pwd": str(cwd),
        "resources": str(resources.relative_to(a.evidence))})
    return code


def _copy_and_pin_fixture(a, fixture: Path, c2fixture: Path, pin: dict,
                          pin_path: Path, draft_path: Path) -> dict:
    need(not c2fixture.exists(), "C2 discovery fixture already exists")
    shutil.copytree(fixture, c2fixture, symlinks=True)
    verified = c2fixture / "verified/lib.rs"
    original = c2fixture / "original/lib.rs"
    base, orig = verified.read_bytes(), original.read_bytes()
    draft_bytes = draft_path.read_bytes()
    annotated, source_report = prepare_c2_bytes(base, orig, draft_bytes, pin)
    verified.write_bytes(annotated)
    source_report.update({"fixture_verified_path": str(verified),
                          "fixture_original_path": str(original),
                          "original_source_sha256_after": digest(original.read_bytes()),
                          "source_pin_sha256": digest(pin_path.read_bytes()),
                          "draft_sha256_expected": pin["draft_sha256"]})
    need(source_report["draft_sha256"] == pin["draft_sha256"], "C2 draft source pin differs")
    need(source_report["original_source_sha256_after"] == pin["ghost_stripped_runtime_sha256"],
         "C2 original source changed")
    _record(a.evidence / "c2-source-certificate.json", source_report)
    return source_report


def _capture_support(a, fixture: Path, tool: Path, env: dict[str, str], source_report: dict,
                     schema: Path) -> dict[str, Any]:
    exporter = tool / "bin/vf-rust-mir-exporter"
    capture = a.proof_root / "research/challenge-8/overnight-sort4/capture.py"
    capmod = importlib_module(capture)
    rows: dict[str, Any] = {}
    for mode, extra in (("normal", []), ("readonly", ["--vf-rust-mir-exporter:preprocess-readonly"])):
        mir_bin = a.evidence / f"c2-{mode}-mir.bin"
        code = _run_stage(a, f"{mode}-export",
                          [str(exporter), "verified/lib.rs",
                           f"--sysroot={a.compiler_sysroot}", "--edition", "2021", *extra],
                          fixture, env, cap=180, stdout_path=mir_bin)
        rows[f"{mode}-export"] = {"exit": code, "sha256": digest(mir_bin.read_bytes()) if mir_bin.exists() else None}
        decoded = a.evidence / f"c2-{mode}-mir.txt"
        if code == 0:
            dec = _run_stage(a, f"{mode}-decode", ["capnp", "decode", str(schema), "VfMir"],
                             fixture, env, cap=90, stdin_path=mir_bin, stdout_path=decoded)
        else:
            dec = None
        rows[f"{mode}-decode"] = {"exit": dec,
                                  "sha256": digest(decoded.read_bytes()) if decoded.exists() else None}
        if dec == 0:
            graph = capmod.graph_inventory(decoded, a.evidence, f"c2-{mode}")
            rows[f"{mode}-complete_function"] = graph
    refine = _run_stage(a, "refinement", [str(tool / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021", "original/lib.rs", "verified/lib.rs"],
                       fixture, env, cap=180)
    rows["refinement"] = {"exit": refine, "log_sha256": digest((a.evidence / "c2-refinement.log").read_bytes())}
    complete = (all(rows.get(k, {}).get("exit") == 0 for k in
                    ("normal-export", "normal-decode", "readonly-export", "readonly-decode", "refinement")) and
                all(rows.get(f"{mode}-complete_function", {}).get("source_comparator_calls") == 5 and
                    rows.get(f"{mode}-complete_function", {}).get("complete_record_fields_present") ==
                    ["inputs", "localDecls", "basicBlocks"]
                    for mode in ("normal", "readonly")))
    source_pair = [digest((fixture / p).read_bytes()) for p in ("verified/lib.rs", "original/lib.rs")]
    unchanged = source_pair == [source_report["annotated_verified_sha256"],
                                 source_report["ghost_stripped_runtime_sha256"]]
    rows.update({"support_all_zero": complete, "fixture_source_pair_unchanged": unchanged,
                 "source_pair_sha256": source_pair, "proof_credit": False,
                 "full_mir_capture_is_support_only": True,
                 "complete_graph_capture_for_raw_review": complete,
                 "c2_ordered_operands_unwind_status": (
                     "UNREVIEWED_COMPLETE_GRAPH_CAPTURE" if complete else "NOT_CONFIRMED")})
    _record(a.evidence / "c2-mir-support.json", rows)
    return rows


def importlib_module(path: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("c2_sort4_capture", path)
    need(spec is not None and spec.loader is not None, f"capture module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _default_off_c1_prefix_probe(a, fixture: Path, tool: Path,
                                 env: dict[str, str], c1_result: dict[str, Any],
                                 pin: dict[str, Any]) -> dict[str, Any]:
    """Recheck the existing C1 positive after C2 patch, with C2 explicitly off."""
    probe_fixture = a.evidence / "c2-default-off-c1-prefix-fixture"
    need(not probe_fixture.exists(), "C2 default-off probe fixture already exists")
    shutil.copytree(fixture, probe_fixture, symlinks=True)
    verified = probe_fixture / "verified/lib.rs"
    original = probe_fixture / "original/lib.rs"
    before = [digest(verified.read_bytes()), digest(original.read_bytes())]
    need(before == [pin["base_verified_sha256"], pin["ghost_stripped_runtime_sha256"]],
         "C2 default-off probe received a changed C1 source pair")
    ast_path = probe_fixture / "actual-c1-prefix-post-ast.ml"
    if ast_path.exists():
        ast_path.unlink()
    probe_env = env.copy()
    probe_env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{tool}/bin:" + probe_env.get("LD_LIBRARY_PATH", "")
    probe_env["SORT4_ACTUAL_AST_SCOPE_TEST"] = "1"
    probe_env["SORT4_ACTUAL_C1_PREFIX_TEST"] = "1"
    probe_env["SORT4_C1_PREFIX_CONTROL"] = "none"
    probe_env["SORT4_C1_OUTPUT_EQ"] = "1"
    probe_env["SORT4_STRICT_LFT_CUT"] = "1"
    probe_env["SORT4_ACTUAL_C2_DISCOVERY_TEST"] = "0"
    probe_env["SORT4_C2_DISCOVERY"] = "0"
    for key in ("SORT4_C1_DEBT_CONTROL", "SORT4_HRTB_OUTPUT",
                "SORT4_HRTB_OUTPUT_TARGETS", "SORT4_CALLBACK_UNWIND",
                "SORT4_STRICT_LFT_TRACE", "SORT4_STRICT_LFT_RELOCATE"):
        probe_env.pop(key, None)
    command = [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
               "-verbose", "2", "verified/lib.rs"]
    code = _run_stage(a, "default-off-c1-prefix-positive", command,
                      probe_fixture, probe_env, cap=600)
    log_path = a.evidence / "c2-default-off-c1-prefix-positive.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    scope_rows = re.findall(
        r"SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) "
        r"pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) "
        r"header_posts=([0-9a-f]{64})", log)
    prefix_rows = re.findall(
        r"SORT4-ACTUAL-C1-PREFIX-ONLY admitted normal_boundary=after_source194 "
        r"before_c2=source195 fnmut=1 outcomes=normal,direct_unwind "
        r"post=CURRENT_source4,F,thread,types,optional_dst suffix_removed=102 "
        r"delayed_kept=24 eager_kept=102 labels=(\d+) gotos=(\d+) "
        r"control=none post_ast=([0-9a-f]{64}) NOT_CALLABLE_SUMMARY", log)
    expected_post = c1_result.get("bounded_prefix", {}).get("positive", {}).get(
        "positive_post_ast_sha256_captured")
    c1_profile = json.loads((a.proof_root / C1_PROFILE).read_text())
    expected_pre_ast = c1_profile.get("pre_ast_sha256")
    errors = [line for line in log.splitlines()
              if ": error:" in line or line.startswith("Fatal error:")]
    dead = [line for line in log.splitlines() if re.search(r"\): dead code$", line)]
    parser = importlib_module(a.cloud_dir / "strict-cut-false-posts-audit.py")
    caller = parser.proof_entries(log, "sort4_stable")
    helper_rows = {}
    for name in ("recover_pair", "join_four_owned_cells"):
        entries = parser.proof_entries(log, name)
        before_target = len(entries) == len(caller) == 1 and entries[0] < caller[0]
        segment = log[entries[0]:caller[0]] if before_target else ""
        helper_rows[name] = {"unique_before_target": before_target,
                             "return_seen": "Executing return statement" in segment,
                             "leak_seen": "Leak check." in segment,
                             "error_absent": ": error:" not in segment}
    helpers_ok = all(all(row.get(k) is True for k in
                         ("unique_before_target", "return_seen", "leak_seen", "error_absent"))
                     for row in helper_rows.values())
    target_segment = log[caller[0]:] if len(caller) == 1 else ""
    output_eq_sites = [line for line in log.splitlines()
                       if line.startswith("SORT4-C1-OUTPUT-EQ ")]
    source_after = [digest(verified.read_bytes()), digest(original.read_bytes())]
    ast_fresh = ast_path.is_file() and ast_path.stat().st_size > 0
    ast_copy = a.evidence / "c2-default-off-c1-prefix-post-ast.ml"
    if ast_fresh:
        shutil.copy2(ast_path, ast_copy)
    accepted = (code == 0 and not errors and not dead and len(scope_rows) == 1 and
                scope_rows[0][0] == pin["base_verified_sha256"] and
                scope_rows[0][1] == expected_pre_ast and
                scope_rows[0][2] == expected_post and
                len(prefix_rows) == 1 and expected_post is not None and
                prefix_rows[0][2] == expected_post and ast_fresh and helpers_ok and
                len(caller) == 1 and "Leak check." in target_segment and
                "Executing return statement" in target_segment and
                "0 errors found (" in log and len(output_eq_sites) == 1 and
                "count=1 later_calls=0" in output_eq_sites[0] and
                source_after == before)
    result = {"classification": "C2_PATCH_DEFAULT_OFF_C1_PREFIX_REPLAY_PASSED" if accepted else
              "C2_PATCH_DEFAULT_OFF_C1_PREFIX_REPLAY_INCONCLUSIVE",
              "accepted_as_c2": False, "actual_sort4_proved": False,
              "exit": code, "source_pair_sha256_before": before,
              "source_pair_sha256_after": source_after,
              "scope_admission_rows": scope_rows, "prefix_only_rows": prefix_rows,
              "expected_pre_ast_sha256": expected_pre_ast,
              "expected_prior_c1_post_ast_node_sha256": expected_post,
              "fresh_nonempty_post_ast": ast_fresh,
              "post_ast_file_sha256": digest(ast_copy.read_bytes()) if ast_copy.is_file() else None,
              "same_unit_helpers": helper_rows, "target_entry_count": len(caller),
              "target_return_seen": "Executing return statement" in target_segment,
              "target_leak_seen": "Leak check." in target_segment,
              "output_equality_diagnostics": output_eq_sites,
              "error_lines": errors, "dead_code_lines": dead,
              "log_sha256": digest(log_path.read_bytes()) if log_path.exists() else None,
              "c2_discovery_opt_in": "0", "proof_credit_scope": "C1 regression only"}
    _record(a.evidence / "c2-default-off-c1-prefix-result.json", result)
    need(accepted, "C2 translator default-off C1 prefix regression did not pass")
    return result


def run_discovery(a, fixture: Path, c1_tool: Path, env: dict[str, str],
                  c1_result: dict[str, Any], snapshot_fn) -> dict[str, Any]:
    """Capture C2 full-source support and original-AST diagnostic; never prove C2."""
    gate = c1_result.get("bounded_prefix", {}).get("positive", {})
    need(gate.get("classification") == "PREFIX_ONLY_BOUNDED_C1_THEOREM" and
         gate.get("bounded_full_vf0_normal_unwind_post_return_leak") is True and
         gate.get("actual_sort4_proved") is False and
         gate.get("callable_summary") == "PREFIX_ONLY_NOT_CALLABLE_SUMMARY",
         "C2 discovery blocked: fresh bounded C1 VF0 prerequisite is not confirmed")
    pin_path = a.proof_root / PIN
    draft_path = a.proof_root / DRAFT
    profile_path = a.proof_root / PROFILE
    pin = json.loads(pin_path.read_text())
    profile = json.loads(profile_path.read_text())
    patch = a.proof_root / PATCH
    need(profile.get("classification") == C2_SCAFFOLD_CLASS and
         profile.get("source_sha256") == pin["annotated_verified_sha256"] and
         profile.get("original_source_sha256") == pin["ghost_stripped_runtime_sha256"] and
         profile.get("c1_base_source_sha256") == pin["base_verified_sha256"] and
         profile.get("patch_sha256") == digest(patch.read_bytes()) and
         profile.get("always_reject_after_scaffold_ast_emit") is True and
         profile.get("default_off_unchanged") is True and
         profile.get("cloud_discovery_enabled") is True,
         "C2 discovery profile/source/patch pin differs")
    need(profile.get("kernel_changed") is False and profile.get("memory_model_changed") is False,
         "C2 discovery patch profile claims kernel or memory-model changes")
    patch_lines = patch.read_text().splitlines()
    need([s for s in patch_lines if s.startswith(("--- ", "+++ "))] ==
         [f"--- a/{TRANSLATOR.as_posix()}", f"+++ b/{TRANSLATOR.as_posix()}"],
         "C2 discovery patch must touch only the translator module")
    base_translator = profile.get("base_translator_sha256")
    need(isinstance(base_translator, str) and len(base_translator) == 64 and
         digest((c1_tool / TRANSLATOR).read_bytes()) == base_translator,
         "C2 delta base does not match the already-built C1 translator")
    c1_inputs_path = a.evidence / "c1-prefix-profile-inputs.json"
    need(c1_inputs_path.is_file(), "fresh C1 translator profile input record is missing")
    c1_inputs = json.loads(c1_inputs_path.read_text())
    need(c1_inputs.get("patched_translator_sha256") == base_translator and
         c1_inputs.get("profile_sha256") == digest((a.proof_root / C1_PROFILE).read_bytes()) and
         c1_inputs.get("patch_sha256") == digest((a.proof_root / C1_PATCH).read_bytes()) and
         c1_inputs.get("accepted") is False,
         "C2 base is not the exact freshly built, unaccepted C1 translator profile")

    evidence_fixture = a.evidence / "c2-discovery-fixture"
    source_report = _copy_and_pin_fixture(a, fixture, evidence_fixture, pin,
                                          pin_path, draft_path)
    baseline_snapshot = snapshot_fn(a, c1_tool)
    c2_source = c1_tool
    need(baseline_snapshot["critical"][str(TRANSLATOR)] == base_translator,
         "C2 delta does not follow the exact C1-built isolated translator")
    need(_run_stage(a, "translator-patch-check",
                    ["git", "-C", str(c2_source), "apply", "--check", str(patch)],
                    c2_source, env, cap=60) == 0,
         "C2 translator delta does not apply after the C1 patch chain")
    need(_run_stage(a, "translator-patch-apply",
                    ["git", "-C", str(c2_source), "apply", str(patch)],
                    c2_source, env, cap=60) == 0,
         "C2 translator delta apply failed")
    patched_translator = digest((c2_source / TRANSLATOR).read_bytes())
    need(patched_translator == profile.get("patched_translator_sha256"),
         "C2 patched translator hash differs from profile")
    need(digest((c2_source / KERNEL).read_bytes()) == baseline_snapshot["critical"][str(KERNEL)],
         "C2 delta changed the frozen kernel")
    deps = a.work_root / "vfdeps-adf88dc"
    c2_env = env.copy()
    c2_env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{c2_source}/bin:" + c2_env.get("LD_LIBRARY_PATH", "")
    c2_env["SORT4_ACTUAL_AST_SCOPE_TEST"] = "1"
    c2_env["SORT4_ACTUAL_C1_PREFIX_TEST"] = "0"
    c2_env["SORT4_C1_PREFIX_CONTROL"] = "none"
    c2_env["SORT4_C1_OUTPUT_EQ"] = "0"
    c2_env["SORT4_STRICT_LFT_CUT"] = "1"
    c2_env["SORT4_ACTUAL_C2_DISCOVERY_TEST"] = "0"
    c2_env["SORT4_C2_DISCOVERY"] = "0"
    c2_env["SORT4_C2_DISCOVERY_PROFILE"] = str(a.proof_root / PROFILE)
    for key in ("SORT4_C1_DEBT_CONTROL", "SORT4_HRTB_OUTPUT",
                "SORT4_HRTB_OUTPUT_TARGETS", "SORT4_CALLBACK_UNWIND",
                "SORT4_STRICT_LFT_TRACE", "SORT4_STRICT_LFT_RELOCATE"):
        c2_env.pop(key, None)
    c2_env["PATH"] = str(deps / "bin") + os.pathsep + c2_env.get("PATH", "")
    c2_env["CAPNP_INC_DIR"] = str(deps / "include")
    c2_env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"

    _record(a.evidence / "c2-translator-profile-inputs.json", {
        "profile_sha256": digest(profile_path.read_bytes()),
        "patch_sha256": digest(patch.read_bytes()),
        "proof_sha": os.environ.get("PROOF_SHA"),
        "c1_prefix_profile_sha256": digest((a.proof_root / C1_PROFILE).read_bytes()),
        "c1_prefix_patch_sha256": digest((a.proof_root / C1_PATCH).read_bytes()),
        "fresh_c1_profile_inputs_sha256": digest(c1_inputs_path.read_bytes()),
        "c2_activation_sha256": digest((a.evidence / "c2-activation.json").read_bytes()),
        "base_translator_sha256": base_translator,
        "patched_translator_sha256": patched_translator,
        "source_certificate_sha256": digest((a.evidence / "c2-source-certificate.json").read_bytes()),
        "kernel_unchanged": True, "discovery_only": True, "proof_credit": False})
    need(_run_stage(a, "console-build", ["make", "-C", str(c2_source / "src"),
             "../bin/verifast", "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
             c2_source, c2_env, cap=900) == 0, "C2 discovery isolated translator build failed")
    need(digest((c2_source / TRANSLATOR).read_bytes()) == patched_translator,
         "C2 translator changed during build")
    after = snapshot_fn(a, c2_source)
    need(after["critical"][str(KERNEL)] == baseline_snapshot["critical"][str(KERNEL)] and
         after["head"] == baseline_snapshot["head"] and
         after["effective_rsspec"] == baseline_snapshot["effective_rsspec"] and
         after["proof_std"] == baseline_snapshot["proof_std"] and
         after["critical"][str(TRANSLATOR)] == patched_translator and
         all(after["critical"][key] == value for key, value in baseline_snapshot["critical"].items()
             if key != str(TRANSLATOR)) and
         all(after["binaries"][key] == value for key, value in baseline_snapshot["binaries"].items()
             if key != "bin/verifast") and
         after["binaries"]["bin/verifast"] != baseline_snapshot["binaries"]["bin/verifast"] and
         after["modified_names"] == baseline_snapshot["modified_names"],
         "C2 build changed frozen kernel/spec/proof library or translator")
    _record(a.evidence / "c2-tool-snapshot.json", after)

    default_off_probe = _default_off_c1_prefix_probe(a, fixture, c2_source,
                                                      env, c1_result, pin)

    support = _capture_support(a, evidence_fixture, c2_source, c2_env, source_report,
                               a.production_source / "src/rust_frontend/vf_mir/vf_mir.capnp")
    need(support["support_all_zero"] and support["fixture_source_pair_unchanged"],
         "C2 full normal/readonly MIR and refinement support failed")
    c2_env["SORT4_ACTUAL_C2_DISCOVERY_TEST"] = "1"
    c2_env["SORT4_C2_DISCOVERY"] = "1"
    ast_name = profile.get("scaffold_ast_filename")
    expected_diagnostic = profile.get("intentional_refusal_marker")
    expected_refusal = profile.get("source_refusal_marker")
    need(ast_name == "actual-c2-unbound-scaffold-ast.ml" and
         isinstance(expected_diagnostic, str) and expected_diagnostic and
         isinstance(expected_refusal, str) and expected_refusal and
         expected_diagnostic == "SORT4-C2-DISCOVERY: UNBOUND_C2_LIFETIME_NOT_PROOF scaffold_AST_emitted",
         "C2 profile lacks exact scaffold AST path/diagnostic/refusal markers")
    ast_path = evidence_fixture / ast_name
    if ast_path.exists():
        ast_path.unlink()
    verifier = [str(c2_source / "bin/verifast"), "-rustc_args", "--edition 2021",
                "-verbose", "2", "verified/lib.rs"]
    diag_code = _run_stage(a, "positive-unbound-scaffold-diagnostic", verifier,
                           evidence_fixture, c2_env, cap=600)
    diag_log_path = a.evidence / "c2-positive-unbound-scaffold-diagnostic.log"
    diag_log = diag_log_path.read_text(errors="replace") if diag_log_path.exists() else ""
    ast_fresh = ast_path.is_file() and ast_path.stat().st_size > 0
    ast_copy = a.evidence / "actual-c2-unbound-scaffold-ast.ml"
    if ast_fresh:
        shutil.copy2(ast_path, ast_copy)
    ast_hash = digest(ast_copy.read_bytes()) if ast_copy.is_file() else None
    ast_inv = unbound_scaffold_ast_inventory(ast_copy.read_text(errors="replace")) if ast_copy.is_file() else {"status": "NOT_CONFIRMED"}
    diag_errors = [line for line in diag_log.splitlines()
                   if ": error:" in line or line.startswith("Fatal error:")]
    diagnosis_ok = (diag_code in (1, 2) and len(diag_errors) == 1 and
                    expected_diagnostic in diag_errors[0] and
                    diag_log.count(expected_diagnostic) == 1 and ast_fresh and
                    ast_inv.get("status") == "CONFIRMED_C2_UNBOUND_SCAFFOLD_RUNTIME_INVENTORY")
    diag = {"classification": "C2_UNBOUND_SCAFFOLD_ONLY_NOT_PROOF" if diagnosis_ok else "C2_UNBOUND_SCAFFOLD_INCONCLUSIVE",
            "exit": diag_code, "expected_diagnostic_marker": expected_diagnostic,
            "error_lines": diag_errors,
            "diagnostic_marker_count": diag_log.count(expected_diagnostic),
            "fresh_nonempty_unbound_scaffold_ast": ast_fresh, "unbound_scaffold_ast_sha256": ast_hash,
            "ast_inventory": ast_inv, "source_certificate_sha256": digest((a.evidence / "c2-source-certificate.json").read_bytes()),
            "raw_log_sha256": digest(diag_log_path.read_bytes()) if diag_log_path.exists() else None,
            "invocation_stage_sha256": digest((a.evidence / "c2-positive-unbound-scaffold-diagnostic-stage.json").read_bytes()),
            "pinned_translator_sha256": patched_translator,
            "same_invocation_ast_emission": ast_fresh and diag_log.count(expected_diagnostic) == 1,
            "source_pair_sha256_after": [digest((evidence_fixture / p).read_bytes()) for p in
                                          ("verified/lib.rs", "original/lib.rs")],
            "actual_sort4_proved": False, "accepted": False,
            "proof_credit_scope": "unbound declaration scaffold structure only; no C2 proof or summary",
            "placeholder": C2_PLACEHOLDER,
            "placeholder_source_line": C2_PLACEHOLDER_SOURCE_LINE,
            "type_interp_or_lifetime_binding_proved": False}
    _record(a.evidence / "c2-diagnostic-result.json", diag)

    mutant = a.evidence / "c2-source-hash-mutant"
    need(not mutant.exists(), "C2 hash-mutant fixture already exists")
    shutil.copytree(evidence_fixture, mutant, symlinks=True)
    mutant_source = mutant / "verified/lib.rs"
    data = mutant_source.read_bytes()
    need(data.count(ANNOTATED_C2) == 1, "C2 source-hash mutant target call is not unique")
    original_operands = b"v_base.add(3), &*v_base.add(2)"
    need(data.count(original_operands) == 1, "C2 operand mutation anchor is missing or ambiguous")
    mutant_bytes = data.replace(original_operands, b"v_base.add(2), &*v_base.add(3)", 1)
    mutant_source.write_bytes(mutant_bytes)
    mutant_ast = mutant / ast_name
    if mutant_ast.exists():
        mutant_ast.unlink()
    mutant_code = _run_stage(a, "source-hash-mutant", verifier, mutant, c2_env, cap=600)
    mutant_log_path = a.evidence / "c2-source-hash-mutant.log"
    mutant_log = mutant_log_path.read_text(errors="replace") if mutant_log_path.exists() else ""
    mutant_errors = [line for line in mutant_log.splitlines()
                     if ": error:" in line or line.startswith("Fatal error:")]
    refusal = (mutant_code in (1, 2) and len(mutant_errors) == 1 and
               mutant_log.count(expected_refusal) == 1 and
               (not mutant_ast.exists() or mutant_ast.stat().st_size == 0) and
               not re.search(r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function 'sort4_stable'", mutant_log))
    _record(a.evidence / "c2-source-hash-mutant-result.json", {
        "classification": "C2_SOURCE_HASH_REFUSAL_BEFORE_AST_OR_BODY" if refusal else "C2_SOURCE_HASH_CONTROL_INCONCLUSIVE",
        "exit": mutant_code, "expected_refusal_marker": expected_refusal,
        "error_lines": mutant_errors,
        "source_sha256": digest(mutant_bytes),
        "base_source_sha256": digest(data),
        "refusal_marker_count": mutant_log.count(expected_refusal),
        "ast_emitted": mutant_ast.is_file() and mutant_ast.stat().st_size > 0,
        "target_body_entry_seen": bool(re.search(r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function 'sort4_stable'", mutant_log)),
        "log_sha256": digest(mutant_log_path.read_bytes()) if mutant_log_path.exists() else None,
        "proof_credit": False})
    result = {"classification": diag["classification"], "accepted": False,
              "actual_sort4_proved": False, "full_body_exit_zero": False,
              "callable_summary": "C2_UNBOUND_SCAFFOLD_ONLY_NOT_PROOF",
              "diagnostic": diag, "support": support,
              "c2_ordered_operands_unwind_status": "UNREVIEWED_COMPLETE_GRAPH_CAPTURE",
              "default_off_c1_prefix_regression": default_off_probe,
              "source_hash_mutant_intended": refusal,
              "translator_profile_inputs": "c2-translator-profile-inputs.json",
              "proof_credit_scope": "unbound C2 scaffold diagnostic only; no C2 bounded theorem",
              "type_interp_or_lifetime_binding_proved": False}
    _record(a.evidence / "c2-discovery-result.json", result)
    return result
