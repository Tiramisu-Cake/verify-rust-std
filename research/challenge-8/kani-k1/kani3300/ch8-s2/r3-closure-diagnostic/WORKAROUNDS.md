# Workaround assessment — proposals only, NOT_APPLIED / NOT_RUN

Pins and citation abbreviations are in SOURCE-TRACE.md. Neither proposal is an established remedy; neither has native/proof credit. Safety/domain/frame conditions are obligations, not a license to add assumptions. Preserve all existing failures, covers, S1 and nonS2 behavior.

## A. Old-free ensures with harness snapshots

Concrete diagnostic change: at `S:F:459` replace only `old(verify::sorting_s2_swap::capture::<T,F>(v_base,a_pos,b_pos))` by `verify::sorting_s2_swap::capture::<T,F>(v_base,a_pos,b_pos)`. Keep all five requires, modifies, signature and body. This makes snapshot capture occur in the post-state. In active u8/KeyLess mode, evaluating `pair::post(pair::capture(now),now,a,b)` is equivalent to `now[b] >= now[a]` (including equality/coincident positions); it loses relation to entry bytes. It is **not equivalent** to the old-state contract. A constant sorted pair can satisfy it while destroying both original bytes. Using `ensures(|_| true)` would lose even pair order and would change a larger factor; it is not the proposed old-only variant.

The present `swap_pfc` already has a separate entry snapshot at batch.rs:79 and exact transfer assertion at81, plus whole15 frame at82 and useful-return/coincident/reverse/taken covers at83-86. Keeping these would retain that harness's assertion-level relation over initialized u8/KeyLess inputs and bounded 13-position interior-base domain **if actually verified**. It would not restore a reusable original-function contract. `sort13_assumed` uses Replace and bypasses the actual swap body: old-free sortedness plus two-address havoc cannot imply multiplicity/full-byte preservation, so its current full-count postcondition is not justified. Harness snapshots around the caller can detect a failure; they do not constrain each reusable verified replacement or prove a callee contract. No summary may be promoted from DIAGNOSTIC_ASSUMED.

| Obligation | Retained by unchanged clauses/assertions | Lost or still unproved |
|---|---|---|
| Domain/safety | five original pointer/offset/allocation/read-write requires; callback restriction; no new T/F bounds | no extra type, allocation, alias, panic or unwinding domain admitted |
| Initialization | raw reads only after valid initialized-pair premises; arbitrary array fixture initializes all15 | moving snapshot to harness must not read before those premises or read uninitialized scratch |
| Frame | original two-address modifies; existing whole-array assertion and canaries | arbitrary FnMut side effects still excluded; no capture of unrestricted comparator state |
| Exact state transfer | harness assertion with owned PairSnapshot can check actual-body behavior in that harness | reusable ensures no longer remembers original a/b bytes; caller contracts lose entry-to-exit relation |
| Multiplicity/order | post-state pair order retained; full counts checked in actual harness if it runs | order alone cannot justify network full multiset; verified consumer may invent values |
| PFC consumers | safety-only uses may still consume frame on separately qualified same domains | PFC checks weakened contract, not the old one; previous registration/proofs cannot qualify stronger consumers |

All generated outer closures remain and the original swap **still enters mark_unused** in every selected mode. In particular, ordinary weak_swap body substitution remains the wrong-body path, independently of old. Therefore this is useful only to distinguish original-body old/remember effects after eliminating ordinary-stub mismatch as the observed cause. It is not a guarantee-preserving production workaround for current S2 verified consumers.

Required controls before any claimed remedy: unchanged exact-transfer/full15 frame assertions and covers; duplicate/equal/reverse indices; canaries and initialized-only reads; full order and full byte counts for sort13; deliberate value-invention/count mutation must fail; weak swap named negative must still compile and fail at its intended assertion, not compile; out-of-bounds and comparator-outside-frame negative controls; same T/F/geometry, S1/nonS2 stack/body invariance. Each future execution requires review14 and independent GO/accounting.

## B. Separately contracted wrapper

An additive wrapper, e.g. `unsafe fn swap_s2_contract<T,F>(base:*mut T,a:usize,b:usize,f:&mut F)` forwarding once to actual swap, can carry the full five requires, two-location modifies and exact old pair relation guarded for u8/KeyLess. It can have unchanged generic bounds and return unit. **Adding it alone does not bypass anything:** the original function remains contracted and its reachable Original mode still performs four lookups. The wrapper generates its own four names; a PFC checking the wrapper is not automatically a PFC for actual swap. Existing `merge::profiles::swap_profile` is already a separate target (`S:V/merge/profiles.rs:170-224`); its existence supplies no compilation observation or qualification for S2.

A potentially guarantee-preserving *future design* would need, only under the S2 opt-in, to relocate the complete reusable contract to that wrapper, suppress original-function contract instrumentation in that cfg, and route **every relevant S2 consumer** through the wrapper. Runtime original body/signature and all nonS2/S1 instrumentation must stay exact. This is a semantic candidate requiring its own patch, review and GO; no such edits are applied here. If even safety::requires/modifies remain expanded on original under S2, has_contract still holds and original mark_unused remains. Removing only its sorting ensures is insufficient.

To retain guarantees, wrapper PFC must inline/verify the *actual original callee body* with its required valid inputs, never ordinary-stub it, never assume a leaf theorem. The wrapper must carry/establish all five safety predicates and exact frame, and perform one real call with same comparator and provenance. Reusable postcondition must retain an owned entry snapshot via old() or an independently checked ghost-input protocol tying a snapshot to actual entry memory. A freely supplied snapshot argument without equality-to-entry proof is unsound. Do not obtain a compiling wrapper by adding Copy/Freeze/purity bounds to actual generic helper or by switching to u8 unconditionally; closed u8 scope belongs only to conditional S2 relation and qualified consumers.

| Obligation | Condition for preservation |
|---|---|
| Domain and init | same nonwrapping two offsets, same allocation, readable initialized/writable addresses; snapshots after premises; no broader consumers |
| Frame | exact two destinations, no callback writes elsewhere; no broad/full-memory summary; equal locations supported |
| State relation and multiplicity | same old PairSnapshot and conditional exact transfer at every wrapper call; order alone is insufficient |
| Body and panic semantics | one actual call, same normal-return scope; preserve existing safety/unwind exclusions, do not claim new unwind proof |
| PFC qualification | new wrapper PFC at same T/F/geometry; full actual-body leaf evidence; all consumers retargeted explicitly, no qualification by registration |
| Negative controls | retain original weak-sort and weak-merge checks; ordinary-stubbing a contracted wrapper recreates same metadata/body mismatch, so a source-bound mutant control must be designed and qualified, not dropped |
| S1/nonS2 | original safety and modifies stacks unchanged outside exact S2 cfg; verify inactive specializations remain non-reading |

Even this relocation still uses old() in wrapper; if original-body MIR/debug loss is the cause, wrapping may reproduce it. It does not answer the cause question. It can retain the contract *in principle* only with the complete migration and controls above; an additive wrapper or a harness-only relation cannot. A tool-pass fix that honors ordinary stub precedence is a different potential remedy and is outside this no-edit task; neither bypassing lookup nor fabricating ClosureDefs is authorized.
