# U64-TEN-CALLER reuse of the two U64-TEN-LEAVES leaves

Historical Build: dd2f7e52-52a5-46fd-a8a2-d5658713ad90 (pool k1-standard4, Cloud SUCCESS, lane COMPLETE).
Reviewed source: 9009451c82740af506708b7a2217099b57970807; library commit/tree
e4c696648a5a4ff4f92dbe1ec7ed145afea25ee8 / 3c600416e508b037ebdfe817f6dc93d0314c9b21.
Request usixtyfourten-swap9-backing10-insert-tail9-20261102, SHA256 251b71d5...fe5d4da42.
Bounded evidence: ../u64ten-leaves/g1.{summary.md,status.txt,checks-grep.txt,checks-lines.txt,peaks.txt,
tooling.txt}, ../RESULT-U64-TEN-LEAVES.md. These are rows of the OLD Build, not rows of a caller Build.

| Reused leaf (old row) | Historical fact | Summary consumed by caller | Dependency closure retained |
|---|---|---|---|
| u64ten_swap_prefix9_backing10 | real-body no-stub PFC SUCCESS, 0/413 failed, covers 9/9, VT 100.61334s, CBMC 397352KiB | stub_verified(swap_u64_net9) | swap_u64_net9 clauses/body, region9_u64/count9_u64/canonical/U64Cmp (u64nine.rs), StrictU64/strict_less::<u64>, specfix swap_geometry/pair_models/swap_transfer/swap_ordered, real raw swap_if_less, ub_checks predicates |
| u64ten_insert_strict_u64_begin0_tail9 | real-body no-stub PFC SUCCESS, 0/640 failed, covers 9/9, VT 79.74734s, CBMC 992880KiB | stub_verified(insert_tail_profile::<StrictU64>) | insert_tail_profile clauses/body, tail_region/tail_len/model_sorted/model_count, StrictU64 profile + PROFILE_PROBE_STRICT_U64 static, real raw insert_tail, ub_checks predicates |

Byte identity (static_check.py, asserted): `git diff 9009451c82 f057b7e4eb -- library` is empty (same
library tree 3c600416e5); smallsort.rs, network.rs, u64nine.rs, merge.rs, specfix.rs, ub_checks.rs equal
9009451c82; tenleaves.rs equals 9009451c82 plus only the appended `mod caller;` registration. Both leaf
roots, their annotations/covers/fixtures and both targets/contracts are therefore unchanged (no semantic
drift). Protected lane = 30f77e8599; tooling-static.txt hashes equal U64-TEN-LEAVES. Same pin Kani
9461e07af7 / nightly-2026-10-12; same measurement flags; both builds standard4.

## Domain match: leaf executed domain vs caller actual use

| Item | Swap leaf (old) | Caller swap use | Insert leaf (old) | Caller insert use |
|---|---|---|---|---|
| T / F | u64 / U64Cmp | u64 / U64Cmp (actual F of small_sort) | u64 / U64Cmp | u64 / U64Cmp |
| CMP value | StrictU64::CMP | received `*is_less`, asserted canonical | StrictU64::CMP | received `*is_less`, asserted canonical |
| Model / order | full u64, `<` | same (swap_u64_net9 hardcodes StrictU64) | StrictU64 identity, `<` | P = StrictU64 |
| Backing / init | exact any [u64;10], fully init | exact any [u64;10] (positive), fully init | exact any [u64;10] | same array |
| Offset / geometry | base+0, distinct a,b<9 | actual root+0, asserted distinct a,b<9 | begin+0, tail+9 | asserted begin==root, tail==begin+9 |
| Probe | independent any u64 by value | ContextU64Ten.probe = the one root probe | StrictU64::set_probe(any) | StrictU64::probe()==ctx.probe asserted |
| Frame | 8 cells outside pair, v[9] | pair-only modifies; adapter asserts v[9]==initial_tail | whole region10 writable | whole region10 writable; no tail frame after |
| Premise | none (values unrestricted) | none | sorted prefix9 (profile requires) | prefix9 sorted ASSERTED from real network |

Leaf domains contain the executed caller domain: any [u64;10] input at root+0 and an arbitrary
independent full u64 probe. The swap leaf covers every pair a!=b<9, incl. all 25 network edges
(n10-call-map.tsv); the insertion leaf covers every sorted-prefix9 backing10 state with any probe,
which is exactly what the caller asserts before the summary. Controls use [0;10]/probe0 and
[2^40;10]/probe 2^40: points of both leaf domains.

## prefix -> whole count algebra and single probe

register_u64ten: initial_prefix_count9 = count(pre[..9], probe); initial_tail = pre[9];
initial_count10 := initial_prefix_count9 + (initial_tail==probe) as usize, then
kani::assert(initial_count10 == count(pre[..10], probe)) - computed and checked, never assumed.
Swap phase (each of 25): swap_u64_net9 ensures count9_u64 preserved (pair-only modifies); adapter asserts
count9_u64==initial_prefix_count9 and *v.add(9)==initial_tail through the checked actual base.
Before insertion: asserts count9_u64==initial_prefix_count9, *tail==initial_tail and
model_count<StrictU64>(begin,10)==initial_count10 (same probe; StrictU64::probe()==ctx.probe asserted).
Insert summary ensures model_count(10) preserved; adapter asserts ==initial_count10 after. Final root
check: count10_preserved_u64(pre, v, probe) (pure typed count_matching_values over full u64).
One probe: the root's `probe` is the only value; register_u64ten writes ContextU64Ten.probe and
StrictU64::set_probe(probe) before the actual entry; nothing else sets either. Neither summary has the
statics in its modifies set; frames are re-asserted in both adapters and after return.

## G1 <-> G2 source identity

G1 and G2 are planned on the same library commit a6010df7b451da55d4227ad5960b0c93992f10f0 / tree
514c6f841cf2af3b27f6d9aa8f27c86e24c562af. Between the packages only research metadata changes
(RUN-REQUEST.json := g2.request.json, packet/ledger files). If a G1R/G2R compile repair changes the
library, a new identity and source-dependency equivalence record are required (task rules).

Source identity does not establish compilation, reachability or new proof results of the caller.
