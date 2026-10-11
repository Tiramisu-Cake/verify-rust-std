# Native C1–C4 capture, 2026-10-11

Policy revision read: `c7ca8c467aecf10a4b53039372ee97714f854ee3`
(WORK-POLICY/COMPLETION-PLAN integrated on this branch at
`6726a08d30b37d6d0f4ae65c3d8c2861615d249a`). This is an internal research
fragment for `small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T,&T)->bool>`.
The intended consumer is the actual function's `len >= 8` caller edge to
`sort4_stable` (twice in that branch). Neither the call edge nor a callee
summary is established here.

## Exact diagnostic and hypothesis

Starting from the fresh source-linked native C1 VF0 on the experimental Rust
ZST-size repair profile, preserve its safe-reference entry `v: &mut [T]`,
`scratch: &mut [MaybeUninit<T>]`, and `is_less: &mut F`. Keep the explicit
`size_of::<T>() == 0` return, `len >= 8` branch, exact reviewed slice-to-pointer
expression, opaque MU scratch, and C1 comparator. Add the actual std comparator
sequence `(3,2)`, `(c,a)`, `(d,b)` after C1, where `a,b,c,d` are computed from
the source `c1,c2` boolean expressions. Re-split and rejoin CURRENT source
ownership after each comparator; each direct unwind marker restores the whole
CURRENT source plus untouched tail, MU scratch, F, thread and type resources.
The size guard is an internal diagnostic restriction, not a proved guard from
the actual caller or a generic `sort4_stable` contract.

Hypothesis: with the existing C2–C4 ghost annotation shapes and selected-four
lemmas, the compiler/exporter/refiner accept this one source-linked four-call
fragment and the translator can serialize its complete original AST before
any proof rewrite. Capture success means exact verified/original source pair,
normal and readonly typed MIR, refinement success, four compiler FnMut calls,
four ordered lifetime cuts, a complete pre-AST artifact, and the intentional
`NATIVE-C4-CAPTURE: FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF` refusal **before**
`Verifying function 'small_sort_general_with_scratch'`. Any other first failure
is an inconclusive capture, not a semantic negative or C4 proof.

The new default-off translator mode copies only the reviewed source-specific
placeholder parser for `'cmp2`, `'cmp3`, `'cmp4` and retains their four regular
cuts in the original AST. It admits one exact native target body, full unwind
checking, the driver-supplied verified source SHA-256, four comparator/marker
source expressions and four compiler FnMut AST calls. It always dumps the AST
and refuses. It adds no kernel rule, generic callback inference, ownership or
alias semantics, live proof rewrite, or accepted profile. The isolated C4 tool
is copied from the C1 bound tool; only its translator changes. The driver
checks full pre/post snapshots, the frozen kernel, exact ZST `verifast1.ml`
hash and all other non-translator inputs. The source builder and all compiler,
exporter, refiner, and verifier execution run only in Cloud Build. No local
proof-source extraction or proof execution is used.

## Decision after fresh capture

If source/MIR/refinement or AST capture fails, preserve the first causal
stage and raw artifacts and repair only this source-specific diagnostic within
the authorized profile. A new semantic or resource rule is a stop boundary.
If capture succeeds, independently inspect source correspondence, complete
normal/readonly MIR, local declarations, StorageLive/Dead edges, callback
normal/direct-unwind successors, marker cleanup blocks and full automatic
contract. Only then derive an exact pre-AST/hash-pinned C1–C4 bound transform
from the already reviewed per-call projection/strict-scope/recovery mechanism.
Its positive must execute all four real callbacks and pass strict lifetime,
dead-code, free/leak, unit, full CURRENT normal/direct-unwind post and
refinement checks, with local intended false normal and each unwind control.
Reject source mutation, extra body, malformed opt-in and mixed profiles at
admission. Source capture alone is `NOT_RUN` for target proof and creates no
callable summary. External `as_mut_ptr`, caller guards/overflow, C5,
select/copies, generic full sort4 and composition with maintainer profiles
remain outside this fragment.
