#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Read-only hosted certificate checker for pinned FnMut HRTB admission evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
CALLBACK_FIXTURE = HERE / "callback-cases.rs"
PREPARED_FIXTURE = HERE / "hrtb-prepared-cases.rs"
CASE_RE = re.compile(rb"(?m)^// CASE_BEGIN ([a-z0-9_]+)\r?\n(.*?)^// CASE_END \1\r?\n", re.S)
ANNOTATION_BLOCK = re.compile(rb"/\*@.*?@\*/", re.S)
ANNOTATION_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
BOUND_RE = re.compile(
    r"^MERGE_HRTB_BOUND function=([^ ]+) F=([^ ]+) T=([^ ]+) regions=([^ ]+) output=([^ ]+)$"
)
CALL_RE = re.compile(
    r"^MERGE_HRTB_CALL registered=([01]) function=std::ops::FnMut::call_mut "
    r"(?:(?:F=([^ ]+) T=([^ ]+) lifetime=([^ ]+) )|"
    r"source_substs=(\d+) ghost_substs=(\d+) eligible_bounds=(\d+) )"
    r"call=(verified/lib\.rs\(\d+,\d+(?:-\d+(?:,\d+)?)?\))$"
)
REGISTER_RE = re.compile(r'CallExpr \(loc "([^"]+)", "#register_type_projection_equality"')


# Each call entry is [location, registered, ghost_F, ghost_tuple_types,
# ghost_tuple_lifetimes, method_lifetime, eligible_bounds]. Source case text and
# decoded MIR are independently checked against these predeclared expectations.
MATRIX = {
    "callback": {
        "hrtb_bool_common_lifetime_two_calls": {
            "bound": ["hrtb_bool_common_lifetime_two_calls", "F", "T", "'a,'b", "bool"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"],
            "calls": [
                ["verified/lib.rs(19,17-74)", 1, "F", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 1],
                ["verified/lib.rs(20,18-75)", 1, "F", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 1],
            ],
        },
        "hrtb_wrong_output_u8": {
            "bound": None,
            "decoded_regions": ["'a", "'b"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = u8>,",
                       "compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"],
            "decoded_output": "u8",
            "calls": [["verified/lib.rs(19,13-70)", 0, "F", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 0]],
        },
        "hrtb_unconstrained_output": {
            "bound": None,
            "decoded_regions": ["'a", "'b"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T)>,",
                       "compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"],
            "decoded_output": None,
            "calls": [["verified/lib.rs(19,13-70)", 0, "F", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 0]],
        },
        "hrtb_wrong_ghost_function_type": {
            "bound": ["hrtb_wrong_ghost_function_type", "F", "T", "'a,'b", "bool"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "compare/*@::<G, (&'cmp T, &'cmp T), 'cmp>@*/"],
            "calls": [["verified/lib.rs(19,13-70)", 0, "G", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 1]],
        },
        "hrtb_wrong_ghost_referent_type": {
            "bound": ["hrtb_wrong_ghost_referent_type", "F", "T", "'a,'b", "bool"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "compare/*@::<F, (&'cmp U, &'cmp U), 'cmp>@*/"],
            "calls": [["verified/lib.rs(19,13-70)", 0, "F", ["U", "U"], ["'cmp", "'cmp"], "'cmp", 1]],
        },
        "hrtb_unequal_ghost_lifetimes": {
            "bound": ["hrtb_unequal_ghost_lifetimes", "F", "T", "'a,'b", "bool"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "compare/*@::<F, (&'left T, &'right T), 'left>@*/"],
            "calls": [["verified/lib.rs(19,13-74)", 0, "F", ["T", "T"], ["'left", "'right"], "'left", 1]],
        },
        "hrtb_single_region_source_bound": {
            "bound": None,
            "decoded_regions": [],
            "source": ["F: core::ops::FnMut(&'cmp T, &'cmp T) -> bool,",
                       "compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"],
            "decoded_output": "bool",
            # Declaration-level type equality, not call-site registration.
            "ast_registration_nodes": ["verified/lib.rs(8,1-14,51)"],
            "calls": [["verified/lib.rs(19,13-70)", 0, "F", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 0]],
        },
        "hrtb_bound_must_stay_with_its_body": {
            "bound": ["hrtb_bound_only", "F", "T", "'a,'b", "bool"],
            "call_body": "hrtb_unrelated_body_call",
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "callback/*@::<G, (), 'static>@*/"],
            # A declaration equality for the separate source-bound function;
            # the unrelated body's call remains unregistered.
            "ast_registration_nodes": ["verified/lib.rs(17,1-88)"],
            "calls": [["verified/lib.rs(22,13-47)", 0, "G", [], [], "'static", 0]],
        },
    },
    "prepared": {
        "prepared_hrtb_bool_shared_references": {
            "bound": ["prepared_hrtb_bool_shared_references", "F", "T", "'a,'b", "bool"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"],
            "calls": [["verified/lib.rs(62,18-65,10)", 1, "F", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 1]],
        },
        "prepared_hrtb_wrong_ghost_function_type": {
            "bound": ["prepared_hrtb_wrong_ghost_function_type", "F", "T", "'a,'b", "bool"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "compare/*@::<G, (&'cmp T, &'cmp T), 'cmp>@*/"],
            "calls": [["verified/lib.rs(59,18-62,10)", 0, "G", ["T", "T"], ["'cmp", "'cmp"], "'cmp", 1]],
        },
        "prepared_hrtb_wrong_ghost_referent_type": {
            "bound": ["prepared_hrtb_wrong_ghost_referent_type", "F", "T", "'a,'b", "bool"],
            "source": ["F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,",
                       "compare/*@::<F, (&'cmp U, &'cmp U), 'cmp>@*/"],
            "calls": [["verified/lib.rs(59,18-62,10)", 0, "F", ["U", "U"], ["'cmp", "'cmp"], "'cmp", 1]],
        },
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_annotations(source: bytes) -> bytes:
    return ANNOTATION_LINE.sub(b"", ANNOTATION_BLOCK.sub(b"", source))


def read_fixture(path: Path) -> tuple[bytes, dict[str, bytes]]:
    raw = path.read_bytes()
    matches = list(CASE_RE.finditer(raw))
    if not matches:
        raise RuntimeError(f"no CASE_BEGIN blocks in {path}")
    names = [match.group(1).decode("ascii") for match in matches]
    if len(names) != len(set(names)):
        raise RuntimeError(f"duplicate case names in {path}")
    prefix = raw[:matches[0].start()]
    return raw, {name: prefix + match.group(2) for name, match in zip(names, matches)}


def hosted_guard() -> None:
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            os.environ.get("RUNNER_OS") != "Linux" or
            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):
        raise RuntimeError("HRTB certificate requires hosted Linux Actions on overnight/merge-26.10")
    expected = os.environ.get("GITHUB_SHA")
    if not expected:
        raise RuntimeError("GITHUB_SHA is required for exact-dispatch certificate evidence")
    actual = subprocess.run(["git", "rev-parse", "HEAD"], check=True,
                            capture_output=True, text=True).stdout.strip()
    if actual != expected:
        raise RuntimeError("checkout HEAD differs from dispatched GITHUB_SHA")


def parse_marker_log(log: str) -> tuple[list[list[str]], list[list[str]]]:
    bounds: list[list[str]] = []
    calls: list[list[str]] = []
    for line in log.splitlines():
        if line.startswith("MERGE_HRTB_BOUND "):
            match = BOUND_RE.fullmatch(line)
            if match is None:
                raise ValueError(f"malformed source-bound marker: {line}")
            bounds.append(list(match.groups()))
        elif line.startswith("MERGE_HRTB_CALL "):
            match = CALL_RE.fullmatch(line)
            if match is None:
                raise ValueError(f"malformed call-registration marker: {line}")
            registered, function_f, function_t, lifetime, source_n, ghost_n, eligible_n, loc = match.groups()
            calls.append([loc, int(registered), function_f, function_t, lifetime,
                          source_n, ghost_n, int(eligible_n) if eligible_n is not None else None])
    return bounds, calls


def ast_call(ast: str, location: str) -> str | None:
    needle = f'CallExpr (loc "{location}", "std::ops::FnMut::call_mut", ['
    start = ast.find(needle)
    if start < 0 or ast.find(needle, start + 1) >= 0:
        return None
    end = ast.find("], [], [", start + len(needle))
    return None if end < 0 else ast[start:end]


def ast_call_args(ast: str, location: str) -> tuple[str | None, list[str], list[str]]:
    node = ast_call(ast, location)
    if node is None:
        return None, [], []
    f_match = re.search(r'IdentTypeExpr \(loc "[^"]+", None, "([^\"]+)"\);', node)
    tuple_pos = node.find("StructTypeExpr")
    tuple_part = node[tuple_pos:] if tuple_pos >= 0 else ""
    types = re.findall(r'IdentTypeExpr \(loc "[^"]+", None, "([^\"]+)"\)', tuple_part)
    all_types = re.findall(r'IdentTypeExpr \(loc "[^"]+", None, "([^\"]+)"\)', node)
    lifetimes = [value for value in all_types if value.startswith("'")]
    static_lifetimes = re.findall(r'ManifestTypeExpr \(loc "[^"]+", StaticLifetime\)', node)
    lifetimes.extend(["'static"] * len(static_lifetimes))
    tuple_types = [value for value in types if not value.startswith("'")]
    return (f_match.group(1) if f_match else None), tuple_types, lifetimes


def fixture_case_check(name: str, spec: dict, fixture_body: bytes) -> bool:
    text = fixture_body.decode("utf-8")
    return all(fragment in text for fragment in spec["source"])


def function_segment(decoded: str, function: str) -> str:
    marker = f'defPath = "{function}"'
    start = decoded.find(marker)
    if start < 0:
        return ""
    next_fn = decoded.find('defPath = "', start + len(marker))
    return decoded[start:next_fn if next_fn >= 0 else len(decoded)]


def decode_case_check(spec: dict, decoded: str, case: str,
                      bound_function: str | None) -> bool:
    function = bound_function
    if function is None:
        function = case
    segment = function_segment(decoded, function)
    if not segment or 'defId = "std::ops::FnMut"' not in segment:
        return False
    region_literal = "boundRegions = [" + ", ".join(f'"\\{region}"' for region in
                                                   spec.get("decoded_regions", ["'a", "'b"])) + "]"
    if region_literal not in segment:
        return False
    clauses = segment.split("clauses = [", 1)[-1].split("generics = [", 1)[0]
    fnmut_start = clauses.find('defId = "std::ops::FnMut"')
    if fnmut_start < 0:
        return False
    fnmut_clause = clauses[fnmut_start:]
    fnmut_end = fnmut_clause.find("boundRegions = ")
    fnmut_clause = fnmut_clause[:fnmut_end] if fnmut_end >= 0 else fnmut_clause
    if ('param = "F"' not in fnmut_clause or fnmut_clause.count('param = "T"') != 2):
        return False
    expected_output = spec.get("decoded_output", "bool")
    if expected_output is None:
        return not any('defId = "std::ops::FnOnce::Output"' in section
                       for section in re.split(r"\(\s*projection\s*=\s*\(", clauses)[1:])
    if expected_output not in ("bool", "u8"):
        return False
    output_sections = [section for section in
                       re.split(r"\(\s*projection\s*=\s*\(", clauses)[1:]
                       if 'defId = "std::ops::FnOnce::Output"' in section]
    if len(output_sections) != 1:
        return False
    output_section = output_sections[0]
    projection_args = output_section.split("term =", 1)[0]
    if ('defId = "std::ops::FnOnce::Output"' not in projection_args or
            projection_args.count('param = "F"') != 1 or
            projection_args.count('param = "T"') != 2):
        return False
    if region_literal not in output_section:
        return False
    if expected_output == "bool":
        return re.search(r"term\s*=\s*\(\s*ty\s*=\s*\(\s*kind\s*=\s*\(\s*bool\s*=\s*void",
                         output_section) is not None
    return re.search(r"term\s*=\s*\(\s*ty\s*=\s*\(\s*kind\s*=\s*\(\s*uInt\s*=\s*\(\s*u8\s*=\s*void",
                     output_section) is not None


def classify(spec: dict, evidence: dict) -> dict:
    expected_bound = spec.get("bound")
    expected_bounds = [expected_bound] if expected_bound is not None else []
    parsed_bounds = evidence["bounds"]
    expected_calls = spec["calls"]
    parsed_calls = evidence["calls"]
    failures = []
    if parsed_bounds != expected_bounds:
        failures.append("source_bound_markers")
    if len(parsed_calls) != len(expected_calls):
        failures.append("call_marker_count")
    ast = evidence["ast"]
    expected_regs = []
    observed_call_locs = []
    for index, expected in enumerate(expected_calls):
        if index >= len(parsed_calls):
            break
        location, registered, ghost_f, ghost_tuple, ghost_lifetimes, method_lft, eligible = expected
        log_call = parsed_calls[index]
        expected_log = [location, registered]
        if registered:
            expected_log.extend([ghost_f, ghost_tuple[0], method_lft, None, None, None])
            if evidence["bounds"] != [spec.get("bound")] or eligible != 1:
                failures.append(f"registered_call_{index}_without_one_exact_bound")
        else:
            expected_log.extend([None, None, None, "3", "3", eligible])
        normalized = log_call[:2] + log_call[2:5] + log_call[5:7] + [log_call[7]]
        target_log = expected_log[:5] + expected_log[5:7] + [expected_log[7]]
        if normalized != target_log:
            failures.append(f"call_marker_{index}")
        observed_call_locs.append(log_call[0])
        node = ast_call(ast, location)
        if node is None:
            failures.append(f"ast_call_{index}")
        else:
            actual_f, actual_types, actual_lifetimes = ast_call_args(ast, location)
            if (actual_f != ghost_f or actual_types != ghost_tuple or
                    actual_lifetimes != ghost_lifetimes + [method_lft]):
                failures.append(f"ast_call_substitutions_{index}")
        if registered:
            expected_regs.append(location)
    actual_regs = REGISTER_RE.findall(ast)
    expected_ast_regs = spec.get("ast_registration_nodes", expected_regs)
    if not set(expected_regs).issubset(set(expected_ast_regs)):
        failures.append("matrix_call_registration_expectation")
    if actual_regs != expected_ast_regs:
        failures.append("registration_ast_nodes")
    if not evidence["fixture_source_matches"]:
        failures.append("source_fixture_hash_or_fragment")
    if not evidence["decoded_mir_matches"]:
        failures.append("decoded_mir_bound_or_output")
    if not evidence["source_unchanged"]:
        failures.append("source_integrity")
    exits = evidence["stage_exit_codes"]
    if (exits.get("exporter") != 0 or exits.get("decode") != 0 or
            exits.get("refinement") != 0 or exits.get("verifast") not in (0, 1) or
            evidence["stages"] != exits or
            (exits.get("verifast") == 1 and evidence["proof_classification"] == "PASS")):
        failures.append("stage_vector")
    if evidence.get("expected_rejection") is not None or evidence.get("expected_error") is not None:
        failures.append("proof_negative_not_admission")
    if not evidence["expected_body_present"]:
        failures.append("body_scope")
    return {"status": "ADMISSION_CERTIFICATE" if not failures else "INCONCLUSIVE",
            "failures": failures, "expected_call_locations": [call[0] for call in expected_calls],
            "observed_call_locations": observed_call_locs,
            "expected_call_registration_locations": expected_regs,
            "expected_registration_locations": expected_ast_regs,
            "observed_registration_locations": actual_regs}


def fail_closed_controls(spec: dict, evidence: dict) -> dict[str, bool]:
    controls = {}
    base = classify(spec, evidence)
    expected_status = "ADMISSION_CERTIFICATE"
    controls["valid_evidence_accepted"] = base["status"] == expected_status
    for stage in ("exporter", "decode", "verifast", "refinement"):
        mutant = copy.deepcopy(evidence)
        mutant["stages"][stage] = 0 if mutant["stages"].get(stage) != 0 else 1
        controls[f"wrong_stage_{stage}_rejected"] = classify(spec, mutant)["status"] != expected_status
    for label, key in (("source_changed", "source_unchanged"),
                       ("fixture_mismatch", "fixture_source_matches"),
                       ("decoded_mir_mismatch", "decoded_mir_matches"),
                       ("body_scope", "expected_body_present")):
        mutant = copy.deepcopy(evidence)
        mutant[key] = False
        controls[f"{label}_rejected"] = classify(spec, mutant)["status"] != expected_status
    if evidence["bounds"]:
        mutant = copy.deepcopy(evidence)
        mutant["bounds"] = []
        controls["missing_bound_rejected"] = classify(spec, mutant)["status"] != expected_status
        for index, field in ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4)):
            mutant = copy.deepcopy(evidence)
            mutant["bounds"][index][field] += "_mutant"
            controls[f"wrong_bound_field_{field}_rejected"] = classify(spec, mutant)["status"] != expected_status
        mutant = copy.deepcopy(evidence)
        mutant["bounds"].append(list(evidence["bounds"][0]))
        controls["extra_bound_rejected"] = classify(spec, mutant)["status"] != expected_status
    else:
        mutant = copy.deepcopy(evidence)
        mutant["bounds"] = [["unexpected", "F", "T", "'a,'b", "bool"]]
        controls["extra_bound_rejected"] = classify(spec, mutant)["status"] != expected_status
    for index in range(len(evidence["calls"])):
        for label, transform in (
            ("missing", lambda rows: rows.pop(index)),
            ("location", lambda rows: rows[index].__setitem__(0, "verified/lib.rs(999,1-2)")),
            ("registration", lambda rows: rows[index].__setitem__(1, 1 - rows[index][1])),
            # Registered markers omit eligible_n. A forged numeric value must
            # still disagree with that schema; for unregistered calls, flip
            # the explicitly logged count.
            ("eligible_bound", lambda rows: rows[index].__setitem__(
                7, 0 if rows[index][7] is None else 1 - rows[index][7])),
        ):
            mutant = copy.deepcopy(evidence)
            try:
                transform(mutant["calls"])
            except IndexError:
                continue
            controls[f"call_{index}_{label}_rejected"] = classify(spec, mutant)["status"] != expected_status
        expected_call = spec["calls"][index]
        original_node = ast_call(evidence["ast"], expected_call[0])
        if original_node is not None:
            for label, old, new in (
                    ("ghost_F", expected_call[2], "G" if expected_call[2] != "G" else "F"),
                    ("ghost_T", expected_call[3][0] if expected_call[3] else None,
                     "U" if expected_call[3] and expected_call[3][0] != "U" else "T"),
                    ("ghost_lifetime", expected_call[4][0] if expected_call[4] else None,
                     "'wrong")):
                if old is None:
                    continue
                old_token = f'None, "{old}"'
                new_token = f'None, "{new}"'
                changed_node = original_node.replace(old_token, new_token, 1)
                if changed_node != original_node:
                    mutant = copy.deepcopy(evidence)
                    mutant["ast"] = mutant["ast"].replace(original_node, changed_node, 1)
                    controls[f"call_{index}_ast_{label}_rejected"] = (
                        classify(spec, mutant)["status"] != expected_status)
    mutant = copy.deepcopy(evidence)
    if evidence["calls"]:
        mutant["calls"].append(list(evidence["calls"][-1]))
    controls["extra_call_rejected"] = classify(spec, mutant)["status"] != expected_status
    if classify(spec, evidence)["expected_registration_locations"]:
        mutant = copy.deepcopy(evidence)
        mutant["ast"] = REGISTER_RE.sub("", mutant["ast"], count=1)
        controls["missing_ast_registration_rejected"] = classify(spec, mutant)["status"] != expected_status
    else:
        mutant = copy.deepcopy(evidence)
        mutant["ast"] += '\nCallExpr (loc "verified/lib.rs(999,1-2)", "#register_type_projection_equality", [])'
        controls["unexpected_registration_rejected"] = classify(spec, mutant)["status"] != expected_status
    mutant = copy.deepcopy(evidence)
    mutant["ast"] += '\nCallExpr (loc "verified/lib.rs(999,1-2)", "#register_type_projection_equality", [])'
    controls["extra_ast_registration_rejected"] = classify(spec, mutant)["status"] != expected_status
    return controls


def load_evidence(root: Path, group: str, case: str, fixture_path: Path,
                  fixture_body: bytes, spec: dict) -> tuple[dict, dict]:
    case_dir = root / f"checked-{('callback-model' if group == 'callback' else 'hrtb-prepared')}" / "cases" / case
    needed = ["classification.json", "metadata.json", "verifast.log", "proof-ast.ml",
              "decode.out", "compiler-mir.bin", "compiler-mir-sha256.txt",
              "source-before-sha256.json", "source-after-sha256.json", "source-unchanged.txt",
              "original/lib.rs", "verified/lib.rs"]
    for stage in ("exporter", "decode", "verifast", "refinement"):
        needed += [f"{stage}-exit-code.txt", f"source-integrity-{stage}.json"]
    missing = [name for name in needed if not (case_dir / name).is_file()]
    if missing:
        raise RuntimeError(f"{case}: missing evidence artifacts {missing}")
    files = {name: (case_dir / name).read_bytes() for name in needed}
    artifact_hashes = {
        path.relative_to(case_dir).as_posix(): sha(path.read_bytes())
        for path in sorted(case_dir.rglob("*")) if path.is_file()
    }
    classification = json.loads(files["classification.json"])
    metadata = json.loads(files["metadata.json"])
    stages = classification.get("stages")
    source_before = json.loads(files["source-before-sha256.json"])
    source_after = json.loads(files["source-after-sha256.json"])
    stage_exit_codes = {}
    unchanged = (classification.get("source_unchanged_at_every_stage") is True and
                 source_before == source_after and source_before.get("verified/lib.rs") == metadata.get("verified_sha256") and
                 source_before.get("original/lib.rs") == metadata.get("original_sha256") and
                 files["source-unchanged.txt"].strip() == b"true")
    for stage in ("exporter", "decode", "verifast", "refinement"):
        row = json.loads(files[f"source-integrity-{stage}.json"])
        unchanged = unchanged and row.get("unchanged") is True and row.get("source_before") == row.get("source_after")
        stage_exit = int(files[f"{stage}-exit-code.txt"].strip())
        stage_exit_codes[stage] = stage_exit
        unchanged = unchanged and stage_exit == stages.get(stage)
    mir_hash = files["compiler-mir-sha256.txt"].decode("ascii").strip()
    unchanged = unchanged and sha(files["compiler-mir.bin"]) == mir_hash
    source_matches = (
        metadata.get("case") == case and metadata.get("ghost_strip_exact_bytes") is True and
        metadata.get("verified_sha256") == sha(fixture_body) and
        metadata.get("original_sha256") == sha(strip_annotations(fixture_body)) and
        files["verified/lib.rs"] == fixture_body and
        files["original/lib.rs"] == strip_annotations(fixture_body) and
        metadata.get("expected_bodies") and fixture_case_check(case, spec, fixture_body)
    )
    bounds, calls = parse_marker_log(files["verifast.log"].decode("utf-8", "replace"))
    evidence = {
        "bounds": bounds, "calls": calls,
        "ast": files["proof-ast.ml"].decode("utf-8", "replace"),
        "decoded_mir_matches": decode_case_check(spec, files["decode.out"].decode("utf-8", "replace"), case,
                                                  spec["bound"][0] if spec.get("bound") else None),
        "fixture_source_matches": bool(source_matches),
        "source_unchanged": bool(unchanged), "stages": stages,
        "stage_exit_codes": stage_exit_codes,
        "expected_rejection": classification.get("expected_rejection"),
        "expected_error": classification.get("expected_error"),
        "expected_body_present": set(
            [spec.get("call_body", case)] +
            ([spec["bound"][0]] if spec.get("bound") else [])).issubset(
                set(metadata.get("expected_bodies", []))),
        "proof_classification": classification.get("classification"),
        "full_positive_gate": classification.get("full_positive_gate"),
        "body_execution_records": classification.get("body_execution_records"),
        "case_dir": str(case_dir),
    }
    report = {"proof_classification": evidence["proof_classification"],
              "proof_status": ("PASS" if evidence["proof_classification"] == "PASS" else "INCONCLUSIVE"),
              "proof_full_positive_gate": evidence["full_positive_gate"],
              "source_integrity": evidence["source_unchanged"],
              "stages": stages, "body_execution_records": evidence["body_execution_records"],
              "artifact_sha256": artifact_hashes, "compiler_mir_sha256": mir_hash,
              "fixture_sha256": sha(fixture_path.read_bytes()),
              "verified_sha256": metadata.get("verified_sha256"),
              "original_sha256": metadata.get("original_sha256")}
    return evidence, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True,
                        help="hosted run evidence directory containing checked-callback-model and checked-hrtb-prepared")
    parser.add_argument("--output", type=Path, required=True,
                        help="new evidence directory for the certificate report")
    args = parser.parse_args()
    hosted_guard()
    if args.output.exists():
        raise RuntimeError(f"refusing to overwrite certificate output: {args.output}")
    callback_raw, callback_cases = read_fixture(CALLBACK_FIXTURE)
    prepared_raw, prepared_cases = read_fixture(PREPARED_FIXTURE)
    run_manifest = args.evidence_root / "environment.txt"
    if not run_manifest.is_file():
        raise RuntimeError(f"hosted run environment manifest missing: {run_manifest}")
    env_lines = run_manifest.read_text(errors="replace").splitlines()
    dispatch_sha = os.environ["GITHUB_SHA"]
    if (f"Source SHA: {dispatch_sha}" not in env_lines or
            f"Actions SHA: {dispatch_sha}" not in env_lines):
        raise RuntimeError("HRTB evidence root source/Actions SHA differs from current dispatch")
    args.output.mkdir(parents=True)
    report = {
        "profile": "m2-hrtb-source-call-ast-certificate-v1",
        "source_sha": dispatch_sha,
        "fixtures": {"callback-cases.rs": sha(callback_raw),
                     "hrtb-prepared-cases.rs": sha(prepared_raw)},
        "excluded_cases": {
            "prepared_hrtb_missing_comparator_own":
                "excluded: normal and unwind posts are weakened to true",
        },
        "cases": {},
    }
    all_passed = True
    for group, mapping, fixture_path, case_bodies in (
            ("callback", MATRIX["callback"], CALLBACK_FIXTURE, callback_cases),
            ("prepared", MATRIX["prepared"], PREPARED_FIXTURE, prepared_cases)):
        for case, spec in mapping.items():
            if case not in case_bodies:
                raise RuntimeError(f"{fixture_path.name}: missing predeclared case {case}")
            evidence, proof = load_evidence(args.evidence_root, group, case, fixture_path,
                                            case_bodies[case], spec)
            certificate = classify(spec, evidence)
            controls = fail_closed_controls(spec, evidence)
            controls_passed = all(controls.values())
            all_passed &= certificate["status"] == "ADMISSION_CERTIFICATE" and controls_passed
            report["cases"][case] = {
                "admission_status": certificate["status"],
                "admission_failures": certificate["failures"],
                "expected_bound": spec.get("bound"),
                "expected_calls": spec["calls"],
                "observed_bounds": evidence["bounds"],
                "observed_calls": evidence["calls"],
                "observed_registration_ast_locations": certificate["observed_registration_locations"],
                "classifier_fail_closed_mutations": controls,
                "classifier_controls_passed": controls_passed,
                **proof,
            }
            print(f"{case}: {certificate['status']} (proof: {proof['proof_status']})", flush=True)
    report["classifier_controls_passed"] = all_passed
    report["claim_boundary"] = (
        "HRTB admission and AST registration only; proof classifications remain separate and are not inferred from markers")
    (args.output / "hrtb-admission-certificate.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "aggregate.json").write_text(json.dumps({
        "classifier_controls_passed": all_passed,
        "admission_status": {name: row["admission_status"] for name, row in report["cases"].items()},
        "proof_status": {name: row["proof_status"] for name, row in report["cases"].items()},
        "claim_boundary": report["claim_boundary"],
    }, indent=2) + "\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"HRTB admission certificate failed: {error}", file=sys.stderr)
        sys.exit(2)
