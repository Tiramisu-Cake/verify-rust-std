#!/usr/bin/env python3
"""Cloud-only adversarial controls for first-callback HRTB admission.

This module is inert when imported. It captures the exact MIR exports produced
by the pinned verifier/refiner in the authorized Cloud Build, replays isolated
Cap'n Proto mutations through byte-identical copied tools, and records only
intended-target refusals. Importing, parsing fixtures, and editing source never
run a compiler, exporter, verifier, or refiner on the VPS.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


EXPECTED_HRTB_ERROR = "First callback recovery requires the typed source FnMut Continue call"
REFINER_SUCCESS = "QUALIFIED_FIRST_FNMUT_CONTINUE_EDGE:"
REFINER_UNWIND_ERROR = (
    "The source-bound first FnMut::call_mut unwind edge must be Continue on both sides")
CALL_ANNOTATION = b"::<F, (&'cmp u64, &'cmp u64), 'cmp>"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"pinned Cloud helper is unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _matching_end(text: str, start: int, opening: str, closing: str) -> int:
    """Find a balanced Cap'n Proto text delimiter, ignoring quoted strings."""
    if start >= len(text) or text[start] != opening:
        raise ValueError(f"expected {opening!r} at decoded-text offset {start}")
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError(f"unterminated {opening}{closing} Cap'n Proto text value")


def _field_span(block: str, field: str, opening: str = "[") -> tuple[int, int]:
    matches = list(re.finditer(rf"\b{re.escape(field)}\s*=\s*", block))
    if len(matches) != 1:
        raise ValueError(f"{field}: expected one field in selected record, got {len(matches)}")
    start = matches[0].end()
    closing = {"[": "]", "(": ")", "{": "}"}[opening]
    end = _matching_end(block, start, opening, closing)
    return start, end


def _split_items(text: str) -> list[str]:
    """Split a decoded list at commas outside nested Cap'n Proto values."""
    result: list[str] = []
    start = 0
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    quoted = escaped = False
    for index, char in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char in pairs:
            stack.append(pairs[char])
        elif char in ")]}":
            if not stack or stack.pop() != char:
                raise ValueError("unbalanced decoded Cap'n Proto item")
        elif char == "," and not stack:
            item = text[start:index].strip()
            if item:
                result.append(item)
            start = index + 1
    if quoted or stack:
        raise ValueError("unterminated decoded Cap'n Proto item")
    item = text[start:].strip()
    if item:
        result.append(item)
    return result


def _item_spans(text: str) -> list[tuple[int, int]]:
    """Return ranges of top-level comma-separated values within a Cap'n Proto list."""
    spans: list[tuple[int, int]] = []
    start = 0
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    quoted = escaped = False
    for index, char in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char in pairs:
            stack.append(pairs[char])
        elif char in ")]}":
            if not stack or stack.pop() != char:
                raise ValueError("unbalanced decoded Cap'n Proto item")
        elif char == "," and not stack:
            if text[start:index].strip():
                spans.append((start, index))
            start = index + 1
    if quoted or stack:
        raise ValueError("unterminated decoded Cap'n Proto item")
    if text[start:].strip():
        spans.append((start, len(text)))
    return spans


def _field_list(block: str, field: str) -> tuple[int, int, list[str]]:
    start, end = _field_span(block, field, "[")
    return start, end, _split_items(block[start + 1:end - 1])


def _unique_function_body(decoded: str) -> tuple[int, int, str]:
    list_start, list_end = _field_span(decoded, "bodies", "[")
    list_text = decoded[list_start + 1:list_end - 1]
    candidates = []
    for start, end in _item_spans(list_text):
        segment = list_text[start:end]
        # Body's own defPath precedes its nested MIR operands in schema order.
        match = re.search(r'\bdefPath\s*=\s*"([^\"]+)"', segment)
        if match is None or match.group(1).split("::")[-1] not in (
                "insert_tail", "insert_tail_first_callback_prefix"):
            continue
        if "clauses = [" in segment or "implBlockClauses = [" in segment:
            candidates.append((list_start + 1 + start, list_start + 1 + end, segment))
    if len(candidates) != 1:
        raise ValueError(f"expected one insert_tail body with clause lists, found {len(candidates)}")
    return candidates[0]


def _clause_list_ranges(decoded: str) -> list[tuple[str, int, int, list[str]]]:
    body_start, _, body = _unique_function_body(decoded)
    fields = []
    for field in ("clauses", "implBlockClauses"):
        for match in re.finditer(rf"\b{field}\s*=\s*\[", body):
            start = match.end() - 1
            end = _matching_end(body, start, "[", "]")
            fields.append((field, body_start + start, body_start + end,
                           _split_items(body[start + 1:end - 1])))
    return fields


def _field_text(block: str, field: str, opening: str = "(") -> str:
    start, end = _field_span(block, field, opening)
    return block[start:end]


def _quoted_field(block: str, field: str) -> str | None:
    found = re.findall(rf'\b{re.escape(field)}\s*=\s*"([^\"]*)"', block)
    return found[0] if len(found) == 1 else None


def _regions(block: str) -> list[str]:
    _, _, values = _field_list(block, "boundRegions")
    return [value.strip().strip('"') for value in values]


def _args(block: str) -> str:
    _, end = _field_span(block, "args", "[")
    start = re.search(r"\bargs\s*=\s*\[", block).end() - 1
    return re.sub(r"\s+", "", block[start + 1:end - 1])


def _bool_output(block: str) -> bool:
    return re.search(r"\bterm\s*=\s*\(\s*ty\s*=\s*\(\s*kind\s*=\s*\(\s*bool\s*=\s*void\s*\)\s*\)\s*\)",
                     block) is not None


def _target_clauses(decoded: str) -> tuple[str, list[tuple[str, str, list[str]]]]:
    """Return unique FnOnce::Output projection and paired FnMut trait clauses."""
    all_clauses = []
    for _, _, _, clauses in _clause_list_ranges(decoded):
        all_clauses.extend(clauses)
    projections = [c for c in all_clauses
                   if "projection = (" in c and
                   (lambda d: d is not None and
                    d.endswith("FnOnce::Output"))(_quoted_field(c, "defId"))]
    if len(projections) != 1:
        raise ValueError(f"expected one FnOnce::Output projection clause, found {len(projections)}")
    projection = projections[0]
    p_args = _args(projection)
    p_regions = _regions(projection)
    traits = [c for c in all_clauses
              if "trait = (" in c and
              (lambda d: d is not None and d.endswith("FnMut"))(_quoted_field(c, "defId")) and
              _args(c) == p_args and _regions(c) == p_regions]
    if len(traits) != 1:
        raise ValueError(f"expected one paired FnMut trait clause, found {len(traits)}")
    paired = [("projection", projection, p_regions), ("trait", traits[0], _regions(traits[0]))]
    return p_args, paired


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one exact Cap'n Proto anchor, found {count}")
    return text.replace(old, new, 1)


def _replace_clause(decoded: str, which: str, old_clause: str, new_clause: str) -> str:
    count = decoded.count(old_clause)
    if count != 1:
        raise ValueError(f"{which}: selected clause is not unique in decoded message")
    return decoded.replace(old_clause, new_clause, 1)


def _mutate_clause(decoded: str, mutation: str) -> str:
    _, paired = _target_clauses(decoded)
    projection = paired[0][1]
    trait = paired[1][1]
    if mutation.startswith("trait_binder_"):
        regions = _regions(trait)
        if len(regions) != 2 or regions[0] == regions[1]:
            raise ValueError("paired FnMut clause does not have two distinct binders")
        start, end = _field_span(trait, "boundRegions", "[")
        if mutation == "trait_binder_count":
            new_list = json.dumps([regions[0]])
        elif mutation == "trait_binder_order":
            new_list = json.dumps([regions[1], regions[0]])
        elif mutation == "trait_binder_identity":
            new_list = json.dumps([regions[0], "'foreign"])
        else:
            raise ValueError(f"unknown trait binder mutation: {mutation}")
        mutated_trait = trait[:start] + new_list + trait[end:]
        return _replace_clause(decoded, "trait binder", trait, mutated_trait)
    if mutation == "projection_binder_ref_mismatch":
        regions = _regions(projection)
        if len(regions) != 2 or regions[0] == regions[1]:
            raise ValueError("Output projection does not have two distinct binders")
        start, end = _field_span(projection, "boundRegions", "[")
        mutated = projection[:start] + json.dumps(["'foreign", regions[1]]) + projection[end:]
        return _replace_clause(decoded, "projection/ref mismatch", projection, mutated)
    if mutation == "wrong_output":
        if not _bool_output(projection):
            raise ValueError("selected projection is not the expected bool output")
        mutated = _replace_once(projection, "bool = void", "uInt = (u8 = void)", "Output bool")
        return _replace_clause(decoded, "Output type", projection, mutated)
    if mutation == "ambiguous_projection":
        for field, start, end, clauses in _clause_list_ranges(decoded):
            if projection in clauses:
                body_start, _, _ = _unique_function_body(decoded)
                list_start, list_end = start, end
                inside = decoded[list_start + 1:list_end - 1]
                # The exact canonical clause is inserted beside itself. The
                # paired-trait search remains unique while eligible outputs
                # become ambiguous.
                replacement = inside + ("\n        " if inside.strip() else "") + projection + ","
                return decoded[:list_start + 1] + replacement + decoded[list_end - 1:]
        raise ValueError("selected Output projection is not in an eligible body clause list")
    if mutation in ("wrong_source_F", "wrong_source_u64"):
        replacements = []
        for label, clause in (("projection", projection), ("FnMut trait", trait)):
            args_start = re.search(r"\bargs\s*=\s*\[", clause)
            if args_start is None:
                raise ValueError(f"{label}: args list absent")
            prefix, suffix = clause[:args_start.end()], clause[args_start.end():]
            old, new = (("param = \"F\"", "param = \"G\"")
                        if mutation == "wrong_source_F" else
                        ("uInt = (u64 = void)", "uInt = (u8 = void)"))
            if mutation == "wrong_source_u64":
                count = clause.count(old)
                if count != 2:
                    raise ValueError(f"{label} source u64: expected two tuple referents, found {count}")
                replacements.append(clause.replace(old, new))
            else:
                replacements.append(_replace_once(clause, old, new, f"{label} source type"))
        changed = _replace_clause(decoded, "wrong source type projection", projection, replacements[0])
        return _replace_clause(changed, "wrong source type trait", trait, replacements[1])
    raise ValueError(f"unknown HRTB clause mutation: {mutation}")


def _mutate_call_unwind(decoded: str, call_line: int, action: str = "cleanup") -> str:
    body_start, _, body = _unique_function_body(decoded)
    body_start += 0
    # Use the source-bound call span, then alter only that call's unwind union.
    candidates = []
    for match in re.finditer(r"\bcall\s*=\s*\(", body):
        start = match.end() - 1
        end = _matching_end(body, start, "(", ")")
        record = body[start:end]
        call_span = re.search(r"\bcallSpan\s*=\s*\(", record)
        if call_span is None:
            continue
        span_end = _matching_end(record, call_span.end() - 1, "(", ")")
        span = record[call_span.end() - 1:span_end]
        if re.search(rf"\bline\s*=\s*{call_line}\b", span):
            candidates.append((start, end, record))
    if len(candidates) != 1:
        raise ValueError(f"expected one FnCallData at source line {call_line}, found {len(candidates)}")
    start, end, record = candidates[0]
    if "unwindAction = (continue = void)" not in record:
        raise ValueError("source-bound first callback call is not Continue in captured MIR")
    cleanup_indices = []
    # Keep the synthetic Cleanup target valid by reusing an existing cleanup
    # edge in the same source function.
    for block in re.finditer(r"\bbasicBlocks\s*=\s*\[", body):
        list_start = block.end() - 1
        list_end = _matching_end(body, list_start, "[", "]")
        for item in _split_items(body[list_start + 1:list_end - 1]):
            if "isCleanup = true" not in item:
                continue
            ident = re.search(r"\bid\s*=\s*\(\s*index\s*=\s*(\d+)\s*\)", item)
            if ident:
                cleanup_indices.append(ident.group(1))
        break
    if not cleanup_indices:
        existing = re.search(r"unwindAction\s*=\s*\(\s*cleanup\s*=\s*\(\s*index\s*=\s*(\d+)\s*\)\s*\)",
                             body)
        if existing:
            cleanup_indices.append(existing.group(1))
    if action == "cleanup":
        if not cleanup_indices:
            raise ValueError("no existing cleanup BasicBlockId available for the unwind mutation")
        replacement = f"unwindAction = (cleanup = (index = {cleanup_indices[0]}))"
    elif action == "terminate":
        replacement = "unwindAction = (terminate = void)"
    else:
        raise ValueError(f"unknown unwind mutation action: {action}")
    changed_record = _replace_once(record, "unwindAction = (continue = void)",
                                   replacement, "first callback unwind")
    return decoded[:body_start + start] + changed_record + decoded[body_start + end:]


def _call_unwind_at_line(decoded: str, call_line: int) -> str:
    _, _, body = _unique_function_body(decoded)
    candidates = []
    for match in re.finditer(r"\bcall\s*=\s*\(", body):
        start = match.end() - 1
        end = _matching_end(body, start, "(", ")")
        record = body[start:end]
        span_match = re.search(r"\bcallSpan\s*=\s*\(", record)
        if span_match is None:
            continue
        span_end = _matching_end(record, span_match.end() - 1, "(", ")")
        span = record[span_match.end() - 1:span_end]
        if re.search(rf"\bline\s*=\s*{call_line}\b", span):
            actions = re.findall(r"\bunwindAction\s*=\s*\(\s*(continue|cleanup|terminate|unreachable)\s*=", record)
            if len(actions) == 1:
                candidates.append(actions[0])
    if len(candidates) != 1:
        raise ValueError(f"expected one call unwind at source line {call_line}, found {len(candidates)}")
    return candidates[0]


def _relocate_first_markers_to_late(source: bytes) -> tuple[bytes, int]:
    marker_names = (b"first_callback_close::", b"first_callback_scope_end::",
                    b"first_callback_recover::")
    if any(source.count(name) != 1 for name in marker_names):
        raise ValueError("expected one complete first-callback marker trio")
    close_at = source.index(marker_names[0])
    recover_at = source.index(marker_names[2])
    start = source.rfind(b"\n", 0, close_at) + 1
    end = source.find(b"\n", recover_at)
    if end < 0:
        raise ValueError("recovery marker does not end at a source line boundary")
    end += 1
    sequence = source[start:end]
    if not (sequence.index(marker_names[0]) < sequence.index(marker_names[1]) <
            sequence.index(marker_names[2])):
        raise ValueError("first callback marker order changed")
    if sequence.count(b"\n") != 3:
        raise ValueError("expected exactly the three adjacent marker lines")
    late_anchor = b"if !is_less(&tmp, &*sift) {"
    if source.count(late_anchor) != 1:
        raise ValueError("late comparator source anchor is not unique")
    without = source[:start] + source[end:]
    late_at = without.index(late_anchor)
    line_end = without.find(b"\n", late_at)
    if line_end < 0:
        raise ValueError("late comparator call is not line terminated")
    insert_at = line_end + 1
    mutated = without[:insert_at] + sequence + without[insert_at:]
    new_late = mutated.index(late_anchor)
    return mutated, mutated[:new_late].count(b"\n") + 1


def _encode(text: str, schema: Path, include_dirs: list[Path], cwd: Path,
            env: dict[str, str], output: Path) -> None:
    command = ["capnp", "encode"]
    for directory in include_dirs:
        command.extend(["-I", str(directory)])
    command.extend([str(schema), "VfMir"])
    with output.open("wb") as stream:
        result = subprocess.run(command, input=text, text=True, stdout=stream,
                                stderr=subprocess.PIPE, cwd=cwd, env=env,
                                check=False)
    if result.returncode != 0 or output.stat().st_size == 0:
        raise RuntimeError(f"capnp encode failed: {result.stderr!r}")


def _decode(raw: Path, schema: Path, include_dirs: list[Path], cwd: Path,
            env: dict[str, str], output: Path) -> str:
    command = ["capnp", "decode"]
    for directory in include_dirs:
        command.extend(["-I", str(directory)])
    command.extend([str(schema), "VfMir"])
    with raw.open("rb") as source:
        result = subprocess.run(command, stdin=source, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=cwd, env=env,
                                check=False)
    if result.returncode != 0 or not result.stdout:
        raise RuntimeError(f"capnp decode failed: {result.stderr!r}")
    output.write_bytes(result.stdout)
    return result.stdout.decode("utf-8")


def _tool_tree(tool_home: Path, case: Path,
               env: dict[str, str]) -> tuple[Path, dict[str, str]]:
    """Create a copied executable directory with all other pinned assets linked."""
    root = case / "tool"
    bin_dir = root / "bin"
    bin_dir.mkdir(parents=True)
    for child in tool_home.iterdir():
        if child.name == "bin":
            continue
        link = root / child.name
        if not link.exists():
            link.symlink_to(child, target_is_directory=child.is_dir())
    source_bin = tool_home / "bin"
    for child in source_bin.iterdir():
        if child.name in ("verifast", "refinement-checker", "vf-rust-mir-exporter"):
            continue
        (bin_dir / child.name).symlink_to(child, target_is_directory=child.is_dir())
    child_env = dict(env)
    child_env["PATH"] = str(bin_dir) + os.pathsep + child_env.get("PATH", "")
    lib_path = child_env.get("LD_LIBRARY_PATH", "")
    child_env["LD_LIBRARY_PATH"] = str(source_bin) + (os.pathsep + lib_path if lib_path else "")
    return bin_dir, child_env


def _exporter_wrapper(bin_dir: Path, real_exporter: Path, *, capture: Path | None = None,
                      replay: Path | None = None, allowed: tuple[str, ...] =
                      ("verified/lib.rs",)) -> tuple[Path, str]:
    wrapper = bin_dir / "vf-rust-mir-exporter"
    if capture is not None and replay is not None:
        raise ValueError("exporter wrapper cannot capture and replay simultaneously")
    code = ["#!/usr/bin/env python3", "import os, pathlib, subprocess, sys",
            f"real = {str(real_exporter)!r}", f"allowed = {allowed!r}"]
    code.extend([
        "if not any(arg in allowed for arg in sys.argv[1:]):",
        "    raise SystemExit('admission control exporter refused unexpected source argv')"])
    if replay is not None:
        code.extend([f"raw = pathlib.Path({str(replay)!r})",
                     "sys.stdout.buffer.write(raw.read_bytes())",
                     "raise SystemExit(0)"])
    else:
        code.extend(["result = subprocess.run([real, *sys.argv[1:]], stdout=subprocess.PIPE,",
                     "                        stderr=subprocess.PIPE, check=False)"])
        if capture is not None:
            code.extend([f"target = pathlib.Path({str(capture)!r})",
                         "if result.returncode == 0 and not target.exists():",
                         "    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)",
                         "    with os.fdopen(fd, 'wb') as output: output.write(result.stdout)",
                         "    target.with_suffix(target.suffix + '.argv.json').write_text(",
                         "        __import__('json').dumps(sys.argv[1:]))"])
        code.extend(["sys.stdout.buffer.write(result.stdout)",
                     "sys.stderr.buffer.write(result.stderr)",
                     "raise SystemExit(result.returncode)"])
    wrapper.write_text("\n".join(code) + "\n", encoding="utf-8")
    wrapper.chmod(0o755)
    return wrapper, _sha(wrapper)


def _run_verifast(label: str, evidence: Path, args, env: dict[str, str], base,
                  source_pair: tuple[bytes, bytes], *, replay: Path | None = None,
                  capture: Path | None = None) -> dict:
    case = evidence / label
    case.mkdir(parents=True)
    source_dir = case / "sources"
    (source_dir / "original").mkdir(parents=True)
    (source_dir / "verified").mkdir()
    (source_dir / "original/lib.rs").write_bytes(source_pair[0])
    (source_dir / "verified/lib.rs").write_bytes(source_pair[1])
    bin_dir, child_env = _tool_tree(Path(args.tool_home), case, env)
    real_vf = Path(args.tool_home) / "bin/verifast"
    local_vf = bin_dir / "verifast"
    shutil.copy2(real_vf, local_vf)
    local_vf.chmod(local_vf.stat().st_mode | 0o111)
    vf_hash = _sha(real_vf)
    if _sha(local_vf) != vf_hash:
        raise RuntimeError("copied verifier differs from pinned executable")
    wrapper, wrapper_hash = _exporter_wrapper(
        bin_dir, Path(args.tool_home) / "bin/vf-rust-mir-exporter",
        capture=capture, replay=replay)
    status = base.run_stage(source_dir, "verifast", [
        str(local_vf), "-rustc_args", "--edition 2021", "-verbose", "1",
        "-dump_ast_with_locs", "proof-ast.ml", "verified/lib.rs"], child_env,
        timeout_seconds=args.verifier_seconds, combine=True)
    log_path = source_dir / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    return {"exit_code": status, "log": log, "log_sha256": _sha(log_path) if log_path.is_file() else None,
            "verifast_sha256": _sha(local_vf), "pinned_verifast_sha256": vf_hash,
            "exporter_wrapper_sha256": wrapper_hash,
            "captured_export_sha256": _sha(capture) if capture is not None and capture.is_file() else None,
            "captured_export_argv": (json.loads(capture.with_suffix(capture.suffix + ".argv.json").read_text())
                                     if capture is not None and capture.with_suffix(
                                         capture.suffix + ".argv.json").is_file() else None),
            "replay_export_sha256": _sha(replay) if replay is not None else None,
            "source_sha256": {"original": _sha(source_dir / "original/lib.rs"),
                              "verified": _sha(source_dir / "verified/lib.rs")}}


def _registration(log: str) -> bool:
    return re.search(r"MERGE_HRTB_CALL registered=1 .*\bT=u64\b", log) is not None


def _positive_vf(outcome: dict) -> bool:
    log = outcome["log"]
    return (outcome["exit_code"] == 0 and _registration(log) and
            "MERGE_FIRST_CALLBACK_LOCAL_CONTINUE" in log and
            "0 errors found" in log and
            not re.search(r"\berror:", log, re.I) and
            "dead code" not in log.lower())


def _intended_hrtb_refusal(outcome: dict) -> bool:
    log = outcome["log"]
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    return (outcome["exit_code"] not in (0, 125, 127, None) and
            "MERGE_HRTB_CALL registered=0" in log and
            EXPECTED_HRTB_ERROR in log and len(errors) == 1 and
            EXPECTED_HRTB_ERROR in errors[0])


def _encode_and_replay_mutants(evidence: Path, args, env: dict[str, str], base,
                               source_pair: tuple[bytes, bytes], decoded: str,
                               pristine_raw: Path, include_dirs: list[Path],
                               *, mutations: tuple[str, ...]) -> dict:
    evidence.mkdir(parents=True, exist_ok=False)
    results = {}
    for mutation in mutations:
        family = evidence / mutation
        family.mkdir()
        baseline = _run_verifast(f"{mutation}/positive-baseline", evidence, args, env,
                                 base, source_pair, replay=pristine_raw)
        baseline_ok = _positive_vf(baseline)
        results[mutation] = {"positive_baseline": {
            "matched": baseline_ok, "registration_u64": baseline_ok,
            "exit_code": baseline["exit_code"], "log_sha256": baseline["log_sha256"],
            "verifast_sha256": baseline["verifast_sha256"],
            "exporter_wrapper_sha256": baseline["exporter_wrapper_sha256"],
            "replay_export_sha256": baseline["replay_export_sha256"]}}
        if not baseline_ok:
            results[mutation].update(matched=False, status="POSITIVE_BASELINE_FAILED_MUTANT_NOT_RUN")
            continue
        try:
            mutated_decoded = _mutate_clause(decoded, mutation)
            mutated_raw = family / "mutated.bin"
            _encode(mutated_decoded, Path(args.schema), include_dirs, family, env, mutated_raw)
        except Exception as error:
            results[mutation].update(matched=False, status="NOT_RUN_UNIQUE_MUTATION_SETUP_FAILED",
                                     blocker=f"{type(error).__name__}: {error}")
            continue
        outcome = _run_verifast(f"{mutation}/mutant", evidence, args, env,
                                base, source_pair, replay=mutated_raw)
        matched = _intended_hrtb_refusal(outcome)
        results[mutation].update({"matched": matched,
            "status": "INTENDED_HRTB_MATCHER_REFUSAL" if matched else "INCONCLUSIVE_WRONG_OR_EARLIER_FAILURE",
            "expected_registration": "MERGE_HRTB_CALL registered=0",
            "expected_error": EXPECTED_HRTB_ERROR,
            "exit_code": outcome["exit_code"], "log_sha256": outcome["log_sha256"],
            "verifast_sha256": outcome["verifast_sha256"],
            "exporter_wrapper_sha256": outcome["exporter_wrapper_sha256"],
            "mutated_export_sha256": _sha(mutated_raw)})
    return results


def _source_annotation_mutant(source: bytes, mutation: str) -> bytes:
    if source.count(CALL_ANNOTATION) != 1:
        raise ValueError("verified source does not contain one exact first-call annotation")
    if mutation == "wrong_ghost_F":
        changed = b"::<u64, (&'cmp u64, &'cmp u64), 'cmp>"
    elif mutation == "wrong_ghost_u64":
        changed = b"::<F, (&'cmp u8, &'cmp u8), 'cmp>"
    elif mutation == "wrong_ghost_lifetime":
        changed = b"::<F, (&'static u64, &'cmp u64), 'cmp>"
    else:
        raise ValueError(f"unknown source annotation mutation: {mutation}")
    return source.replace(CALL_ANNOTATION, changed, 1)


def _source_ghost_controls(evidence: Path, args, env: dict[str, str], base,
                           source_pair: tuple[bytes, bytes], *,
                           mutations: tuple[str, ...]) -> dict:
    evidence.mkdir(parents=True, exist_ok=False)
    results = {}
    for mutation in mutations:
        family = evidence / mutation
        family.mkdir()
        # Each family gets a fresh real-export baseline before any ghost edit.
        capture = family / "positive-export.bin"
        baseline = _run_verifast(f"{mutation}/positive-baseline", evidence, args, env,
                                 base, source_pair, capture=capture)
        baseline_ok = _positive_vf(baseline)
        row = {"positive_baseline": {"matched": baseline_ok,
                "registration_u64": baseline_ok, "exit_code": baseline["exit_code"],
                "log_sha256": baseline["log_sha256"],
                "exporter_wrapper_sha256": baseline["exporter_wrapper_sha256"],
                "captured_export_sha256": baseline["captured_export_sha256"]}}
        if not baseline_ok:
            row.update(matched=False, status="POSITIVE_BASELINE_FAILED_MUTANT_NOT_RUN")
            results[mutation] = row
            continue
        try:
            mutant_pair = (source_pair[0], _source_annotation_mutant(source_pair[1], mutation))
        except Exception as error:
            row.update(matched=False, status="NOT_RUN_SOURCE_MUTATION_SETUP_FAILED",
                       blocker=f"{type(error).__name__}: {error}")
            results[mutation] = row
            continue
        outcome = _run_verifast(f"{mutation}/mutant", evidence, args, env,
                                base, mutant_pair)
        matched = _intended_hrtb_refusal(outcome)
        row.update({"matched": matched,
            "status": "INTENDED_HRTB_MATCHER_REFUSAL" if matched else "INCONCLUSIVE_WRONG_OR_EARLIER_FAILURE",
            "expected_registration": "MERGE_HRTB_CALL registered=0",
            "expected_error": EXPECTED_HRTB_ERROR,
            "exit_code": outcome["exit_code"], "log_sha256": outcome["log_sha256"],
            "exporter_wrapper_sha256": outcome["exporter_wrapper_sha256"],
            "source_sha256": outcome["source_sha256"]})
        results[mutation] = row
    return results


def _isolate_legacy_fixture(template: bytes, cfg: str, expected_functions: int) -> bytes:
    """Mirror the old runner's source-only cfg isolation without its tool pins."""
    lines = template.splitlines(keepends=True)
    out: list[bytes] = []
    in_cases = active = False
    selected = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(b"#[cfg(hrtb_"):
            match = re.fullmatch(rb"#\[cfg\((hrtb_[a-z0-9_]+)\)\]", stripped)
            if match is None:
                raise ValueError("legacy HRTB fixture selector syntax changed")
            in_cases = True
            active = match.group(1).decode() == cfg
            if active:
                selected += 1
            continue
        if not in_cases or active:
            out.append(line)
    if selected != expected_functions:
        raise ValueError(f"{cfg}: expected {expected_functions} selected bodies, found {selected}")
    result = b"".join(out)
    if b"#[cfg(hrtb_" in result:
        raise ValueError(f"{cfg}: inactive selector leaked into isolated fixture")
    return result


def _legacy_regression_controls(evidence: Path, args, env: dict[str, str], base,
                                template_path: Path) -> dict:
    cases = (
        ("hrtb_positive", "positive", 1, 1, "positive"),
        ("hrtb_u8", "non_boolean", 0, 1, "non_boolean"),
        ("hrtb_no_output", "unconstrained_output", 0, 1, "unconstrained_output"),
        ("hrtb_wrong_f", "wrong_function_type", 0, 1, "wrong_function_type"),
        ("hrtb_wrong_t", "wrong_referent_type", 0, 1, "wrong_referent_type"),
        ("hrtb_unequal_lifetimes", "unequal_lifetimes", 0, 1, "unequal_lifetimes"),
        ("hrtb_second_call", "second_call_unannotated", 1, 2, "second_call_unannotated"),
        ("hrtb_second_body", "first_body", 1, 2, "first_body"),
    )
    receipt: dict = {"status": "RUN", "matched": False, "cases": {}}
    try:
        template = template_path.read_bytes()
        template_sha = _sha(template_path)
    except Exception as error:
        return {"status": "NOT_RUN_TEMPLATE_MISSING", "matched": False,
                "blocker": f"{type(error).__name__}: {error}"}
    root = evidence / "legacy-eight"
    root.mkdir(parents=True, exist_ok=False)
    receipt.update(template_sha256=template_sha,
        classification="TRANSLATOR_REGRESSION_CONTROLS_NO_PROOF_CREDIT")

    def run_one(case_name: str, cfg: str, function: str, expected_registered: int,
                expected_calls: int, fixture_bytes: bytes) -> dict:
        case = root / case_name
        case.mkdir()
        source_dir = case / "sources"
        (source_dir / "original").mkdir(parents=True)
        (source_dir / "verified").mkdir()
        source = source_dir / "verified/lib.rs"
        source.write_bytes(fixture_bytes)
        shutil.copy2(source, source_dir / "original/lib.rs")
        bin_dir, child_env = _tool_tree(Path(args.tool_home), case, env)
        local_vf = bin_dir / "verifast"
        shutil.copy2(Path(args.tool_home) / "bin/verifast", local_vf)
        local_vf.chmod(local_vf.stat().st_mode | 0o111)
        vf_sha = _sha(Path(args.tool_home) / "bin/verifast")
        if _sha(local_vf) != vf_sha:
            raise RuntimeError("legacy fixture copied verifier hash mismatch")
        wrapper, wrapper_sha = _exporter_wrapper(bin_dir,
            Path(args.tool_home) / "bin/vf-rust-mir-exporter",
            allowed=("verified/lib.rs",))
        cfg_arg = f"--edition 2021 --crate-type lib --cfg {cfg}"
        status = base.run_stage(source_dir, "verifast", [str(local_vf), "-rustc_args",
            cfg_arg, "-skip_specless_fns", "-verbose", "1", "verified/lib.rs"],
            child_env, timeout_seconds=args.verifier_seconds, combine=True)
        log_path = source_dir / "verifast.log"
        log = log_path.read_text(errors="replace") if log_path.is_file() else ""
        traces = re.findall(r"MERGE_HRTB_CALL registered=[01] [^\n]*", log)
        registered = [line for line in traces if "MERGE_HRTB_CALL registered=1 " in line]
        verified_body = any(f"Verifying function '{function}'" in line
                            for line in log.splitlines())
        classification = ("ownership_failure" if "No matching heap chunks" in log else
                          "type_failure" if re.search(r"error: Type mismatch\.?", log) else
                          "unsupported_frontend" if re.search(
                              r"error\[E[0-9]+\]|Failed to run rustc|error: aborting due", log) else
                          "other_verifier_failure")
        marker_line = None
        if expected_registered:
            lines = fixture_bytes.splitlines()
            fn_idx = next((i for i, line in enumerate(lines)
                           if b"pub unsafe fn " + function.encode() + b"<" in line), None)
            if fn_idx is not None:
                fn_end = next((i for i in range(fn_idx + 1, len(lines))
                               if b"pub unsafe fn " in lines[i]), len(lines))
                marker_idx = next((i for i in range(fn_idx, fn_end)
                                   if b"/*@::<" in lines[i]), None)
                if marker_idx is not None:
                    marker_line = marker_idx + 1
        registered_at_expected = (not expected_registered or marker_line is not None and any(
            f"lib.rs({marker_line}," in line for line in registered))
        no_frontend = classification in ("ownership_failure", "type_failure")
        matched = (status == 1 and len(traces) == expected_calls and
                   len(registered) == expected_registered and verified_body and
                   no_frontend and registered_at_expected)
        return {"matched": matched,
            "status": "EXPECTED_TRANSLATOR_REGRESSION_FAILURE" if matched else
                      "INCONCLUSIVE_WRONG_ROUTE_OR_FRONTEND_FAILURE",
            "cfg": cfg, "function": function, "exit_code": status,
            "classification": classification, "expected_calls": expected_calls,
            "observed_call_traces": len(traces), "expected_registrations": expected_registered,
            "observed_registrations": len(registered),
            "verified_body_observed": verified_body,
            "expected_equality_call_line": marker_line,
            "registration_at_expected_call": registered_at_expected,
            "verifast_sha256": _sha(local_vf), "exporter_wrapper_sha256": wrapper_sha,
            "fixture_sha256": _sha(source), "log_sha256": _sha(log_path) if log_path else None}

    try:
        # A fresh positive fixture precedes the remaining family. It must reach
        # the typed equality and fail only at the intentionally absent heap.
        cfg, function, registered, calls, _ = cases[0]
        fixture = _isolate_legacy_fixture(template, cfg, 1)
        baseline = run_one("positive-baseline", cfg, function, registered, calls, fixture)
        receipt["positive_baseline"] = baseline
        if not baseline["matched"]:
            receipt.update(status="POSITIVE_BASELINE_FAILED_MUTANTS_NOT_RUN", matched=False)
            return receipt
        for cfg, function, registered, calls, _ in cases:
            fixture = _isolate_legacy_fixture(template, cfg, 2 if cfg == "hrtb_second_body" else 1)
            receipt["cases"][cfg] = run_one(cfg, cfg, function, registered, calls, fixture)
        receipt["matched"] = all(row["matched"] for row in receipt["cases"].values())
        receipt["status"] = "ALL_EIGHT_EXPECTED_REGRESSION_FAILURES" if receipt["matched"] else \
                             "LEGACY_REGRESSIONS_INCOMPLETE_OR_INCONCLUSIVE"
    except Exception as error:
        receipt.update(status="INCONCLUSIVE_REGRESSION_SETUP_FAILURE", matched=False,
                       blocker=f"{type(error).__name__}: {error}")
    return receipt


def _refiner_capture(evidence: Path, args, env: dict[str, str], base,
                     source_pair: tuple[bytes, bytes]) -> tuple[dict[str, Path], dict]:
    case = evidence / "official-refiner-capture"
    case.mkdir()
    source_dir = case / "sources"
    (source_dir / "original").mkdir(parents=True)
    (source_dir / "verified").mkdir()
    (source_dir / "original/lib.rs").write_bytes(source_pair[0])
    (source_dir / "verified/lib.rs").write_bytes(source_pair[1])
    bin_dir, child_env = _tool_tree(Path(args.tool_home), case, env)
    real_refiner = Path(args.tool_home) / "bin/refinement-checker"
    local_refiner = bin_dir / "refinement-checker"
    shutil.copy2(real_refiner, local_refiner)
    local_refiner.chmod(local_refiner.stat().st_mode | 0o111)
    refiner_sha = _sha(real_refiner)
    if _sha(local_refiner) != refiner_sha:
        raise RuntimeError("copied official refiner differs from pinned executable")
    wrapper, wrapper_hash = _refiner_exporter_capture(bin_dir,
        Path(args.tool_home) / "bin/vf-rust-mir-exporter", case)
    status = base.run_stage(source_dir, "official-refiner-capture", [
        str(local_refiner), "--check-first-fnmut-continue", "--rustc-args",
        "--edition 2021", "original/lib.rs", "verified/lib.rs"], child_env,
        timeout_seconds=args.stage_seconds, combine=True)
    log = (source_dir / "official-refiner-capture.log").read_text(errors="replace")
    streams = {side: case / f"{side}.bin" for side in ("original", "verified")}
    receipt = {"exit_code": status, "success_marker": REFINER_SUCCESS,
        "success_marker_present": REFINER_SUCCESS in log,
        "no_refinement_errors": "No refinement errors found" in log,
        "log_sha256": _sha(source_dir / "official-refiner-capture.log"),
        "refiner_sha256": _sha(local_refiner),
        "exporter_wrapper_sha256": wrapper_hash,
        "export_sha256": {s: _sha(p) for s, p in streams.items() if p.is_file()}}
    if not (status == 0 and receipt["success_marker_present"] and
            receipt["no_refinement_errors"] and all(p.is_file() and p.stat().st_size for p in streams.values())):
        raise RuntimeError(f"official first-Continue refiner positive capture did not pass: {receipt}")
    return streams, receipt


def _refiner_exporter_capture(bin_dir: Path, real_exporter: Path,
                              capture_root: Path) -> tuple[Path, str]:
    wrapper = bin_dir / "vf-rust-mir-exporter"
    wrapper.write_text(
        "#!/usr/bin/env python3\nimport os, pathlib, subprocess, sys\n"
        f"real = {str(real_exporter)!r}\nroot = pathlib.Path({str(capture_root)!r})\n"
        "allowed = {'original/lib.rs': 'original', 'verified/lib.rs': 'verified'}\n"
        "if len(sys.argv) < 2 or sys.argv[1] not in allowed:\n"
        "    raise SystemExit('first-Continue capture refused unexpected exporter argv')\n"
        "side = allowed[sys.argv[1]]\n"
        "result = subprocess.run([real, *sys.argv[1:]], stdout=subprocess.PIPE,\n"
        "                        stderr=subprocess.PIPE, check=False)\n"
        "if result.returncode == 0:\n"
        "    target = root / (side + '.bin')\n"
        "    if not target.exists():\n"
        "        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)\n"
        "        with os.fdopen(fd, 'wb') as output: output.write(result.stdout)\n"
        "        target.with_suffix('.argv.json').write_text(__import__('json').dumps(sys.argv[1:]))\n"
        "sys.stdout.buffer.write(result.stdout)\n"
        "sys.stderr.buffer.write(result.stderr)\n"
        "raise SystemExit(result.returncode)\n", encoding="utf-8")
    wrapper.chmod(0o755)
    return wrapper, _sha(wrapper)


def _run_refiner_replay(label: str, evidence: Path, args, env: dict[str, str], base,
                        source_pair: tuple[bytes, bytes], raw_original: Path,
                        raw_verified: Path, *, expected: str | None = None) -> dict:
    case = evidence / label
    case.mkdir()
    source_dir = case / "sources"
    (source_dir / "original").mkdir(parents=True)
    (source_dir / "verified").mkdir()
    (source_dir / "original/lib.rs").write_bytes(source_pair[0])
    (source_dir / "verified/lib.rs").write_bytes(source_pair[1])
    bin_dir, child_env = _tool_tree(Path(args.tool_home), case, env)
    real_refiner = Path(args.tool_home) / "bin/refinement-checker"
    local_refiner = bin_dir / "refinement-checker"
    shutil.copy2(real_refiner, local_refiner)
    local_refiner.chmod(local_refiner.stat().st_mode | 0o111)
    refiner_sha = _sha(real_refiner)
    if _sha(local_refiner) != refiner_sha:
        raise RuntimeError("copied refiner differs from pinned executable")
    # Install an argv-checked two-stream replay wrapper.
    wrapper = bin_dir / "vf-rust-mir-exporter"
    wrapper.write_text(
        "#!/usr/bin/env python3\nimport pathlib, sys\n"
        f"messages = {{'original/lib.rs': pathlib.Path({str(raw_original)!r}), "
        f"'verified/lib.rs': pathlib.Path({str(raw_verified)!r})}}\n"
        "if len(sys.argv) < 2 or sys.argv[1] not in messages:\n"
        "    raise SystemExit('refiner replay refused unexpected exporter argv')\n"
        "sys.stdout.buffer.write(messages[sys.argv[1]].read_bytes())\n",
        encoding="utf-8")
    wrapper.chmod(0o755)
    wrapper_hash = _sha(wrapper)
    status = base.run_stage(source_dir, "official-refinement", [
        str(local_refiner), "--check-first-fnmut-continue", "--rustc-args",
        "--edition 2021", "original/lib.rs", "verified/lib.rs"], child_env,
        timeout_seconds=args.stage_seconds, combine=True)
    log_path = source_dir / "official-refinement.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    if expected is None:
        matched = status == 0 and REFINER_SUCCESS in log and "No refinement errors found" in log
    else:
        errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
        matched = (status not in (0, 125, 127, None) and len(errors) == 1 and
                   expected in errors[0])
    return {"matched": matched, "exit_code": status,
        "expected": expected or REFINER_SUCCESS,
        "expected_present": (expected or REFINER_SUCCESS) in log,
        "log_sha256": _sha(log_path) if log_path.is_file() else None,
        "refiner_sha256": _sha(local_refiner), "pinned_refiner_sha256": refiner_sha,
        "exporter_wrapper_sha256": wrapper_hash,
        # These are the only accepted argv values in the replay wrapper above;
        # replay messages come from the pinned captured exports, not a fresh
        # exporter invocation whose argv sidecars could be consulted here.
        "export_argv": {"original": "original/lib.rs",
                        "verified": "verified/lib.rs"},
        "original_export_sha256": _sha(raw_original),
        "verified_export_sha256": _sha(raw_verified)}


def _run_refiner_unwind_control(evidence: Path, args, env: dict[str, str], base,
                                source_pair: tuple[bytes, bytes],
                                include_dirs: list[Path], source_record: dict) -> dict:
    row: dict = {"matched": False, "status": "NOT_RUN"}
    try:
        evidence.mkdir(parents=True, exist_ok=False)
        streams, capture_receipt = _refiner_capture(evidence, args, env, base, source_pair)
        pristine = _run_refiner_replay("refiner-pristine-replay", evidence, args, env, base,
                                      source_pair, streams["original"], streams["verified"])
        if not pristine["matched"]:
            return {**row, "status": "POSITIVE_REPLAY_FAILED_MUTANT_NOT_RUN",
                    "capture": capture_receipt, "positive_baseline": pristine}
        decoded_path = evidence / "refiner-verified-decoded.txt"
        decoded = _decode(streams["verified"], Path(args.schema), include_dirs,
                          evidence, env, decoded_path)
        line = source_record.get("actual_first_call_line")
        if not isinstance(line, int):
            raise ValueError("source record has no actual_first_call_line")
        mutated_decoded = _mutate_call_unwind(decoded, line, action="terminate")
        mutated_verified = evidence / "refiner-verified-cleanup.bin"
        _encode(mutated_decoded, Path(args.schema), include_dirs, evidence, env, mutated_verified)
        outcome = _run_refiner_replay("refiner-first-unwind-mutant", evidence, args, env, base,
                                      source_pair, streams["original"], mutated_verified,
                                      expected=REFINER_UNWIND_ERROR)
        return {"matched": outcome["matched"],
            "status": "OFFICIAL_FIRST_UNWIND_REJECTION" if outcome["matched"] else
                      "INCONCLUSIVE_WRONG_OR_EARLIER_REFUSAL",
            "capture": capture_receipt, "positive_baseline": pristine,
            "expected_diagnostic": REFINER_UNWIND_ERROR,
            "mutant": outcome}
    except Exception as error:
        return {**row, "status": "NOT_RUN_UNIQUE_SETUP_OR_REPLAY_FAILED",
                "blocker": f"{type(error).__name__}: {error}"}


def _fullbody_source_record(source_record: dict) -> tuple[Path, dict] | None:
    case_value = source_record.get("full_body_case")
    record = source_record.get("full_body_source_record")
    if isinstance(case_value, dict):
        record = case_value.get("source_record", record)
        case_value = case_value.get("path")
    if not isinstance(case_value, str) or not isinstance(record, dict):
        return None
    case = Path(case_value)
    if not (case / "original/lib.rs").is_file() or not (case / "verified/lib.rs").is_file():
        return None
    return case, record


def _run_fullbody_cleanup_controls(evidence: Path, args, env: dict[str, str], base,
                                   include_dirs: list[Path], source_record: dict) -> dict:
    evidence.mkdir(parents=True, exist_ok=False)
    fullbody = _fullbody_source_record(source_record)
    if fullbody is None:
        return {"status": "NOT_RUN_FULLBODY_CASE_NOT_SUPPLIED", "matched": False,
                "blocker": "source_record must carry full_body_case and full_body_source_record"}
    case, full_record = fullbody
    pair = ((case / "original/lib.rs").read_bytes(), (case / "verified/lib.rs").read_bytes())
    first_line = full_record.get("actual_first_call_line")
    late_line = full_record.get("actual_late_call_line")
    if not isinstance(first_line, int) or not isinstance(late_line, int):
        return {"status": "NOT_RUN_FULLBODY_SOURCE_LINES_MISSING", "matched": False}
    raw = evidence / "fullbody-positive-export.bin"
    baseline = _run_verifast("fullbody-cleanup/positive-baseline", evidence, args, env,
                             base, pair, capture=raw)
    route_ok = (_registration(baseline["log"]) and
                "MERGE_FIRST_CALLBACK_LOCAL_CONTINUE" in baseline["log"] and
                EXPECTED_HRTB_ERROR not in baseline["log"])
    common = {"positive_baseline": {"matched": route_ok,
                "exit_code": baseline["exit_code"], "log_sha256": baseline["log_sha256"],
                "captured_export_sha256": baseline["captured_export_sha256"]}}
    if not route_ok:
        return {**common, "status": "POSITIVE_FULLBODY_TARGET_ROUTE_FAILED_MUTANTS_NOT_RUN",
                "matched": False}
    decoded_path = evidence / "fullbody-positive-decoded.txt"
    try:
        decoded = _decode(raw, Path(args.schema), include_dirs, evidence, env, decoded_path)
    except Exception as error:
        return {**common, "status": "NOT_RUN_FULLBODY_DECODE_FAILED", "matched": False,
                "blocker": f"{type(error).__name__}: {error}"}

    first_cleanup: dict = {"matched": False, "status": "NOT_RUN"}
    try:
        cleanup_text = _mutate_call_unwind(decoded, first_line, action="cleanup")
        cleanup_raw = evidence / "fullbody-first-call-cleanup.bin"
        _encode(cleanup_text, Path(args.schema), include_dirs, evidence, env, cleanup_raw)
        out = _run_verifast("fullbody-cleanup/first-call-cleanup-mutant", evidence,
            args, env, base, pair, replay=cleanup_raw)
        errors = [line for line in out["log"].splitlines()
                  if re.search(r"\berror:", line, re.I)]
        matched = (out["exit_code"] not in (0, 125, 127, None) and
                   EXPECTED_HRTB_ERROR in out["log"] and len(errors) == 1 and
                   EXPECTED_HRTB_ERROR in errors[0])
        first_cleanup = {"matched": matched,
            "status": "FIRST_MARKER_REFUSES_CLEANUP_EDGE" if matched else
                      "INCONCLUSIVE_WRONG_OR_EARLIER_FAILURE",
            "expected_diagnostic": EXPECTED_HRTB_ERROR,
            "exit_code": out["exit_code"], "log_sha256": out["log_sha256"],
            "mutated_export_sha256": _sha(cleanup_raw)}
    except Exception as error:
        first_cleanup = {"matched": False, "status": "NOT_RUN_UNIQUE_CLEANUP_SETUP_FAILED",
            "blocker": f"{type(error).__name__}: {error}"}

    late_cleanup: dict = {"matched": False, "status": "NOT_RUN"}
    try:
        if _call_unwind_at_line(decoded, late_line) != "cleanup":
            raise ValueError("source-bound late comparator MIR call is not a Cleanup edge")
        mutated_verified, mutated_late_line = _relocate_first_markers_to_late(pair[1])
        mutant_pair = (pair[0], mutated_verified)
        out = _run_verifast("fullbody-cleanup/late-marker-mutant", evidence,
                             args, env, base, mutant_pair)
        errors = [line for line in out["log"].splitlines()
                  if re.search(r"\berror:", line, re.I)]
        error_at_late = bool(errors and f"verified/lib.rs({mutated_late_line}," in errors[0])
        matched = (out["exit_code"] not in (0, 125, 127, None) and
                   "MERGE_HRTB_CALL registered=0" in out["log"] and
                   len(errors) == 1 and EXPECTED_HRTB_ERROR in errors[0] and
                   error_at_late)
        late_cleanup = {"matched": matched,
            "status": "FIRST_MARKER_REFUSES_LATE_CLEANUP_CALL" if matched else
                      "INCONCLUSIVE_WRONG_OR_EARLIER_FAILURE",
            "late_call_unwind": "cleanup", "expected_diagnostic": EXPECTED_HRTB_ERROR,
            "expected_error_line": mutated_late_line, "error_at_late_call": error_at_late,
            "exit_code": out["exit_code"], "log_sha256": out["log_sha256"],
            "mutant_source_sha256": out["source_sha256"]}
    except Exception as error:
        late_cleanup = {"matched": False, "status": "NOT_RUN_LATE_MARKER_SETUP_FAILED",
            "blocker": f"{type(error).__name__}: {error}"}
    return {**common, "first_call_cleanup": first_cleanup,
            "late_cleanup_marker": late_cleanup,
            "matched": first_cleanup.get("matched") is True and
                       late_cleanup.get("matched") is True}


def run(evidence: Path, args, env: dict[str, str], execute_case,
        positive_case: Path, source_record: dict) -> dict:
    """Run Cloud-only baselines and narrow wrong-HRTB/unwind admission controls."""
    evidence = Path(evidence)
    positive_case = Path(positive_case)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse first-callback admission controls: {evidence}")
    evidence.mkdir(parents=True)
    if not callable(execute_case):
        raise TypeError("hosted execute_case callback is required")
    source_dir = positive_case
    original_path = source_dir / "original/lib.rs"
    verified_path = source_dir / "verified/lib.rs"
    if not (original_path.is_file() and verified_path.is_file()):
        # Existing campaign passes the case directory itself; tolerate an
        # older caller passing its enclosing cases directory only when unique.
        candidates = list(source_dir.glob("*/original/lib.rs"))
        if len(candidates) != 1:
            reason = "positive source pair unavailable or ambiguous"
            return _not_run_receipt(evidence, reason)
        original_path = candidates[0]
        verified_path = candidates[0].parent.parent / "verified/lib.rs"
    source_pair = (original_path.read_bytes(), verified_path.read_bytes())
    include_dirs = list(dict.fromkeys([
        Path(args.schema).parent, *getattr(args, "capnp_include", ())]))
    here = Path(__file__).resolve().parent
    base_path = here.parents[1] / "merge/overnight/copy-on-drop-prove.py"
    base = _load("first_callback_admission_cloud_runner", base_path)
    if not base.require_hosted_cloud():
        raise RuntimeError("first-callback admission controls require hosted Cloud Build")
    record = {"schema": "first-callback-admission-controls-v1",
        "classification": "ADMISSION_CONTROLS_ONLY_NO_PROOF_CREDIT",
        "source_sha256": {"original": _sha(original_path), "verified": _sha(verified_path)},
        "tool_sha256": {name: _sha(Path(args.tool_home) / "bin" / name)
                        for name in ("verifast", "vf-rust-mir-exporter", "refinement-checker")},
        "schema_sha256": _sha(Path(args.schema)),
        "positive_case": str(positive_case), "controls": {}}
    pristine_export = evidence / "vf-positive-export.bin"
    baseline = _run_verifast("verifast-positive-baseline", evidence, args, env, base,
                             source_pair, capture=pristine_export)
    baseline_ok = _positive_vf(baseline)
    record["verifast_positive_baseline"] = {
        "matched": baseline_ok, "registration_u64": baseline_ok,
        "exit_code": baseline["exit_code"], "log_sha256": baseline["log_sha256"],
        "verifast_sha256": baseline["verifast_sha256"],
        "exporter_wrapper_sha256": baseline["exporter_wrapper_sha256"],
        "captured_export_sha256": baseline["captured_export_sha256"]}
    if not baseline_ok:
        return _not_run_receipt(evidence,
            "fresh positive verifier baseline did not observe registered FnMut/u64 HRTB call",
            record)
    decoded_path = evidence / "vf-positive-decoded.txt"
    try:
        pristine_decoded = _decode(pristine_export, Path(args.schema), include_dirs,
                                   evidence, env, decoded_path)
        # Prove the captured verifier export can be re-encoded and still reaches
        # the same target registration before admitting any mutated message.
        pristine_reencoded = evidence / "vf-positive-reencoded.bin"
        _encode(pristine_decoded, Path(args.schema), include_dirs, evidence, env,
                pristine_reencoded)
        replay = _run_verifast("verifast-reencoded-positive-baseline", evidence, args,
                               env, base, source_pair, replay=pristine_reencoded)
        replay_ok = _positive_vf(replay)
        record["verifast_capnp_replay_baseline"] = {
            "matched": replay_ok, "registration_u64": replay_ok,
            "exit_code": replay["exit_code"], "log_sha256": replay["log_sha256"],
            "reencoded_export_sha256": _sha(pristine_reencoded),
            "verifast_sha256": replay["verifast_sha256"],
            "exporter_wrapper_sha256": replay["exporter_wrapper_sha256"]}
        if not replay_ok:
            return _not_run_receipt(evidence,
                "fresh Cap'n Proto replay baseline did not preserve positive registration",
                record)
    except Exception as error:
        return _not_run_receipt(evidence,
            f"positive export decode/re-encode setup failed: {type(error).__name__}: {error}",
            record)

    clause_mutations = ("wrong_output", "trait_binder_count", "trait_binder_order",
        "trait_binder_identity", "projection_binder_ref_mismatch", "ambiguous_projection",
        "wrong_source_F", "wrong_source_u64")
    record["controls"]["compiler_clause_mutations"] = _encode_and_replay_mutants(
        evidence / "compiler-clauses", args, env, base, source_pair, pristine_decoded,
        pristine_export, include_dirs, mutations=clause_mutations)
    ghost_mutations = ("wrong_ghost_F", "wrong_ghost_u64", "wrong_ghost_lifetime")
    record["controls"]["ghost_call_mutations"] = _source_ghost_controls(
        evidence / "ghost-call", args, env, base, source_pair, mutations=ghost_mutations)
    here = Path(__file__).resolve().parent
    record["controls"]["legacy_eight_regressions"] = _legacy_regression_controls(
        evidence / "legacy-eight-controls", args, env, base,
        here.parents[1] / "verifast-fnmut-hrtb-regressions.rs")

    record["controls"]["fullbody_cleanup_markers"] = _run_fullbody_cleanup_controls(
        evidence / "fullbody-cleanup", args, env, base, include_dirs, source_record)
    record["controls"]["official_refiner_first_unwind_mutation"] = _run_refiner_unwind_control(
        evidence / "official-refiner-unwind", args, env, base, source_pair,
        include_dirs, source_record)
    required = []
    for family in ("compiler_clause_mutations", "ghost_call_mutations"):
        required.extend(row.get("matched") is True for row in record["controls"][family].values())
    legacy = record["controls"]["legacy_eight_regressions"]
    required.append(legacy.get("matched") is True)
    required.extend((record["controls"]["fullbody_cleanup_markers"].get("matched") is True,
                     record["controls"]["official_refiner_first_unwind_mutation"].get("matched") is True))
    record["all_matched"] = bool(required) and all(required)
    record["status"] = "ALL_INTENDED_ADMISSION_REFUSALS" if record["all_matched"] else \
                        "CONTROLS_INCOMPLETE_OR_INCONCLUSIVE"
    record["proof_credit"] = False
    record["limitations"] = ("Admission controls test targeted rejection only; they establish no proof of "
        "insert_tail safety, panic recovery, semantic preservation, or verifier soundness.")
    (evidence / "receipt.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def _not_run_receipt(evidence: Path, blocker: str, prior: dict | None = None) -> dict:
    record = dict(prior or {})
    record.update(schema="first-callback-admission-controls-v1",
        classification="ADMISSION_CONTROLS_ONLY_NO_PROOF_CREDIT",
        status="NOT_RUN_POSITIVE_SETUP_BLOCKED", blocker=blocker,
        all_matched=False, proof_credit=False,
        limitations="No intended negative was credited because its positive replay gate did not pass.")
    (evidence / "receipt.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record
