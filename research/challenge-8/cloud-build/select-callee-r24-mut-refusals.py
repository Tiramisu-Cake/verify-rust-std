#!/usr/bin/env python3
"""Collect source-envelope refusals for the closed R24 mutable selector.

The caller supplies the positive source fixture, the pinned source stripper,
and the existing native stage callback. This module creates isolated source
controls and classifies only an exact native certificate refusal. It never
credits a proof or treats compiler/setup failures as intended refusals.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import copy
from types import SimpleNamespace
import uuid
from typing import Any, Callable


SCHEMA = "select-r24-mut-refusal-collection-v1"
SUMMARY_RELATIVE = Path("cases/r24-mut-refusals/MUT-REFUSALS.json")
R24_PHASE_ENV = "SORT4_R24_SESSION_PHASE_ID"
R21_PHASE_ENV = "SORT4_R20_CALLEE_PHASE_ID"
PROFILE_ENV = "SORT4_SELECT_PROFILE"
CASE_ENV = "SORT4_R24_MUTABLE_CASE"
ROOT_ENV = "SORT4_R24_MUTABLE_REPO_ROOT"
R24_PHASE = "SORT4-ACTUAL-SELECT-2026-10-24-R24"
R21_PHASE = "SORT4-ACTUAL-SELECT-2026-10-23-R21"
PROFILE = "experimental-s6-26.10-v1"
LANE = "o26-select-callee-r20"
SUPPORTED_PROVIDER = {
    "provider": "cloud-build", "project": "smallsort-ci", "region": "global",
    "os": "ubuntu-22.04", "arch": "x86_64",
}
TOOL_SPEC_RELATIVE = Path("bin/rust/std/lib.rsspec")
POSITIVE_ORIGINAL_SHA256 = (
    "3bf0bf792c8135bf964f19b3aaadef38b8ca5ee9ec95107029ad99d28a807aaa"
)
POSITIVE_VERIFIED_SHA256 = (
    "74b20681c4c34cdc9ecd0fbb7fb3d44c51941e5d9640ede5705c5d6b6fa25165"
)
CAPTURE_PINS_SHA256 = (
    "b10d8f472fd9babc5e73cb7a8da14ad691b0563975d0d6d956366165a47401d0"
)
CAPTURE_PINS_RELATIVE = Path(
    "research/challenge-8/task-history/select-callee-r24/P2-MUT-CAPTURE-PINS.json"
)
MUTABLE_SIGNATURE = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *mut Element,\n"
    b"    false_val: *mut Element,\n) -> *mut Element\n"
)
RUNTIME_SENTINEL = (
    b"crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()"
)
MARKER_PREFIX = "SORT4-R24-MUTABLE-CERTIFICATES:"
REFUSAL_PREFIX = 'Fatal error: exception Failure("SORT4-R24-MUTABLE-CERTIFICATES: refusal: '
REFUSAL_SUFFIX = '")'
SOURCE_HASH_REFUSAL = "exact mutable verified source SHA256"
ROUTE_REFUSAL = "exact R24/R21 profile and unwind-preserving route required"
PARTIAL_SELECTOR_REFUSAL = "partial mutable case/root selector"
UNKNOWN_CASE_REFUSAL = "mutable case selector must be one closed enum value"
LEGACY_SELECTOR = "SORT4_R24_CHECKED_POINTER_OUTCOMES"
# The real legacy flag is rejected by the earlier const-profile admit() route
# guard before the mutable certificate family is reached (observed ed261d30).
LEGACY_REFUSAL = "exact R24/R21 certified fractional nine-body route required"
LEGACY_MARKER_PREFIX = "SORT4-R24-CHECKED-POINTER-OUTCOMES:"
LEGACY_REFUSAL_PREFIX = 'Fatal error: exception Failure("' + LEGACY_MARKER_PREFIX + ' refusal: '


SOURCE_CONTROLS = (
    "const-substitution",
    "extra-pointer-depth",
    "swapped-selected-pointer-operand",
    "swapped-final-branch-result",
    "changed-runtime-body",
    "renamed-generic-element",
    "changed-cleanup-graph",
)
CONTEXT_CONTROLS = (
    "wrong-phase",
    "partial-case-root",
    "unknown-case",
    "legacy-selector",
)
ALL_CONTROLS = SOURCE_CONTROLS + CONTEXT_CONTROLS
EXPECTED_REFUSALS = {
    **{name: SOURCE_HASH_REFUSAL for name in SOURCE_CONTROLS},
    "wrong-phase": ROUTE_REFUSAL,
    "partial-case-root": PARTIAL_SELECTOR_REFUSAL,
    "unknown-case": UNKNOWN_CASE_REFUSAL,
    "legacy-selector": LEGACY_REFUSAL,
}
ERROR_MARKERS = (
    "Fatal error:", "error:", "Cannot prove", "Assertion might not hold",
    "Verification failed", "timed out", "TIMEOUT",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
ELEMENT_TOKEN = re.compile(rb"\bElement\b")


class RefusalError(ValueError):
    """Malformed fixture, route, native stage, or unexpected diagnostic."""


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RefusalError("R24-MUT-REFUSALS: " + why)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _source_pair_hashes(case: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for rel in (Path("original/lib.rs"), Path("verified/lib.rs")):
        path = case / rel
        _need(path.is_file() and not path.is_symlink(),
              "source target missing or symlinked: " + rel.as_posix())
        result[rel.as_posix()] = _sha(path.read_bytes())
    return result


def _replace_once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    _need(raw.count(old) == 1, "control anchor absent/ambiguous: " + label)
    return raw.replace(old, new, 1)


def mutate_verified_source(variant: str, verified: bytes) -> bytes:
    """Return one uniquely anchored, compile-valid source-envelope mutation."""
    _need(variant in SOURCE_CONTROLS, "unknown source control")
    _need(isinstance(verified, bytes) and verified.count(MUTABLE_SIGNATURE) == 1,
          "exact mutable select signature absent/ambiguous")
    _need(verified.count(RUNTIME_SENTINEL) == 1,
          "exact mutable runtime select expression absent/ambiguous")

    if variant == "const-substitution":
        _need(b"*const Element" not in verified and verified.count(b"*mut Element") >= 1,
              "const substitution precondition differs")
        # This changes only the inner Element pointer token. An enclosing
        # `*mut *mut Element` retains its outer mutable slot pointer.
        changed = verified.replace(b"*mut Element", b"*const Element")
        _need(b"*const *const Element" not in changed,
              "const substitution changed outer slot depth")
        return changed

    if variant == "extra-pointer-depth":
        _need(b"*mut Element" in verified, "mutable Element pointer absent")
        changed = verified.replace(b"*mut Element", b"*mut *mut Element")
        _need(b"*mut *mut *mut Element" in changed,
              "extra pointer depth did not preserve the outer mutable slot")
        return changed

    if variant == "swapped-selected-pointer-operand":
        return _replace_once(
            verified, RUNTIME_SENTINEL,
            b"crate::intrinsics::select_unpredictable(condition, false_val, true_val).assume_init()",
            variant)

    if variant == "swapped-final-branch-result":
        return _replace_once(
            verified, RUNTIME_SENTINEL,
            b"crate::intrinsics::select_unpredictable(!condition, true_val, false_val).assume_init()",
            variant)

    if variant == "changed-runtime-body":
        return _replace_once(
            verified, RUNTIME_SENTINEL, b"{ " + RUNTIME_SENTINEL + b" }", variant)

    if variant == "renamed-generic-element":
        _need(ELEMENT_TOKEN.search(verified) is not None,
              "Element generic identifier absent")
        return ELEMENT_TOKEN.sub(b"R24MutatedElement", verified)

    if variant == "changed-cleanup-graph":
        # The initialized Box is local to the result block and must be dropped
        # on its normal edge. It adds a real cleanup edge without changing the
        # already-pinned std files or the mutable native tool profile.
        return _replace_once(
            verified, RUNTIME_SENTINEL,
            b"{ let _r24_cleanup_box: Box<u8> = Box::new(0u8); " +
            RUNTIME_SENTINEL + b" }", variant)

    raise AssertionError("unreachable source control")


def _child_environment_delta(control: str, repo: Path) -> dict[str, str | None]:
    delta: dict[str, str | None] = {CASE_ENV: "positive", ROOT_ENV: str(repo)}
    if control == "wrong-phase":
        delta[R24_PHASE_ENV] = "SORT4-ACTUAL-SELECT-WRONG-PHASE"
    elif control == "partial-case-root":
        delta[ROOT_ENV] = None
    elif control == "unknown-case":
        delta[CASE_ENV] = "not-a-closed-mutable-case"
    elif control == "legacy-selector":
        delta[LEGACY_SELECTOR] = "1"
    return delta


@contextmanager
def _temporary_environment(delta: dict[str, str | None]):
    previous = {key: os.environ.get(key) for key in delta}
    try:
        for key, value in delta.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _validate_route(env: dict[str, str], repo: Path, build_id: str) -> None:
    _need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          env.get(R24_PHASE_ENV) == R24_PHASE and
          env.get(R21_PHASE_ENV) == R21_PHASE and
          env.get(PROFILE_ENV) == PROFILE and env.get("LANE") == LANE and
          not env.get("GITHUB_ACTIONS"), "exact live R24/R21 Cloud route required")
    _need(isinstance(build_id, str) and UUID_RE.fullmatch(build_id) is not None and
          build_id == env.get("CLOUD_BUILD_ID"),
          "exact current native Cloud Build UUID required")
    for key in ("SMALLSORT_EXECUTION_PROVIDER", R24_PHASE_ENV, R21_PHASE_ENV,
                PROFILE_ENV, "LANE", "CLOUD_BUILD_ID"):
        _need(os.environ.get(key) == env.get(key),
              "supplied route snapshot differs from live process environment: " + key)
    _need(repo.is_absolute() and repo.is_dir(), "absolute mutable std repository required")
    allowed = {R24_PHASE_ENV, R21_PHASE_ENV, PROFILE_ENV}
    unexpected = sorted(key for key in env
                        if key.startswith("SORT4_") and key not in allowed)
    _need(not unexpected, "ambient mutable/legacy semantic opt-ins refused")
    _need(CASE_ENV not in env and ROOT_ENV not in env,
          "mutable case/root selector must be absent in the parent process")


def _validate_provider_record(provider_record: object, build_id: str) -> dict[str, Any]:
    _need(isinstance(provider_record, dict) and
          all(provider_record.get(key) == value
              for key, value in SUPPORTED_PROVIDER.items()) and
          provider_record.get("build_id") == build_id,
          "validated native Cloud provider record is incomplete or mismatched")
    return provider_record


def _load_capture_pins(repo: Path) -> dict[str, Any]:
    path = repo / CAPTURE_PINS_RELATIVE
    _need(path.is_file() and not path.is_symlink() and
          _sha(path.read_bytes()) == CAPTURE_PINS_SHA256,
          "exact positive mutable capture pins required")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise RefusalError("R24-MUT-REFUSALS: capture pins malformed") from exc
    _need(value.get("schema") == "select-r24-mut-positive-capture-pins-v1" and
          value.get("accepted") is False and value.get("proof_credit") == 0 and
          value.get("publication_allowed") is False and
          value.get("source", {}).get("original_sha256") == POSITIVE_ORIGINAL_SHA256 and
          value.get("source", {}).get("verified_sha256") == POSITIVE_VERIFIED_SHA256 and
          value.get("source", {}).get("contract_text_sha256") ==
          "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870" and
          value.get("source", {}).get("specialization") ==
          "T = *mut Element; Element unrestricted",
          "positive capture pins source-only identity differs")
    return value


def _write_summary(path: Path, summary: dict[str, Any]) -> None:
    _need(not path.exists() and not path.is_symlink(),
          "fresh mutable refusal summary required")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp")
    temporary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def _read_log(case: Path, stage: object, stage_name: str) -> tuple[bytes, str, str]:
    _need(isinstance(stage, dict), "native stage result is not an object")
    log_name = stage_name + ".log"
    _need(stage.get("stdout") == log_name and stage.get("stderr") == log_name,
          "native stage stdout/stderr log binding differs")
    path = case / log_name
    _need(path.is_file() and not path.is_symlink(), "native refusal log missing/symlinked")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RefusalError("R24-MUT-REFUSALS: native refusal log is not strict UTF-8") from exc
    return raw, text, path.relative_to(case).as_posix()


def _expected_refusal_line(control: str) -> str:
    prefix = LEGACY_REFUSAL_PREFIX if control == "legacy-selector" else REFUSAL_PREFIX
    return prefix + EXPECTED_REFUSALS[control] + REFUSAL_SUFFIX


def _classify_log(control: str, text: str) -> tuple[bool, str | None, str]:
    expected = EXPECTED_REFUSALS[control]
    lines = [line.strip() for line in text.splitlines()
             if any(marker.casefold() in line.casefold() for marker in ERROR_MARKERS)]
    expected_line = _expected_refusal_line(control)
    marker_lines = [line.strip() for line in text.splitlines()
                    if MARKER_PREFIX in line or LEGACY_MARKER_PREFIX in line]
    _need(not marker_lines or marker_lines == [expected_line],
          "native certificate marker inventory differs from exact expected refusal")
    if len(lines) != 1 or lines[0] != expected_line:
        return False, None, (
            "unexpected native diagnostic; expected exact refusal line")
    return True, expected, "exact source-envelope refusal observed"


def _case_source_pair(positive_verified: bytes, owner: object) -> tuple[bytes, bytes]:
    _need(callable(getattr(owner, "strip_ghost", None)),
          "pinned owner ghost-strip API unavailable")
    verified = positive_verified
    original = owner.strip_ghost(verified)
    _need(isinstance(original, bytes) and owner.strip_ghost(verified) == original,
          "fresh control original/verified ghost-strip identity differs")
    return original, verified


def _stage_errors(stage: object, case: Path, stage_name: str,
                  before: dict[str, str], after: dict[str, str],
                  tool_home: Path, native_build_id: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(stage, dict):
        return ["native stage result is not an object"]
    argv = [str(tool_home / "bin/verifast"), "-rustc_args",
            "--edition 2021", "-verbose", "1", "verified/lib.rs"]
    if stage.get("status") != "RAN":
        errors.append("native stage status is not RAN")
    if type(stage.get("exit")) is not int or stage.get("exit") != 2:
        errors.append("native refusal stage exit is not exactly 2")
    if stage.get("timeout") is True or stage.get("timed_out") is True or \
       stage.get("status") in ("TIMEOUT", "TIMED_OUT") or stage.get("exit") in (124, 137):
        errors.append("native refusal stage timed out")
    if stage.get("name") not in (None, stage_name):
        errors.append("native stage name differs")
    if stage.get("build_id") not in (None, native_build_id):
        errors.append("native stage build ID differs")
    if stage.get("argv") != argv:
        errors.append("native stage argv differs")
    if stage.get("source_before") != before or stage.get("source_after") != after or \
       before != after or stage.get("source_unchanged") is not True:
        errors.append("native stage source changed or stage source binding differs")
    if stage.get("intrinsic_gate_active") is not False or \
       stage.get("pointer_drop_gate_active") is not False:
        errors.append("legacy intrinsic/pointer-drop gate flags were active")
    return errors


def make_link_stage_runner(link: object, args: object) -> Callable[..., object]:
    """Adapt the frozen capture ``LINK.stage`` API to the collector callback."""
    stage_method = getattr(link, "stage", None)
    _need(callable(stage_method), "frozen capture LINK.stage API unavailable")

    def run(*, case: Path, variant: str, name: str, build_id: str,
            child_environment_delta: dict[str, str | None]) -> object:
        del variant, build_id, child_environment_delta
        native_args = SimpleNamespace(
            tool_home=Path(args.tool_home),
            schema=Path(args.schema),
            compiler_sysroot=str(args.compiler_sysroot),
            deadline_epoch=int(args.deadline_epoch),
        )
        argv = [str(Path(args.tool_home) / "bin/verifast"), "-rustc_args",
                "--edition 2021", "-verbose", "1", "verified/lib.rs"]
        return stage_method(case, name, argv, native_args,
                            gates=False, pointer_drop=False, cap_seconds=1200)

    return run


def make_frontend_capture_runner(capture: object, args: object,
                                 capture_errors: Callable[..., list[str]]) -> Callable[..., dict[str, Any]]:
    """Adapt the frozen NORMAL/readonly capture and nine-body decoder services."""
    guard = getattr(capture, "GUARD", None)
    _need(callable(getattr(guard, "capture_case", None)) and
         callable(getattr(capture, "full_body_capture", None)) and
         callable(getattr(capture, "clear_semantic_opt_ins", None)),
         "frozen NORMAL/readonly mutable capture services unavailable")

    def run(*, case: Path, source_record: dict[str, Any]) -> dict[str, Any]:
        record = copy.deepcopy(source_record)
        record["original_sha256"] = _source_pair_hashes(case)["original/lib.rs"]
        record["verified_sha256"] = _source_pair_hashes(case)["verified/lib.rs"]
        record["ghost_strip_identity"] = True
        capture_args = SimpleNamespace(
            tool_home=Path(args.tool_home), schema=Path(args.schema),
            compiler_sysroot=str(args.compiler_sysroot),
            deadline_epoch=int(args.deadline_epoch), first_barrier=False,
            fingerprint_probe=False,
        )
        capture.clear_semantic_opt_ins()
        result = guard.capture_case(case, record, capture_args)
        stages = result.get("stages") if isinstance(result, dict) else None
        full = capture.full_body_capture(case, record, stages or {})
        errors = capture_errors(capture, record, case, result, full, None,
                                require_fingerprint=False)
        return {"source_record": record, "guard_capture": result,
                "stages": stages if isinstance(stages, dict) else {},
                "full_body_capture": full, "errors": list(errors)}

    return run


def collect_controls(*, evidence: Path, positive_case: Path, repo: Path,
                     owner: object, source_record: dict[str, Any],
                     frontend_runner: Callable[..., dict[str, Any]],
                     tool_home: Path, tool_spec: bytes,
                     build_id: str, provider_record: dict[str, Any],
                     stage_runner: Callable[..., object],
                     env: dict[str, str] | None = None,
                     source_controls: tuple[str, ...] = SOURCE_CONTROLS,
                     context_controls: tuple[str, ...] = CONTEXT_CONTROLS) -> dict[str, Any]:
    """Create controls and execute each through the caller's pinned native stage.

    `frontend_runner` invokes the frozen NORMAL/readonly exporters, decoders,
    refinement, and nine-body service. `stage_runner` is the existing Cloud
    `cap.LINK.stage` adapter wrapped by the main driver. Tests inject only
    synthetic service results.
    """
    env = dict(os.environ if env is None else env)
    _validate_route(env, repo, build_id)
    provider_record = _validate_provider_record(provider_record, build_id)
    _need(isinstance(tool_spec, bytes), "exact pinned lib.rsspec bytes required")
    _need(tool_home.is_absolute() and tool_home.is_dir() and not tool_home.is_symlink(),
          "exact current native tool home required")
    tool_binary = tool_home / "bin/verifast"
    tool_spec_path = tool_home / TOOL_SPEC_RELATIVE
    _need(tool_binary.is_file() and not tool_binary.is_symlink() and
          tool_spec_path.is_file() and not tool_spec_path.is_symlink() and
          tool_spec_path.read_bytes() == tool_spec,
          "current native binary/tool-spec files differ from supplied pins")
    _need(evidence.is_absolute() and evidence.is_dir() and not evidence.is_symlink(),
          "absolute fresh evidence directory required")
    _need(positive_case.is_dir() and not positive_case.is_symlink(),
          "fresh pinned positive source fixture required")
    _need(positive_case.resolve() ==
          (evidence / "cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut").resolve(),
          "positive source pair must come from the current R24 mutable source capture")
    pins = _load_capture_pins(repo)
    _need(isinstance(source_record, dict) and
          source_record.get("classification") ==
          "SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE" and
          source_record.get("original_sha256") == POSITIVE_ORIGINAL_SHA256 and
          source_record.get("verified_sha256") == POSITIVE_VERIFIED_SHA256 and
          source_record.get("specialization") ==
          "T = *mut Element; Element unrestricted" and
          source_record.get("source_order") and
          source_record.get("ghost_strip_identity") is True and
          source_record.get("typed_mir_binding_established") is False and
          source_record.get("helper_proof_status") == "NOT_RUN" and
          source_record.get("publication_status") == "NOT_PUBLISHED" and
          source_record.get("proof_credit") == 0,
          "source-only positive nine-body record differs or overstates admission")
    positive_pair = _source_pair_hashes(positive_case)
    _need(positive_pair == {
        "original/lib.rs": POSITIVE_ORIGINAL_SHA256,
        "verified/lib.rs": POSITIVE_VERIFIED_SHA256,
    }, "positive source fixture differs from exact capture pins")
    positive_original = (positive_case / "original/lib.rs").read_bytes()
    positive_verified = (positive_case / "verified/lib.rs").read_bytes()
    _need(callable(getattr(owner, "strip_ghost", None)) and
          owner.strip_ghost(positive_verified) == positive_original,
          "positive source fixture ghost-strip identity differs")
    requested = tuple(source_controls) + tuple(context_controls)
    _need(requested and len(set(requested)) == len(requested) and
          set(requested) <= set(ALL_CONTROLS), "closed refusal-control inventory differs")
    summary_path = evidence / SUMMARY_RELATIVE
    _need(not summary_path.exists() and not summary_path.is_symlink(),
          "fresh mutable refusal summary required")
    root = evidence / SUMMARY_RELATIVE.parent / "variants"
    _need(not root.exists() and not root.is_symlink(),
          "fresh mutable refusal evidence directory required")
    root.mkdir(parents=True)
    summary: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": "INCOMPLETE_SOURCE_ENVELOPE_REFUSALS",
        "scope": "SOURCE_ENVELOPE_REFUSALS_ONLY; NO INTERNAL-PREDICATE CLAIM",
        "native_build_id": build_id,
        "provider_record": copy.deepcopy(provider_record),
        "r24_session_phase_id": env.get(R24_PHASE_ENV),
        "r21_route_phase_id": env.get(R21_PHASE_ENV),
        "provider": env.get("SMALLSORT_EXECUTION_PROVIDER"),
        "lane": env.get("LANE"), "profile": env.get(PROFILE_ENV),
        "tool_spec_sha256": _sha(tool_spec),
        "positive_source_hashes": positive_pair,
        "positive_source_record": copy.deepcopy(source_record),
        "capture_pins_sha256": CAPTURE_PINS_SHA256,
        "requested_controls": list(requested), "controls": {},
        "artifact_inventory": [], "complete": False,
        "accepted": False, "publication_allowed": False, "proof_credit": 0,
    }
    primary_error: BaseException | None = None
    primary_traceback = None
    for control in requested:
        case = root / control
        stage_name = "r24-mut-refusal-" + control
        row: dict[str, Any] = {
            "control": control,
            "case_path": case.relative_to(evidence).as_posix(),
            "mutation": control if control in SOURCE_CONTROLS else None,
            "expected_gate": EXPECTED_REFUSALS[control],
            "child_environment_delta": _child_environment_delta(control, repo),
            "source_before": None,
            "source_after": None,
            "source_unchanged": False,
            "ghost_strip_identity": False,
            "stage_name": stage_name,
            "stage": None,
            "frontend_capture": None,
            "diagnostic": None,
            "classification": "UNKNOWN_UNCLASSIFIED",
            "errors": [],
            "accepted": False, "publication_allowed": False, "proof_credit": 0,
        }
        summary["controls"][control] = row
        try:
            case.mkdir()
            if control in SOURCE_CONTROLS:
                verified = mutate_verified_source(control, positive_verified)
                original = owner.strip_ghost(verified)
                _need(isinstance(original, bytes) and owner.strip_ghost(verified) == original,
                      control + ": mutated source pair fails ghost-strip identity")
            else:
                original, verified = positive_original, positive_verified
            (case / "original").mkdir()
            (case / "verified").mkdir()
            (case / "original/lib.rs").write_bytes(original)
            (case / "verified/lib.rs").write_bytes(verified)
            before = _source_pair_hashes(case)
            row["source_before"] = before
            row["ghost_strip_identity"] = owner.strip_ghost(verified) == original
            delta = row["child_environment_delta"]
            case_record = copy.deepcopy(source_record)
            case_record["original_sha256"] = before["original/lib.rs"]
            case_record["verified_sha256"] = before["verified/lib.rs"]
            case_record["ghost_strip_identity"] = True
            frontend = frontend_runner(case=case, source_record=case_record)
            row["frontend_capture"] = frontend
            if not isinstance(frontend, dict) or frontend.get("errors") != []:
                row["errors"].extend(
                    frontend.get("errors", ["NORMAL/readonly frontend capture incomplete"])
                    if isinstance(frontend, dict) else
                    ["NORMAL/readonly frontend capture result is malformed"])
                row["source_after"] = _source_pair_hashes(case)
                row["source_unchanged"] = before == row["source_after"]
                continue
            with _temporary_environment(delta):
                stage = stage_runner(case=case, variant=control, name=stage_name,
                                     build_id=build_id, child_environment_delta=delta)
            row["stage"] = stage
            after = _source_pair_hashes(case)
            row["source_after"] = after
            row["source_unchanged"] = before == after
            row["errors"].extend(_stage_errors(
                stage, case, stage_name, before, after, tool_home, build_id))
            if isinstance(stage, dict):
                raw, text, log_relative = _read_log(case, stage, stage_name)
                row["log"] = {"path": log_relative, "bytes": len(raw),
                              "sha256": _sha(raw)}
                matched, gate, reason = _classify_log(control, text)
                row["diagnostic"] = {"text": text.strip(), "gate": gate,
                                     "matches_expected_refusal": matched}
                if not matched:
                    row["errors"].append(reason)
                if row["errors"]:
                    row["classification"] = "UNKNOWN_UNCLASSIFIED"
                else:
                    row["classification"] = "NATIVE_SOURCE_ENVELOPE_REFUSAL_SOURCE_REPORTED"
            else:
                row["errors"].append("native stage result unavailable")
        except BaseException as exc:
            row["errors"].append("control collection exception: " + type(exc).__name__)
            row["exception"] = {"type": type(exc).__name__, "message": str(exc)}
            try:
                row["source_after"] = _source_pair_hashes(case)
                row["source_unchanged"] = row["source_before"] == row["source_after"]
            except BaseException as source_exc:
                row["errors"].append("source reread failed: " + type(source_exc).__name__)
            primary_error = exc
            primary_traceback = exc.__traceback__
            break

    inventory = []
    try:
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                summary.setdefault("errors", []).append(
                    "refusal artifact symlink: " + path.relative_to(evidence).as_posix())
                continue
            if path.is_file():
                data = path.read_bytes()
                inventory.append({"path": path.relative_to(evidence).as_posix(),
                                  "bytes": len(data), "sha256": _sha(data)})
    except BaseException as exc:
        summary["artifact_inventory_error"] = {
            "type": type(exc).__name__, "message": str(exc)}
        summary.setdefault("errors", []).append(
            "refusal artifact inventory failed: " + type(exc).__name__)
        if primary_error is None:
            primary_error = exc
            primary_traceback = exc.__traceback__
    summary["artifact_inventory"] = inventory
    summary["complete"] = (
        set(summary["controls"]) == set(requested) and
        all(row["classification"] == "NATIVE_SOURCE_ENVELOPE_REFUSAL_SOURCE_REPORTED"
            and row["source_unchanged"] is True and row["ghost_strip_identity"] is True
            and isinstance(row.get("frontend_capture"), dict)
            and row["frontend_capture"].get("errors") == []
            for row in summary["controls"].values()) and
        len(inventory) == sum(1 for path in root.rglob("*") if path.is_file()) and
        not summary.get("errors") and primary_error is None
    )
    summary["classification"] = (
        "COMPLETE_SOURCE_REPORTED_REFUSAL_COLLECTOR_NO_PROOF_CREDIT"
        if summary["complete"] else "INCOMPLETE_SOURCE_ENVELOPE_REFUSALS")
    summary["accepted"] = False
    summary["publication_allowed"] = False
    summary["proof_credit"] = 0
    try:
        _write_summary(evidence / SUMMARY_RELATIVE, summary)
    except BaseException:
        if primary_error is None:
            raise
    if primary_error is not None:
        raise primary_error.with_traceback(primary_traceback)
    return summary


def audit_controls(*, evidence: Path, positive_case: Path, repo: Path,
                   owner: object, capture: object,
                   capture_errors: Callable[..., list[str]], tool_home: Path,
                   tool_spec: bytes, build_id: str,
                   provider_record: dict[str, Any],
                   env: dict[str, str] | None = None) -> dict[str, Any]:
    """Reopen and revalidate physical source/frontend/native refusal evidence."""
    env = dict(os.environ if env is None else env)
    errors: list[str] = []
    try:
        _validate_route(env, repo, build_id)
        provider_record = _validate_provider_record(provider_record, build_id)
        summary_path = evidence / SUMMARY_RELATIVE
        _need(summary_path.is_file() and not summary_path.is_symlink(),
              "physical mutable refusal summary missing or symlinked")
        raw_summary = summary_path.read_bytes()
        try:
            summary = json.loads(raw_summary.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise RefusalError("R24-MUT-REFUSALS: summary JSON is malformed") from exc
        _need(isinstance(summary, dict) and summary.get("schema") == SCHEMA and
              summary.get("requested_controls") == list(ALL_CONTROLS) and
              summary.get("native_build_id") == build_id and
              summary.get("provider_record") == provider_record and
              summary.get("r24_session_phase_id") == env.get(R24_PHASE_ENV) == R24_PHASE and
              summary.get("r21_route_phase_id") == env.get(R21_PHASE_ENV) == R21_PHASE and
              summary.get("provider") == "cloud-build" and summary.get("lane") == LANE and
              summary.get("profile") == PROFILE and
              summary.get("tool_spec_sha256") == _sha(tool_spec) and
              summary.get("capture_pins_sha256") == CAPTURE_PINS_SHA256 and
              summary.get("accepted") is False and
              summary.get("publication_allowed") is False and
              type(summary.get("proof_credit")) is int and summary.get("proof_credit") == 0,
              "refusal summary route, schema, or proof boundary differs")
        _need(positive_case.is_dir() and not positive_case.is_symlink() and
              positive_case.resolve() ==
              (evidence / "cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut").resolve(),
              "positive source fixture path differs")
        positive_pair = _source_pair_hashes(positive_case)
        _need(positive_pair == {
            "original/lib.rs": POSITIVE_ORIGINAL_SHA256,
            "verified/lib.rs": POSITIVE_VERIFIED_SHA256,
        } and summary.get("positive_source_hashes") == positive_pair,
              "positive mutable source pins differ during audit")
        positive_record = summary.get("positive_source_record")
        _need(isinstance(positive_record, dict) and
              positive_record.get("classification") ==
              "SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE" and
              positive_record.get("original_sha256") == POSITIVE_ORIGINAL_SHA256 and
              positive_record.get("verified_sha256") == POSITIVE_VERIFIED_SHA256 and
              positive_record.get("specialization") ==
              "T = *mut Element; Element unrestricted" and
              positive_record.get("ghost_strip_identity") is True and
              positive_record.get("typed_mir_binding_established") is False and
              positive_record.get("helper_proof_status") == "NOT_RUN" and
              positive_record.get("publication_status") == "NOT_PUBLISHED" and
              positive_record.get("proof_credit") == 0,
              "positive source-record status differs during audit")
        positive_original = (positive_case / "original/lib.rs").read_bytes()
        positive_verified = (positive_case / "verified/lib.rs").read_bytes()
        _need(owner.strip_ghost(positive_verified) == positive_original,
              "positive source ghost-strip identity differs during audit")
        root = evidence / SUMMARY_RELATIVE.parent / "variants"
        controls = summary.get("controls")
        _need(root.is_dir() and not root.is_symlink() and isinstance(controls, dict) and
              set(controls) == set(ALL_CONTROLS),
              "physical refusal control directory or exact control order differs")
        for control in ALL_CONTROLS:
            row = controls[control]
            expected_case = root / control
            try:
                _need(isinstance(row, dict) and row.get("control") == control and
                      row.get("case_path") == expected_case.relative_to(evidence).as_posix() and
                      expected_case.is_dir() and not expected_case.is_symlink(),
                      "control row or physical case path differs: " + control)
                actual_pair = _source_pair_hashes(expected_case)
                expected_verified = (
                    mutate_verified_source(control, positive_verified)
                    if control in SOURCE_CONTROLS else positive_verified)
                expected_original = owner.strip_ghost(expected_verified)
                actual_original = (expected_case / "original/lib.rs").read_bytes()
                actual_verified = (expected_case / "verified/lib.rs").read_bytes()
                _need(actual_original == expected_original and
                      actual_verified == expected_verified,
                      "physical source bytes do not reproduce the pinned control: " + control)
                _need(row.get("source_before") == actual_pair and
                      row.get("source_after") == actual_pair and
                      row.get("source_unchanged") is True and
                      owner.strip_ghost(actual_verified) == actual_original and
                      row.get("ghost_strip_identity") is True,
                      "control physical source bytes/ghost-strip identity differ: " + control)
                _need(row.get("child_environment_delta") ==
                      _child_environment_delta(control, repo) and
                      row.get("expected_gate") == EXPECTED_REFUSALS[control],
                      "control child selector or expected gate differs: " + control)
                frontend = row.get("frontend_capture")
                _need(isinstance(frontend, dict) and frontend.get("errors") == [] and
                      isinstance(frontend.get("source_record"), dict),
                      "frontend capture is incomplete: " + control)
                frontend_record = frontend["source_record"]
                _need(frontend_record.get("original_sha256") == actual_pair["original/lib.rs"] and
                      frontend_record.get("verified_sha256") == actual_pair["verified/lib.rs"],
                      "frontend source record differs from current bytes: " + control)
                frontend_errors = capture_errors(
                    capture, frontend_record, expected_case,
                    frontend.get("guard_capture"), frontend.get("full_body_capture"),
                    None, require_fingerprint=False)
                _need(frontend_errors == [],
                      "frontend NORMAL/readonly capture no longer validates: " + control)
                stage = row.get("stage")
                stage_name = "r24-mut-refusal-" + control
                stage_errors = _stage_errors(stage, expected_case, stage_name,
                                             actual_pair, actual_pair,
                                             tool_home, build_id)
                _need(stage_errors == [],
                      "native refusal stage no longer validates: " + control)
                raw_log, text, relative_log = _read_log(expected_case, stage, stage_name)
                _need(row.get("log") == {"path": relative_log, "bytes": len(raw_log),
                                          "sha256": _sha(raw_log)},
                      "physical native refusal log inventory differs: " + control)
                matched, gate, _reason = _classify_log(control, text)
                _need(matched and gate == EXPECTED_REFUSALS[control] and
                      row.get("diagnostic", {}).get("matches_expected_refusal") is True and
                      row.get("diagnostic", {}).get("gate") == gate,
                      "native refusal diagnostic differs: " + control)
            except BaseException as exc:
                errors.append(control + ": " + type(exc).__name__ + ": " + str(exc))
        inventory = []
        for path in sorted(root.rglob("*")):
            _need(not path.is_symlink(),
                  "refusal artifact symlink during audit: " + path.relative_to(evidence).as_posix())
            if path.is_file():
                data = path.read_bytes()
                inventory.append({"path": path.relative_to(evidence).as_posix(),
                                  "bytes": len(data), "sha256": _sha(data)})
        _need(summary.get("artifact_inventory") == inventory,
              "physical refusal artifact inventory differs")
    except BaseException as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
        summary = {} if "summary" not in locals() else summary
    complete = (not errors and summary.get("complete") is True and
                summary.get("classification") ==
                "COMPLETE_SOURCE_REPORTED_REFUSAL_COLLECTOR_NO_PROOF_CREDIT")
    return {
        "schema": "select-r24-mut-refusal-audit-v1",
        "complete": complete,
        "classification": ("COMPLETE_SOURCE_REPORTED_REFUSALS_NO_PROOF_CREDIT"
                           if complete else "INCOMPLETE_SOURCE_ENVELOPE_REFUSALS"),
        "controls_checked": list(ALL_CONTROLS),
        "errors": errors,
        "accepted": False, "publication_allowed": False, "proof_credit": 0,
    }
