# R19 c3 candidate: implementation note (unverified until Cloud)

Implements [C3-NEXT-DESIGN](../select-s5-r18/C3-NEXT-DESIGN.md). Defect: the actual sort4 body passes c2 and stops at `let c3 = is_less(&*c, &*a);` with no `ref_precreated_token(v_base+2+1)` (Build `0ee7f658`); the translator overlay accepted indexed markers 1/2 only.

## Changes (R17 tool chain, pins updated in place)

The Cloud adapters, recipe and lane route are keyed by the R17 routing literal and fixed file paths, so R19 keeps the R18 routing precedent and updates the pinned R17-chain files in place (as R17 S2–S5 did); earlier bytes remain at their commits and R18's pin (`87a0bfe5`) now refuses the new profile.

- `actual-sort4-c2-recovery-r17.patch` (base `6c04f608`, result `c5253a3c`): explicit count `SORT4_ACTUAL_BODY_INDEXED_CALLS` (absent or `2` keeps R17 behaviour; `3` enables c3; anything else, or a count without the exact c2 opt-in, fails). Indexed markers `__vf_callback_unwind_four(k)` match only for `2 <= k <= N` with k-specific names `cmpk_k/leftk_ref/rightk_ref/leftk_fraction/rightk_fraction`; out-of-range or malformed markers stay unparsed and the declared/parsed inventory check refuses them. Per-index line key (k>=3 reads entry k of the five ordered `CALL_LINES`), `callback_unwind_count = k-1`, c2 argument calls complete; per-index `'cmpk` declaration range, one `__vf_callback_scopek` per index (any other scope marker refused), exact ordered cut list `'cmp..'cmpN`, strictly increasing source order; N declaration groups of six relocated locals, deferred remainder `24-6(N-1)`; marker inventory and relocation insertions = N. Synthetic scope validator controls grow from 7 to 13 (three-call positive; cross-call read, escape, missing/duplicate/unexpected marker).
- `a1-actual-body-c2.py`: `construct_c3` layers c3 on the unchanged c2 output: fresh `cmp3_k`, split four cells, borrow all four, `share_full_borrow` all four, `precreate_ref` only the selected operands `c` and `a` (program locals, so the reference address is the operand term itself, no address bridge), ordered tuple own, normal and direct-unwind `callback_four_debt` + `recover_four_sources`, `end_lft_binding::<'cmp3>`. Same checked predicates/lemmas as c2; no new premise.
- `a1-actual-body-r17.py`: routes `actual_indexed_calls == 3` to `construct_c3`, sets/pops the explicit count, adds the eight c3 controls and the `indexed-count-off` frontend control.
- `control.py`: R19 account/window registration; profile SHA pin; requires `actual_c2_recovery_enabled` and `actual_indexed_calls == 3`.

## Controls (read by message and location in Brief)

c3: missing unselected shares (base+1/+3: leak on the (0,0) path or missing share elsewhere), missing base0 end token, wrong ordered pair (a,c), wrong ref resource (b), wrong marker index (2), missing fourth debt token, displaced marker, index-4 marker with no call (N=3). Frontend: `indexed-count-off` (3 markers with expected 2). All seven c2 controls rerun on the c3 source.

Invariants: runtime bytes/CFG unchanged (`strip_ghost` equality checked statically for the positive and every control); no axiom, assumed bridge, leak statement or relaxed leak check; c4/c5, selectors and copies untouched; no credit.
