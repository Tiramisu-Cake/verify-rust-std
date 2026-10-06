# Remaining approved tools: SmallSort applicability screening

Source review completed 2026-10-06 at fork research HEAD
`b7416c18035c714258e2a476eebdfa1609f7f66c`. The owner requested this screening
after the closed [VeriFast/Kani no-patch assessment](SORT4-NO-PATCH-ASSESSMENT.md),
then approved recording the result and preparing the next agent task.
Current authorization is in [STATUS](STATUS.md); the selected bounded task is
[RAPX-APPLICABILITY-PHASE](RAPX-APPLICABILITY-PHASE.md).

**Decision: select RAPx for an applicability and detector-coverage experiment.**
No ready route to the full unrestricted safety contract has been established.
This note contains source observations, inferences and open questions, not new
verification results. No tool was installed, compiled or run for this screening.
No generic target coverage or approval of a strengthened public contract follows.

## Scope and comparison

The [approved-tools list](../../doc/src/tools.md) contains ESBMC, Flux, Kani,
KMIR, RAPx and VeriFast. Kani and VeriFast were examined in the previous phase;
this review covers the remaining four using their existing integrations and
official implementation sources. Requirements come from
[Challenge 8](../../doc/src/challenges/0008-smallsort.md) and the
[full research contract](SORT4-CONTRACT.md): unrestricted valid `T` and
`F: FnMut(&T, &T) -> bool`, pointer validity/provenance, possibly uninitialized
scratch, one ownership sequence, legal callback effects and normal/panic exits.

| Tool / integrated profile | Generic code and unsafe memory: observed source facts | Panic / destructor limitation | Selection inference |
| --- | --- | --- | --- |
| ESBMC 8.5; Kani frontend pin `152c6a8c875d9886a67e229247b4826d6105ccfd` | [Workflow][esbmc-workflow] generates Kani GOTO with `--only-codegen`; [runner][esbmc-runner] feeds it to ESBMC directly. Existing job selects arithmetic harnesses. | This integration does not independently replace the Rust frontend or its generated checks/effect model. No new panic experiment was performed. | A different backend alone does not turn concrete type/callback instantiations into a universal generic proof or automatically close frontend instrumentation gaps. Defer as a direct solution to those blockers. This is not a claim about every possible ESBMC integration. |
| Flux, commit `9c1b5e278791f57eed1fd109816bbe180423fa9d` | [Integrated workflow][flux-workflow]; generic refinement checking and raw-pointer modeling exist. Do not infer that current Flux supports no unsafe Rust from older papers. | [Checker][flux-checker] follows normal call/drop successors; `UnwindResume` still has an explicit cleanup-checking TODO. | Do not select first for the required panic-state argument. Generic support alone does not establish our ownership/initialization/unwind contract. |
| KMIR `ubuntu-jammy-0.4.226`; source tag v0.4.226 at `0db4f49a0ad12ec4b8e0faab4486470ad3854556` | [Integration][kmir-workflow]; [feature checklist][kmir-features] says type parameters are monomorphized, pointers are partially supported, and the address model is incomplete. Its support labels concern concrete execution tests. | Checklist explicitly excludes panic unwinding; user `Drop` does not run. [Semantics][kmir-semantics] treats Drop as continuing to its normal target. | Not a current route to this full generic/panic safety requirement. |
| RAPx 0.7.50; source tag v0.7.50 at `7d61d9377033c48a4df8954f34cc076e97a93816`; Rust nightly-2026-02-05 | [Integration][rapx-workflow]; [checker][rapx-memory] and [call model][rapx-call] include symbolic generic layout, pointer obligations and `select_unpredictable`. [Contract assets][rapx-contracts] cover copy alignment, range validity and non-overlap. | Arbitrary callback effects and direct panic post-state are not established. Specific coverage concerns below require falsification tests. | Best candidate for a small applicability gate, not an accepted verifier replacement or a completed target proof. |

## RAPx: positive evidence and unresolved mechanisms

### Generic layout and scratch copying

Observed in [call.rs][rapx-call]: generic `size_of::<T>()` and `align_of::<T>()`
are connected to shared symbolic layout terms; the model also handles
`select_unpredictable`. The copy contract requires source/destination pointer
validity, alignment and non-overlap without requiring destination values to be
initialized first. This is relevant to actual `MaybeUninit` scratch callers.
It does not by itself prove padding treatment, non-Copy ownership, scratch access
or preservation of comparator effects. The selection model permits either input
value; its adequacy for safety must not be conflated with exact sorting behavior.

Open: verify that the selected generic body is actually analyzed for symbolic
`T`/`F`, not merely accepted, skipped or instantiated at a few concrete types.
Concrete controls can test detector behavior but cannot establish universality.

### Unsupported calls and panic paths

Observed in [call.rs][rapx-call], lines 183-233: unsupported calls get a fresh
return value (a Boolean is constrained to 0/1). This fallback does not visibly
apply a general update for all memory the callback can legally affect.
This is a concern about effect coverage, not an executed proof of a false pass.

The [CFG builder][rapx-graph] includes cleanup successors for calls, assertions
and drops. Therefore it would be inaccurate to say all panic paths are omitted.
However, the [trace executor][rapx-exec] does not supply call cleanup to
`exec_call`, and handles `UnwindResume` without a state transformation. This
does not establish the required relationship between callback effects and the
state visible on direct unwind. Determine which paths and obligations are
actually generated in the diagnostic; a panic/no-panic label is insufficient.

Actual sort4 makes five comparisons before its first copy and has no local Drop
guard. Its first-callback direct-unwind obligation must be assessed in that
shape. A synthetic cleanup-only negative tests an additional model capability;
it must not be reported as an executed path in sort4 itself. RAPx need not use
VeriFast's tuple/token notation: the obligation is equivalent Rust safety and
state preservation, not a particular proof encoding.

### Concrete ZST alignment concern

Observed in [memory.rs][rapx-memory], lines 25-41: `check_align` returns
`ProvedByRule` if `zst_guard` succeeds. [The guard][rapx-util], lines 432-466,
tests whether the contract's type argument resolves to a concrete zero-sized
type. In contrast, the target [copy contract][rust-copy] explicitly requires
aligned pointers even when `count * size_of::<T>()` is zero.

Inference: a misaligned pointer to `#[repr(align(8))] struct Z;` at
`copy_nonoverlapping::<Z>` is a precise candidate for a missed alignment
obligation. **No end-to-end false SOUND result has been reproduced.** Another
checkpoint could reject the fixture, so inspect the exact predicate and location.
Pair it with a valid aligned ZST control and ordinary non-ZST controls. Construct
the invalid pointer without an earlier invalid reference or unrelated UB.

### What a verdict means

In pinned [display.rs][rapx-display], `SOUND` means no generated required or
hazard obligation is left unproved. `UNSOUND` also includes `Unknown`; it is not
necessarily a demonstrated counterexample. Neither spelling establishes that
all required target operations and paths produced obligations.

The existing integration searches for `result: UNSOUND`; absence of that text
does not establish that the intended function was selected. The diagnostic must
record analyzed bodies, checkpoint identities, path/case coverage, actual proof
statuses, warnings and exit codes. Missing targets/checkpoints, unsupported calls
relevant to the claim and unknown results must remain visible.

## Upstream freshness check, separate from the executable profile

Source inspection also checked Flux
`1b17bc7e348419f322698cfeeafb779a242e9239` (the cleanup TODO persists), KMIR
`4d793252bcd77091ee759ca6cd1629db41ed5496` (the relevant checklist limitations
persist), and RAPx `a9eda1f2643c91571b82bea0ba276e225d063a89`.
RAPx's latter Cargo workspace declares version 0.7.54 and contains intervening
alias/provenance, byte-model and verdict changes. Its alignment early-success
rule still appears in [current memory.rs][rapx-memory-current]. Publication of
that package version was not verified. These observations authorize neither an
upgrade nor a claim that all versions behave identically.

## Decision boundary and independent contract question

Run the bounded [RAPx phase](RAPX-APPLICABILITY-PHASE.md) on the exact integrated
0.7.50 profile: alignment first, then memory/generic coverage, then callback and
panic coverage, advancing only when the preceding gate permits it. A demonstrated
miss or essential unsupported behavior closes this profile's applicability gate;
it does not authorize patching RAPx, silently upgrading it or switching tools.
If all gates pass, propose the next exact-source proof task for an owner decision.
Passing fixtures alone never completes generic sort4 or Challenge 8.

The [contract clarification](SORT4-CONTRACT.md#established-concrete-theorem-and-required-contract-clarification)
remains independent: are full range separation and the single-owner nondropped
scratch protocol admissible for the public target? These are explicit research
premises, not organizer-approved strengthening. Tool selection does not answer
that question; no organizer contact, tool application or upstream PR is authorized.
The bounded diagnostics may proceed without representing those premises as
accepted challenge coverage.

## Immutable primary sources

Repository integration links below are pinned to the screening checkpoint.
Tool implementation links use the inspected source commits. Existing target
results remain in [coverage](coverage.md) and [EXPERIMENT-LOG](EXPERIMENT-LOG.md).

[esbmc-workflow]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7416c18035c714258e2a476eebdfa1609f7f66c/.github/workflows/goto-transcoder.yml
[esbmc-runner]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7416c18035c714258e2a476eebdfa1609f7f66c/scripts/run-goto-transcoder.sh
[flux-workflow]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7416c18035c714258e2a476eebdfa1609f7f66c/.github/workflows/flux.yml
[flux-checker]: https://github.com/flux-rs/flux/blob/9c1b5e278791f57eed1fd109816bbe180423fa9d/crates/flux-refineck/src/checker.rs#L788-L865
[kmir-workflow]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7416c18035c714258e2a476eebdfa1609f7f66c/.github/workflows/kmir.yml
[kmir-features]: https://github.com/runtimeverification/mir-semantics/blob/0db4f49a0ad12ec4b8e0faab4486470ad3854556/docs/feature-checklist.md
[kmir-semantics]: https://github.com/runtimeverification/mir-semantics/blob/0db4f49a0ad12ec4b8e0faab4486470ad3854556/kmir/src/kmir/kdist/mir-semantics/kmir.md
[rapx-workflow]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7416c18035c714258e2a476eebdfa1609f7f66c/.github/workflows/rapx.yml
[rapx-call]: https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/vm/call.rs
[rapx-memory]: https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/property_checker/memory.rs
[rapx-util]: https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/property_checker/util.rs
[rapx-contracts]: https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/contract/assets/std-api-requires.json
[rapx-graph]: https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/analysis/path/graph.rs
[rapx-exec]: https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/vm/exec.rs
[rapx-display]: https://github.com/safer-rust/RAPx/blob/7d61d9377033c48a4df8954f34cc076e97a93816/rapx/src/verify/display.rs
[rapx-memory-current]: https://github.com/safer-rust/RAPx/blob/a9eda1f2643c91571b82bea0ba276e225d063a89/rapx/src/verify/property_checker/memory.rs
[rust-copy]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b7416c18035c714258e2a476eebdfa1609f7f66c/library/core/src/ptr/mod.rs
