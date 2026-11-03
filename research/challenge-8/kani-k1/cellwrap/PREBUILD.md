# CELLWRAP PRE-BUILD review packet (G1 prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-merge, slug `cellwrap`. Prepared 2026-11-03;
T0 not started (starts at the actual G1 dispatch after coordinator GO). Registers no phase, grants no dispatch.

## Identities
- Branch `experiment/kani-k1-cellwrap-20261103`; base `e0fda080f5ea479d8f4fb801f4b42adde2b3259f` (library tree
  `d4ec476a7a…` = v6); task commit `e3b5b86c26` (TASK-CELLWRAP.md sha256 `9e07bfe7…36cb`).
- Library commit `5ad316e7ec6f5b7b961c351153a0a781016c9341`, library tree **`257cad4054926cf6a8a12475b1efca924a764beb`**.
  `verify/wrap/cellwrap.rs` (new) sha256 `7aff84c5…4e34`; `verify/wrap.rs` sha256 `6f757a1d…8c0c` = base + 3 appended
  lines (blank, `#[cfg(kani_smallsort_controls)]`, `mod cellwrap;`), at the end so `wrap.rs:61` stays put.
  smallsort.rs (`78fc8fe8…ed61`), network.rs (`d3d0047b…7f7a`) and every other library file byte-identical to base.
- Lane files (k1g.sh LANE_PATHS) at HEAD = tooling base e0fda080f5 (`git diff --stat` empty); Kani `9461e07af7`,
  nightly-2026-10-12. `check-tooling BUILD e0fda080f5…` after G1. Tool unit tests OK (python only).

## Patch (`wrap::cellwrap`, opt-in via the module gate only; no cfg inside the child)
- `TaggedKey {key: u8, tag: u8}`, `#[derive(Clone, Copy)]` = network.rs layout. Element `Cell<TaggedKey>`.
- `cellwrap_key_order` = network.rs `mutating_key_order` body (static gate: equal modulo name, `TaggedKeyCell` alias and
  cover text): volatile-reads both, writes `kani::any()` keys, keeps tags, cover "changes both keys", returns any bool.
- Reused from `wrap` (unchanged): `canonical` (address compare), `canonical_guard` (literal `wrap.rs:61`), `pair_region`,
  `always_true` (controls). New `tagged_region` = `stable_region` body for this type; `pair_tag_count` counts tags.
- `cellwrap_stable`: requires `tagged_region(v, scratch)`, `canonical(cmp, cellwrap_key_order)`; modifies the pair;
  ensures (one line, cellwrap.rs:71) `old(pair_tag_count(v, probe)) == pair_tag_count(v, probe)`. Body = `stable_cell`
  with the type: guard, then `<Cell<TaggedKey> as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut cmp)`.
- `cellwrap_stable_tag_corruption` (control-only wrapper): identical contract (ensures cellwrap.rs:92) and body, then
  `v[0]` tag `^= 1` (static gate: equal to the positive wrapper modulo name and these 2 lines).
- `cellwrap_n2_body!` = the `stable_cell_n2` body (backing4, active pair 1..3, any probe, scratch [init, uninit] with
  len 0..=2, input frame `v[0]`,`v[3]` full value, scratch frame). Roots 1 and 2 expand it; only the wrapper differs.

## Semantic diff against `wrap::stable_cell_n2` (`semantic-diff.txt`)
- Type `Cell<u8>` → `Cell<TaggedKey>`; comparator `cell_less` (pure) → `cellwrap_key_order` (rewrites keys).
- Ensures: `pair_sorted(v)` dropped (no key order can be promised); full-byte `pair_count` → tag `pair_tag_count`.
  Requires/modifies/guard/body/frame asserts unchanged in form. Covers: `input_covers` (key order/ties) replaced by probe
  hit/miss on tags, tags exchanged / tags stay (both comparator outcomes reach the ensures), entry return; plus the
  comparator's key-change cover. Scratch covers kept.

## Route (source, smallsort.rs)
`Cell<TaggedKey>` is !Freeze → blanket `impl<T> StableSmallSortTypeImpl for T` (30-47): len ≥ 2 →
`insertion_sort_shift_left(v, 1, is_less)` (574-602) → one `insert_tail(base, base+1)` (536-571): one comparison on
the two pair cells; if true, tmp = read v[1], copy v[0]→v[1], guard writes tmp → v[0]. Scratch never touched. All writes
(comparator `Cell::set`, copies) are inside the modified pair. Lane uses `--no-assert-contracts` (run-kani.sh), so root
3's plain call runs the body, as WRAP-N2 `rejects_always_true`.

## Static gate (`check_cellwrap.py` → `static-check-prebuild.json`, ok 20/20); rustfmt `--check` clean (`rustfmt-check.txt`)
Library delta exactly the 2 files; wrap.rs = base + mod lines; guard line 61 unchanged; lines ≤ 100; two one-line
ensures; expect_check needle only on them; PFC targets; plain control; mutant/comparator/TaggedKey equalities;
ordinary 202 = macsplit `ordinary-expected.txt`; ordinary PFC 36; cfg-on 384 → **387** with exact delta +3 (the roots;
`cfg-on-expected.txt`); retired unchanged; request rows; RUN-REQUEST.json = g1.request.json. No local compile, so
"no warnings" is first established by G1 (all imports/items used in cfg-on; module absent in cfg-off).

## G1 request (`g1.request.json` = RUN-REQUEST.json, sha256 `4a019ce8b2a77335a05d9cf3e8054220120bc94c97bec4e09d3003a30b6d3014`)
Validated (`--require-runner gcb-e2-standard-4 --max-total-minutes 720`): kind diagnostic, k1-merge, controls true
(`--cfg kani_smallsort_controls`), jobs 1, uninit off, 10 min/row, `--exact`, terse. Rows (`verify::wrap::cellwrap::`):

| # | Root | Expect | expect_check / gate |
|---|---|---|---|
| 1 | cellwrap_stable_tags_n2 | SUCCESS | covers 8/8 (7 harness + comparator) |
| 2 | cellwrap_tag_corruption_control | FAILED | `pair_tag_count(v, probe)`; only failure = ensures cellwrap.rs:92 |
| 3 | cellwrap_wrong_comparator_control | FAILED | `wrap canonical comparator required`; only failure = wrap.rs:61 |

Root 2 covers expected 6/8 (corruption makes both tag-shape covers unsat); root 3: guard cover sat, the comparator's
cover may be listed unsat (wrapper returns first). Covers are gated only on root 1.

## Budget / slots / window (k1g.sh budget, `budget-prebuild.txt`)
Project: 210 builds, used $91.3380, reserved by unfinished $0.8100, cap $98.96. G1 reserve (3×10+30)×$0.0135 =
**$0.810** → $92.958 ≤ cap; own spent $0 + $0.810 ≤ own cap $0.90. One build, no retry (one compile-error repair only if
own spent + reserve ≤ $0.90). Slots: 1 unfinished now (coordinator to confirm it is not k1-merge); G1 makes 2. Window
main 150 + closeout 30 from T0; G1 envelope 60 min.

## Risks
- First compile of the child: an error is a compile-error repair case (budget permits at most one).
- Description rendering of the ensures (root 2): needle is a substring of the one-line source text (SPECDIAG precedent).
- Not claimed: key order, N > 2, unstable blanket, arbitrary FnMut, panic/unwind, uninit detection.
