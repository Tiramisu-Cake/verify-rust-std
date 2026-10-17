"""Pure fail-closed A1 workflow admission checks.

The service validates runner-reported records; it is not a proof checker and
cannot authenticate their truth. Its state is a workflow signal only, never
independent verifier proof credit.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


class AdmissionError(ValueError):
    """A record is missing, inconsistent, stale, or fails its intended gate."""


# Expected stage / predicate / location / outcome / classification. These
# names follow selected-proof.CONTROLS and driver.classify. Case source and unit
# identities are deliberately supplied separately by the exact matrix manifest.
MATRIX: dict[str, tuple[str, str, str, str, str]] = {
    "OFF": ("frontend", "duplicate-trait-parameter", "trait declaration", "baseline", "BASELINE_ONLY"),
    "P0a": ("impl-body-and-conformance", "16<=result<=32", "default threshold body", "pass", "NATIVE_INTENDED_PASS"),
    "P0b": ("impl-body-and-conformance", "16<=result<=32", "Freeze threshold body", "pass", "NATIVE_INTENDED_PASS"),
    "P0c": ("caller-proof", "len<=32-and-len+16<=48", "guard observer assertions", "pass", "POSITIVE_INTENDED"),
    "P-dispatch": ("translated-call-gate", "original-common-trait-item", "threshold/small_sort call AST", "pass", "POSITIVE_INTENDED"),
    "P1": ("export-decode-refinement", "full-interface-shape", "small_sort interface", "pass", "POSITIVE_INTENDED"),
    "N-binder-collapse": ("identity-validation", "distinct-input-binder-identities", "synthetic required-fn input", "refuse", "NEGATIVE_INTENDED"),
    "N-alpha-valid": ("identity-validation", "consistent-bijective-region-renaming", "synthetic required-fn input", "accept-representation", "REPRESENTATION_ONLY"),
    "N-free-region": ("well-scopedness", "all-regions-in-scope", "synthetic input type", "refuse", "NEGATIVE_INTENDED"),
    "N-region-swap": ("call-binding-admission", "compiler-input-region-map", "generic trait call binding", "refuse", "NEGATIVE_INTENDED"),
    "N-no-F": ("generic-scope-validation", "method-F-present-and-constrained", "synthetic trait declaration", "refuse", "NEGATIVE_INTENDED"),
    "N-clauses": ("interface-admission", "full-HRTB-FnMut-Output-bool-clauses", "trait interface certificate", "refuse", "NEGATIVE_INTENDED"),
    "N-default-contract": ("impl-body-post", "result<=32", "mutated default threshold body", "fail", "NEGATIVE_INTENDED"),
    "N-freeze-contract": ("impl-body-post", "result<=32", "mutated Freeze threshold body", "fail", "NEGATIVE_INTENDED"),
    "N-false31": ("caller-assertion", "len<=31", "guard observer assertion", "fail", "NEGATIVE_INTENDED"),
    "N-source": ("source-admission", "exact-source-and-item-identity", "source certificate", "refuse", "NEGATIVE_INTENDED"),
    "N-binding": ("call-binding-admission", "original-generic-trait-binding", "translated trait call", "refuse", "NEGATIVE_INTENDED"),
    "N-clause-redirect": ("translated-call-gate", "no-clause-ignoring-impl-redirect", "dispatch trace and call AST", "refuse", "NEGATIVE_INTENDED"),
    "N-duplicate": ("inventory-admission", "exact-closed-impl-item-inventory", "compiler impl inventory", "refuse", "NEGATIVE_INTENDED"),
    "R1": ("NONE_OBSERVED", "full normal/unwind/free/leak/dead-code obligations", "canonical_slice_as_mut_ptr", "pass", "POSITIVE_INTENDED"),
    "R2": ("NONE_OBSERVED", "full normal/unwind/free/leak/dead-code obligations", "canonical_slice_as_mut_ptr_mu", "pass", "POSITIVE_INTENDED"),
    "R3": ("NONE_OBSERVED", "full normal/unwind/free/leak/dead-code obligations", "native_slice_pointer_consumer", "pass", "POSITIVE_INTENDED"),
    "R4": ("verification", "v_base != source_base", "native_slice_pointer_consumer assertion", "fail", "NEGATIVE_INTENDED"),
    "R5": ("verification", "unrelated[..1] |-> ?unrelated_values", "native_slice_pointer_consumer assertion", "fail", "NEGATIVE_INTENDED"),
    "R6": ("verification", "scratch_base[..1] |-> ?initialized_values", "native_slice_pointer_consumer assertion", "fail", "NEGATIVE_INTENDED"),
    "R7": ("NONE_OBSERVED", "full normal/unwind/free/leak/dead-code obligations", "selected_threshold_body", "pass", "POSITIVE_INTENDED"),
}
MATRIX_CASES = frozenset(MATRIX)
IMPL_IDS = frozenset({"default16", "freeze32"})
THRESHOLD_BODY_CASES = frozenset({"P0a", "P0b", "N-default-contract", "N-freeze-contract"})
CALLER_BODY_CASES = frozenset({"P0c", "N-false31"})
INTERFACE_ONLY_CASES = frozenset({
    "P-dispatch", "P1", "N-binder-collapse", "N-alpha-valid", "N-free-region",
    "N-region-swap", "N-no-F", "N-clauses", "N-source", "N-binding",
    "N-clause-redirect", "N-duplicate",
})
CALLER_FOCUS_TARGET = "a1_guard_observer"
INTERFACE_FOCUS_TARGET = "verified/lib.rs:0"
RUN_PIN_FIELDS = ("tool_id", "profile_id", "proof_id", "infra_id", "target_id")
CASE_IDENTITY_FIELDS = ("source_id", "unit_id")
CLASSIFICATIONS = frozenset({
    "BASELINE_ONLY", "NATIVE_INTENDED_PASS", "POSITIVE_INTENDED",
    "NEGATIVE_INTENDED", "REPRESENTATION_ONLY",
})


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def _nonempty_string(value: Any, label: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"missing {label}")
    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return deepcopy(value)


def _pins(record: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(_nonempty_string(record.get(key), key) for key in RUN_PIN_FIELDS)


def _check_executed(record: Mapping[str, Any], label: str, *, expected_mode: str = "none") -> None:
    _require(record.get("skipped") is False, f"{label} skipped or skip status missing")
    mode = record.get("focus_mode")
    _require(mode == expected_mode, f"{label} focus mode mismatch")
    _require(record.get("focus_only") is (expected_mode != "none"),
             f"{label} focus-only status mismatch")


def _focus_impl_for_case(case_id: str) -> str:
    if case_id in ("P0a", "N-default-contract"):
        return "default16"
    if case_id in ("P0b", "N-freeze-contract"):
        return "freeze32"
    raise AdmissionError(f"{case_id} is not a threshold-body case")


def _case_execution(case_id: str, row: Mapping[str, Any], expected: Mapping[str, Any],
                    inventory: Mapping[str, Mapping[str, str]]) -> None:
    if case_id in THRESHOLD_BODY_CASES:
        _check_executed(row, f"case {case_id}", expected_mode="actual-body-and-conformance")
        impl = _focus_impl_for_case(case_id)
        target = inventory[impl]["compiler_item_id"]
        _require(expected.get("focused_item_id") == target,
                 f"manifest focus item for {case_id} is not bound to expected inventory")
        _require(row.get("focused_item_id") == target,
                 f"case {case_id} focus target does not match expected compiler item")
        _require(row.get("body_count") == 1,
                 f"case {case_id} must execute exactly its focused body")
        _require(row.get("proof_kind") == "actual_body",
                 f"case {case_id} actual body attestation required")
        compiler = row.get("compiler_identity")
        _require(isinstance(compiler, Mapping) and compiler.get("impl") == impl and
                 compiler.get("compiler_item_id") == target and
                 compiler.get("compiler_impl_id") == inventory[impl]["compiler_impl_id"],
                 f"case {case_id} compiler identity is not the exact expected item")
        expected_failure = case_id in ("N-default-contract", "N-freeze-contract")
        body = row.get("body")
        envelope = row.get("native_envelope")
        _require(isinstance(body, Mapping) and isinstance(envelope, Mapping),
                 f"case {case_id} body and native conformance attestations required")
        if expected_failure:
            location = "mutated default threshold body" if impl == "default16" else "mutated Freeze threshold body"
            _require(body.get("stage") == "impl-body-post" and
                     body.get("predicate") == "result<=32" and
                     body.get("location") == location and body.get("outcome") == "fail" and
                     body.get("classification") == "runner-reported-intended-negative" and
                     body.get("target_reached") is True and
                     body.get("failure_observed") is True and
                     body.get("verified") is False,
                     f"case {case_id} body failure was not observed at the intended post")
            _require(envelope.get("stage") == "native-envelope-conformance" and
                     envelope.get("predicate") == "normal+unwind-posts-preserved" and
                     envelope.get("location") == location and envelope.get("outcome") == "pass" and
                     envelope.get("classification") == "runner-reported-conformance-preserved" and
                     envelope.get("normal_posts_preserved") is True and
                     envelope.get("unwind_posts_preserved") is True,
                     f"case {case_id} native envelope was not independently preserved")
            _require(row.get("focus_body_reached") is True and
                     row.get("focus_body_verified") is False and
                     row.get("focus_conformance_verified") is True,
                     f"case {case_id} negative body must be reached, unproved, with envelope preserved")
        else:
            location = f"{impl} threshold item"
            _require(body.get("stage") == "impl-body" and
                     body.get("predicate") == "16<=result<=32" and
                     body.get("location") == location and body.get("outcome") == "pass" and
                     body.get("classification") == "runner-reported-body-pass",
                     f"case {case_id} body gate mismatch")
            _require(envelope.get("stage") == "native-envelope-conformance" and
                     envelope.get("predicate") == "16<=result<=32" and
                     envelope.get("location") == location and envelope.get("outcome") == "pass" and
                     envelope.get("classification") == "runner-reported-conformance-pass",
                     f"case {case_id} native conformance gate mismatch")
            _require(row.get("focus_body_reached") is True and
                     row.get("focus_body_verified") is True and
                     row.get("focus_conformance_verified") is True,
                     f"case {case_id} focused body and conformance were not both observed")
        return

    if case_id in CALLER_BODY_CASES:
        _check_executed(row, f"case {case_id}", expected_mode="caller-body")
        _require(row.get("focus_target") == CALLER_FOCUS_TARGET,
                 f"case {case_id} focus target must be the exact source observer")
        _require(row.get("body_count") == 1,
                 f"case {case_id} caller body was not executed")
        if case_id == "P0c":
            _require(row.get("caller_body_reached") is True and
                     row.get("caller_body_verified") is True and
                     row.get("assertions_reached") == ["len<=32", "requirement<=48"],
                     "P0c observer assertions were not both reached")
        else:
            _require(row.get("caller_body_reached") is True and
                     row.get("caller_body_verified") is False and
                     row.get("reached_predicate") == "len<=31" and
                     row.get("assertion_failure_observed") is True,
                     "N-false31 did not fail at its intended assertion")
        return

    if case_id in INTERFACE_ONLY_CASES:
        _check_executed(row, f"case {case_id}", expected_mode="interface-only")
        _require(row.get("focus_target") == INTERFACE_FOCUS_TARGET,
                 f"case {case_id} must focus the verified interface with zero bodies")
        _require(row.get("body_count") == 0 and row.get("interface_verified") is True,
                 f"case {case_id} interface-only run executed a body or omitted structural check")
        _require(row.get("case_credit") == expected["classification"] and
                 row.get("proof_credit") is False,
                 f"case {case_id} interface case credit must not claim proof credit")
        for forbidden in ("impl", "compiler_identity", "proof_kind", "body", "native_envelope"):
            _require(forbidden not in row, f"case {case_id} interface-only row published {forbidden}")
        return

    _check_executed(row, f"case {case_id}", expected_mode="none")


def validate_inventory(inventory: Any, expected: Mapping[str, Mapping[str, str]]) -> None:
    """Require the exact closed inventory and distinct compiler identities."""
    _require(isinstance(inventory, (list, tuple)), "inventory must be a list")
    _require(set(expected) == IMPL_IDS, "expected inventory must name default16 and freeze32")
    seen_impl: set[str] = set()
    seen_items: set[str] = set()
    seen_compiler_ids: set[str] = set()
    for row in inventory:
        _require(isinstance(row, Mapping), "inventory row must be an object")
        impl = _nonempty_string(row.get("impl"), "inventory impl")
        compiler_id = _nonempty_string(row.get("compiler_impl_id"), "compiler impl identity")
        item_id = _nonempty_string(row.get("compiler_item_id"), "compiler item identity")
        _require(impl in IMPL_IDS, f"unexpected impl {impl}")
        _require(impl not in seen_impl, f"duplicate impl {impl}")
        _require(item_id not in seen_items, f"duplicate compiler item identity {item_id}")
        _require(compiler_id not in seen_compiler_ids, f"duplicate compiler impl identity {compiler_id}")
        _require(expected[impl].get("compiler_impl_id") == compiler_id,
                 f"compiler impl identity mismatch for {impl}")
        _require(expected[impl].get("compiler_item_id") == item_id,
                 f"compiler item identity mismatch for {impl}")
        seen_impl.add(impl)
        seen_items.add(item_id)
        seen_compiler_ids.add(compiler_id)
    _require(seen_impl == IMPL_IDS, "inventory is not the exact closed impl set")


def _validate_case(case_id: str, row: Mapping[str, Any], expected: Mapping[str, Any],
                   pins: tuple[str, ...], build_id: str,
                   inventory: Mapping[str, Mapping[str, str]]) -> None:
    _require(case_id in MATRIX, f"unexpected matrix case {case_id}")
    _require(row.get("case_id") == case_id, f"case id mismatch for {case_id}")
    _require(_pins(row) == pins, f"case {case_id} has stale/mismatched run pins")
    _require(row.get("source_id") == expected["source_id"],
             f"case {case_id} source identity mismatch")
    _require(row.get("unit_id") == expected["unit_id"], f"case {case_id} unit identity mismatch")
    for key in ("stage", "predicate", "location", "outcome", "classification"):
        _require(row.get(key) == expected[key], f"case {case_id} {key} mismatch")
    _require(expected["classification"] in CLASSIFICATIONS,
             f"case {case_id} classification is not an accepted exact class")
    _require(row.get("build_id") == build_id, f"case {case_id} build mismatch")
    _require(row.get("record_kind") == "runner_attestation",
             f"case {case_id} is not a runner attestation")
    _require(row.get("proof_credit") is not True,
             f"case {case_id} runner attestation cannot claim independent proof credit")
    _case_execution(case_id, row, expected, inventory)


def _validate_expected_cases(expected_cases: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    _require(set(expected_cases) == MATRIX_CASES,
             "expected matrix manifest must bind the exact complete case set")
    checked = {}
    for case_id, expected in expected_cases.items():
        _require(isinstance(expected, Mapping), f"expected case {case_id} must be an object")
        _require(case_id in MATRIX, f"unexpected expected case {case_id}")
        _nonempty_string(expected.get("source_id"), f"{case_id} expected source_id")
        _nonempty_string(expected.get("unit_id"), f"{case_id} expected unit_id")
        for key, value in zip(("stage", "predicate", "location", "outcome", "classification"), MATRIX[case_id]):
            _require(expected.get(key) == value, f"manifest expectation mismatch for {case_id} {key}")
        checked[case_id] = _freeze(dict(expected))
    return checked


@dataclass(frozen=True)
class A1Admission:
    """Accumulate validated source-reported gates without mutating accepted data."""

    expected_inventory: Mapping[str, Mapping[str, str]]
    expected_run_pins: Mapping[str, str]
    expected_impl_inputs: Mapping[str, Mapping[str, str]]
    expected_cases: Mapping[str, Mapping[str, Any]]
    _implementations: dict[str, Mapping[str, Any]] = field(default_factory=dict, init=False, repr=False)
    _matrix_records: dict[str, Mapping[str, Any]] = field(default_factory=dict, init=False, repr=False)
    _run_pins: tuple[str, ...] | None = field(default=None, init=False, repr=False)
    _build_id: str | None = field(default=None, init=False, repr=False)
    build_terminal_success: bool = field(default=False, init=False)
    collector_success: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        frozen_inventory = _freeze(self.expected_inventory)
        frozen_impl_inputs = _freeze(self.expected_impl_inputs)
        frozen_pins = _freeze(self.expected_run_pins)
        _require(set(frozen_inventory) == IMPL_IDS, "expected inventory must name both impls")
        _require(set(frozen_impl_inputs) == IMPL_IDS, "expected impl inputs must name both impls")
        _require(set(frozen_pins) == set(RUN_PIN_FIELDS), "run pins must include exact tool/profile/proof/infra/target")
        for key, value in frozen_pins.items():
            _nonempty_string(value, f"expected {key}")
        validate_inventory(
            [{"impl": impl, **dict(ids)} for impl, ids in frozen_inventory.items()], frozen_inventory)
        for impl in IMPL_IDS:
            _nonempty_string(frozen_impl_inputs[impl].get("source_id"), f"{impl} source_id")
            _nonempty_string(frozen_impl_inputs[impl].get("unit_id"), f"{impl} unit_id")
        frozen_cases = _validate_expected_cases(self.expected_cases)
        baseline_source = frozen_impl_inputs["default16"]["source_id"]
        _require(frozen_impl_inputs["freeze32"]["source_id"] == baseline_source,
                 "both actual impl proofs must use the same certified source pair")
        for case_id, impl in (("P0a", "default16"), ("P0b", "freeze32")):
            _require(all(frozen_cases[case_id][key] == frozen_impl_inputs[impl][key]
                         for key in CASE_IDENTITY_FIELDS),
                     f"{case_id} must bind the actual {impl} proof input")
        for case_id in THRESHOLD_BODY_CASES:
            impl = _focus_impl_for_case(case_id)
            _require(frozen_cases[case_id].get("focused_item_id") ==
                     frozen_inventory[impl].get("compiler_item_id"),
                     f"{case_id} focused item must bind to expected compiler inventory")
        for case_id in ("P0c", "P-dispatch", "P1"):
            _require(frozen_cases[case_id]["source_id"] == baseline_source,
                     f"{case_id} must use the certified positive source pair")
        object.__setattr__(self, "expected_inventory", frozen_inventory)
        object.__setattr__(self, "expected_impl_inputs", frozen_impl_inputs)
        object.__setattr__(self, "expected_run_pins", frozen_pins)
        object.__setattr__(self, "expected_cases", MappingProxyType(frozen_cases))

    @property
    def implementations(self) -> Mapping[str, Mapping[str, Any]]:
        return MappingProxyType(dict(self._implementations))

    @property
    def matrix_records(self) -> Mapping[str, Mapping[str, Any]]:
        return MappingProxyType(dict(self._matrix_records))

    def _candidate_run(self, record: Mapping[str, Any]) -> tuple[tuple[str, ...], str]:
        pins = _pins(record)
        expected = tuple(self.expected_run_pins[key] for key in RUN_PIN_FIELDS)
        _require(pins == expected, "record run pins do not match the pinned A1 run")
        build_id = _nonempty_string(record.get("build_id"), "build_id")
        if self._run_pins is not None:
            _require(self._run_pins == pins, "stale or mismatched run pins")
            _require(self._build_id == build_id, "mixed build ids")
        return pins, build_id

    def _commit_run(self, candidate: tuple[tuple[str, ...], str]) -> None:
        if self._run_pins is None:
            object.__setattr__(self, "_run_pins", candidate[0])
            object.__setattr__(self, "_build_id", candidate[1])

    def record_implementation(self, record: Mapping[str, Any]) -> None:
        """Record actual body plus generated native-envelope conformance gates."""
        _require(isinstance(record, Mapping), "implementation record must be an object")
        candidate_run = self._candidate_run(record)
        impl = _nonempty_string(record.get("impl"), "impl")
        _require(impl in IMPL_IDS, f"unexpected impl {impl}")
        _require(impl not in self._implementations, f"duplicate implementation record {impl}")
        _require(record.get("record_kind") == "runner_attestation", "not a runner attestation")
        _require(record.get("proof_credit") is not True,
                 "runner attestation cannot claim independent proof credit")
        _require(record.get("proof_kind") == "actual_body", "actual body proof required")
        _check_executed(record, f"{impl} implementation",
                        expected_mode="actual-body-and-conformance")
        validate_inventory(record.get("inventory"), self.expected_inventory)
        expected_input = self.expected_impl_inputs[impl]
        _require(record.get("source_id") == expected_input["source_id"],
                 f"{impl} source identity mismatch")
        _require(record.get("unit_id") == expected_input["unit_id"], f"{impl} unit identity mismatch")
        row = record.get("compiler_identity")
        _require(isinstance(row, Mapping), "compiler_identity required")
        _require(row.get("impl") == impl, "compiler identity impl mismatch")
        _require(row.get("compiler_item_id") == self.expected_inventory[impl].get("compiler_item_id"),
                 "compiler item mismatch")
        _require(row.get("compiler_impl_id") == self.expected_inventory[impl].get("compiler_impl_id"),
                 "compiler impl mismatch")
        _require(record.get("focused_item_id") == row.get("compiler_item_id"),
                 "focus target does not match actual compiler item")
        _require(record.get("body_count") == 1, "actual impl run must execute exactly one body")
        _require(record.get("focus_body_verified") is True,
                 "focused actual body was not verified")
        _require(record.get("focus_conformance_verified") is True,
                 "focused native conformance was not verified")
        for gate_name in ("body", "native_envelope"):
            gate = record.get(gate_name)
            _require(isinstance(gate, Mapping), f"{gate_name} gate required")
            _require(gate.get("stage") == ("impl-body" if gate_name == "body" else "native-envelope-conformance"),
                     f"{gate_name} stage mismatch")
            _require(gate.get("predicate") == "16<=result<=32", f"{gate_name} predicate mismatch")
            _require(gate.get("location") == f"{impl} threshold item", f"{gate_name} location mismatch")
            _require(gate.get("outcome") == "pass", f"{gate_name} did not pass")
            _require(gate.get("classification") == "proved-by-runner", f"{gate_name} proof record unproved")
        stored = _freeze(dict(record))
        self._implementations[impl] = stored
        self._commit_run(candidate_run)

    def record_matrix(self, records: Any) -> None:
        """Validate all exact cases before atomically storing any of them."""
        _require(isinstance(records, (list, tuple)), "matrix records must be a list")
        _require(len(records) == len(MATRIX_CASES), "matrix must have exact case count")
        candidate: dict[str, Mapping[str, Any]] = {}
        candidate_run: tuple[tuple[str, ...], str] | None = None
        for row in records:
            _require(isinstance(row, Mapping), "matrix row must be an object")
            case_id = _nonempty_string(row.get("case_id"), "case_id")
            _require(case_id not in candidate, f"duplicate matrix case {case_id}")
            row_run = self._candidate_run(row)
            if candidate_run is None:
                candidate_run = row_run
            else:
                _require(candidate_run == row_run, "mixed matrix run identities")
            _validate_case(case_id, row, self.expected_cases[case_id], row_run[0], row_run[1],
                           self.expected_inventory)
            candidate[case_id] = _freeze(dict(row))
        _require(set(candidate) == MATRIX_CASES, "matrix case set incomplete or unexpected")
        _require(candidate_run is not None, "empty matrix")
        self._matrix_records.clear()
        self._matrix_records.update(candidate)
        self._commit_run(candidate_run)

    def report_build(self, *, terminal_success: bool, collector_success: bool) -> None:
        """Build and collector status cannot replace implementation or matrix gates."""
        object.__setattr__(self, "build_terminal_success", terminal_success is True)
        object.__setattr__(self, "collector_success", collector_success is True)

    @property
    def common_summary_available(self) -> bool:
        return (set(self._implementations) == IMPL_IDS
                and self._run_pins is not None
                and all(_pins(record) == self._run_pins and record.get("build_id") == self._build_id
                        for record in self._implementations.values()))

    @property
    def first_matrix_accepted(self) -> bool:
        return (self.common_summary_available
                and set(self._matrix_records) == MATRIX_CASES
                and self.build_terminal_success and self.collector_success)

    def state(self) -> str:
        if self.first_matrix_accepted:
            return "source-reported-first-matrix-gates-satisfied"
        if self.common_summary_available:
            return "source-reported-common-summary-gate-satisfied-matrix-incomplete"
        return "blocked"
