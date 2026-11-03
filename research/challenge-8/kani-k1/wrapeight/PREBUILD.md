# WRAPEIGHT PRE-BUILD (prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Stable owner k1-merge, slug wrapeight. Prepared 2026-11-03.
T0 = actual dispatch after coordinator GO. This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-wrapeight-20261103`; base `e8e238db9d87323fa4da011a1a8b37fb76ec91c0` (library tree
  `d4ec476a7a`, v6); task commit `fc969a7113` (TASK-WRAPEIGHT.md sha256 30d6d43a…1347).
- WRAPMORE carry-over (first library commits): `git cherry-pick 0bf64c1c32 716e094b61` → `0fede6d2f9`, `46464f84ce`;
  patch-ids equal the originals; they touch only `verify/wrap.rs` and `verify/wrap/more.rs`; library tree after them
  **`7cdb7ee5eb8343ee943c9b79b2a4ecdb04fa60b8`** = WRAPMORE G2 tree. No tooling/research/other file touched.
- WRAPEIGHT library commit `76219f4b21be267f7e2e2c543d73ee5bf40ed712`, library tree
  **`49e5af24f007a5336240c420db173d4854f777fe`**; only `wrap/more.rs` (blob `1f476056f0` → `95eb99ce41`, sha256
  4f9dee77…25d8), pure append after the WRAPMORE text (prefix byte-identical, gate check). wrap.rs sha256
  1df51c18…92be = WRAPMORE; smallsort.rs sha256 78fc8fe8…ed61 (unchanged). Kani pin 9461e07a.
- Lane files equal the base `e8e238db9d` (check-tooling base). Their delta vs the older `30f77e85` is only the
  `CAP_USD` 88.96 → 93.96 lines in `k1g.sh`; the six bound files are identical.
- Request `wrapeight/g1.request.json` = `RUN-REQUEST.json`, id `wrapeight-g1-20261103`, sha256
  7cde45d2f9fc09da6617d11fc82403cc75e01e0a06a628c77ac0fb95cc4aee9b; `validate_request(…, 720)` OK.

## Semantic diff (new items vs `*_n4` / `*_n4_backing6`; full text `semantic-diff.txt`)
- Wrappers `stable_cell_n8` :417, `unstable_cell_n8` :438, `unstable_byte_n8` :455, `unstable_byte_n9` :472: the
  N4 wrapper with 4 → N in `stable_region_n`/`span_region`, `modifies`, `span_sorted`, `span_count` (in and out of
  `old`), `from_raw_parts_mut`; SAFETY/route comments. Guard, comparator, trait call unchanged.
- Roots `*_n8_backing10` :484/:517/:541, `unstable_byte_n9_backing11` :554: backing `[l, x0..x{N-1}, r]` of N+2
  `kani::any` bytes, span `v[1..N+1]`, frame `v[0]`, `v[N+1]`; Stable Cell keeps the N4 scratch frame (slot 0
  initialized, `scratch_len ≤ 2`). Literals N4 → N8/N9. `n4_covers(a,b,c,d,probe)` → new `span_covers(x, probe)`
  :401 = the same six first-pair `input_covers` + one strictly-reversed-keys cover over the **whole** span
  (literal `wrap full-span strictly reversed keys return`). Unwind 16, unwinding assertions on, no stub.
- Old targets, helpers, roots, guard, parent wrap.rs untouched.

## Contracts (all `canonical(cmp, <same comparator>)`; ensures `span_sorted::<_,N>(v)` and
`old(span_count::<_,N>(v,probe)) == span_count::<_,N>(v,probe)`, independent full-u8 probe)
| Wrapper | requires (region) | modifies | Trait call |
|---|---|---|---|
| `stable_cell_n8` | `stable_region_n::<8>(v, scratch)` | `slice(v,8)` | `<Cell<u8> as Stable>` |
| `unstable_cell_n8` | `span_region::<Cell<u8>,8>(v)` | `slice(v,8)` | `<Cell<u8> as Unstable>` |
| `unstable_byte_n8` | `span_region::<u8,8>(v)` | `slice(v,8)` | `<u8 as Unstable>` |
| `unstable_byte_n9` | `span_region::<u8,9>(v)` | `slice(v,9)` | `<u8 as Unstable>` |

## Route by source (smallsort.rs)
- Cell Stable N8: !Freeze ⇒ blanket `default fn` (30-46) ⇒ `insertion_sort_shift_left(v,1)`: 7 tails, ≤ 7 shifts.
- Cell Unstable N8: blanket (75-88) ⇒ `small_sort_fallback` (199) ⇒ insertion from 1, as above.
- u8 N8/N9: Freeze ⇒ FreezeMarker (shared/mod.rs:13) ⇒ (90-101) ⇒ FreezeMarker+CopyMarker impl (142-171): size 1 ≤ 8
  and 1·32 ≤ 4096 (162) ⇒ `small_sort_network` (311): 2 ≤ len ≤ 32; `no_merge = len < 18` (330) ⇒ region = v[0..len]
  (333). **N8**: 8 < 9 ⇒ presorted 1 (339-346) ⇒ `insertion_sort_shift_left(region,1)` (349): 7 `insert_tail`; return
  (351). **N9**: 9 ≥ 9, < 13 ⇒ `sort9_optimal` (342; len check 424 passes; 25 straight-line `swap_if_less`), presorted
  9 ⇒ `insertion_sort_shift_left(region,9)`: offset = len passes 580, loop 593 runs 0 times; return. No merge, the
  32-slot stack array is never used.
- Unwind: max iterations 9 (`span_count`/`span_sorted`/`span_covers` at N9), insertion 7 tails × ≤ 7 shifts;
  need ≥ 10; `unwind(16)` as N2/N4.

## Harnesses and covers (`wrap::more::`, all expect SUCCESS)
| # | Root | Path | Own asserts | Covers |
|---|---|---|---|---|
| 1 | stable_cell_n8_backing10 | Stable blanket → insertion | input frame; scratch frame | 2 scratch + 7 + entry = **10** |
| 2 | unstable_cell_n8_backing10 | Unstable blanket → fallback | input frame | 7 + entry = **8** |
| 3 | unstable_byte_n8_backing10 | u8 network, insert_tail | input frame | **8** |
| 4 | unstable_byte_n9_backing11 | u8 network, sort9_optimal | input frame | **8** |
Gate: PFC SUCCESS, 0 failures, all covers satisfied (10/8/8/8). TIMEOUT/FAILED = bounded row fact, no retry; a real
counterexample is reported to the coordinator immediately.

## Static (`check_wrapeight.py` → `static-check.json` ok 29/29; rustfmt `--check`, `git diff --check` clean)
- Ordinary **202** unchanged (sha256 78c4c050…79e7); ordinary-PFC **36** unchanged.
- cfg-on 384 (base) → **392** after WRAPMORE → **396** now; exact added set = the four names above
  (`cfg-on-expected.txt`, sha256 37f96fea…c3be). Opt-in PFC counted apart: 2 → 9 → **13** (cfg-on PFC total 38 → 45
  → 49). Retired none. New PFC targets = the four wrappers, no `stub_verified`.
- No local cargo/rustc/Kani: the first compile of the four new items is the Build itself; "no warnings" is checked
  after it by `log-grep '[-]> .*smallsort'`.

## Budget / slots (`k1g.sh budget`, 2026-11-03T18:22Z)
- Project: 206 builds, used $89.9475, reserved by unfinished $0.0000, cap $93.96.
- Reserve (4×10+30)×$0.0135 = **$0.945** ⇒ 89.9475 + 0 + 0.945 = $90.8925 ≤ $93.96. Own: $0 + $0.945 ≤ $1.00.
  Compile-error repair is allowed only if own spent + $0.945 ≤ $1.00, i.e. the failed Build cost ≤ $0.055.
- Slots: project ≤ 2 unfinished, k1-merge ≤ 1; none unfinished now. Re-check `budget` immediately before dispatch.
- Window: main 150 + closeout 30 min from T0; Build envelope 70 min.

## Risks
- Insertion cost grows with N (N4 Cell 84–152 s): N8 Cell rows may TIMEOUT at 10 min — a row fact, N not reduced.
- N9 sort9_optimal: 25 compare-swaps on 9 symbolic bytes plus a 9-element count model; untested shape.
- Scope: concrete u8/Cell<u8>, fixed N8/N9 only; no generic T/F, no panic/unwind, no stability claim.
