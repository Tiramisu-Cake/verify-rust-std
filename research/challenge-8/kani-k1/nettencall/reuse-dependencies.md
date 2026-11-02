# NETTEN-CALLER reuse of the two NETTEN-LEAVES leaves

Historical Build: f6fdbf06-58fa-4c1d-9692-c8236cc38892 (pool k1-standard4, Cloud SUCCESS, lane COMPLETE).
Reviewed source: 1914e42274cb2a7e574a0d6497c4a9922983a9cf; library commit/tree
23ba8cfddbce1cf0313ab402fd6376d157a0f845 / 74e42aaa191879280e8e7827c1e32a4ac65d5f18.
Request netten-leaves-swap9-backing10-insert-tail9-20261102, SHA256 83e3a471...291c6f8094.
Bounded evidence: ../netten-leaves/g1.{summary.md,status.txt,checks-lines.txt,peaks.txt,tooling.txt},
../RESULT-NETTEN-LEAVES.md. These are rows of the OLD Build, not rows of the NETTEN-CALLER Build.

| Reused leaf (old row) | Historical fact | Summary consumed by caller | Dependency closure retained |
|---|---|---|---|
| netten_swap_prefix9_backing10 | PFC SUCCESS, 0/412, covers 8/8, VT 77.10969s, CBMC 355216KiB | stub_verified(swap_net9) | swap_net9 clauses/body, region9/count9/canonical, StrictU8/strict_less, specfix swap models, real raw swap_if_less, ub_checks predicates |
| netten_insert_strict_u8_begin0_tail9 | PFC SUCCESS, 0/631, covers 8/8, VT 59.589855s, CBMC 1013808KiB | stub_verified(insert_tail_profile::<StrictU8>) | insert_tail_profile clauses/body, tail_region/tail_len/model_sorted/model_count, StrictU8 profile/probe static, real raw insert_tail, ub_checks predicates |

Byte identity (static_check.py, asserted): `git diff 1914e42274 9835bd00dc -- library` is empty;
smallsort.rs, network.rs, netcomp.rs, specfix.rs, ub_checks.rs equal 1914e42274; netten.rs equals
1914e42274 plus only the appended `mod caller;` registration. Both leaf roots, their annotations,
covers, fixtures and targets are therefore unchanged. Protected lane = 30f77e8599; tooling hashes
equal NETTEN-LEAVES (tooling-static.txt). Same pin Kani 9461e07af7 / nightly-2026-10-12, same flags.

## Domain match: leaf executed domain vs caller actual use

| Item | Swap leaf (old) | Caller swap use | Insert leaf (old) | Caller insert use |
|---|---|---|---|---|
| T / F | u8 / U8Cmp | u8 / U8Cmp (actual F of small_sort) | u8 / U8Cmp | u8 / U8Cmp |
| CMP value | StrictU8::CMP | received `*is_less`, asserted canonical | StrictU8::CMP | received `*is_less`, asserted canonical |
| Model / order | full value, `<` | same (swap_net9 hardcodes StrictU8) | StrictU8 identity, `<` | P = StrictU8 |
| Backing / init | exact any [u8;10], fully init | exact any [u8;10] (positive), fully init | exact any [u8;10] | same array |
| Offset / geometry | base+0, distinct a,b<9 | actual root+0, asserted distinct a,b<9 | begin+0, tail+9 | asserted begin==root, tail==begin+9 |
| Probe | independent any u8 by value | ContextTen.probe = the one root probe | StrictU8::set_probe(any) | StrictU8::probe()==ctx.probe asserted |
| Frame | 8 cells outside pair, v[9] | pair-only modifies; adapter asserts v[9]==initial_tail | whole region10 writable | whole region10 writable; no tail frame after |
| Premise | none (values unrestricted) | none | sorted prefix9 (profile requires) | prefix9 sorted ASSERTED from real network |

Leaf domains equal the executed caller domain: any [u8;10] input (any root positive) and an
arbitrary independent u8 probe. The swap leaf covers every pair a!=b<9 incl. all 25 network edges;
the insertion leaf covers every sorted-prefix9 backing10 state, which is exactly what the caller
asserts before the summary. The negative controls use [0;10]/probe0, a point of both domains.

## prefix -> whole count algebra and single probe

register10: initial_prefix_count9 = count(pre[..9], probe); initial_tail = pre[9];
initial_count10 := initial_prefix_count9 + (initial_tail==probe) as usize, then
kani::assert(initial_count10 == count(pre[..10], probe)) - computed and checked, never assumed.
Swap phase (each of 25): swap_net9 ensures count9 preserved (pair-only modifies), adapter asserts
count9==initial_prefix_count9 and v[9]==initial_tail through the checked actual base.
Before insertion: asserts count9==initial_prefix_count9, v[9]==initial_tail and
model_count<StrictU8>(begin,10)==initial_count10 (same probe, StrictU8::probe()==ctx.probe asserted).
Insert summary ensures model_count(10) preserved; adapter asserts ==initial_count10 after. Final root
check: count(pre,probe)==count(v,probe) with pure typed count_matching_values.
One probe: the root's `probe` is the only value; register10 writes ContextTen.probe and
StrictU8::set_probe(probe) before the actual entry; nothing else sets either. Neither summary has
the statics in its modifies set; frames are re-asserted in both adapters and after return.

Source identity does not establish compilation, reachability or new proof results of the caller.
