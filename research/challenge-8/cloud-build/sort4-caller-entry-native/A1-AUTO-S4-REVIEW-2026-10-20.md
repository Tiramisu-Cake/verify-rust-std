# A1 Autonomous S4 independent review — 2026-10-20

**Decision: GO for the bounded S4 Cloud submission after exact committed-closure verification and the coordinator's live preflight.** This is source-correspondence activation approval only; it grants no proof credit and does not predict the P0a/P1 result.

## Review scope and finding

Reviewed the S4 delta from `e8279683b1b1546f38e9b9e770768cd2b7f532bf`: the HIR Fresh lifetime projection in `a1-compiler-inventory.py`, its synthetic controls, S4 profile/source-check, and the active control/entry/runner/backend/recipe profile wiring.

The new projection is bounded by the already validated `small_sort` signature. It requires exactly one plain type parameter `F` followed by three Fresh lifetime parameters with the expected kinds, flags, void bounds, and valid high/low identity words. Before any normalization, each Fresh ID must render to the exact, ordered Body input region name already accepted by the input/binder checks; duplicates within the declarations or across selected Bodies are rejected. Only the validated Fresh low words are projected to their input-slot numbers in a transient comparison record. Body/impl/type IDs, spans, other fields, and unknown metadata remain compared; raw inventory records are not modified. No free-region, capture, or positional check is bypassed.

This is supported by the pinned exporter/translator behavior documented in `A1-AUTO-SESSION-2026-10-20.md`: Fresh lifetime IDs are LocalDefIndex values rendered as `'__N`, matching the encoded elided input Region IDs. The comparison therefore removes invocation-local naming variance only after an explicit bijection check. Legacy synthetic records may omit HIR, while presence remains part of equality; present null, partial, malformed, stale, reordered, duplicated, or wrongly typed HIR fails closed. I found no recursive normalization of unknown Fresh-like metadata.

Profile routing consistently selects `A1-AUTO-S4-PROFILE-2026-10-20.json` in control.py, entry, runner, backend, and the sorted recipe. I recomputed the entry, runner, helper, and source-check hashes against the S4 profile; all matched. The session window, owner, budget, build timeout, lane restrictions, and sequential-build controls remain unchanged. The profile records P0a/P1 and the first matrix as NOT_RUN, `N-false31` as NOT_RUN, and `proof_credit: false`.

## Controls and limits

The S4 HIR synthetic suite was reported by its worker as **9 PASS** (test source reviewed); the existing region-alpha suite was **7 PASS**, admission suite **23 PASS**, and profile-gate suite **5 PASS**. These controls cover valid Fresh/input bijections and rejection of stale, wrong, reordered, collapsed, reused, malformed, partial, null, out-of-range, wrongly typed, flag/bounds, and unknown-metadata cases. `git diff --check` is clean. I did not run the suites independently.

No actual MIR replay, compiler toolchain, full proof runner, Cloud evidence, or raw logs were inspected. Cloud must establish whether this projection resolves the compiler-inventory mismatch and then evaluate the unchanged P0a/P1 and full-matrix obligations. The original 26-row lifecycle and own-negative obligations remain intact; no statuses or proof claims are upgraded by this review.
