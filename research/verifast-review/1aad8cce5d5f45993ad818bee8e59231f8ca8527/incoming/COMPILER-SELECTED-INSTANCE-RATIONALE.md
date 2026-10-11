# Compiler-selected instance evidence candidate

This candidate is scoped to `SORT4-CALLER-DERIVED-BOUND-CLOUD-2026-10-11` and
is default-off. The source base is VeriFast commit
`f76012fb518703b1d98e243ac4f487f16877cfcb`; the compiler pin is nightly
1.100.0 at `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`. Exact file and patch
digests are recorded in `COMPILER-SELECTED-INSTANCE-PINS.json`.

The probe is inserted at `encode_fn_call_data`, where the exporter has both
the original MIR body and call span. The probe is enabled only when
`SMALLSORT_EXECUTION_PROVIDER=cloud-build`,
`SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID=SORT4-CALLER-DERIVED-BOUND-CLOUD-2026-10-11`,
and the explicit evidence opt-in matches that same phase ID. It whitelists only the exact fixture caller DefPaths
`selected_freeze_basecase`, `selected_freeze_basecase_false_31`, and
`selected_freeze_basecase_missing_source_array`. Within those bodies it filters
only the exact local trait callee DefPaths
`StableSmallSortTypeImpl::small_sort_threshold` and
`StableSmallSortTypeImpl::small_sort`, matching the copied fixture source; it
does not use an external `core::...` DefPath or a global item-name match. It obtains `body.typing_env(tcx)`, and queries
`ty::Instance::try_resolve` for the original callee DefId and generic args. It
logs the caller DefPath, actual body TypingEnv, exact callee and resolved
instance DefPaths/DefId, resolution none/error when applicable, the resolved
implementation source span on success, and call source span.
This is intended to establish compiler-selected implementation identity from
the real body context, including a Freeze-qualified diagnostic caller when the
compiler exposes that selection.

The probe is evidence-only: the result is not written into MIR/Cap'n Proto,
does not alter specialization or translation, and cannot enable a theorem by
itself. The unconstrained runtime `quicksort` context may fail to resolve to the
Freeze implementation; that outcome is expected evidence against transferring
the selected diagnostic theorem to generic quicksort. Do not substitute a
hand-built `TypingEnv` if the body context is absent or insufficient. If the
pinned compiler API or actual caller context does not support the query, stop
and report that as a blocker for this phase.

Before any execution, the existing runner must attest the extracted source
MD5 and proof manifest against the phase pins; this exporter probe does not
replace, relax, or bypass that admission. This patch was not compiled or
executed, by the Cloud-only compiler boundary. The only validation performed
here is a patch dry-run against the pinned source file. No source/MIR pair, compiler binding, translator acceptance, or proof
status is established. The next allowed step is applying and compiling this
candidate in the already-authorized Cloud lane, then inspecting the complete
exporter log before any binding gate is considered.
