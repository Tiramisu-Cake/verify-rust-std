# Native C1–C4 exact-bound candidate (2026-10-11)

This candidate binds the four compiler-derived `FnMut::call_mut` switches in the captured safe-entry `small_sort_general_with_scratch` prefix. Its runtime statements match the repository's `sort4_stable` C1–C4 comparisons and `a/b/c/d` pointer selections. The guard for zero-sized `T`, the `len < 8` return, `scratch: &mut [MaybeUninit<T>]`, and unrestricted `FnMut(&T,&T)->bool` remain present. The actual caller and subsequent select/C5/copy path are outside this fragment; the candidate cannot supply a callable summary for full SmallSort.

The falsifiable hypothesis is that the already reviewed source-specific binding rules suffice: relocate only the four captured callback temporary groups into four strict lifetime children; register the exact compiler-derived `FnOnce::Output = bool` projection at each call; close comparison debt on both outcomes; and route each direct unwind through its captured recovery, selected/four-cell join, full source/tail/scratch/F/type restoration, then the original `unwinding` return. The normal path retains every recovery, assertion, current-source re-split, and final post. No kernel, generic callback, alias, ownership, `MaybeUninit` inverse, or parser rule is added.

Admission requires the exact verified-source, original-source, normal/readonly full MIR, and pre-transform full AST hashes from the capture; one target body; all original labels, four calls and markers at the captured coordinates; full unwind and dead-code checks; default-off isolated mode. The positive must exit 0 with complete normal/early/direct-unwind posts, plus refinement and resource checks. Four unwind false assertions and one normal false assertion must fail at their intended assertions; malformed/mixed/source/extrabody admissions must refuse before proof. A frontend/setup failure or new semantic obligation is a blocker, not a negative proof result.

The capture's source pair is `0f92a609c898df5271cbafd04cea688bf7b46c8b4786f8313b8ff99db995e9c4` / `9628df15e3a42643d671bd1e9f5684e0bdd81162e26ab8233ce704a9657942df`; normal/readonly full MIR are `b0da712d2b16c76d1baac91ae69c591ddeab308a2242e196fe876fd27e35e24d` / `79c16a30be7b2921ccdaa35c66aac496f236d900130fff72a36b81524e50ef86`; pre-transform AST is `65b9ddf282ab3b8d123bba3725600528936ff09e236c4261841d61f66cb5ae18`. These identify the only admitted source. The capture was diagnostic and has no proof credit.

The Cloud transport carries one combined source-only translator diff, `native-c4-bound-combined.patch` (`6ddb6602…`), from the reviewed C1 translator `381e80eb…` to `a1be12ce…`. Applying the historical capture overlay (`a67b4b11…`, resulting `b1faa4cd…`) followed by the bound overlay (`323c13a9…`) produces the exact same final translator bytes; both incremental patches remain in the repository for audit. Combining these diffs changes package size only. The bound driver checks the base and final hashes, all non-translator modified hashes, the original capture source-input manifest, and the complete source/MIR/AST certificate.

The first bound Cloud run reached the exact pre-AST SHA and refused on the compound AST/HRTB inventory before verification. The current follow-up emits the four individual inventory counts and the actual derived HRTB `F:T` pairs, retains the same refusal predicate, and makes no proof-rule change. This diagnostic determines whether an implementation correction within the reviewed binder is possible or a new semantic requirement blocks the phase.

The active phase needs only the pure ghost byte stripper from the older C2
discovery driver. `ghost-strip.py` copies exactly its GHOST_BLOCK/GHOST_LINE
regex assignments and strip_ghost function (AST identity checked statically;
no local fixture generation executed). The dormant C2 discovery proof runner
is omitted from this phase's transport; existing archived input/profile remains
available at historical Git SHAs. Generated original source hashes and paired
refinement remain mandatory Cloud gates. No annotation grammar or stripper
behavior is changed, and no model/C1 gate is skipped.
