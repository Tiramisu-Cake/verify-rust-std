# R19 checked insert_tail unwind cleanup — 2026-10-22

T0 2026-10-22T16:08:18Z; main 18:08:18Z; absolute 18:38:18Z. Owner/lane `merge`; phase `MERGE-UNWIND-CLEANUP-R19-2026-10-22`; fresh 3600 Cloud seconds, no carry. Probe `4af31693`, baseline `17fe08b5`, source `6fd50c69`. Tool `a66c1d30` → candidate `39f6b0ca` (only `vf_mir_translator.ml`).

## Defect

R18 P1 (Build `e70d2723`, `R18-PROOF1-RESULT-20261022.json`): the raw caller `b2_three_from_local` stops at `verified/lib.rs(461)` while freeing locals, `No matching heap chunks: array_<u64>(values_addr, 3, _)`, directly after the `insert_tail` call. The translator lowers `UnwindAction::Continue` to `return unwinding()`; the checked source cleanup after the call (assert current array, drop u64 owners, `array_to_array_`) runs only on the normal edge. On unwind, `insert_tail`'s unchanged `on_unwind_ens` leaves `begin[..3] |-> ?panic_current` and `foreach(panic_current, own::<u64>(t))`, which are never converted before local release.

## Rule (tool)

Opt-in source marker `r19_insert_tail_unwind_cleanup();` as the head command of one ghost block. Admission (static error otherwise):

- the body is `b2_three_from_local` and has no first/late/callback/R9 recovery plan;
- exactly one marked block, no declarations, no other marker occurrence;
- the remaining commands are exactly `assert array::<u64>(begin, _, ?c); r9_drop_u64_owners(t, c); array_to_array_(begin);`;
- the block starts on the line after the single `insert_tail` call in the same file; that call has a target, `UnwindAction::Continue`, an outcome switch and the stock `return unwinding()` unwind statement; the marker must be consumed by such a call.

The marker head is removed; the remaining block runs on the normal path at its source position (as in R18) and a fresh copy runs on that call's unwinding arm before `return unwinding()`.

Invariant: the copy is ordinary checked ghost code — an assert, the checked lemma `r9_drop_u64_owners` and the prelude lemma `array_to_array_`. It consumes exactly the callee's unwind resources and leaves `array_` for local release. No wrapper/callee post, runtime, CFG edge/target, trusted premise, `leak`, axiom, address-only ownership or RawPtr/Ref conversion changes. Without the marker the translator is unchanged.

## Pins and admission

Profile `GLUE-PROFILE.json` delta from `947be6e0` is exactly `effective_tool_commit`, `translator_sha256`, `guard_return_trace_patch_sha256`, `ordered_patch_chain[-1].sha256` and `r19_registration`. `prove.py` reverts these, rehashes to `947be6e0` and then applies the unchanged R17 admission. The cumulative trace patch `f2e92cec..39f6b0ca` is now emitted with `-U1` context; `build-profile.sh` still applies it with `git apply --check` and the translator/kernel/refiner source pins check the result. `provider-overlays.py` changes only the `prove.py` digest. `control.py` registers R19 like R18: exact ledger/window/authorization, recipe delta (adds the R19 ledger and `r19-unwind-controls.py`, drops only the unused R11-retry inputs/ledger records), unchanged historical ledgers/R13/R14/R17 profile, exact profile/patch/provider bytes, provider pins rechecked, transport cap.

Transport: the probe was already 363 bytes over the fixed 191×3990 transport. Fit by `-U1` patch context, removal of comment-only lines and docstrings from unpinned Python sources (AST-identical), and the two recipe removals; candidate payload 570423 (slack 1144).

## Distinguishing controls (Cloud)

Derived from the prepared raw caller and dispatched like it (`r19-unwind-controls.py`): `missing_marker` (R18 form → free-locals `array_` refusal at the wrapper's closing brace), `displaced_marker` (blank line → not consumed), `other_function` (marked block elsewhere), `cleanup_edge` (`R19Keep` Drop local turns the unwind into a Cleanup edge), `missing_owner_drop` (shape refusal). Each requires exporter/decode exit 0, a non-zero non-setup verifier exit and exactly one diagnostic line with the expected message at the expected source line; otherwise INCONCLUSIVE. The `missing_owner_drop` case is refused by the static shape gate rather than by a verifier leak check.

## Claims

A raw caller all-stage exit 0 with both targets is a bounded raw-caller claim only. The original caller/prefix (`as_mut_ptr`/unsize, borrow/lifetime) remains OPEN and separate. No acceptance, B2, qualification or independent credit.
