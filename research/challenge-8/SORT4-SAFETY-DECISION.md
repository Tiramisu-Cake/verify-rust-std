# `sort4_stable` generic-safety feasibility decision

Follow-up approval: [SORT4-CONTRACT-PHASE.md](SORT4-CONTRACT-PHASE.md) permits
refining the contract and selecting one concrete architecture proposal from
existing evidence. No new VeriFast run, patch build/application or semantic
implementation is authorized. This assessment's existing proof boundaries
remain unchanged; use [STATUS](STATUS.md) for the current checkpoint.

## Decision

**No established source-exact route under the frozen VeriFast profile was
identified; no generic diagnostic was dispatched.** This is a feasibility
assessment, not a theorem that every unchanged-tool route is impossible, and
not an executed `sort4_stable` proof. The approved Kani functional harnesses
were completed independently in [the hosted functional result](SORT4-RESULTS.md).
The only established unrestricted
generic target result remains the isolated `has_efficient_in_place_swap`
size helper; none of it proves comparator calls, pointer copying, or
`sort4_stable` ownership.

## Obligations versus existing evidence

The exact target is
[`library/core/src/slice/sort/shared/smallsort.rs`](../../library/core/src/slice/sort/shared/smallsort.rs),
blob `e555fce440872898e47fd5114f32eb15401d07df`. Its five actual
`FnMut(&T, &T) -> bool` calls need tuple-2 argument ownership and the
higher-ranked `FnOnce::Output = bool` projection. Each call creates two
shared-reference obligations and needs a normal continuation that accounts
for the live borrow and callback resources. Safety alone does not require
ending each shared borrow before the next comparison; shared borrows may
coexist where the Rust lifetimes permit it. By normal return, the proof must
recover the resources required by its postcondition. Each callback can unwind
directly; on that edge, the proof must account for the source/frame resources,
the current callback resource/state, and one current logical ownership
sequence while preserving permitted callback effects. The actual
body then needs four initialized and valid source reads, four valid writes,
the per-copy non-overlap condition, a sufficient cross-range separation
argument, and an ownership protocol for generic values after copying. The
caller’s `Freeze` bound is not on `sort4_stable` and does not imply `Copy`.
Safety cannot add comparator purity/order assumptions.

The first frozen-verifier blocker is evidenced by an actual `insert_tail`
comparator. Repeating the same callback setup under a `sort4_stable` label
would test a new body, but the evidence makes the same callback-boundary
failure likely; this is an inference from the shared compiler `FnMut` shape,
not an executed sort4 VeriFast result. It was judged unlikely to change the
phase decision:

- In [run 37400422055](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37400422055),
  unchanged VeriFast 26.09 reached the real generic `FnMut::call_mut` setup
  and failed to construct the tuple-2 `Args.own` resource. Related ghost
  closure and prelude-overlay attempts are documented as parser/definition
  failures in [the tuple ownership note](verifast-tuple-parser.md); they did
  not prove a comparator call.
- Compiler MIR evidence records the actual `for<'a, 'b> FnMut<(&'a T, &'b T)>`
  bound and `for<'a, 'b> FnOnce::Output = bool`. The compiler MIR evidence is
  recorded in [run 37408278446](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37408278446).
  The unchanged release translator omits that bound-region projection at a
  call; the tuple-parser-only diagnostic, before the HRTB translator patch,
  in [run 37407173581](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37407173581)
  reaches the Output-versus-bool mismatch. The targeted HRTB diagnostic,
  using the tuple-parser profile, in [run 37409198258](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37409198258)
  advanced past that return-type mismatch, then stopped at the actual
  `tail.read()` ownership obligation. This required a verifier semantic patch
  that this phase forbids; it is evidence of the missing capability, not
  authorization to import it. The guard regressions and borrow-access result
  in [run 37410979109](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410979109)
  still did not establish complete recovery of the comparison resources.
- The separate unchanged-release normal recovery control in
  [run 37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808)
  proves a useful but narrower fact: a generic `T` caller can recover two
  current cells and `T.own` after ordinary shared references in a natural
  block. It includes no `FnMut` callback, five sequential comparisons,
  source-exact lifetime boundary, or callback unwind. The later actual
  `insert_tail` diagnostics retain direct-unwind, scope, and storage blockers;
  see [the prepared-phase report](PREPARED-PHASE-2026-10-06.md).

Together these results show a missing tuple/HRTB/resource-recovery proof
route, not a `sort4_stable` failure. The shorter body removes insertion's gap,
loop, guard and `ManuallyDrop` obligations, but still makes five callback
calls and copies generic values. A new hosted unchanged-release probe was
judged likely to reach the same front-end/callback boundary and not change
this decision, so it was not justified.

## Remaining safety and UB obligations

No generic `sort4_stable` property is checked yet. A future proof must still
establish:

- provenance, alignment, bounds and initialization for all four source
  elements and four destination slots, including ZST pointer semantics;
- non-overlap for each executed `copy_nonoverlapping`, plus a clear
  cross-copy argument preventing earlier writes from changing later sources;
- no lost prior destination resources and exactly one current logical
  ownership sequence for non-`Copy`, destructor-bearing values, without
  assuming a second independently droppable copy;
- all five callback calls at their actual generic types, accounting for the
  live shared-borrow resources at each continuation and recovering the full
  resources required by the normal and direct-unwind posts;
- the updated `F` and frame state, including valid interior/callback effects
  on both normal and panic paths; sortedness/stability require separate
  functional assumptions;
- explicit evidence for dangling/misaligned access, uninitialized reads,
  immutable-byte mutation and invalid values.

The Kani evidence ledger records two material instrumentation boundaries:
`copy_nonoverlapping` validity checks are unsupported in the pinned run
37396688760, and the immutable-byte mutation detector gap was reproduced in
37397720683. A default-check functional success cannot close either category.
The other UB categories also need results applicable to this target; previous
isolated detector controls are not a proof of this generic function.

## Architecture question for a later owner decision

If generic safety is pursued, first decide whether to authorize a separately
reviewed VeriFast capability for source-derived tuple-2 field ownership and
for instantiating the compiler-exported two-bound-region `FnOnce::Output =
bool` predicate at the matching `FnMut::call_mut`. That proposal must preserve
the actual `F`, both `T` types, binder scope, and call substitutions; it must
not infer equality from an expected return type. Acceptance would require
source/tool hashes, positive proof that both real comparison borrows are
created and recovered, normal and direct-unwind resource posts, plus negative
regressions for absent/different/ambiguous projections, mismatched `F`/`T`,
and non-Boolean output. The unchanged tool profile remains the baseline; any
semantic change requires a trust/admissibility review and a regression gate
before implementation.

Even if accepted and passed, that capability would only unblock the first
callback boundary. It would not establish the five-call source-exact lifetime
sequence, direct-unwind recovery, destination/source ownership protocol,
pointer provenance, the omitted overlap contract, or the Kani detector gaps.
Those need their own reviewed proof route and criteria. No architecture
change, later phase, or external publication is authorized by this report.
