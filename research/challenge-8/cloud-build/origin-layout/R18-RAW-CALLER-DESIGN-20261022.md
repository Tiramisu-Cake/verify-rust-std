# R18 raw caller frontier and RawPtr control diagnosis — 2026-10-22

T0 2026-10-22T14:08:51Z; main 16:08:51Z; absolute 16:38:51Z. Owner/lane `merge`; phase `MERGE-RAW-CALLER-R18-2026-10-22`; fresh 3600 Cloud seconds, no carry. Source baseline `6fd50c69...`; tool `a66c1d30214e463a16a325cdef30b0ec8555e0af`; reused profile `GLUE-PROFILE.json` SHA-256 `947be6e0...026d` (unchanged).

## D1 — RawPtr positive refinement2 is a harness defect, not a RawPtr refusal

Brief, Build `2256a4c8-2a4d-4a5c-8b61-a252730eae70`, `r17-rawptr-controls/cases/identical_local_rawmut/refinement.log` (file `ccfb2363...`, SHA `2df97d36...`, request `2872fe89...`), lines 1–3, exact:
`Fatal error: exception Failure("--check-first-fnmut-continue requires exactly one source-bound insert_tail or named prefix")`, raised from `refinement_checker/main.ml` line 507. Verified source (file `f8284312...`, SHA `5e0c92d3...`) is the 7-line isolated control without insert_tail.

Cause: `first-callback.py` sets `args.first_fnmut_continue = True` for the whole actual-body block; `r17-rawptr-controls.run` dispatched with those campaign args, so `prove.py` added `--check-first-fnmut-continue` to the control refiner command. The refiner therefore never reached RawPtr matching. The four negative controls ran with the same flag, so their R17 classifications did not observe the intended RawPtr diagnostics either.

Fix: each isolated control dispatches with `copy.copy(args)` and `first_fnmut_continue=False` (same pattern as `r8-geometry-controls.py`). The campaign args object is not mutated. Classification gates, diagnostics, stage/source receipts and expected verifier behavior are unchanged. Applicability: only the five r17 RawPtr control units; the actual body/raw caller/original caller cases keep the campaign flag.

Additional observation (same Build, `verifast.log` file `5177a3bb...`, SHA `f712c4d1...`, request `96e47c89...`, line 131): the positive control's VeriFast stage reports `No matching heap chunks: array_<u64>(values_addr, 3, _)` while freeing locals. The positive control gate requires exporter/decode/refinement 0 and only a non-setup VeriFast code, so this does not change its classification; it records that VeriFast local cleanup requires the uninitialized-array form.

## D2 — raw caller `array_inv444` frontier

Brief, same Build, raw caller `verifast.log` (file `9f7eba37...`, SHA `64531849...`, requests `2e3b109b...`, `139ddcdc...`), lines 3472–3492: the `assert array::<u64>(begin, 3, ?r16_current)` at verified line 442 succeeds by auto-closing `array` from the element points-to chunks ("Consuming chunk (retry)" / "Producing auto-closed chunk"). A VeriFast `assert` does not keep the auto-closed chunk. The next ghost call `array_inv::<u64>()` has the all-unknown requirement `[?f]array::<T>(?p, ?count, ?elems)`, so no auto-close is possible and it fails with `No matching heap chunks: [_]array<u64>(_, _, _)` (prelude_core.rsspec 274).

Fix: a checked lemma with explicit inputs, placed in the raw caller's verified suffix only:

```
lem r18_u64_array_inv(p: *u64, count: usize)
    req [?f]array::<u64>(p, count, ?vs);
    ens [f]array::<u64>(p, count, vs) &*& count == length(vs) &*&
        pointer_within_limits(p) == true &*& pointer_within_limits(p + count) == true;
{ array_inv::<u64>(); }
```

The caller calls `r18_u64_array_inv(begin, 3)` before the existing assert and `r9_make_u64_owners`; the lone `array_inv::<u64>()` call is removed. Invariant: the lemma body is verified by VeriFast against the prelude `array_inv`; its ensures are a subset of `array_inv`'s ensures for the same chunk; it consumes and returns the same fraction/chunk and creates no ownership. Runtime, actual insert_tail/Drop body, wrapper pre/normal/unwind posts, original caller suffix, and the normal-cleanup annotation are unchanged. No trusted premise, axiom, address-only ownership or RawPtr/Ref conversion is added.

## Registration

`control.py` registers exactly R18: own ledger `CURRENT-RECOVERY-R18-BUDGET-20261022.json`, exact authorization text, T0/main/absolute, 3600 seconds, timeout 510..1200 with the R17 execute budget (outer1200/execute780/soft765/publication420, nested140 retained), merge lane, pinned-objects, R13/R14 upload guard. Source preflight requires the recipe to add only the R18 ledger; all prior BUDGET ledgers, R13 mode, R14 gate, R17 baseline profile, `GLUE-PROFILE.json` and `provider-overlays.py` byte-identical to probe `c99dfde0`; profile SHA `947be6e0...`; every provider pin rechecked in the selected closure; worktree entries equal; transport cap. Final main/absolute recheck after source validation. Reconcile keeps the spent alias equal to used seconds for R18.

## Required Cloud outcome classes

RawPtr controls: positive must reach refinement 0; each negative must show its exact refiner diagnostic; otherwise INCONCLUSIVE. Raw caller: any next VeriFast frontier (insert_tail call, normal cleanup, free locals, unwind path) is recorded exactly; all-stage exit0 with both targets would be a bounded raw-caller claim only. Original caller/prefix gates, isolated body, R9/array controls are separate and unchanged. No acceptance, B2, qualification or independent credit.
