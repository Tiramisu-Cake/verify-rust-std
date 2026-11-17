# S1-07 U-only source-local applicability

187 original unresolved check observations processed: **187 justified, 0 UNKNOWN**.
Status remains **UNREACHABLE**. This justifies only generated safety-check
applicability, not execution of the checks, the Boolean sorting relation, PFC,
qualified acceptance, or independent proof credit.

| Rule | Observations | Exact pinned source sites |
|---|---:|---|
| abs_diff | 50 | num/uint_macros.rs:3222,3224 |
| alignment | 25 | ptr/const_ptr.rs:1479 |
| multiple | 12 | num/uint_macros.rs:3916 |
| allocation | 18 | ub_checks.rs:148 |
| fmt | 28 | fmt/mod.rs:820 |
| active_post | 54 | verify/sorting_model.rs:97,100,106,111,112,113,118 |

Source commit `5be85699b8826e3286c0bf89efb9affefac0acb5`, producer commit
`0aac16ef62da9e9d5645782d458593e5d78143ba`, run `43923266772`.
`INPUTS.json` pins existing inputs to task commit `2f3ede5ff4`, complete source
blob hashes, exact source anchor hashes, and structured projection identities.
`U.json` retains each original group, row, harness, property ID, class,
description, status, exact site/function/context, source hash, evidence hashes,
operation, rule, and checked premises. Repeated IDs in different harnesses remain
separate observations.

## Arguments checked by replay

**abs_diff.** The exact full function selects `other - self` when `self < other`,
and `self - other` otherwise. For unsigned operands in `[0, 2^64-1]`, the first
difference is in `[1, 2^64-1]`, the second in `[0, 2^64-1]`. Both avoid underflow.
The byte-only alternative is not selected by the exact `usize` instance on the
pinned x86_64 target. Matching a subtraction elsewhere in the file is insufficient.

**alignment.** The exact function panics before subtraction unless
`align.is_power_of_two()`. Its pinned definition is `count_ones() == 1`, so zero
cannot pass. Passing alignments are the 64 powers `2^k`, `0 <= k < 64`; `align-1`
is nonnegative and representable. Both the guard and helper definition are checked.

**multiple.** The complete match on `rhs` selects its separate zero arm before
`self % rhs`; the operation is in the nonzero arm. Thus its divisor is in
`[1, 2^64-1]`.

**allocation.** The complete conditional selects `usize::MAX` for zero size;
the division is confined to the other arm, so its divisor is nonzero. This is
only the division-by-zero check, not an allocation correctness claim.

**fmt.** The exact expression is `s.len() << 1`. Pinned Kani
`codegen/rvalue.rs:328–339` constructs the checked-shift flag from
`RHS > shift_max`; its usize arm at :291 defines `shift_max = pointer_width - 1`.
The export pins x86_64 and the rule pins usize width 64. Thus `1 > 63` is false
for every LHS. Pinned `checked_shl` and `overflowing_shl` independently anchor the
same Rust shift-count semantics. There is no length bound on the string and no
claim about other operations in this function.

**active_post.** The complete function, `CAP=32`, and `Snapshot` array definition
are checked. Passing the initial guard gives equal input/output lengths
`n <= 32`. The first loop starts at `i=1`; a body execution has `1 <= i < n`,
so both `values[i]` and `values[i-1]` are valid and `i+1 <= n`. For `n=0,1` it
has no body execution. The second loop starts at zero: its body has `i < n`, so
`before.values[i]` is inside its 32-element array. Its inner loop starts at
`j=0`, has `j < n`, and indexes both arrays safely. At each inner header,
`old_count,new_count <= j`; each conditional increment adds at most one. On the
back-edge both counts are at most `j+1 <= n <= 32`. All index increments are also
at most 32. Returns can only shorten these loops. The executable certificate
checks every admitted length and induction state, including both counter
increment choices (11,968 transitions). It does not enumerate sampled element
values as a proof of sorting. This argument works for arbitrary accepted
Snapshot/value pairs, independent of ensures/caller/canary/model-control origin.

## Replay and failure behavior

Run from any directory:

```
python3 -B /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-07/run-43923266772/accept-u/replay.py
python3 -B -m unittest discover -s /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-07/run-43923266772/accept-u -p 'test_*.py' -v
```

Default replay compares exact deterministic U.json bytes. `--write` regenerates
only that file. The loader checks the pinned manifest, existing inputs, git
source blobs, and exact anchors before interpreting records. The semantic path
then checks original request/group/row/harness/property namespaces, full safety
operation shapes, and bounds. Unknown/malformed identities or violated premises
produce ERROR (nonzero), never PASS or an invented allowance. No unsubstantiated
record is silently omitted. The current immutable input has no unresolved rule
case, hence UNKNOWN=0.

Mutation tests also bypass digest gates in memory to test structural and
source-premise rejection independently of cryptographic integrity. All six rule
families are covered; all 187 observations are tested against eight metadata
mutations. Tests do not modify source inputs or historical receipts.

## Boundaries

The 226 existing allowed checks and two negative-return covers remain read-only;
no new conclusion is assigned to them. `accept/ACCEPT.json`, its INPUTS manifest,
and the unfinished `accept-v2/` stop-marker retain their original bytes. The
stop-marker is hashed only for preservation and supplies no admission.

No artifacts are copied; existing compact projections are referenced in place.
The provenance chain is source-reported property identity plus exact pinned
source-local reasoning, not newly established compiler AST/MIR provenance or
formal B2 proof. No PFC or success binding is evaluated, no qualified count is
recomputed, and no source, policy, CI, ledger, push, or publication is changed.
