# Strict CUT relocation: translated local IDs, TEST only

Fresh Cloud relocation evidence retained the exact source pair (`66bf5a6e…`,
`9b41aef5…`), full NORMAL/readonly target MIR (`10356bf1…`, `9fdee764…`),
zero export/decode/refinement exits, and the no-relocation first error at
`verified/lib.rs(84,9-38)`. With the frozen `d557082b…` CUT and `e7189430…`
relocation patches, the relocated run refused before proof entry at
`verified/lib.rs(52,1-56,10): Strict relocation local type inventory changed`.
The six declaration traces and one-insertion trace were absent.

The cause is a representation mismatch at the admission gate. MIR and
`State.local_decl_types` use raw `_27`–`_32`; `translate_local_decl` stores
`Mir.local_decl.id` after `translate_local_decl_id_`, which tags these six
unmapped compiler temporaries as `$_27`–`$_32`. The original TEST patch
compares those translated fields with raw strings, so its first uniqueness
check finds no selected declaration. The new, separate TEST delta must keep
raw IDs for source/MIR type checks and derive each corresponding translated
ID through the existing translator function. It must require six unique,
unaliased mappings and use only those mapped IDs for declaration selection,
removal, and identity checks. The trace must retain `inner=_27`…`inner=_32`
for the frozen capture classifier and also print each translated ID. The
exact type, initial address-taken, six-declaration and one-insertion gates
remain mandatory. No kernel, resource rule, source, or MIR operation changes.

The next Cloud build `293435cf` passed the three patch SHA gates but the
isolated console stopped at the translator type check before any relocation
capture: `translate_to_vf_local_decl loc d` inferred `d` as the unrelated
`var_id_trs_entry` record, whose `id` field shares the `Mir.local_decl` label.
The mapped-ID delta now annotates only the selected `List.map` binder as
`Mir.local_decl`. This resolves record-label ambiguity without changing the
selection, six type/address checks, translated-ID mapping, declaration AST,
or proof semantics. That build remains inconclusive; no callback result was
observed.

The only diagnostic is the unchanged `positive_f_bound` fixture. Run the
unmapped baseline and mapped candidate on the same exact source and both
complete MIR graphs. The baseline must still reject at 84:9–38; the mapped
run must emit all six raw/translated pairs and one insertion, then either
report one new first proof blocker or full fixture VF0. All normal and direct
`Continue` unwind posts, dead-code, leak, uninitialized/validity and
refinement checks stay enabled. A setup, mapping, source/MIR, AST-count or
changed-baseline failure is inconclusive. Neither outcome accepts CUT,
relocation, or actual sort4.

Before acceptance, all-path normal/unwind liveness, post-cut use and renewed
StorageLive, address escape, Drop/cleanup, live heap/bound/outer type retention,
source/MIR mutation negatives, normal/unwind resource recovery, combined S6
and no-cut callback regressions, and separate actual-sort4 admission remain
**OPEN**. `StorageDead` at line 103 is never assumed on direct unwind.
