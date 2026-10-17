"""Pure classification of same-invocation A1 focused observations.

Results are runner-reported candidates, never independently established proof.
This parser cannot authenticate its inputs or replace the pinned kernel's body
and conformance checks. The outer runner must establish execution selection
from the compiler/AST source range and the frozen focus semantics separately.
"""
from __future__ import annotations

import re
from typing import Mapping, Any

BODY = {"P0a": "default16", "P0b": "freeze32",
        "N-default-contract": "default16", "N-freeze-contract": "freeze32"}
CALLER = {"P0c", "N-false31"}
NEGATIVE = {"N-default-contract", "N-freeze-contract", "N-false31"}
SUPPORT_STAGES = ("normal-export", "normal-decode", "readonly-export",
                  "readonly-decode", "refinement")


def first_error(log: str) -> str | None:
    """Use the first diagnostic, never a later convenient predicate match."""
    for line in log.splitlines():
        if (": error:" in line or
                line.startswith(("Fatal error:", "error:", "error[")) or
                re.fullmatch(r"verified/lib\.rs\(\d+,\d+(?:-\d+)?\): dead code", line)):
            return line
    return None


def failure_context(log: str, *, alias: str, focus_line: int) -> dict:
    """Parse only context notes belonging to the first reported error.

    The pinned text console emits symbolic execution contexts after that error.
    ``Verifying function`` is pushed inside the focused body continuation;
    prototype compatibility has a separate earlier frame. Missing/ambiguous
    frames cannot establish body entry. No verbose marker is treated as proof.
    """
    diagnostic = first_error(log)
    unknown = {"stage": "UNESTABLISHED", "body_frame_observed": False,
               "header_frame_observed": False, "proof_credit": False}
    if diagnostic is None or not re.fullmatch(r"__a1_impl_[1-9][0-9]*_item_[1-9][0-9]*_small_sort_threshold", alias):
        return unknown
    lines = log.splitlines()
    start = lines.index(diagnostic) + 1
    body, header = [], []
    pattern = re.compile(r"(?:.*/)?verified/lib\.rs\(([1-9][0-9]*),[0-9]+"
                         r"(?:-(?:[1-9][0-9]*,)?[0-9]+)?\): note: (.*)\Z")
    for line in lines[start:]:
        if first_error(line) is not None:
            break
        match = pattern.fullmatch(line)
        if match is None:
            continue
        message = match.group(2)
        if message == f"Verifying function '{alias}'":
            body.append(int(match.group(1)))
        elif message == f"Function '{alias}': Function prototype implementation check":
            header.append(int(match.group(1)))
    if body == [focus_line] and not header:
        return {**unknown, "stage": "impl-body", "body_frame_observed": True}
    if header == [focus_line] and not body:
        return {**unknown, "stage": "prototype-conformance", "header_frame_observed": True}
    return unknown


def classify_focus(case_id: str, observation: Mapping[str, Any],
                   ast_gates_result: Mapping[str, Any], source: str,
                   verifier_log: str) -> dict:
    """Classify an intended body/assertion location after structural gates.

    Required AST bundle: ``threshold`` is threshold_posts' return value;
    callers also supply ``caller`` (caller_calls) and ``mir_binding`` (the
    source-reported paired MIR binding). A separately reviewed execution gate
    must supply body_count/conformance facts before A1Admission may use this
    candidate. This function deliberately does not manufacture those facts.
    """
    result = {"case_id": case_id, "classification": "INCONCLUSIVE",
              "candidate_passed": False, "body_verified": False,
              "intended_failure_observed": False,
              "body_count": None, "native_conformance_verified": None,
              "proof_credit": False,
              "assurance": "runner-reported-candidate-only"}

    def refuse(why: str, stage: str = "admission") -> dict:
        return {**result, "reason": why, "first_causal_stage": stage}

    if case_id not in BODY and case_id not in CALLER:
        return refuse("unsupported focused proof case")
    if observation.get("case_id") != case_id:
        return refuse("focused observation belongs to another case")
    if observation.get("focus_is_export_or_translation_filter") is not False:
        return refuse("complete exported/translated unit not established")
    support = observation.get("paired_support", {})
    if not isinstance(support, Mapping) or support.get("paired_support_passed") is not True:
        return refuse("paired export/decode/refinement missing", "source-support")
    stages = observation.get("stages", {})
    if not isinstance(stages, Mapping):
        return refuse("stage inventory missing")
    for name in SUPPORT_STAGES:
        if not isinstance(stages.get(name), Mapping) or stages[name].get("exit") != 0:
            return refuse("earlier support stage failed or was not run", name)
    proof = stages.get("verification")
    if not isinstance(proof, Mapping) or proof.get("exit") is None:
        return refuse("focused verification not run", "verification")
    artifacts = observation.get("artifacts", {})
    if not isinstance(artifacts, Mapping) or not isinstance(artifacts.get("proof-ast.ml"), Mapping) or not artifacts["proof-ast.ml"].get("sha256"):
        return refuse("same-invocation AST missing", "translation")
    threshold = ast_gates_result.get("threshold")
    if not isinstance(threshold, Mapping) or threshold.get("classification") != "STRUCTURE_ONLY_UNRUN_PROOF":
        return refuse("complete common/impl native-post structural gate missing")
    focus_line = observation.get("focus_source_line")
    if not isinstance(focus_line, int) or focus_line <= 0 or observation.get("focus") != f"verified/lib.rs:{focus_line}":
        return refuse("one exact nonzero source focus required")
    if case_id in BODY:
        impl = threshold.get("impls", {}).get(BODY[case_id])
        if (observation.get("focus_stage") != "bodies" or threshold.get("stage") != "bodies" or
                not isinstance(impl, Mapping) or impl.get("source_line") != focus_line):
            return refuse("body focus is not the compiler/AST-bound threshold item")
        intended_line = impl.get("diagnostic_post_line")
        if not isinstance(intended_line, int) or intended_line <= 0:
            return refuse("native range post location is not compiler-bound")
        intended_bound = 32
        predicate = "result<=32" if case_id in NEGATIVE else "16<=result<=32"
    else:
        caller = ast_gates_result.get("caller")
        binding = ast_gates_result.get("mir_binding")
        if (observation.get("focus_stage") != "caller" or threshold.get("stage") != "caller" or
                threshold.get("common_checked") is not True or
                not isinstance(caller, Mapping) or caller.get("classification") != "CALL_AST_STRUCTURE_ONLY" or
                caller.get("owner") != "a1_guard_observer" or caller.get("source_line") != focus_line or
                not isinstance(binding, Mapping) or binding.get("schema") != "a1-call-binding-observation-v1" or
                binding.get("binding", {}).get("caller") != "a1_guard_observer"):
            return refuse("checked common summary and paired MIR/final AST caller binding missing")
        assertion_lines = [i for i, line in enumerate(source.splitlines(), 1)
                           if re.fullmatch(r"\s*//@\s*assert len <= 31;\s*", line)]
        if case_id == "N-false31" and len(assertion_lines) != 1:
            return refuse("one certified false31 source assertion required")
        intended_line = assertion_lines[0] if assertion_lines else focus_line
        intended_bound = 31
        predicate = "len<=31" if case_id in NEGATIVE else "len<=32-and-len+16<=48"
    diagnostic = first_error(verifier_log)
    result.update(first_error=diagnostic, verifier_exit=proof["exit"], predicate=predicate)
    if case_id not in NEGATIVE:
        if proof["exit"] != 0 or diagnostic is not None:
            return refuse("positive focused invocation did not finish VF0", "verification")
        return {**result, "classification": "FOCUSED_VF0_CANDIDATE",
                "candidate_passed": True, "body_verified": True,
                "first_causal_stage": "NONE_OBSERVED"}
    if proof["exit"] == 0 or diagnostic is None:
        return refuse("expected failure absent or no first causal diagnostic", "verification")
    locations = [int(n) for n in re.findall(r"(?:^|/)verified/lib\.rs\((\d+),", diagnostic)]
    if (intended_line not in locations or "Cannot prove" not in diagnostic or
            re.search(r"<=\s*" + str(intended_bound) + r"\b", diagnostic) is None):
        return refuse("failure is earlier than or differs from the intended predicate/location", "verification")
    if case_id in BODY:
        context = failure_context(verifier_log, alias=impl.get("alias", ""),
                                  focus_line=focus_line)
        result["error_context"] = context
        if context["stage"] != "impl-body":
            return refuse("native post diagnostic does not establish actual body entry", "verification")
    return {**result, "classification": "INTENDED_FOCUSED_FAILURE_CANDIDATE",
            "candidate_passed": True, "intended_failure_observed": True,
            "target_reached": True, "first_causal_stage": "verification"}
