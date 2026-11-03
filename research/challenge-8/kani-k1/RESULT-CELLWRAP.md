# RESULT CELLWRAP — PASS (D2 N2 pilot: blanket Stable, key-rewriting comparator, tag permutation + frame)

Task `TASK-CELLWRAP.md` (`e3b5b86c26`), base `e0fda080f5`, packet `cellwrap/PREBUILD.md`, GO for `b4d9ad1a34`. Library commit
`5ad316e7ec`, library tree **`257cad4054926cf6a8a12475b1efca924a764beb`**: new opt-in `verify/wrap/cellwrap.rs` +
`#[cfg(kani_smallsort_controls)] mod cellwrap;` appended to `wrap.rs`; nothing else in library changed. Static 20/20
(ordinary 202 / ordinary-PFC 36 unchanged, cfg-on 384 → 387 = exact +3), rustfmt clean; no compiler warning points to
cellwrap.rs (`cellwrap/g1.warnings.txt`; the `unstable feature` lines are core `lib.rs` feature gates).
## G1 `cb236d43-b79d-46d6-8483-bcfdb9518f9b` / `cellwrap-g1-diagnostic-n2-20261103`
COMPLETE, gate and expectation true, Kani exit 1 (from the 2 controls); head/Kani `9461e07af7`/request sha256 `4a019ce8…3014`
match; check-tooling vs e0fda080f5 ok. Standard-4, controls on, jobs 1, uninit off, wall 3:06, whole-run max RSS 1984976 KiB.
| # | Root (`wrap::cellwrap::`) | Status | VT s | Fail/total | Covers | cbmc RSS | Failure location |
|---|---|---|---|---|---|---|---|
| 1 | cellwrap_stable_tags_n2 | SUCCESS = exp. | 27.65 | 0/315 | 8/8 | 0.26 GiB | — |
| 2 | cellwrap_tag_corruption_control | FAILED = exp. | 36.38 | 1/319 | 6/8 | 0.84 GiB | ensures `old(pair_tag_count(v, probe)) == …` cellwrap.rs:92 |
| 3 | cellwrap_wrong_comparator_control | FAILED = exp. | 0.25 | 1/116 | 1/2 | not sampled | `wrap canonical comparator required` wrap.rs:61 |
## Gate
Root 1 SUCCESS with all 8 covers (scratch empty / uninit tail, probe hits / misses a tag, tags exchanged / stay, entry
return, comparator changes both keys). Each control failed exactly 1 check, the assigned one, by description and location.
Root 2's 6/8 and root 3's 1/2 covers are the predicted unsat ones (corrupted tag shapes; comparator not reached); not gated.
Cost $0.1890 (own cap $0.90, reserve $0.810); project after: used $91.5270 / $98.96, reserved $0.81 (PERMANY).
## Proved (bounded)
For `v` = two initialized `Cell<TaggedKey {key: u8, tag: u8}>` at offset 1 of a 4-element backing array, any scratch of
length 0..=2 with no overlap, and the comparator fn pointer equal to `cellwrap_key_order` (reads both, writes arbitrary
keys, keeps tags, arbitrary bool), `<Cell<TaggedKey> as StableSmallSortTypeImpl>::small_sort` (blanket → insertion)
returns normally, writes only the pair, and for every u8 probe the tag count in the pair is unchanged (N2 tag
permutation); backing elements 0 and 3 and the scratch slot keep their full values. Unwind 16.
## Not proved
Any key order or stability; N > 2; the unstable blanket entry; arbitrary `FnMut` or any other comparator (the guard
rejects them); panic/unwind, uninit detection. Root 1 is opt-in (controls), not an ordinary proof.

CELLWRAP ЗАВЕРШЁН
