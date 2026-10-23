#!/usr/bin/env python3
"""Closed R24 entry for source-envelope refusal controls and physical audit."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import traceback
from types import SimpleNamespace
from typing import Any


MODE_REL = Path("research/challenge-8/task-history/select-callee-r24/P2-MUT-REFUSAL-MODE.json")
MODE_SHA256 = "acec242babdbf1ddbd8913ce4c8b2a296fb2ef806b14d0c1f8353f9eb7a954c7"
MODE_SCHEMA = "select-r24-mut-refusal-mode-v1"
R24 = "SORT4-ACTUAL-SELECT-2026-10-24-R24"
R21 = "SORT4-ACTUAL-SELECT-2026-10-23-R21"
OWNER = "select-sort4"
LANE = "o26-select-callee-r20"
PROFILE = "experimental-s6-26.10-v1"

CAPTURE_ADAPTER_REL = Path("research/challenge-8/cloud-build/select-callee-r24-mut-capture.py")
CAPTURE_ADAPTER_SHA256 = "96e770129d1fc08e798e4b3ce8ad3bfe5b7ba01b68dafd0e6dfa3e0c8957f756"
CAPTURE_PINS_REL = Path("research/challenge-8/task-history/select-callee-r24/P2-MUT-CAPTURE-PINS.json")
CAPTURE_PINS_SHA256 = "b10d8f472fd9babc5e73cb7a8da14ad691b0563975d0d6d956366165a47401d0"
MATRIX_DIAG_REL = Path("research/challenge-8/cloud-build/select-callee-r24-mut-matrix-proof.py")
MATRIX_DIAG_SHA256 = "f0907ded785ed659309277a497d8425f882dbd492da2d6c3e81cdc4b1088cbf8"
MUTABLE_NATIVE_SHA256 = "8a481421396de618e50f8a6b7a408ffd9f048fd94397e647c3002e1489723d0c"
CLASSIFIED_REL = Path("research/challenge-8/cloud-build/select-callee-r24-mut-classified-proof.py")
CLASSIFIED_SHA256 = "bcbc28fe5db67419e3fed16851e741452829b51ac9113ff6db55c8084003d992"
CLASSIFIED_MODE_REL = Path("research/challenge-8/task-history/select-callee-r24/P2-MUT-CLASSIFIED-PROOF-MODE.json")
CLASSIFIED_MODE_SHA256 = "3e17c17a993f01e8d136effd2ec3026f11825ef30793eb5178d9fe2f787131b7"
MATRIX_MODE_REL = Path("research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PROOF-MODE.json")
MATRIX_MODE_SHA256 = "7870ea7c985914a1af049f685d62291bfe8d9768c0e4719c40422106d559fa94"
MATRIX_PINS_REL = Path("research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PINS.json")
MATRIX_PINS_SHA256 = "5aee793196c2e0ab5960f1c0ea4aab8880ca68e61d74876363e2ccf3febadbed"
COLLECTOR_REL = Path("research/challenge-8/cloud-build/select-callee-r24-mut-refusals.py")
COLLECTOR_SHA256 = "a204baa85e37d1eaf4a7ba131fe099f2fcaed16d4fee95e5c0111bfbfc08db19"
ENTAILMENT_REL = Path("research/challenge-8/cloud-build/select-callee-r24-p2-entailment.py")
ENTAILMENT_SHA256 = "a0cdf07ed378e8daf3986661f1fb239391e1632d68b2a3e3654a5d5082bbb389"
CAPTURE_SUMMARY_REL = Path("cases/r24-mut-capture/MUT-CAPTURE-SUMMARY.json")
REFUSAL_SUMMARY_REL = Path("cases/r24-mut-refusals/MUT-REFUSALS.json")
AUDIT_SCHEMA = "select-r24-mut-refusal-entry-audit-v1"
AUDIT_REL = Path("cases/r24-mut-refusals/MUT-REFUSALS-AUDIT.json")
PREFLIGHT_ROOT_REL = Path("cases/r24-mut-refusals/preconditions")
CLASSIFIED_AUDIT_REL = PREFLIGHT_ROOT_REL / "MUT-CLASSIFIED-PROOF-AUDIT.json"
CONSEQUENCE_AUDIT_REL = PREFLIGHT_ROOT_REL / "P2-ENTAILMENT-AUDIT.json"
POSITIVE_SOURCE_REL = Path("cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut")
SOURCE_VIEW_REL = Path("cases/r24-mut-capture/source-repository")
POSITIVE_ORIGINAL_SHA256 = "3bf0bf792c8135bf964f19b3aaadef38b8ca5ee9ec95107029ad99d28a807aaa"
POSITIVE_VERIFIED_SHA256 = "74b20681c4c34cdc9ecd0fbb7fb3d44c51941e5d9640ede5705c5d6b6fa25165"
CONTRACT_SHA256 = "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870"
CONTROLS = [
    "const-substitution", "extra-pointer-depth",
    "swapped-selected-pointer-operand", "swapped-final-branch-result",
    "changed-runtime-body", "renamed-generic-element", "changed-cleanup-graph",
    "wrong-phase", "partial-case-root", "unknown-case", "legacy-selector",
]


class EntryError(RuntimeError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _need(ok: bool, message: str) -> None:
    if not ok:
        raise EntryError("R24-MUT-REFUSAL-ENTRY: " + message)


def _load_exact(path: Path, expected_sha256: str, name: str):
    _need(path.is_file() and not path.is_symlink() and
          _sha(path.read_bytes()) == expected_sha256,
          "frozen module identity differs: " + path.name)
    spec = importlib.util.spec_from_file_location(name, path)
    _need(spec is not None and spec.loader is not None,
          "frozen module loader unavailable: " + path.name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _need(_sha(path.read_bytes()) == expected_sha256,
          "frozen module changed during load: " + path.name)
    return module


def _expected_mode() -> dict[str, Any]:
    return {
        "accepted": False,
        "capture_adapter_file": CAPTURE_ADAPTER_REL.as_posix(),
        "capture_adapter_sha256": CAPTURE_ADAPTER_SHA256,
        "capture_pins_file": CAPTURE_PINS_REL.as_posix(),
        "capture_pins_sha256": CAPTURE_PINS_SHA256,
        "checked_mode": "R24_CLOSED_MUTABLE_SOURCE_ENVELOPE_REFUSALS_ONLY",
        "classified_mode_file": CLASSIFIED_MODE_REL.as_posix(),
        "classified_mode_sha256": CLASSIFIED_MODE_SHA256,
        "classified_module_file": CLASSIFIED_REL.as_posix(),
        "classified_module_sha256": CLASSIFIED_SHA256,
        "collector_file": COLLECTOR_REL.as_posix(),
        "collector_sha256": COLLECTOR_SHA256,
        "controls": CONTROLS,
        "diagnostic_module_file": MATRIX_DIAG_REL.as_posix(),
        "diagnostic_module_sha256": MATRIX_DIAG_SHA256,
        "entailment_module_file": ENTAILMENT_REL.as_posix(),
        "entailment_module_sha256": ENTAILMENT_SHA256,
        "enabled": True,
        "lane": LANE,
        "matrix_mode_file": MATRIX_MODE_REL.as_posix(),
        "matrix_mode_sha256": MATRIX_MODE_SHA256,
        "matrix_pins_file": MATRIX_PINS_REL.as_posix(),
        "matrix_pins_sha256": MATRIX_PINS_SHA256,
        "native_library_sha256": MUTABLE_NATIVE_SHA256,
        "owner": OWNER,
        "phase_id": R24,
        "proof_credit": 0,
        "publication_allowed": False,
        "route_phase_id": R21,
        "schema": MODE_SCHEMA,
        "source_only": True,
    }


def validate_mode(repo: Path, mode_path: Path) -> dict[str, Any]:
    _need(mode_path.resolve() == (repo / MODE_REL).resolve() and
          mode_path.is_file() and not mode_path.is_symlink() and
          _sha(mode_path.read_bytes()) == MODE_SHA256,
          "exact refusal-mode path and raw hash required")
    try:
        mode = json.loads(mode_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise EntryError("R24-MUT-REFUSAL-ENTRY: refusal mode malformed") from exc
    _need(mode == _expected_mode(), "refusal-mode fields, pins, or 11-control inventory differ")
    return mode


def load_services(cloud_dir: Path):
    classified = _load_exact(cloud_dir / CLASSIFIED_REL.name, CLASSIFIED_SHA256,
                             "r24_mut_refusal_classified")
    diag, targets = classified.load_services(cloud_dir)
    _need(_sha((cloud_dir / MATRIX_DIAG_REL.name).read_bytes()) == MATRIX_DIAG_SHA256,
          "diagnostic wrapper identity differs")
    lib = diag.load_library(cloud_dir)
    old = _load_exact(cloud_dir / CAPTURE_ADAPTER_REL.name,
                      CAPTURE_ADAPTER_SHA256, "r24_mut_refusal_capture")
    collector = _load_exact(cloud_dir / COLLECTOR_REL.name,
                            COLLECTOR_SHA256, "r24_mut_refusal_collector")
    entailment = _load_exact(cloud_dir / ENTAILMENT_REL.name,
                             ENTAILMENT_SHA256, "r24_mut_refusal_entailment")
    _need(_sha((cloud_dir / "select-callee-r24-mut-proof.py").read_bytes()) ==
          MUTABLE_NATIVE_SHA256, "mutable native proof library pin differs")
    return {"classified": classified, "diag": diag, "targets": targets,
            "lib": lib, "old": old, "collector": collector,
            "entailment": entailment}


def _validate_context(args, env: dict[str, str], services: dict[str, Any]) -> dict[str, Any]:
    repo, cloud_dir = Path(args.repo).resolve(), Path(args.cloud_dir).resolve()
    mode = validate_mode(repo, Path(args.refusal_mode_file))
    diag, lib = services["diag"], services["lib"]
    build = diag._validate_context(args, env, lib)
    diag.validate_mode(repo, Path(args.matrix_proof_mode_file), lib)
    services["classified"].validate_classified_mode(
        repo, Path(args.classified_mode_file), lib, services["targets"])
    _need(args.candidate == env.get("PROOF_SHA"),
          "candidate must match exact committed PROOF_SHA")
    sysroot_value = getattr(args, "compiler_sysroot", None)
    _need(Path(args.tool_home).is_absolute() and Path(args.schema).is_absolute() and
          isinstance(sysroot_value, (str, Path)) and str(sysroot_value).strip() and
          Path(sysroot_value).is_absolute() and type(args.deadline_epoch) is int,
          "exact current tool/schema/sysroot/deadline arguments required")
    return {"mode": mode, "build_id": build, "repo": repo, "cloud_dir": cloud_dir}


def _read_capture_summary(evidence: Path, build_id: str,
                          collector: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    path = evidence / CAPTURE_SUMMARY_REL
    _need(path.is_file() and not path.is_symlink(),
          "fresh source-only mutable capture summary missing/symlinked")
    try:
        summary = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise EntryError("R24-MUT-REFUSAL-ENTRY: capture summary malformed") from exc
    _need(isinstance(summary, dict) and
          summary.get("schema") == "select-r24-mut-capture-summary-v1" and
          summary.get("complete") is True and
          summary.get("classification") == "MUTABLE_SOURCE_MIR_CAPTURE_ONLY" and
          summary.get("native_build_id") == build_id and
          summary.get("body_proof_run") is False and
          summary.get("typed_admission") is False and
          summary.get("semantic_rule_enabled") is False and
          summary.get("accepted") is False and summary.get("publication_allowed") is False and
          type(summary.get("proof_credit")) is int and summary.get("proof_credit") == 0,
          "same-build mutable source-only capture summary incomplete or overclaims")
    records = summary.get("source_records")
    source = records.get("final_nine_body") if isinstance(records, dict) else None
    provider = summary.get("provider_record")
    _need(isinstance(source, dict) and
          source.get("classification") == "SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE" and
          source.get("original_sha256") == collector.POSITIVE_ORIGINAL_SHA256 and
          source.get("verified_sha256") == collector.POSITIVE_VERIFIED_SHA256 and
          source.get("specialization") == "T = *mut Element; Element unrestricted" and
          source.get("ghost_strip_identity") is True and
          source.get("typed_mir_binding_established") is False and
          source.get("helper_proof_status") == "NOT_RUN" and
          source.get("publication_status") == "NOT_PUBLISHED" and
          source.get("proof_credit") == 0 and
          records.get("contract_text_sha256") == CONTRACT_SHA256,
          "pinned source-only nine-body record differs or overclaims")
    collector._validate_provider_record(provider, build_id)
    return summary, source


def _load_current_provider(old: object, cloud_dir: Path, build_id: str,
                           collector: object) -> dict[str, Any]:
    loader = getattr(old, "load_provider", None)
    _need(callable(loader), "frozen capture provider loader unavailable")
    provider = loader(cloud_dir)
    require = getattr(provider, "require_supported_provider", None)
    _need(callable(require), "frozen provider require_supported_provider API unavailable")
    record = require()
    return collector._validate_provider_record(record, build_id)


def _validate_positive_capture_artifacts(evidence: Path, summary: dict[str, Any],
                                         source: dict[str, Any], owner: object,
                                         capture: object, old: object) -> None:
    case = evidence / POSITIVE_SOURCE_REL
    errors = old._capture_errors(
        capture, source, case, summary.get("guard_capture"),
        summary.get("full_body_capture"), summary.get("fingerprint"))
    errors.extend(old._final_source_pair_errors(
        evidence / "cases/r24-mut-capture", case, source, owner))
    _need(errors == [], "current positive source capture physical audit failed: " +
          "; ".join(errors))


def _precondition_audits(args, services: dict[str, Any], env: dict[str, str],
                         runner_exit: int, failed_stage: str, evidence: Path,
                         *, persist: bool) -> dict[str, Any]:
    # Frozen audits write to their caller-selected output. Use a private temporary
    # directory so these checks cannot overwrite the established matrix audits.
    with tempfile.TemporaryDirectory(prefix="r24-mut-refusal-preflight-") as temp:
        output = Path(temp) / "audit.json"
        audit_args = SimpleNamespace(**vars(args))
        audit_args.output = output
        audit_args.runner_exit = runner_exit
        audit_args.failed_stage = failed_stage
        try:
            classified = services["classified"].audit(
                audit_args, diag=services["diag"], targets=services["targets"], env=env)
        except BaseException as exc:
            _record_precondition_receipt(
                evidence, CLASSIFIED_AUDIT_REL,
                {"schema": "select-r24-mut-classified-audit-exception-v1",
                 "complete": False, "exception": {"type": type(exc).__name__,
                 "message": str(exc), "traceback": traceback.format_exc()}},
                persist=persist, original_error=exc)
            raise
        _record_precondition_receipt(
            evidence, CLASSIFIED_AUDIT_REL, classified, persist=persist)
        _need(isinstance(classified, dict) and classified.get("evidence_complete") is True and
              classified.get("accepted") is False and
              classified.get("publication_allowed") is False and
              classified.get("proof_credit") == 0,
              "same-tool classified all-eight audit is incomplete")
        # argparse supplies Path objects, while the frozen consequence audit's
        # stage-identity guard intentionally requires a nonempty string.
        entailment_args = SimpleNamespace(**vars(audit_args))
        entailment_args.compiler_sysroot = str(args.compiler_sysroot)
        try:
            consequence = services["entailment"].audit(
                entailment_args, diag=services["diag"])
        except BaseException as exc:
            _record_precondition_receipt(
                evidence, CONSEQUENCE_AUDIT_REL,
                {"schema": "select-r24-p2-consequence-audit-exception-v1",
                 "complete": False, "exception": {"type": type(exc).__name__,
                 "message": str(exc), "traceback": traceback.format_exc()}},
                persist=persist, original_error=exc)
            raise
        _record_precondition_receipt(
            evidence, CONSEQUENCE_AUDIT_REL, consequence, persist=persist)
        _need(isinstance(consequence, dict) and
              consequence.get("evidence_complete") is True and
              consequence.get("accepted") is False and
              consequence.get("publication_allowed") is False and
              consequence.get("proof_credit") == 0,
              "same-tool checked P2 consequence audit is incomplete")
        return {"classified_audit": classified,
                "p2_consequence_audit": consequence}


def _record_precondition_receipt(evidence: Path, relative: Path,
                                 current: object, *, persist: bool,
                                 original_error: BaseException | None = None) -> None:
    path = evidence / relative
    if persist:
        try:
            _write_json(path, current)
        except BaseException as write_error:
            if original_error is not None:
                if hasattr(original_error, "add_note"):
                    original_error.add_note(
                        "precondition exception receipt write failed: " +
                        type(write_error).__name__ + ": " + str(write_error))
                return
            raise
        return
    try:
        _need(path.is_file() and not path.is_symlink(),
              "persisted precondition audit missing/symlinked: " + relative.name)
        saved = json.loads(path.read_text(encoding="utf-8"))
        _need(saved == current,
              "freshly recomputed precondition audit differs: " + relative.name)
    except BaseException as receipt_error:
        if original_error is not None:
            if hasattr(original_error, "add_note"):
                original_error.add_note(
                    "precondition exception receipt comparison failed: " +
                    type(receipt_error).__name__ + ": " + str(receipt_error))
            return
        if isinstance(receipt_error, (OSError, UnicodeDecodeError, ValueError)):
            raise EntryError("R24-MUT-REFUSAL-ENTRY: persisted precondition audit malformed: " +
                             relative.name) from receipt_error
        raise


def run(args, *, env=None, services=None) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    services = load_services(Path(args.cloud_dir)) if services is None else services
    context = _validate_context(args, env, services)
    evidence = Path(args.evidence).resolve()
    preconditions = _precondition_audits(
        args, services, env, 0, "complete", evidence, persist=True)
    capture_summary, source_record = _read_capture_summary(
        evidence, context["build_id"], services["collector"])
    current_provider = _load_current_provider(
        services["old"], context["cloud_dir"], context["build_id"], services["collector"])
    _need(current_provider == capture_summary["provider_record"],
          "fresh native provider record differs from current capture summary")
    positive_case = evidence / POSITIVE_SOURCE_REL
    source_view = evidence / SOURCE_VIEW_REL
    _need(source_view.is_dir() and not source_view.is_symlink(),
          "current capture committed-source view missing/symlinked")
    owner = services["old"].load_source_writers(source_view)["owner"]
    runtime = services["old"].load_capture_runtime(
        context["repo"], context["cloud_dir"], evidence)
    _need(isinstance(runtime, dict) and runtime.get("capture") is not None,
          "frozen mutable capture runtime unavailable")
    capture = runtime["capture"]
    _validate_positive_capture_artifacts(
        evidence, capture_summary, source_record, owner, capture, services["old"])
    frontend_runner = services["collector"].make_frontend_capture_runner(
        capture, args, services["old"]._capture_errors)
    link = getattr(capture, "LINK", None)
    stage_runner = services["collector"].make_link_stage_runner(link, args)
    result = services["collector"].collect_controls(
        evidence=evidence, positive_case=positive_case, repo=context["repo"],
        owner=owner, source_record=source_record,
        frontend_runner=frontend_runner, tool_home=Path(args.tool_home).resolve(),
        tool_spec=(Path(args.tool_home).resolve() /
                   services["collector"].TOOL_SPEC_RELATIVE).read_bytes(),
        build_id=context["build_id"], provider_record=capture_summary["provider_record"],
        stage_runner=stage_runner, env=env)
    result["precondition_audits"] = preconditions
    return result


def audit(args, *, env=None, services=None) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    services = load_services(Path(args.cloud_dir)) if services is None else services
    errors: list[str] = []
    report: dict[str, Any] = {}
    try:
        context = _validate_context(args, env, services)
        evidence = Path(args.evidence).resolve()
        preconditions = _precondition_audits(
            args, services, env, args.runner_exit, args.failed_stage,
            evidence, persist=False)
        capture_summary, source_record = _read_capture_summary(
            evidence, context["build_id"], services["collector"])
        current_provider = _load_current_provider(
            services["old"], context["cloud_dir"], context["build_id"], services["collector"])
        _need(current_provider == capture_summary["provider_record"],
              "fresh native provider record differs from current capture summary")
        source_view = evidence / SOURCE_VIEW_REL
        _need(source_view.is_dir() and not source_view.is_symlink(),
              "current capture committed-source view missing/symlinked")
        owner = services["old"].load_source_writers(source_view)["owner"]
        runtime = services["old"].load_capture_runtime(
            context["repo"], context["cloud_dir"], evidence)
        capture = runtime["capture"]
        _validate_positive_capture_artifacts(
            evidence, capture_summary, source_record, owner, capture, services["old"])
        collector_audit = services["collector"].audit_controls(
            evidence=evidence,
            positive_case=evidence / POSITIVE_SOURCE_REL,
            repo=context["repo"], owner=owner, capture=capture,
            capture_errors=services["old"]._capture_errors,
            tool_home=Path(args.tool_home).resolve(),
            tool_spec=(Path(args.tool_home).resolve() /
                       services["collector"].TOOL_SPEC_RELATIVE).read_bytes(),
            build_id=context["build_id"],
            provider_record=capture_summary["provider_record"], env=env)
        _need(collector_audit.get("complete") is True,
              "refusal collector physical audit is incomplete")
        report.update({"complete": True,
                       "classification": "COMPLETE_SOURCE_REPORTED_REFUSALS_NO_PROOF_CREDIT",
                       "precondition_audits": preconditions,
                       "capture_summary": capture_summary,
                       "source_record": source_record,
                       "collector_audit": collector_audit})
    except BaseException as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
        report["exception"] = {"type": type(exc).__name__, "message": str(exc),
                               "traceback": traceback.format_exc()}
    report.update({"schema": AUDIT_SCHEMA,
                   "complete": report.get("complete") is True and not errors,
                   "evidence_complete": report.get("complete") is True and not errors,
                   "errors": errors,
                   "runner_exit": args.runner_exit,
                   "failed_stage": args.failed_stage,
                   "accepted": False, "publication_allowed": False,
                   "proof_credit": 0})
    _write_json(Path(args.output), report)
    return report


def _write_json(path: Path, value: object) -> None:
    _need(not path.exists() and not path.is_symlink(),
          "fresh refusal entry audit output required")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name("." + path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "audit"))
    for name in ("repo", "cloud-dir", "evidence", "tool-home", "schema",
                 "compiler-sysroot", "refusal-mode-file", "classified-mode-file",
                 "matrix-proof-mode-file"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--runner-exit", type=int)
    parser.add_argument("--failed-stage")
    args = parser.parse_args()
    if args.action == "run":
        result = run(args)
        print(json.dumps({"complete": result.get("complete"),
                          "classification": result.get("classification"),
                          "accepted": False, "proof_credit": 0}, sort_keys=True))
        if result.get("complete") is not True:
            raise SystemExit(4)
    else:
        _need(args.output is not None and args.runner_exit is not None and
              args.failed_stage is not None,
              "audit requires output, runner exit, and failed-stage status")
        result = audit(args)
        print(json.dumps({"complete": result["complete"],
                          "evidence_complete": result["evidence_complete"],
                          "accepted": False, "proof_credit": 0}, sort_keys=True))
        if result["evidence_complete"] is not True:
            raise SystemExit(4)


if __name__ == "__main__":
    main()
